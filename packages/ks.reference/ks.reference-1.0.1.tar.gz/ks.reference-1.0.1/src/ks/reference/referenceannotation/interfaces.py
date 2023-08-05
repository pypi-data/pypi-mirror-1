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
"""Interfaces for the Zope 3 based referenceannotation package

$Id: interfaces.py 17245 2007-03-12 19:52:06Z ucray $
"""
__author__  = "Anton Oprya"
__license__	= "ZPL"
__version__ = "$Revision: 17245 $"
__date__ = "$Date: 2007-03-12 22:52:06 +0300 (Пнд, 12 Мар 2007) $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Datetime, Tuple, Set, Field

referenceannotationkey = "reference.referenceannotation.ReferenceAnnotation"
                
class IReferenceProxy(Interface):
        ob = Field()
        reference = Field()
        uniqid = Field()
        title = Field()
        __name__ = Field()     

class IReferenceTuple(Interface):
    
    references = Tuple()
    
    def items(ob, ref_type = None, backward = False):
        """Accepts an argument ref_type which is a type of connection 
        and returns the list of objects.
        """
    def setlink(ref):
        """Add link to references"""
    
    def dellink(ref):
        """Delete link from references"""
        
class IReferable(Interface):
    pass

    