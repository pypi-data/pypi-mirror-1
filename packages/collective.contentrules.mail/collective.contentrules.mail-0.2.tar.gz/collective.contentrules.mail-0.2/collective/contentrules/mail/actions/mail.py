# -*- coding: utf-8 -*-
# Copyright (c) 2008 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface
from zope.interface import implements
from zope.formlib import form
from zope.schema import TextLine
from zope.schema import Text
from zope.schema import Choice
from zope.schema import getFieldsInOrder

from Products.CMFCore.utils import getToolByName

from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import EditForm
from plone.contentrules.rule.interfaces import IRuleElementData
from plone.contentrules.rule.interfaces import IExecutable

from collective.contentrules.mail import MessageFactory as _
from collective.contentrules.mail import LOG
from collective.contentrules.mail.browser.widget import ModelWidget
from collective.contentrules.mail.interfaces import IMailModel

class IMailAction(Interface):
    """Definition of the configuration available for a mail action
    """

    model = Choice(
        title=_(u"Mail model"),
        required=True,
        vocabulary="collective.contentrules.mail.vocabulary.model",)

    mimetype = Choice(
        title=_(u"Mail mimetype"),
        required=True,
        vocabulary="collective.contentrules.mail.vocabulary.mimetype",)

    subject = TextLine(
        title=_(u"Subject"),
        description=_(u"Subject of the message"),
        required=True)

    source = TextLine(
        title=_(u"Email source"),
        description=_("The email address that sends the email. If no email is"\
                      " provided here, it will use the portal from address."),
        required=False)

    recipients = TextLine(
        title=_(u"Email recipients"),
        description=_("The email where you want to send this message. To send"\
            " it to different email addresses, just separate them with commas."),
        required=True)

    message = Text(
        title=_(u"Message"),
        description=_(u"Type in here the message that you want to mail."),
        required=True)

class MailAction(SimpleItem):
    """
    The implementation of the action defined before
    """
    implements(IMailAction, IRuleElementData)

    model = ''
    mimetype = ''
    subject = ''
    source = ''
    recipients = ''
    message = ''
    
    element = 'collective.contentrules.mail.actions.Mail'

    @property
    def summary(self):
        return _(u"Email report to ${recipients}",
                 mapping=dict(recipients=self.recipients))


class MailActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IMailAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        # Get event objet
        obj = self.event.object

        # Get replacer interface from model
        model = getUtility(IMailModel, self.element.model)
        replacer_interface = model.replacer_interface

        # Extract all variables from this replacer
        replacer = replacer_interface(obj, None)
        if replacer is None:
            LOG.debug(u"Could not send email. The replacer is not applicable for this type of object.")
            return False
        
        word_ids = [k for k, v in getFieldsInOrder(replacer_interface)]
        words = {}

        for word_id in word_ids:
            words[word_id] = getattr(replacer, word_id)

        # Apply word substitution on every mail fields
        def substitute(text):
            for word_id in word_ids:
                text = text.replace("${%s}" % word_id, words[word_id])

            return text
        
        source = substitute(self.element.source)
        recipients = substitute(self.element.recipients)
        subject = substitute(self.element.subject)
        message = substitute(self.element.message)

        # Process recipients
        recipient_list = []

        for email in recipients.split(','):
            email = email.strip()

            if not email:
                # Remove empty address
                continue

            if email in recipient_list:
                # Remove doubles
                continue

            recipient_list.append(email)

        if not recipient_list:
            # Because there are no recipients, do not send email
            LOG.info(u"""Do not send email "%s": no recipients defined.""" %
                     model.title)
            return False

        recipients = ",".join(recipient_list)

        # Process source
        utool = getToolByName(aq_inner(self.context), "portal_url")
        portal = utool.getPortalObject()

        if not source:
            # no source provided, looking for the site wide from email
            # address
            from_address = portal.getProperty('email_from_address')

            if not from_address:
                raise ValueError, "You must provide a source address for this\
action or enter an email in the portal properties"

            from_name = portal.getProperty('email_from_name')
            source = "%s <%s>" % (from_name, from_address)

        # Encode text using mail charset
        site_properties = portal.portal_properties.site_properties
        site_charset = site_properties.getProperty('default_charset')
        email_charset = portal.getProperty('email_charset')

        if email_charset != site_charset:
            source = source.decode(site_charset).encode(email_charset)
            recipients = recipients.decode(site_charset).encode(email_charset)
            subject = subject.decode(site_charset).encode(email_charset)
            message = message.decode(site_charset).encode(email_charset)

        # Send email
        mailhost = getToolByName(aq_inner(self.context), "MailHost")

        if not mailhost:
            raise ComponentLookupError, \
                "You must have a Mailhost utility to execute this action"

        mimetype = self.element.mimetype
        mailhost.secureSend(message, recipients, source,
                            subject=subject, subtype=mimetype,
                            charset=email_charset, debug=False,
                            From=source)
        return True

class MailAddForm(AddForm):
    """
    An add form for the mail action
    """
    form_fields = form.FormFields(IMailAction)
    form_fields['model'].custom_widget = ModelWidget
    label = _(u"Add Mail Action")
    description = _(u"A mail action can mail different recipient.")
    form_name = _(u"Configure element")

    def create(self, data):
        a = MailAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class MailEditForm(EditForm):
    """
    An edit form for the mail action
    """
    form_fields = form.FormFields(IMailAction)
    form_fields['model'].custom_widget = ModelWidget
    label = _(u"Edit Mail Action")
    description = _(u"A mail action can mail different recipient.")
    form_name = _(u"Configure element")
