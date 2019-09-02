# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 19:14:36 2019

@author: Mahmoud Dawlatly
"""
import sqlite3
import Case

#This is a class definition of the user with a function to create it
class User:
    
    def __init__(self, usrname,fname,lname,password):
        self.usrname = usrname
        self.fname = fname
        self.lname = lname
        self.password = password
        self.cases = []
        
    def save(self):
        conn = sqlite3.connect("App.db")
        with conn:
            cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS User (Username TEXT, Fname TEXT, Lname TEXT, Password TEXT)')
        cursor.execute('INSERT INTO User (Username, Fname,Lname,Password) VALUES(?,?,?,?)',(self.usrname.get(),self.fname.get(),self.lname.get(),self.password.get()))
        conn.commit()
        