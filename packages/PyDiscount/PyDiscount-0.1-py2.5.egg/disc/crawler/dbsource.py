# -*- coding:utf-8 -*-
'''
Created on 2009-4-20

@author: mingqi
'''
import MySQLdb

g_conn = None

def get_conn():
    global g_conn
    if g_conn:
        return g_conn
    g_conn = MySQLdb.connect(host="localhost",
                             user="root",
                             passwd="root", 
                             db="tbd",
                             use_unicode=True,
                             charset="utf8",
                             client_flag=2)
    return g_conn
    
    