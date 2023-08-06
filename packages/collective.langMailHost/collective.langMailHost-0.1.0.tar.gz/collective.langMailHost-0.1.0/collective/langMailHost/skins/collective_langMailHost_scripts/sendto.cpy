## Controller Python Script "sendto"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Send an URL to a friend
##
REQUEST=context.REQUEST

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone.PloneTool import AllowSendto
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError

plone_utils = getToolByName(context, 'plone_utils')
mtool = getToolByName(context, 'portal_membership')
site_properties = getToolByName(context, 'portal_properties').site_properties
pretty_title_or_id = plone_utils.pretty_title_or_id

if not mtool.checkPermission(AllowSendto, context):
    context.plone_utils.addPortalMessage(_(u'You are not allowed to send this link.'), 'error')
    return state.set(status='failure')

at = getToolByName(context, 'portal_actions')
show = False
actions = at.listActionInfos(object=context)
# Check for visbility of sendto action
for action in actions:
    if action['id'] == 'sendto' and action['category'] == 'document_actions':
        show = True
if not show:
    context.plone_utils.addPortalMessage(_(u'You are not allowed to send this link.'), 'error')
    return state.set(status='failure')

urltool = getToolByName(context, 'portal_url')
portal = urltool.getPortalObject()

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

# Find the view action.
context_state = context.restrictedTraverse("@@plone_context_state")
url = context_state.view_url()

send_to_address = REQUEST.send_to_address
send_from_address = REQUEST.send_from_address
comment = REQUEST.get('comment', None)
subject = pretty_title_or_id(context)

#variables = {'send_from_address' : REQUEST.send_from_address,
#             'send_to_address'   : REQUEST.send_to_address,
#             'subject'           : pretty_title_or_id(context),
#             'url'               : url,
#             'title'             : pretty_title_or_id(context),
#             'description'       : context.Description(),
#             'comment'           : REQUEST.get('comment', None),
#             'envelope_from'     : site_properties.email_from_address
#             }

variables = {'send_from_address' : send_from_address,
             'send_to_address'   : send_to_address,
             'subject'           : subject,
             'url'               : url,
             'title'             : pretty_title_or_id(context),
             'description'       : context.Description(),
             'comment'           : comment,
             'envelope_from'     : site_properties.email_from_address
             }

try:
#    plone_utils.sendto( **variables )
#    message = context.sendto_template(context, send_to_address=send_to_address,
#                           send_from_address=send_from_address,
#                           comment=comment, subject=subject, **kwargs)
    message = context.sendto_template(context, **variables)
    subject = unicode(subject.decode('utf-8'))
    host = context.MailHost
    encoding = effective_charset() or portal.getProperty('email_charset')
    envelope_from = send_from_address
    result = host.secureSend(message, send_to_address, envelope_from, subject=subject, subtype='plain', charset=encoding, debug=False, From=send_from_address)
except ConflictError:
    raise
except: # TODO To many things could possibly go wrong. So we catch all.
    exception = context.plone_utils.exceptionString()
    message = _(u'Unable to send mail: ${exception}',
                mapping={u'exception' : exception})
    context.plone_utils.addPortalMessage(message, 'error')
    return state.set(status='failure')

tmsg='Sent page %s to %s' % (url, REQUEST.send_to_address)
transaction_note(tmsg)

context.plone_utils.addPortalMessage(_(u'Mail sent.'))
return state
