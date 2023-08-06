### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Interfaces for the Zope 3 based channel package

$Id: interfaces.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

from zope.interface import Interface
from zope.schema import Tuple, ASCIILine

from ks.channel import _

class IChannel(Interface):

    def send(**kw):
        pass

    addresses = Tuple(
        title=_(u"Addresses"),
        value_type=ASCIILine(title=_(u"Address")),
        unique=True,
        default=())
