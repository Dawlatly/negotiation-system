# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 15:31:20 2019

@author: Mahmoud Dawlatly
"""
import Objective

#This is a Case class that includes all objectives and parties to be stored in the database
class Case:
    def __init__(self,desc,objectives,parties):
        self.desc = desc
        self.objectives = objectives
        self.parties = parties