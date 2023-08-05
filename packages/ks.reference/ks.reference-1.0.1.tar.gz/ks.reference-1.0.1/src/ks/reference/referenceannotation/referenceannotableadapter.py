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

$Id: referenceannotableadapter.py 17245 2007-03-12 19:52:06Z ucray $
"""
__author__  = "Andrey Orlov"
__license__	= "ZPL"
__version__ = "$Revision: 17245 $"
__date__ = "$Date: 2007-03-12 22:52:06 +0300 (Пнд, 12 Мар 2007) $"
 

from referenceannotation import ReferenceAnnotation
from zope.annotation.interfaces import IAnnotations 

from interfaces import referenceannotationkey

def ReferenceAnnotableAdapter(context) :
    return IAnnotations(context).setdefault(referenceannotationkey,ReferenceAnnotation(context))


   

