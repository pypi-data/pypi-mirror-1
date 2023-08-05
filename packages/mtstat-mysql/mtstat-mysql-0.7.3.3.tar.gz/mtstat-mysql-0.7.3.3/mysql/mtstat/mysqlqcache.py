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

class mysqlqcache(mysqlbase.mysqlbase):

    mysqlvars=[
        ('Qcache_hits', ('diff',('d',7,1000),'qhit')) ,
        ('Qcache_inserts', ('diff',('d',7,1000),'qins')) ,
        ('Qcache_lowmem_prunes', ('diff',('d',7,1000),'qlow')) ,
        ('Qcache_not_cached', ('diff',('d',7,1000),'qnot')) ,

        ]

