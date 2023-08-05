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
"""ReferenceBase class for the Zope 3 based reference package

$Id: referenceannotation.py 20896 2007-06-19 12:13:51Z azaretsky $
"""
__author__  = "Anton Oprya"
__license__    = "ZPL"
__version__ = "$Revision: 20896 $"
__date__ = "$Date: 2007-06-19 16:13:51 +0400 (Втр, 19 Июн 2007) $"

from zope.interface import Interface

from persistent import Persistent
from zope.interface import implements
from interfaces import IReferenceTuple
from BTrees.OOBTree import OOSet
from zope.app import intid
from zope import component
import base64

from logging import getLogger

logger = getLogger('reference')

class ReferenceProxy(object) :
    reference = None
    ob = None

    def __init__(self,ob,ref) :
        self.ob = ob
        self.reference = ref
        self.uniqid = component.getUtility(intid.interfaces.IIntIds, context=ob).getId(ref)

    def __getattr__(self,name) :
        return getattr(self.ob,name)

class ReferenceAnnotation(Persistent) :
    __doc__ = IReferenceTuple.__doc__
    implements(IReferenceTuple)

    references = None

    def __init__(self,parent,*kv,**kw) :
        super(ReferenceAnnotation,self).__init__(*kv,**kw)
        self.references = OOSet()
        self.__parent__ = parent

    def items(self, ob, ref_type = None, backward = False):
        if backward :
            name = 'getbackward'
        else :
            name = 'getlink'

        res = []
        for ref in self.references.keys():
            try:
                getattr(ref,name)
                res.append(ref)
            except AttributeError, msg:
                logger.warning('ReferenceAnnotation.items', exc_info=True)


        return [ ReferenceProxy(ob,ref)
                for ob,ref in
                    [ (getattr(ref,name)(ob),ref)
                        for ref in res
                        if (ref_type is None or ref.reference_type == ref_type) ] if ob is not None ]

    def setlink(self, ref):
        ref.__parent__ = self.__parent__
        ids=component.getUtility(intid.interfaces.IIntIds,context=self.__parent__)
        ids.register(ref)
        self.references.insert(ref)

    def dellink(self, ref):
        getOb=component.getUtility(intid.interfaces.IIntIds,context=self).getObject
        if ref in self.references :
            getOb=component.getUtility(intid.interfaces.IIntIds,context=self).getObject
            try :
                IReferenceTuple(getOb(ref.parent1)).references.remove(ref)
            except KeyError :
                logger.warning("Link %(ref)s already removed", dict(ref=ref))
            try :
                IReferenceTuple(getOb(ref.parent2)).references.remove(ref)
            except KeyError :
                logger.warning("Link %(ref)s already removed", dict(ref=ref))

