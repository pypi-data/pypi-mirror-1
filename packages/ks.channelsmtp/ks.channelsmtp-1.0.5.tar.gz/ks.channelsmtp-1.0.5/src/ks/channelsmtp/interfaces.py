### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Interfaces for the Zope 3 based channelsmtp package

$Id: interfaces.py 35341 2008-10-21 09:09:24Z anatoly $
"""
__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 35341 $"
__date__ = "$Date: 2008-10-21 12:09:24 +0300 (Tue, 21 Oct 2008) $"

from zope.interface import Interface
from zope.schema import Choice, ASCIILine

from ks.channel.interfaces import IChannel

from ks.channelsmtp import _

class IChannelSMTP(IChannel):

    fromAddress = ASCIILine(title=_(u'"From" address'))
    
    bccAddress = ASCIILine(title = _(u'"BCC" addreses (use commas as splitter)'),
                           required = False,
                           default = '')

    delivery = Choice(
        title=_(u"Mail Delivery Name"),
        vocabulary="Mail Delivery Names")

    def sendTo(addresses, **kw):
        """Send emails to specified addressess instead of configured ones"""
