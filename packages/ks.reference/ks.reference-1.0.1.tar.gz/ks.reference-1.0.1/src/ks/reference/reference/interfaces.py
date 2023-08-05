### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################                                                 #
# Licensed under the Zope Public License, Version 2.1 (the "License"); you
# may not use this file except in compliance with the License. A copy of the
# License should accompany this distribution.
#
# This software distributed under the License is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#######################################################################

"""Interfaces for the Zope 3 based reference package

$Id: interfaces.py 19643 2007-04-28 12:28:46Z anton_oprya $
"""
__author__  = "Anton Oprya"
__license__    = "ZPL"
__version__ = "$Revision: 19643 $"
__date__ = "$Date: 2007-04-28 16:28:46 +0400 (Сбт, 28 Апр 2007) $"

from zope.interface import Interface
from zope.schema import Text, TextLine, Datetime, Tuple, Set, Field

class IReferenceBase(Interface) :
    """Reference between two objects
    """

    title1 = Text()
    title2 = Text()
    reference_type = Text()
    ob = Field()

    def link1(ob):
        """Get id for parent1"""

    def link2(ob):
        """Get id for parent2"""

    def getlink(ob):
        """Receipt of object from reference.
        """

    def link(ob1,ob2) :
        pass

    def getbackward(ob):
        pass

    def getlink(ob):
        pass
