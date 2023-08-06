### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Adapter of IMailForm to IFormSave interfaces. The adapter is used to send
the entered form in the mailing list by means of components of a product
ng.app.mailfeed.

$Id: mailform2formsave.py 53590 2009-08-14 21:02:34Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 53590 $"

from zope.interface import Interface
from zope.interface import implements
from zope.app.zapi import getUtilitiesFor
from ng.base.form.interfaces import IFormSave
from ng.app.mailfeed.mailtemplate.interfaces import IMailTemplate
from ng.app.mailfeed.addresses.interfaces import IAddresses
from ng.app.mailfeed.sender.interfaces import ISender

class MailForm2FormSave(object) :

    def __init__(self,context):
        self.context = context

    def do(self,d,**kw) :
        message = IMailTemplate(self.context).apply(**dict([ (str(x),y) for x,y in d.items()]))
        for name,address in IAddresses(self.context).values() :
            ISender(self.context).send([address],"To: %s\n" % address + message)
        return True
        