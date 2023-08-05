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
"""Interface of ZCML metadirective "reference"

$Id: metadirectives.py 17245 2007-03-12 19:52:06Z ucray $
"""
__author__  = "Anton Oprya"
__license__	= "ZPL"
__version__ = "$Revision: 17245 $"
__date__ = "$Date: 2007-03-12 22:52:06 +0300 (Пнд, 12 Мар 2007) $"
 
from zope.interface import Interface
import zope

_ = lambda x : x

class IAddReferenceDirective(Interface):
    """Shema of ZCML metadirective "reference"""
    name = zope.schema.TextLine(
        title = u'Name',
        description = u"Name of reference type",
        required=True,
        )
    
    interface1 = zope.configuration.fields.Tokens(
            title=_(u"One or more interfaces"),
            required=True,
            value_type=zope.configuration.fields.GlobalInterface()
            )
                                
    interface2 = zope.configuration.fields.Tokens(
            title=_(u"One or more interfaces"),
            required=True,
            value_type=zope.configuration.fields.GlobalInterface()
            )
                                
    title1 = zope.schema.TextLine(
        title = u'Title',
        description = u"Humanity readable name of reference type",
        required=False,
        )

    title2 = zope.schema.TextLine(
        title = u'Title',
        description = u"Humanity readable name of reference type",
        required=False,
        )

    isreflexive = zope.schema.Bool(
        title = u'Can reflexive?',
        description = u"Link can be reflexive",
        required=False,
        default=False,
        )

    iscommutative = zope.schema.Bool(
        title = u'Is commutative?',
        description = u"Link is commutative",
        required=False,
        default=True,
        )

    ismultiplicative = zope.schema.Bool(
        title = u'Is multiplicative?',
        description = u"Link is multiplicative",
        required=False,
        default=False,
        )
