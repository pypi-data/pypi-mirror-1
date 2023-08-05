### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with last rss news

$Id: product.py 50809 2008-02-21 11:57:42Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 50809 $"


from ng.skin.base.viewlet.viewletmain.mainbox import MainBox
from ng.app.objectqueue.interfaces import IObjectQueue
from ng.app.registry.interfaces import IRegistry
from ng.adapter.adaptiveurl.adaptiveurl import adaptiveURL
from time import time
from zope.app.zapi import traverse           
import sys             

product_list = None
t = time()

class ProductBox(MainBox) :
    """ Folder List """

    foldername = "news"
    @property
    def values(self) :
        global product_list, t
                
        if product_list is None or time() - t > 3600 :
            product_list = []
            
            context = self.context
            for folder in [ x for x in IRegistry(context).param("maintablerow","").split() if x ] :
                product_list.extend([(y.title,adaptiveURL(y,self.request)) for y in context[folder].values()])

            product_list.sort()
            t = time()

        return product_list
        
