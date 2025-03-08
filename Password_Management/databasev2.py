#!/usr/bin/env python
'''created by: Lalit Jagotra'''
import sqlite3
import sys
import secrets
from datetime import timedelta
from datetime import datetime
from datetime import time
import re
import os
class database:
    def __init__(self,**kwargs):
        '''This is the constructor of the class
        database it takes dictionary as argument 
        and set the filename and table'''
        self.filename = kwargs['filename']
        self.table = kwargs['table']
    
    def connect_database(self):
        ''' This creates a database connection'''
        self.db = sqlite3.connect(self.filename)
        self.db.row_factory = sqlite3.Row
    
    def sql_noparam(self,query):
        '''This method is user to run non select queries
        which do not return anything and doesnot take parameters'''
        self.db.execute(query)
        self.db.commit()
    
    def sql_do(self,query,params):
        '''This method is user to run non select queries
        which do not return anything'''
        self.db.execute(query, params)
        self.db.commit()
        print("done")

    def create_table(self,columns):
        #This method is used for creating table
        self.db.execute('drop table if exists {}'.format(self.table))
        l = len(columns)
        query = 'create table ' + self.table + ' ('
        for key in columns.keys():
            query += key + ' ' + columns[key] + ', '
        query=query[:len(query)-2]
        query+= ' )'
        self.cursor= self.db.execute(query)

    def insert(self,columns):
        listk = sorted(columns.keys())
        listv = [columns[k] for k in listk]
        query = 'insert into {} ({}) values ({})'.format(self.table, ','.join(listk), ','.join('?' for k in range(len(listk))))
        self.db.execute(query,listv)
        self.db.commit()

    def delete(self,id):
        query = 'delete from {} where ROW_ID = ?'.format(self.table)
        self.db.execute(query,(id,))
        self.db.commit()

    def update(self,id,columns):
        try:
            updaterow=self.retrieve_row(id)
            for key in columns.keys():    
                updaterow[key]= columns[key]
            self.delete(id)
            self.insert(updaterow)
        finally:
            self.db.commit()

    def retrieve_row(self,id):
        query = 'select * from {} where ROW_ID = ?'.format(self.table)
        self.cursor = self.db.execute(query,(id,))
        return dict(self.cursor.fetchone())

    def userauthenticate(self,params=tuple()):
        if self.table!="users":
            raise print("Error: Unauthorized Query")
            return
        query = 'select * from {} where username = ? and password= ?'.format(self.table)
        self.cursor = self.db.execute(query,params)
        try:
            return dict(self.cursor.fetchone())
        except TypeError as e:
            print("Error occured: athentication Failed!, {}".format(e))
            return {"username":None,"password":None}
    def retrieve_rows(self):
        query = 'select * from {}'.format(self.table)
        retrieverows=list()
        self.cursor = self.db.execute(query)
        #print("this is where cursor is: {}".format(dict(self.cursor)))
        for self.rows in self.cursor:
            retrieverows.append(dict(self.rows))
        return retrieverows
        '''This query returns the number of records in the table as a cursor object which 
	will be a tuple with single entry.(due to Row_factory)So I refreneced its 0th element whcih will return a number'''

    def countrecs(self):
        query ='SELECT COUNT(*) FROM {}'.format(self.table)
        self.cursor = self.db.execute(query)
        return self.cursor.fetchone()[0]

''' This is the main program to test this interface performing the basic crud operation----'''
def main():
    dbdir=os.getcwd()
    db1 = database(filename= dbdir + '\\authenticate',table='users')
    db1.connect_database()
    query = 'drop table if exists users'
    db1.sql_noparam(query)
    db1.create_table(dict(ROW_ID= "int", username= "char", password= "varchar", masterenc="char"))
    usertabledb=str()
    print("---------------------All Databases are re-initialized------------------------------")
    for item in db1.retrieve_rows():
            usertable=(item['username']).split('@')
            for item1 in usertable:
                try:
                    usertabledb+=item1.split('.')[0] + item1.split('.')[1]
                except IndexError as e:
                    print("Error:{}".format(e))
                    usertabledb+=item1
            db2 = database(filename=dbdir+ '\\login',table=usertabledb)
            db2.connect_database()
            query = 'drop table if exists ' + usertabledb
            db1.sql_noparam(query)
            db2.create_table(dict(ROW_ID= "int", username= "char", password= "char",applicationname="char", applicationurl="char"))
            usertabledb=str()

if __name__ == '__main__':main()
