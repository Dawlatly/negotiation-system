# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 15:25:13 2019

@author: Mahmoud Dawlatly
"""
import random
import math
import numpy as np
import Objective
import matplotlib.pyplot as plt
from sklearn.preprocessing import minmax_scale


class Nsga2:
    #Intialisation of the class object
    def __init__(self,objectives):
        #Assigning Hyperparameters
        self.N = 200
        self.max_iters = 500
        self.sd = 10
        self.objs = objectives
        self.fpop = np.zeros([self.N,len(self.objs)])
        self.i = 0
        self.weights = []
        #Assigning the weights of each objective based on the priority provided by the user
        for o in self.objs:
            if(o.priority == 1):
                self.weights.append(0.2)
            else:
                self.weights.append(0.8/(len(self.objs)-1))
            pop = np.random.uniform(o.mn,o.mx,(self.N,1))
            pop = pop.tolist()
            for j in range(0,len(pop)):
                pop[j] = pop[j][0]
            self.fpop[:,self.i] = pop
            self.i = self.i+1
        #Scaling the objective values to be in range of 1 to 10
        for o in self.objs:
            ls = minmax_scale([o.mn,o.mx],feature_range=(1,10))
            o.mn = ls[0]
            o.mx = ls[1]
        
    
    
    #This function will return the optimal front for each objective
    def get_pareto(self,pop):
        pareto = np.ones(len(pop),dtype=bool)
        temp = pop[:,-2:]
        for i in range(len(temp)):
            for j in range(len(temp)):
                if all(temp[i] <= temp[j]) and any(temp[i] < temp[j]):
                    pareto[i] = 0
                break
        return pop[pareto],pop[pareto == 0];
    
    #This function will calculate the crowding distance between the chosen values and returns
    #the ones with the highest crowding distances
    #remove_pop is the number of instances to remove to achieve the maximum population defined
    def crowding_distance(self,pop, remove_pop):
        temp_pop = pop[:,-2:]
        distance = np.zeros((len(temp_pop),1))
        for i in range(np.shape(temp_pop)[1]):
            temp_crowd = np.sort(temp_pop[:,i])[::-1]
            temp_crowd[0] = 1
            for j in range(1,len(temp_crowd)-1):
                idx = np.where(temp_pop==temp_crowd[j])
                distance[idx[0]] += (temp_crowd[j+1]-temp_crowd[j-1])
        pop = np.hstack((pop,distance))
        pop = pop[pop[:,-1].argsort()[::-1]]
        pop = pop[:-remove_pop,:]
        pop = pop[:,:-1]
        return pop
        
        return True
    #This function runs the Nsga2 algorithm
    def pareto(self,pop):
        front = np.copy(pop)
        final_front = np.array([])
        final_front.shape = (0,len(front[0]))
        while (len(final_front) < self.N):
            front,not_front = self.get_pareto(front)
            total_front = len(front) + len(final_front)
            if(total_front > self.N):
                front = self.crowding_distance(front,total_front-self.N)
            final_front = np.vstack((final_front,front.tolist()))
            front = not_front
        return final_front
    
    #This function runs on generation of a standard genetic algorithm
    def ga(self,pop):
        children = self.two_point_crossover(pop)
        mutated_children = self.uniform_mutation(children)
        
        pop = np.vstack((pop,mutated_children))
        q = minmax_scale(pop,feature_range=(1,10))
        
        pop = np.hstack((pop,self.buyer_fitness(q)))
        pop = np.hstack((pop,self.seller_fitness(q)))
        
        return pop
    
    #This function begins the process of MOEA by running GA first and then NSGA-II until the
    #number of generations specified is reached
    def evolve(self):
        gen = 0
        pop = self.ga(self.fpop)
        optimal_front = self.pareto(pop)
        while(gen < self.max_iters):
            optimal_front = self.ga(optimal_front[:,:-2])
            optimal_front = self.pareto(optimal_front)
            gen += 1
        return optimal_front
        
    #This function calculates the probability of the buyer accepting the offer
    def buyer_fitness(self,pop):
        fit = np.zeros([self.N*2,1])    
        for i in range(0,len(pop)):
            for j in range(0,len(pop[i])):
                if(self.objs[j].maximise == 1):
                    accp = math.exp(-((pop[i][j]-self.objs[j].mx)/self.sd)**2)
                else:
                    accp = math.exp(-((pop[i][j]-self.objs[j].mn)/self.sd)**2)

                fit[i] += (accp*self.weights[j])
        return fit
    
    #This function calculates the probability of the seller accepting the offer
    #The objective requirements are inversed as an assumption to evaluate the performance
    #of the model in the toughest scenario where each objective is conflicted by both parties
    def seller_fitness(self,pop):
        fit = np.zeros([self.N*2,1])    
        for i in range(0,len(pop)):
            for j in range(0,len(pop[i])):
                if(self.objs[j].maximise == 1):  
                    accp = math.exp(-((pop[i][j]-self.objs[j].mn)/self.sd)**2)
                else:
                    accp = math.exp(-((pop[i][j]-self.objs[j].mx)/self.sd)**2)

                fit[i] += (accp*self.weights[j])
        return fit
    
    #This function carries out a random two-point crossover between the objective values
    def two_point_crossover(self,pop):
        pop = np.array(pop)
        child = np.empty((len(pop),len(pop[0])))
        for i in range(0,len(pop),2):    
            crossover_point1 = random.randint(0,len(pop[0]))
            crossover_point2 = random.randint(0,len(pop[0]))
            parent1 = i%pop.shape[0]
            parent2 = (i+1)%pop.shape[0]
            if((i+1)%pop.shape[0] != 0):
                child[parent1] = pop[parent1]
                child[parent2] = pop[parent2]
                if(crossover_point1 < crossover_point2):    
                    child[parent1][crossover_point1:crossover_point2] = pop[parent2][crossover_point1:crossover_point2]
                    child[parent2][crossover_point1:crossover_point2] = pop[parent1][crossover_point1:crossover_point2]
                elif(crossover_point2 < crossover_point1):
                    child[parent1][crossover_point2:crossover_point1] = pop[parent2][crossover_point2:crossover_point1]
                    child[parent2][crossover_point2:crossover_point1] = pop[parent1][crossover_point2:crossover_point1]
            else:
                child[i] = pop[i]
        return child
                
    #This function carries out random mutation of each objective value
    def uniform_mutation(self,pop):
        children = pop.copy()
        for i in range(0,len(children)):
            rate = np.random.uniform(-10,10,1)
            rand_index = random.randint(0,len(children[0])-2)
            children[i][rand_index] += rate[0]
        return children

#The snippet of code below was used in evaluation and retrieving results for analysis of the
#model
#To execute this file alone, please uncomment the code below and run right away


#al = []
#price = Objective.Objective("price",200,100,0,1)
#quantity = Objective.Objective("quantity",1000,200,1,0)
#delivery = Objective.Objective("Delivery",7,2,0,0)
#o4 = Objective.Objective("Objective4",80,50,1,0)
#o5 = Objective.Objective("Objective5",5,1,0,0)
#o6 = Objective.Objective("Objective6",3000,1500,0,0)
#o7 = Objective.Objective("Objective7",270,150,1,0)
#o8 = Objective.Objective("Objective8",64,40,1,0)
#o9 = Objective.Objective("Objective9",8800,5400,1,0)
#o10 = Objective.Objective("Objective10",700,600,0,0)
#al.append(price)
#al.append(quantity)
#al.append(delivery)
#al.append(o4)
#al.append(o5)
#al.append(o6)
#al.append(o7)
#al.append(o8)
#al.append(o9)
#al.append(o10)
#test = Nsga2(al)
#b = test.evolve()
#c = test.evolve()
#d = test.evolve()
#e = test.evolve()
#
#
#plt.title("NSGA-II") 
#
## Plot the points using matplotlib 
#plt.scatter(b[2:,-2],b[2:,-1])
#plt.scatter(c[2:,-2],c[2:,-1])
#plt.scatter(d[2:,-2],d[2:,-1])
#plt.scatter(e[2:,-2],e[2:,-1])
#plt.xlabel("Buyer Acceptability")
#plt.ylabel("Seller Acceptability")
#plt.show()


    
