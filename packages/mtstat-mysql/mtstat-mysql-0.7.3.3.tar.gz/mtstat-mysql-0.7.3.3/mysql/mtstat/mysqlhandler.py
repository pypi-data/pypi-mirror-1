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

### mtstat mysqlqps plugin
### Displays mysql queries per second
###
### Authority: monty@inaugust.com

import mysqlbase

class mysqlhandler(mysqlbase.mysqlbase):

    mysqlvars=[
        ('Handler_read_first', ('diff',('d',7,1000),'hf')) ,
        ('Handler_read_next', ('diff',('d',7,1000),'hnxt')) ,
        ('Handler_read_key', ('diff',('d',7,1000),'hkey')) ,
        ('Handler_read_rnd', ('diff',('d',7,1000),'rrnd')) ,
        ('Handler_read_rnd_next', ('diff',('d',7,1000),'rnxt')) ,

        ]

