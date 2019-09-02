# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 16:15:58 2019

@author: Mahmoud Dawlatly
"""
#This is an Objective class to define one objective that will be negotiated
class Objective:
    def __init__(self,desc,mx,mn,maximise,priority):
        self.desc = desc
        self.mx = mx
        self.mn = mn
        self.maximise = maximise
        self.priority = priority
        