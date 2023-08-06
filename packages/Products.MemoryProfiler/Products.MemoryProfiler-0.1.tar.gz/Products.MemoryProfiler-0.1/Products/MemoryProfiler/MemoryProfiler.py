# -*- coding: utf-8 -*-
# Copyright (C)2009 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

'''MemoryProfiler.

'''
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

_ModDict= globals()

from logging import getLogger
from threading import Lock

import time
from guppy import hpy

from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass

_log = getLogger('MemoryProfiler')

_results = None
l = Lock()
myvar = ''

############################################################################
## Persistent Zope objects
class Profiler(SimpleItem,PropertyManager):
  '''Profiler singleton'''
  id= 'MemoryProfiler'
  title= id
  meta_type= 'Memory Profiler'
  security= ClassSecurityInfo()
  security.declareProtected('Profiler: manage',
                            'showStatistic',
                            'manage_changeProperties',
                            'start',
                            'stop',
                            
                            )

  
  security.setDefaultAccess(1)

  _properties= (
    { 'id' : 'title', 'type' : 'string', 'mode' : 'w', },
    { 'id' : 'DefaultLimit', 'type' : 'int', 'mode' : 'w', },
    { 'id' : 'PersistentState', 'type' : 'boolean', 'mode':'w',},
  )
  

  DefaultLimit= 200
  PersistentState = False
    


  manage_options= (
  (
    {'label' : 'Statistics', 'action' : 'showStatistic'},
    )
  + PropertyManager.manage_options
  + SimpleItem.manage_options
  )

  _enabled= 0
  _status = False
  datas = []
  _v_stats = None
  

  def start(self):
    """ start to collect data """
    global myvar
    
    l.acquire()
    try:
      myvar = hpy()
      #hp.setrelheap()
      myvar.setrelheap()
    finally:
        l.release()

    self._status = True
    
    self.datas = []
    _log.info('start to collect memory %s' % id(myvar))
    self.REQUEST.RESPONSE.redirect('showStatistic')
    

  def clear(self):
    """ clear all data """
    self.datas = []
    self.REQUEST.RESPONSE.redirect('showStatistic')

    
  def stop(self):
    """ stop to collect data """
    global myvar

    myvar = None
    _log.info('stop to collect memory %s' % id(myvar))
    self._status = False
    

    self.REQUEST.RESPONSE.redirect('showStatistic')
    
  def status(self):
    return self._status

  def clearDbCache(self):
    """ clear all bd cache """

    [self.Control_Panel.Database[x]._getDB().cacheMinimize() \
     for x in self.Control_Panel.Database.getDatabaseNames()]
    return self.updateSnapshot()




  
  def updateSnapshot(self, heap= True):
    """ update snapshot """
    global myvar
    
    if self.REQUEST.get('pdb',False):
      import pdb as debug;debug.set_trace();
    
    
    _stats = myvar
    _log.info('update snapshot %s' % id(_stats))
    if _stats and heap:
      h = _stats.heap()
      index = self.REQUEST.get('index',None)
      if index is not None:
        h = h[index].get_rp(depth=self.REQUEST.get('depth',2))
      limit = self.REQUEST.get('limit',self.DefaultLimit )
      self.datas.append(self._computeDatas(h, index, limit = limit ))
      self._p_changed = 1
    self.REQUEST.RESPONSE.redirect('showStatistic')

  

  def _computeDatas(self, results, index, limit):
    """ return statistic """

    stat = ''
    i = 0
    while (hasattr(results,'more') and i < (limit / 10)):
        
        r = str(results)
        if index is None:
          if i == 0:
            r = "\n".join(r.split("\n")[:-1])
          else:
            r = "\n".join(r.split("\n")[1:-1])
        else:
          r = "\n".join(r.split("\n")[:-1])
        stat += r + '\n'
        results = results.more
        i += 1
    
    
    return {'size' : hasattr(results,'size') \
            and float(results.size) / (1024 * 1024) or 0,
            'results' : stat,
            'time' : time.time(),
            'type' : 'snapshot',
            }
    
    
  def getStatistics(self, key = None):
    key = self.REQUEST.get('key', key)
    
    if key is not None:
      
      data = [ x for x in self.datas if \
               ('%0.2f' % x['time'])[:len(key)] == key]
      if data:
        return data[0]['results']
    else:
      if self.datas:
        return self.datas[-1]['results']
      
  # presentation
  showStatistic = PageTemplateFile('www/memory.html', globals(), __name__='showStatistic')
  

InitializeClass(Profiler)
    


  

