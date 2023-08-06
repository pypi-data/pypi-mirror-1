### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with last rss news

$Id: product.py 51198 2008-06-26 14:27:12Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 51198 $"


from ng.skin.base.viewlet.viewletmain.mainbox import MainBox
from ng.app.objectqueue.interfaces import IObjectQueue
from ng.app.registry.interfaces import IRegistry
from ng.adapter.adaptiveurl.adaptiveurl import adaptiveURL
from zope.app.intid.interfaces import IIntIds
from time import time
from zope.app.zapi import traverse, getUtilitiesFor
import sys             

product_list = {}

class ProductBox(MainBox) :
    """ Folder List """

    foldername = "news"
    @property
    def values(self) :
      try :
        global product_list
        context = self.context
        try :
          print getUtilitiesFor(IIntIds,context)
          cid = getUtilitiesFor(IIntIds,context).next()[1].getId(context)
        except StopIteration,msg :
          print "!!!",msg
          cid = 1                          
        
        l,t = data = product_list.setdefault(cid,[[],0])
                
        if  time() - t > 3600 :
            del l[:]
            for folder in [ x for x in IRegistry(context).param("maintablerow","").split() if x ] :
                l.extend([(y.title,adaptiveURL(y,self.request)) for y in context[folder].values()])

            l.sort()
            data[1] = time()

        return l
        
      except Exception,msg :
        print msg
        