### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Interfaces for the Zope 3 based mailersmtp package

$Id: interfaces.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

from zope.interface import Interface
from zope.schema import Choice, Bool, ASCIILine, Text, TextLine

from ks.mailer.interfaces import IMailer

from ks.mailersmtp import _

class IMailerSMTPAnnotable(Interface):
    pass

mailersmtpannotationkey = u'ks.mailersmtp.mailersmtp.MailerSMTP'

class IMailerSMTP(IMailer):

    use_container = Bool(
        title=_(u"Use container"),
        default=False)

    use_alternative = Bool(
        title=_(u"Use alternative"),
        default=False)

    mime = ASCIILine(
        title=_(u"Mime type"),
        default="text/plain")

    filename = ASCIILine(
        title=_(u"File name"),
        default="body")

    Subject = TextLine(
        title=_(u'"Subject:" template'))

    mail_header = Text(
        title=_(u"Header template"),
        required=False,
        default=u'',
        missing_value=u'')

    mail_footer = Text(
        title=_(u"Footer template"),
        required=False,
        default=u'',
        missing_value=u'')
