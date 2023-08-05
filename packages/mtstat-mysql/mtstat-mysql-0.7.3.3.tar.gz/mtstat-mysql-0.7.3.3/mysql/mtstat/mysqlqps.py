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

class mysqlqps(mysqlbase.mysqlbase):

    mysqlvars=[
        ('Uptime', ('total',('d',7,1000),'uptime')),
        ('Com_select', ('diff',('d',7,1000),'sel')) ,
        ('Com_insert', ('diff',('d',7,1000),'ins')) ,
        ('Com_delete', ('diff',('d',7,1000),'del')) ,
        ('Com_update', ('diff',('d',7,1000),'upd')) ,
        ('Questions',('diff',('d',7,1000),'quest')) ,

        ]

