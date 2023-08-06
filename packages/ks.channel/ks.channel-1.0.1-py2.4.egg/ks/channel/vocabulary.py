### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""The Channel vocabulary class.

$Id: vocabulary.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Zaretsky"
__license__	= "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

from zope.interface import classProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.app.component.vocabulary import UtilityVocabulary
from interfaces import IChannel

class ChannelsVocabulary(UtilityVocabulary):
    classProvides(IVocabularyFactory)
    interface = IChannel
    nameOnly = True
