### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/) 
# Все права защищены, 2006-2007                                       
#
# Developed by Key Solutions (http://keysolutions.ru/)                             
# All right reserved, 2006-2007                                       
#######################################################################
# Licensed under the Zope Public License, Version 2.1 (the "License"); you
# may not use this file except in compliance with the License. A copy of the
# License should accompany this distribution.
#
# This software distributed under the License is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#######################################################################
"""The referenceedit MixIn to view class.

$Id: referenceedit.py 23747 2007-11-10 01:47:31Z cray $
"""
__author__  = "Anton Oprya"
__license__	= "ZPL"
__version__ = "$Revision: 23747 $"
__date__ = "$Date: 2007-11-10 04:47:31 +0300 (Сбт, 10 Ноя 2007) $"

from ks.reference.referenceannotation.interfaces import IReferenceTuple
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.container.browser.contents import getPrincipalClipboard
from zope.app import zapi
from zope.app.traversing.interfaces import TraversalError
from zope.component.interfaces import IFactory
from zope.app import intid
from zope import component
import base64


class ReferenceEditPage(BrowserView):
    referencelist_view = ViewPageTemplateFile("referenceedit.pt")
    clipboardlist_view = ViewPageTemplateFile("selectreftype.pt")
    
    def __init__(self, context, request):
        super(ReferenceEditPage, self).__init__(context, request)
        self.context = context
        self.request = request
        self.referencetuple = IReferenceTuple(context)
                    
    def getAllLinks(self):
        sm = zapi.getSiteManager(self.context)
        return [ y for x,y in sm.getUtilitiesFor(IFactory) 
                    if x.startswith("reference.reference.")]
    
    def getPossibleLinks(self, ob, links):
        return [ link for link in [y() for y in links]
                    if link.check_link(ob, self.context) ]
    
    def clipboardContents(self):
        clipboard = getPrincipalClipboard(self.request)
        items = clipboard.getContents()
        result = []
        for item in items:
            try:
                target=zapi.traverse(self.context, item['target'])
            except TraversalError:
                pass
            else:
                result.append(target)

        return result
    
    def copyObject(self,*kv,**kw):
        path = zapi.getPath(self.context)
        items = []
        items.append(path)
        clipboard = getPrincipalClipboard(self.request)
        clipboard.clearContents()
        clipboard.addItems('copy', items)
        return self.referencelist_view(self,*kv,**kw)
    
    def supportsDelete(self):
        if len(self.referencetuple.items(self.context)):
            return True
        else:
            return False
    
    def getReferencesList(self, ref_type=None):
        items = self.referencetuple.items(self.context, ref_type)
        return items


    def getBackReferencesList(self, ref_type=None):
        items = self.referencetuple.items(self.context, ref_type, backward=True)
        return items
    
        
    def cancelSelectRefType(self,*kv,**kw):
        return self.referencelist_view(self,*kv,**kw)
            
    
    def getClipboardObjectsInfo(self):
        items = self.clipboardContents()
        ids = component.getUtility(intid.interfaces.IIntIds,context=self.context)
        result = []
        for target in items :
                links = self.getPossibleLinks(target, self.getAllLinks())
                result.append((target, ids.getId(target), links, ))
        return result
    
    def addReferences(self,*kv,**kw):
        ids = component.getUtility(intid.interfaces.IIntIds,context=self.context)
        items = self.clipboardContents()
        for item in items:
            id=ids.getId(item)
            if str(id) in self.request:
                links = self.getPossibleLinks(item, self.getAllLinks())
                for link in links:
                    if link.__name__ in self.request[str(id)]:
                        link.link(item, self.context)
        self.request.response.redirect('referenceedit.html')
        #return self.referencelist_view(self,*kv,**kw)
                        
    def referencePaste(self,*kv,**kw):
        return self.clipboardlist_view(self,*kv,**kw)
    
    def deleteReferences(self,*kv,**kw):
        idlist = self.request.get('ids')
        if not idlist:
            return self.referencelist_view(self,*kv,**kw)
        
        for id in idlist:
            id=int(id)
            self.referencetuple.dellink(
                component.getUtility(intid.interfaces.IIntIds,context=self.context).getObject(int(id))
                )

        return self.referencelist_view(self,*kv,**kw)
    
