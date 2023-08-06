### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The class is intended to define the form and to send it on commit to each address from chosen
list of addresses


$Id: mailform.py 53590 2009-08-14 21:02:34Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53590 $"

from zope.interface import implements
from persistent import Persistent

from interfaces import IMailForm
from ng.app.mailfeed.mailtemplate.interfaces import IMailTemplateAnnotable
from ng.app.mailfeed.addresses.interfaces import IAddressesUtilitable
from ng.app.mailfeed.sender.interfaces import ISenderUtilitable
from ng.base.form.formcontainer import Form
from ng.base.form.interfaces import IFormDialog
#from ng.app.mailfeed.mailtemplate.mailtemplate import MailTemplate
#from ng.app.mailfeed.adresses.adresses import Adresses

from zope.annotation.interfaces import IAttributeAnnotatable
class MailForm(Form,Persistent) :
    implements(IFormDialog,IMailForm,IMailTemplateAnnotable,IAddressesUtilitable,ISenderUtilitable,IAttributeAnnotatable)
    
    mailtemplate = u''
            
    addresses = u''

    sender = u''    