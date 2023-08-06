### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""IMailerSMTPAnnotation to IMailerSMTP adapter for the Zope 3 based mailersmtp package

$Id: mailerannotation.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

from interfaces import mailersmtpannotationkey
from zope.annotation.interfaces import IAnnotations
from mailersmtp import MailerSMTP


def MailerAnnotableAdapter(context):
    annotations = IAnnotations(context)
    if annotations.has_key(mailersmtpannotationkey):
        return annotations[mailersmtpannotationkey]
    else:
        annotation = annotations[mailersmtpannotationkey] = MailerSMTP()
    return annotation
