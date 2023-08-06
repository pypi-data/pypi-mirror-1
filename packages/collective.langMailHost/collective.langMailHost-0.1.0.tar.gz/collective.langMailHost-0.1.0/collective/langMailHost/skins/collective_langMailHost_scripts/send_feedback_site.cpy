## Controller Python Script "send_feedback_site"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Send feedback to portal administrator
##
REQUEST=context.REQUEST

from Products.CMFPlone.utils import transaction_note
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError
#from collective.langMailHost.interfaces import ILangCharset

##
## This may change depending on the called (portal_feedback or author)
state_success = "success"
state_failure = "failure"

plone_utils = getToolByName(context, 'plone_utils')
urltool = getToolByName(context, 'portal_url')
portal = urltool.getPortalObject()
url = urltool()

## make these arguments?
subject = REQUEST.get('subject', '')
message = REQUEST.get('message', '')
sender_from_address = REQUEST.get('sender_from_address', '')
sender_fullname = REQUEST.get('sender_fullname', '')

send_to_address = portal.getProperty('email_from_address')
envelope_from = portal.getProperty('email_from_address')

state.set(status=state_success) ## until proven otherwise

host = context.MailHost # plone_utils.getMailHost() (is private)

def lang_charset():
    properties = getToolByName(portal, 'portal_properties')
    if len(properties.mailhost_properties.getProperty('lang_charset')) != 0:
        lang_charset_tuples = [
            lc.split('|') for lc in properties.mailhost_properties.getProperty('lang_charset')
        ]
        lang_charset = dict(lang_charset_tuples)
        return lang_charset

def effective_lang():
    membership = getToolByName(portal, 'portal_membership')
    properties = getToolByName(portal, 'portal_properties')
    is_member_lang = properties.mailhost_properties.getProperty('is_member_lang_effective')
    member_lang = membership.getAuthenticatedMember().getProperty('language')
    if is_member_lang and member_lang != '' and member_lang is not None:
        return member_lang
    else:
        language_tool = getToolByName(portal, 'portal_languages')
        language_bindings = language_tool.getLanguageBindings()
        return language_bindings[0]

def effective_charset():
    lang = effective_lang()
    if lang:
        return lang_charset().get(lang)


encoding = effective_charset() or portal.getProperty('email_charset')

variables = {'sender_from_address' : sender_from_address,
             'sender_fullname'     : sender_fullname,
             'url'                 : url,
             'subject'             : subject,
             'message'             : message
             }

try:
    message = context.site_feedback_template(context, **variables)
    subject = unicode(subject.decode('utf-8'))
    result = host.secureSend(message, send_to_address, envelope_from, subject=subject, subtype='plain', charset=encoding, debug=False, From=sender_from_address)
except ConflictError:
    raise
except: # TODO Too many things could possibly go wrong. So we catch all.
    exception = plone_utils.exceptionString()
    message = _(u'Unable to send mail: ${exception}',
                mapping={u'exception' : exception})
    plone_utils.addPortalMessage(message, 'error')
    return state.set(status=state_failure)

## clear request variables so form is cleared as well
REQUEST.set('message', None)
REQUEST.set('subject', None)
REQUEST.set('sender_from_address', None)
REQUEST.set('sender_fullname', None)

plone_utils.addPortalMessage(_(u'Mail sent.'))
return state
