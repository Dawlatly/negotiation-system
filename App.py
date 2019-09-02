# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 19:13:17 2019

@author: Mahmoud Dawlatly
"""
from tkinter import *
from tkinter import messagebox
import sqlite3
import User,Case,Objective,Nsga2
import random

#This is the main class and file that includes all core functionalities
class App:
    #Intialisation of the application
    root = Tk()
    root.focus_set()
    
    #This function saves the case into the database
    def save_case(self,a_list,desc,user,user1,frame,page):
        final_list = []
        priority_index = a_list[0].priority.get()
        for a in a_list:
            if(a.desc.get() and a.mn.get().isdigit() and a.mx.get().isdigit()):
                if(a.maximise.get() == "maximise"):
                    a.maximise.set(True)
                else:
                    a.maximise.set(False)
                final_list.append(a)
            else:
                messagebox.showerror("Error", "Invalid or empty input")
                return
        for x in final_list:
            x.priority.set(0)
        final_list[priority_index].priority.set(1)
        conn = sqlite3.connect('App.db')
        cursor = conn.execute('INSERT INTO "Case" (Description) VALUES(?)',(desc,))
        conn.commit()
        cursor = conn.execute('SELECT Id FROM "Case" WHERE Description=?', (desc,))
        id = cursor.fetchall()
        id = id[0][0]
        conn.close()
        
        conn = sqlite3.connect('App.db')
        cursor = conn.execute('SELECT Id FROM User WHERE Username=?', (user,))
        user_id = cursor.fetchall()
        user_id = user_id[0][0]
        conn.close()
        
        conn = sqlite3.connect('App.db')
        cursor = conn.execute('SELECT Id FROM User WHERE Username=?', (user1,))
        oppuser_id = cursor.fetchall()
        oppuser_id = oppuser_id[0][0]
        conn.close()
        
        for a in final_list:
            conn = sqlite3.connect('App.db')
            cursor = conn.execute('INSERT INTO Objective (Description, Minimum,Maximum,Priority,Maximise,CaseId) VALUES(?,?,?,?,?,?)',(a.desc.get(),a.mn.get(),a.mx.get(),a.priority.get(),a.maximise.get(),id))
            conn.commit()
            conn.close()

        conn = sqlite3.connect('App.db')
        cursor = conn.execute('INSERT INTO User_Case (UserId, CaseId) VALUES (?,?)',(user_id,id))
        conn.commit()
        conn.close()
        
        conn = sqlite3.connect('App.db')
        cursor = conn.execute('INSERT INTO User_Case (UserId, CaseId) VALUES (?,?)',(oppuser_id,id))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Message", "Case created successfully")
        
        frame.destroy()
        page.destroy()
        
    #This function shows the objectives for the user to fill in
    def show_objectives(self,no_objectives,page,desc,user,user1):
        user = user.get()
        frame = Toplevel(page)
        frame.geometry("800x400")
        frame.title("Objectives")
        l = []
        a_list = []
        priority = IntVar()
        for i in range(0,int(no_objectives.get())):
            obj_label = Label(frame, text="Objective  "+str(i+1))
            obj_label.place(x=100,y=(50+i*30))
            obj = StringVar()
            obj_entry = Entry(frame,textvar=obj)
            obj_entry.place(x=180,y=(50+i*30))
            mx = StringVar()
            max_label = Label(frame,text="Max")
            max_label.place(x=280,y=(50+i*30))
            max_entry = Entry(frame,textvar=mx,width=5)
            max_entry.place(x=320,y=(50+i*30))
            mn = StringVar()
            min_label = Label(frame,text="Min")
            min_label.place(x=360,y=(50+i*30))
            min_entry = Entry(frame,textvar=mn,width=5)
            min_entry.place(x=400,y=(50+i*30))
            choices = ["maximise","minimise"]
            obj_value = StringVar()
            #obj_value[i].trace_add('write', lambda *args: print(obj_value[i].get()))
            obj_menu = OptionMenu(frame,obj_value,*choices)
            obj_menu.place(x=440,y=(50+i*30))
            
            priority.set(0)
            Radiobutton(frame, text="Priority",variable=priority,value=i).place(x=520,y=(50+i*30))

            
            o = Objective.Objective(obj,mx,mn,obj_value,priority)
            a_list.append(o)
        save = Button(frame,text="Save",command=lambda : (self.save_case(a_list,desc,user,user1,frame,page)))
        save.place(x=700,y=50)
            
    #This function displays the page to create a case 
    def create_case(self,aPage,user):
        page = Toplevel(aPage)
        page.geometry("500x300")
        page.title("Create Case")
        desc_text = Label(page,text="Case Description")
        desc_text.place(x=100,y=50)
        desc_entry = Text(page, height=3,width=20)
        desc_entry.place(x=200,y=50)
        obj_label = Label(page, text="Number of Objectives")
        obj_label.place(x=100,y=150)
        obj_value = StringVar()
        userValue = StringVar()
        choices = ["2","3","4","5","6","7","8","9","10"]        
        obj_menu = OptionMenu(page,obj_value,*choices,command=lambda x: (self.show_objectives(obj_value,page,desc_entry.get('1.0', END),userValue,user)))
        obj_menu.place(x=200,y=150)
        user_text = Label(page, text="Opposing Party")
        user_text.place(x=100,y=100)
        conn = sqlite3.connect('App.db')
        cursor = conn.execute("SELECT Username FROM User")
        data = cursor.fetchall()
        for i in range(0,len(data)):
            data[i] = data[i][0]
        conn.close()
        user_menu = OptionMenu(page, userValue, *data)
        user_menu.place(x=200,y=100)

    #This function shows the best 4 offers that are generated from MOEA
    def view_offer(self,event,offers,page,objs):
        offer = event.widget.cget("text")
        offer = int(offer.replace("Offer ",""))-1
        offer = offers[offer]
        print(event.widget.cget("text"))
        offer_page = Toplevel(page)
        offer_page.geometry("500x500")
        offer_page.title("Offer Details")
        for i in range(0,len(offer)):
            obj_label = Label(offer_page, text=str(objs[i].desc))
            obj_label.place(x=100,y=(50+i*30))
            obj = StringVar()
            obj.set(offer[i])
            obj_entry = Entry(offer_page,textvar=obj)
            obj_entry.place(x=160,y=(50+i*30))
        
    #This function creates an instance of the MOEA and runs it according to the objectives
    #set by the user and the case
    def nsga2(self,objs,page):
        algo = Nsga2.Nsga2(objs)
        offer1 = algo.evolve()
        offer2 = algo.evolve()
        offer3 = algo.evolve()
        offer4 = algo.evolve()
        offer1 = offer1[random.randint(2,len(offer1)-1)]
        offer2 = offer2[random.randint(2,len(offer2)-1)]
        offer3 = offer3[random.randint(2,len(offer3)-1)]
        offer4 = offer4[random.randint(2,len(offer4)-1)]
        offers = []
        offers.append(offer1[:-2])
        offers.append(offer2[:-2])
        offers.append(offer3[:-2])
        offers.append(offer4[:-2])
        offer_page = Toplevel(page)
        offer_page.geometry("500x500")
        for j in range(0,len(offers)):
            case_label = Label(offer_page, text=r"Offer "+str(j+1), fg="blue", cursor="hand2")
            case_label.place(x=100,y=(50+j*50))
            case_label.bind("<Button-1>", lambda x: (self.view_offer(x,offers,offer_page,objs)))
        
    #This function retrieves the case the user is involved in from the database
    def callback(self,event,page):
        case_page = Toplevel(page)
        case_page.geometry("800x400")
        conn = sqlite3.connect('App.db')
        cursor = conn.execute('SELECT Id FROM "Case" WHERE Description=?', (event.widget.cget("text")+"\n",))
        case_id = cursor.fetchall()
        case_id = case_id[0][0]
        case_page.title("Case " + str(case_id))
        cursor = conn.execute('SELECT Description,Minimum,Maximum,Priority,Maximise FROM Objective WHERE CaseId=?', (case_id,))
        objectives = cursor.fetchall()
        conn.close()
        
        objs = []
        
        for i in range(0,len(objectives)):
            obj_label = Label(case_page, text="Objective  "+str(i+1))
            obj_label.place(x=100,y=(50+i*30))
            obj = StringVar()
            obj.set(objectives[i][0])
            obj_entry = Entry(case_page,textvar=obj)
            obj_entry.place(x=180,y=(50+i*30))
            mx = StringVar()
            mx.set(objectives[i][2])
            max_label = Label(case_page,text="Max")
            max_label.place(x=280,y=(50+i*30))
            max_entry = Entry(case_page,textvar=mx,width=5)
            max_entry.place(x=320,y=(50+i*30))
            mn = StringVar()
            mn.set(objectives[i][1])
            min_label = Label(case_page,text="Min")
            min_label.place(x=360,y=(50+i*30))
            min_entry = Entry(case_page,textvar=mn,width=5)
            min_entry.place(x=400,y=(50+i*30))
            o = Objective.Objective(objectives[i][0],objectives[i][1],objectives[i][2],objectives[i][3],objectives[i][4])
            objs.append(o)
        
        generate_btn = Button(case_page,text="Generate Deals",command=lambda: (self.nsga2(objs,case_page)))
        generate_btn.place(x=600,y=50)
        
    #This function displays the cases the user is involved in
    def browse_cases(self,page,user):
        desc = []
        conn = sqlite3.connect('App.db')
        cursor = conn.execute('SELECT Id FROM User WHERE Username=?', (user,))
        user_id = cursor.fetchall()
        user_id = user_id[0][0]
        conn.close()
        
        conn = sqlite3.connect('App.db')
        cursor = conn.execute('SELECT CaseId FROM User_Case WHERE UserId=?', (user_id,))
        case_id = cursor.fetchall()
        print(user_id)
        for i in range(0,len(case_id)):
            case_id[i] = case_id[i][0]
        conn.close()
        
        for case in case_id:
            conn = sqlite3.connect('App.db')
            cursor = conn.execute('SELECT Description FROM "Case" WHERE Id=?', (case,))
            data = cursor.fetchall()
            desc.append(data[0][0].rstrip("\n"))
            conn.close()
        
        cases_page = Toplevel(page)
        cases_page.geometry("500x300")
        cases_page.title("All Cases")
        
        for j in range(0,len(desc)):
            case_label = Label(cases_page, text=r""+desc[j], fg="blue", cursor="hand2")
            case_label.place(x=100,y=(50+j*50))
            case_label.bind("<Button-1>", lambda x: (self.callback(x,cases_page)))
            
        
    #This function is responsible for logging in by checking if the user exists
    def login(self,usrname,password):
        conn = sqlite3.connect('App.db')
        
        cursor = conn.execute("SELECT Username, Password from User WHERE Username=?",(usrname.get(),))
        data = cursor.fetchall()
        if(data):    
            for row in data:
               print ("Username = ", row[0]) 
               print ("Password = ", row[1], "\n")
            
            if(row[1] == password.get()):
                self.welcome_page(row[0])
                print("Logged In")
            else:
                messagebox.showerror("Error","The password you have entered is incorrect")
        else:
            messagebox.showerror("Error","The username you entered doesn't exist")
        conn.close()
    
    #This fucntion displays the home page which is the first page
    def home_page(self):
        self.root.geometry("500x300")
        self.root.title("Home")
        
        title_text =Label(self.root, text="Please login or register if you are a new user")
        title_text.place(x=150,y=50)
        
        usrText =Label(self.root, text="Username: ")
        usrText.place(x=150,y=100)
        
        usrname = StringVar()
        usrEntry = Entry(self.root, textvar=usrname)
        usrEntry.place(x=220,y=100)
        usrEntry.focus_set()
        
        pass_text =Label(self.root, text="Password: ")
        pass_text.place(x=150,y=130)
        
        password = StringVar()
        passEntry = Entry(self.root, textvar=password,show="*")
        passEntry.place(x=220,y=130)
        
        loginBtn = Button(self.root,text="Sign In", command=lambda:(self.login(usrname,password)))
        loginBtn.place(x=220,y=160)
        
        register_btn = Button(self.root,text="Register", command=self.register)
        register_btn.place(x=280,y=160)
        
        self.root.mainloop()
        
    #This function shows the first page when the user logs in successfully
    def welcome_page(self,user):
        App.root.iconify()
        home = Toplevel(App.root)
        home.geometry("500x300")
        title_text =Label(home, text="Welcome, "+user)
        title_text.place(x=50,y=30)
        browse_btn = Button(home,text="Browse Cases",command=lambda: (self.browse_cases(home,user)))
        browse_btn.place(x=100,y=100)
        create_btn = Button(home,text="Create a new Case",command=lambda: (self.create_case(home,user)))
        create_btn.place(x=300,y=100)
    
    
    #This function displays the registration page
    def register(self):
        rgstr = Toplevel(App.root)
        rgstr.geometry("500x300")
        rgstr.title("Sign Up")
        title_text =Label(rgstr, text="Please enter your details")
        title_text.place(x=150,y=40)
        
        #This is a nested function to check if the passwords match
        def check():
            if(password.get() == cpassword.get()):
                conn = sqlite3.connect("App.db")
                with conn:
                    cursor = conn.cursor()
                cursor.execute('CREATE TABLE IF NOT EXISTS User (Id INTEGER PRIMARY KEY, Username TEXT, Fname TEXT, Lname TEXT, Password TEXT)')
                cursor.execute('CREATE TABLE IF NOT EXISTS "Case" (Id INTEGER PRIMARY KEY, Description TEXT)')
                cursor.execute('CREATE TABLE IF NOT EXISTS Objective (Id INTEGER PRIMARY KEY, Description TEXT, Minimum FLOAT, Maximum FLOAT, Priority INTEGER, Maximise BOOLEAN, CaseId INTEGER, FOREIGN KEY (CaseId) REFERENCES "Case"(Id))')
                cursor.execute('CREATE TABLE IF NOT EXISTS User_Case (UserId INTEGER, CaseId INTEGER, FOREIGN KEY(UserId) REFERENCES User(Id), FOREIGN KEY(CaseId) REFERENCES "Case"(Id))')
                cursor.execute('SELECT Username FROM User WHERE Username=?', (usrname.get(),))
                row = cursor.fetchall()
                conn.commit()
                if(not row):
                    user = User.User(usrname,fn,ln,password)
                    user.save()
                    messagebox.showinfo("Message", "Registration successful")
                    rgstr.destroy()
                else:
                    messagebox.showerror("Error", "This username already exists")
            else:
                messagebox.showerror("Error", "The passwords do not match")
        
        usrname_text =Label(rgstr, text="Username: ")
        usrname_text.place(x=150,y=70)
    
        usrname = StringVar()
        usrname_entry = Entry(rgstr, textvar=usrname)
        usrname_entry.place(x=220,y=70)
        
        fn_text =Label(rgstr, text="First Name: ")
        fn_text.place(x=150,y=100)
        
        fn = StringVar()
        fn_entry = Entry(rgstr, textvar=fn)
        fn_entry.place(x=220,y=100)
        
        ln_text =Label(rgstr, text="Last Name: ")
        ln_text.place(x=150,y=130)
        
        ln = StringVar()
        ln_entry = Entry(rgstr, textvar=ln)
        ln_entry.place(x=220,y=130)
        
        pass_text =Label(rgstr, text="Password: ")
        pass_text.place(x=150,y=160)
        
        password = StringVar()
        passEntry = Entry(rgstr, textvar=password,show="*")
        passEntry.place(x=220,y=160)
        
        cpass_text =Label(rgstr, text="Confirm Password: ")
        cpass_text.place(x=150,y=190)
        
        cpassword = StringVar()
        cpass_entry = Entry(rgstr, textvar=cpassword,show="*")
        cpass_entry.place(x=260,y=190)
        
        register_btn = Button(rgstr,text="Register",command=check)
        register_btn.place(x=280,y=210)
        
    def __init__(self):
        self.home_page()