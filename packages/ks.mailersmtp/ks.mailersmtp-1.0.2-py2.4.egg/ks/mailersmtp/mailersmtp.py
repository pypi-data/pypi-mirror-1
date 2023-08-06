### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Mailer class for the Zope 3 based mailer package

$Id: mailersmtp.py 35342 2008-10-21 09:11:52Z anatoly $
"""
__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 35342 $"
__date__ = "$Date: 2008-10-21 12:11:52 +0300 (Tue, 21 Oct 2008) $"

from persistent import Persistent
from zope.component import getUtility
from zope.interface import implements
from zope.app.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty

from ks.lib.mailtemplate import mailtemplate
from ks.mailer.interfaces import ITemplate, ITemplateAdaptable
from ks.mailer.templateadapter import getTemplate

from interfaces import IMailerSMTP

class MailerSMTP(Persistent, Contained):
    implements(IMailerSMTP)

    template = FieldProperty(IMailerSMTP['template'])

    use_container = FieldProperty(IMailerSMTP['use_container'])

    use_alternative = FieldProperty(IMailerSMTP['use_alternative'])

    mime = FieldProperty(IMailerSMTP['mime'])

    filename = FieldProperty(IMailerSMTP['filename'])

    mail_header = FieldProperty(IMailerSMTP['mail_header'])

    mail_footer = FieldProperty(IMailerSMTP['mail_footer'])

    Subject = FieldProperty(IMailerSMTP['Subject'])

    def execute(self, **kw):

        if kw.has_key('attaches'):
            attaches = kw['attaches']
	    del kw['attaches']
	else:
	    attaches = ()
	    
        return mailtemplate.template(\
            use_container=self.use_container,
            use_alternative=self.use_alternative,
            charset='utf-8',
            mime=self.mime,
            filename=self.filename,
            mail_header=self.mail_header.encode('utf-8'),
            mail_footer=self.mail_footer.encode('utf-8'),
	    attaches = attaches,
            text_headers={'Subject' : self.Subject.encode('utf-8')},
            data=kw,
            mail_body=getTemplate(self.template, self)(**kw).encode('utf-8'))
