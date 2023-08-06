#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright (c) 2008 ADITAM project (contact@aditam.org)
#    License: GNU GPLv3
#
#    This file is part of the ADITAM project.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.  See the GNU General Public License
#    for more details.
#

__author__ = '$LastChangedBy: schnei_e@EPITECH.NET $'
__date__ = '$LastChangedDate: 2008-06-10 20:58:23 +0200 (mar, 10 jun 2008) $'
__version__ = '$Rev: 91 $'

"""
Create and populate the database
"""

import aditam.server
from datetime import datetime
from datetime import timedelta
from aditam.server.model.meta import metadata, Session, engine
from aditam.server.model.user import User
from aditam.server.model.group import Group
from aditam.server.model.permission import Permission
from aditam.server.model.job import Job
from aditam.server.model.command import Command, CommandOrder
from aditam.server.model.task import Task
from aditam.server.model.farmnode import FarmNode
from aditam.server.model.report import Report

def create_tables():
    """ Create the database's tables """
    from aditam.server.model import meta
    meta.metadata.drop_all(bind=meta.engine)
    meta.metadata.create_all(bind=meta.engine)

def create_admin():
    """ This will create the user admin """
    g1 = Group()
    g1.group_name = u'admin'
    Session.save(g1)
    u1 = User()
    u1.login = u'admin'
    u1.password = u'admin'
    u1.email_address = 'test@test.com'
    u1.firstname = u'John'
    u1.lastname = u'Doe'
    u1.level = 50
    u1.lang = "en"
    Session.save(u1)
    p1 = Permission()
    p1.permission_name = u"administrate"
    p1.groups.append(g1)
    Session.save(p1)
    g1.users.append(u1)
    Session.commit()

def create_commands():
    """ """
    cmd1 = Command()
    cmd1.command_line=u"ls"
    cmd1.label = u"unix list current dir"
    cmd2 = Command()
    cmd2.command_line=u"ls wqwdqwddwqwd"
    cmd2.label = u"unix list a bad dir"
    cmd3 = Command()
    cmd3.command_line=u"echo toto"
    cmd3.label = u"unix show toto"
    cmd4 = Command()
    cmd4.command_line=u"dir"
    cmd4.label = u"windows list current dir"
    Session.save(cmd1)
    Session.save(cmd2)
    Session.save(cmd3)
    Session.save(cmd4)
    Session.commit()

def create_tasks():
    """
    task1 have commands 1 and 2
    task2 have command 3
    You must launch create_commands before
   """
    task1 = Task()
    task1.label = u"test"
    task2 = Task()
    task2.label = u"test2"
    task3 = Task()
    task3.label = u"test3"
    task4 = Task()
    task4.label = u"Unix OK"
    task5 = Task()
    task5.label = u"Windows OK"
    Session.save(task1)
    Session.save(task2)
    Session.save(task3)
    Session.save(task4)
    Session.save(task5)

    # Link task with commands
    cmd1 = Session.query(Command).get(1)
    cmd2 = Session.query(Command).get(2)
    cmd3 = Session.query(Command).get(3)
    cmd4 = Session.query(Command).get(4)
    command_ord1 = CommandOrder()
    command_ord2 = CommandOrder()
    command_ord3 = CommandOrder()
    command_ord4 = CommandOrder()
    command_ord5 = CommandOrder()
    command_ord6 = CommandOrder()
    command_ord1.position = 1
    
    command_ord2.position = 2
    command_ord3.position = 1
    
    command_ord4.position = 1
    command_ord5.position = 2

    command_ord6.position = 1

    command_ord1.task = task1
    command_ord2.task = task1
    
    command_ord3.task = task2
    
    command_ord4.task = task4
    command_ord5.task = task4
    
    command_ord6.task = task5
    
    command_ord1.command = cmd1
    command_ord2.command = cmd2

    command_ord3.command = cmd3
    
    command_ord4.command = cmd1
    command_ord5.command = cmd3
    
    command_ord6.command = cmd4

    Session.save(command_ord1)
    Session.save(command_ord2)
    Session.save(command_ord3)
    Session.save(command_ord4)
    Session.save(command_ord5)
    Session.save(command_ord6)
    Session.commit()

def create_farmnodes():
    """
    You must launch create_commands before
    farmnode 1 have commands 1 and 2
    farmnode 2 have commands 1
    """
    cmd1 = Session.query(Command).get(1)
    cmd2 = Session.query(Command).get(2)
    cmd3 = Session.query(Command).get(3)
    cmd4 = Session.query(Command).get(3)

    farmnode1 = FarmNode()
    farmnode1.name = u"totosrv"
    farmnode1.ip = "127.0.0.1"
    farmnode1.port = "4242"
    farmnode2 = FarmNode()
    farmnode2.name = u"titisrv"
    farmnode2.ip = "127.0.0.1"
    farmnode2.port = "4243"

    farmnode3 = FarmNode()
    farmnode3.name = u"unix1"
    farmnode3.ip = "192.168.1.2"
    farmnode3.port = "4243"
    
    farmnode4 = FarmNode()
    farmnode4.name = u"win1"
    farmnode4.ip = "192.168.1.1"
    farmnode4.port = "4243"

    farmnode1.commands.append(cmd1)
    farmnode1.commands.append(cmd2)
    farmnode2.commands.append(cmd1)
    farmnode3.commands.append(cmd1)
    farmnode3.commands.append(cmd2)
    farmnode3.commands.append(cmd3)
    farmnode4.commands.append(cmd4)

    Session.save(farmnode1)
    Session.save(farmnode2)
    Session.save(farmnode3)
    Session.save(farmnode4)
    Session.commit()

def create_jobs():
    """
    You must create task before
    Job1 is link to the task 1
    Job2 is link to the task 2
    """
    task1 = Session.query(Task).get(1)
    task2 = Session.query(Task).get(2)
    task3 = Session.query(Task).get(3)
    task4 = Session.query(Task).get(4)
    task5 = Session.query(Task).get(5)
    
    report1 = Report()
    report2 = Report()
    report3 = Report()
    report4 = Report()
    report5 = Report()
    report6 = Report()
    report7 = Report()
    report8 = Report()
    report9 = Report()
    Session.save(report1)
    Session.save(report2)
    Session.save(report3)
    Session.save(report4)
    Session.save(report5)
    Session.save(report6)
    Session.save(report7)
    Session.save(report8)
    Session.save(report9)

    job1 = Job()
    job1.type = u"unix ok"
    job1.task = task4
    job1.execute_date = datetime.now() + timedelta(seconds=15)
    job1.status = "running"
    job1.report = report1

    job2 = Job()
    job2.type = u"win ok"
    job2.task = task5
    job2.execute_date = datetime.now() + timedelta(seconds=20)
    job2.status = "running"
    job2.report = report2

    job3 = Job()
    job3.type = u"failled 1"
    job3.task = task1
    job3.execute_date = datetime.now() + timedelta(minutes=1)
    job3.status = "running"
    job3.report = report3
    
    job4 = Job()
    job4.type = u"failled 2"
    job4.task = task2
    job4.execute_date = datetime.now() + timedelta(minutes=1)
    job4.status = "running"
    job4.report = report4
    
    Session.save(job1)
    Session.save(job2)
    Session.save(job3)
    Session.save(job4)
    Session.commit()

def launch():
    create_tables()
    create_admin()
    create_commands()
    create_tasks()
    create_farmnodes()
    create_jobs()

