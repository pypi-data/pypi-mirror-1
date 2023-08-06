.. contents:: **Table of Contents**

=============
Aditam Server
=============

------------
Description
------------

ADITAM facilitates mass task managing over heterogeneous network.
The project is slipt in 5 parts :
 * adtitam.core (Python) : the common parts of the Aditam agent and server.
 * aditam.server (Python) : the server
 * aditam.agent (Python) : the agent

 * aditam clac (php) : a command line ui.
 * aditam gui (php) : the aditam website.

This package contains the Server part of the ADITAM project.

--------------------
Install Instructions
--------------------

Requires
========

* Python 2.5 : http://www.python.org/download/
* easy_install : http://peak.telecommunity.com/DevCenter/EasyInstall#installing-easy-install
You must add easy_install in your Path on Windows.

OS Independent installation
===========================

* Module installation
Enter in a console::

easy_install aditam.server

* Configure and install the database 
Enter in a console::

aditam-admin --create-db --config-db

Follow the instructions.
Note you need to have the good Python module for your database type : http://www.sqlalchemy.org/docs/04/dbengine.html#dbengine_supported

* Configure the server
Enter in a console::

aditam-admin --server

Follow the instructions.
