=====================
aditam.server package
=====================

.. contents::

Description
===========

ADITAM is a remote task scheduler which facilitates mass task managing over heterogeneous network.
The project contains :

- **adtitam.core** (Python) : the common parts of the Aditam agent and server
- **aditam.server** (Python) : the server in charge of scheduling and distributing the tasks
- **aditam.agent** (Python) : the agent handles orders sent by the tasks manager and execute the tasks sent by it
- **aditam web gui** (php) : the aditam web interface http://www.aditam.org/downloads/cake.tar.gz

This package contains the server of the ADITAM project. It is in charge of scheduling and distributing the tasks.
Informations are stored in database and gave to the agents when tasks are to be executed.

Requires
========

- Python 2.5 : http://www.python.org/download/
- easy_install : http://peak.telecommunity.com/DevCenter/EasyInstall#installing-easy-install

You must add C:\\Python2.5 and C:\\Python2.5\\Scripts in your Path on Windows.

OS Independent installation
===========================

Module installation
-------------------

Enter in a console::

   easy_install aditam.server

Configure and install the database
----------------------------------

Install the Python module for your database : http://www.sqlalchemy.org/docs/04/dbengine.html#dbengine_supported

Enter in a console::

   aditam-admin.py --create-db --config-db

Follow the instructions.

Configure the server
--------------------
Enter in a console::

   aditam-admin.py --server

Follow the instructions.
