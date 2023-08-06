# -*- coding: utf-8 -*-

def prepare(obj):
    from AccessControl.SecurityManagement import newSecurityManager
    from AccessControl.User import system
    newSecurityManager(None,system)

    from os import environ as e
    r=obj.REQUEST


