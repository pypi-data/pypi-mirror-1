### This program is free software; you can redistribute it and/or modify
### it under the terms of the GNU Library General Public License as published by
### the Free Software Foundation; version 2 only
###
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU Library General Public License for more details.
###
### You should have received a copy of the GNU Library General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
### Copyright 2006 Monty Taylor <monty@inaugust.com>

# bootstrap setuptools if necessary
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup (name = "mtstat-mysql",
       version = "0.7.3.3",
       description = "MySQL Plugins for mtstat",
       author = "Monty Taylor",
       author_email = "monty@inaugust.com",
       url = "http://launchpad.net/mtstat",
       license = "GPL",

       py_modules = [],
       packages = ["mysql","mysql.mtstat"],
       entry_points = {
         'mtstat.plugins': [
           'mysqlqps = mysql.mtstat.mysqlqps:mysqlqps',
           'mysqlqcache = mysql.mtstat.mysqlqcache:mysqlqcache',
           'mysqlhandler = mysql.mtstat.mysqlhandler:mysqlhandler',
           'mysqltlocks = mysql.mtstat.mysqltlocks:mysqltlocks'

         ]
       },

      )
