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

### Base class for mysql plugins
###
### Authority: monty@inaugust.com

from mtstat.mtstat import mtstat, cprint, char, cprintlist
import types
import MySQLdb

class mysqlbase(mtstat):


    db=MySQLdb.Connect(read_default_group='mtstat')
    server_info = db.get_server_info()
    if server_info[0]=='4':
      q="show status"
    else:
      q="show global status"
    data={}
    data_last={}
    #queries=0
    #queries_last=0
    #uptime=0
    #uptime_last=0
    val={} 

    mysqlvars=[
        ('Questions',('diff',('d',7,1000),'quest')) , 
        
        ]
    def __init__(self):
        self.formats={}
        for (k,v) in self.mysqlvars:
          self.formats[k]=v[1]
        self.format = ('d',7,1000) #4,1000) #4,1000) #4,1000) #max([f[1] for f in self.formats.values()])+1,1000) #('t', 14, 0)
        self.vars = [f[0] for f in self.mysqlvars]
        self.name = 'mysql'
        #self.nick = [f.lower()[0:self.formats[f][1]] for f in self.vars]
        self.nick = [f[1][2].lower() for f in self.mysqlvars]
        #self.val['mysql_qps']=0
        self.init(self.vars,1)
        #self.cn2['Com_select']=long(5)

    def get_diff(self, key):
        val_now=int(self.data[key])
        try: 
            val_then=int(self.data_last[key])
        except KeyError:
            return 0
        if (val_then==0):
          return 0
        return val_now-val_then

    def extract(self):
        c=self.db.cursor()
        c.execute(self.q)
        for (key,val) in c.fetchall():
          self.data[key]=val
         
        foo="""
        queries_now=int(data['Questions'])
        if (self.queries_last==0):
            self.queries=0
        else:
            self.queries=queries_now-self.queries_last
        self.queries_last=queries_now
        #c.execute(self.u)
        uptime_now=int(data['Uptime'])
        if (self.uptime_last==0):
            self.uptime=1
        else:
            self.uptime=uptime_now-self.uptime_last """
        for f in self.vars:
          tup=[]
          for x in self.mysqlvars: 
            if x[0]==f:
              tup=x[1]
          if (tup[0]=='diff'):
            self.val[f]=self.get_diff(f)
          else:
            self.val[f]=int(self.data[f])
        #self.val['qps']=self.get_diff('Questions')
        #self.val['uptime']=self.uptime
        self.data_last=self.data.copy()

    def show(self):
        "Display stat results"
        line = ''
        for i, name in enumerate(self.vars):
            if isinstance(self.val[name], types.TupleType) or isinstance(self.val[name], types.ListType):
                line = line + cprintlist(self.val[name], self.formats[name])
                sep = ansi['default'] + char['colon']
            else:
                line = line + cprint(self.val[name], self.formats[name])
                sep = char['space']
            if i + 1 != len(self.vars):
                line = line + sep
        return line

    #def width(self):
    #    "Return column width"
    #    w=0
    #    for name in self.format.keys():
    #        w+=self.format[name][1] 
    #        #return len(self.c[name]) * self.format[name][1] + len(self.cn2[name]) - 1
    #    return w


	
# vim:ts=4:sw=4


