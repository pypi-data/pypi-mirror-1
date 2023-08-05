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

$Id: referencebase.py 23747 2007-11-10 01:47:31Z cray $
"""
__author__  = "Anton Oprya"
__license__	= "ZPL"
__version__ = "$Revision: 23747 $"
__date__ = "$Date: 2007-11-10 04:47:31 +0300 (Сбт, 10 Ноя 2007) $"
 
from zope.interface import Interface
from zope.app import intid
import zope.component
from zope.interface import providedBy
from ks.reference.referenceannotation.interfaces import IReferenceTuple

from logging import getLogger

logger = getLogger('reference')

class ReferenceBase(object):
    parent1 = None
    parent2 = None
    
    def link1(self, ob):
        ids = zope.component.getUtility(intid.interfaces.IIntIds, context = ob)
        IReferenceTuple(ob).setlink(self)
        if self.__parent1_interface__[0].providedBy(ob):
            self.parent1 = ids.getId(ob)
        else:
            raise TypeError, "Object %s must provide interface %s" % (ob, self.__parent1_interface__)
        
    
    def link2(self, ob):
        ids = zope.component.getUtility(intid.interfaces.IIntIds, context = ob)
        IReferenceTuple(ob).setlink(self)
        if self.__parent2_interface__[0].providedBy(ob):
            self.parent2 = ids.getId(ob)
        else:
            raise TypeError, "Object %s must provide interface %s" % (ob, self.__parent2_interface__)

    def check_link(self,ob1,ob2) :
        ids = zope.component.getUtility(intid.interfaces.IIntIds, context = ob1)    
        return (self.__parent1_interface__[0].providedBy(ob1) 
            and self.__parent2_interface__[0].providedBy(ob2) 
            and ( not ( not self.isreflexive and ids.getId(ob1) == ids.getId(ob2) ) )
            )

    def link(self,ob1,ob2) :
        self.link1(ob1)
        self.link2(ob2)
        
    def getbackward(self,ob) :
        if not self.iscommutative :
            ids = zope.component.getUtility(intid.interfaces.IIntIds, context = ob)
            id = ids.getId(ob)
            if id == self.parent2:
                return ids.getObject(self.parent1)
        return None
        
    def getlink(self, ob):
        ids = zope.component.getUtility(intid.interfaces.IIntIds, context = ob)
        id = ids.getId(ob)
        if id == self.parent1:
            return ids.getObject(self.parent2)
        elif not self.iscommutative :
            return None
        elif id == self.parent2:
            return ids.getObject(self.parent1)
        else:
            logger.warning("Not linked object %(ob)s", dict(ob=ob))
            return None
