import re
from base64 import b64encode
from AccessControl import Unauthorized#, allow_module
from smtplib import SMTPRecipientsRefused
from zope.component import getUtility
from Acquisition import aq_inner
from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from collective.langMailHost.interfaces import ILangCharset
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.RegistrationTool import RegistrationTool
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('shopinmall')

class RegistrationTool(RegistrationTool):

    security = ClassSecurityInfo()

    security.declarePublic('mailPassword')
    def mailPassword(self, forgotten_userid, REQUEST):
        """ Wrapper around mailPassword """
        membership = getToolByName(self, 'portal_membership')
        if not membership.checkPermission('Mail forgotten password', self):
            raise Unauthorized, "Mailing forgotten passwords has been disabled"

        utils = getToolByName(self, 'plone_utils')
        member = membership.getMemberById(forgotten_userid)

        if member is None:
            raise ValueError, 'The username you entered could not be found'

        # assert that we can actually get an email address, otherwise
        # the template will be made with a blank To:, this is bad
        email = member.getProperty('email')
        if not email:
            raise ValueError('That user does not have an email address.')
        else:
            # add the single email address
            if not utils.validateSingleEmailAddress(email):
                raise ValueError, 'The email address did not validate'
        check, msg = _checkEmail(email)
        if not check:
            raise ValueError, msg

        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).
        reset_tool = getToolByName(self, 'portal_password_reset')
        reset = reset_tool.requestReset(forgotten_userid)
        urltool = getToolByName(self, 'portal_url')
        portal = urltool.getPortalObject()
        email_charset = ILangCharset(portal).effective_charset() or portal.getProperty('email_charset', 'UTF-8')

        subject = portal.translate(msgid=u'mailtemplate_subject_resetpasswordrequest', domain='passwordresettool')
        subject = b64encode(subject.encode(email_charset))
        subject = '=?%s?b?%s?=' %(email_charset, subject)
        mail_text = self.mail_password_template( self
                                               , REQUEST
                                               , member=member
                                               , reset=reset
                                               , password=member.getPassword()
                                               , charset=email_charset
                                               )
        if isinstance(mail_text, unicode):
            mail_text = mail_text.encode(email_charset, 'replace')
        host = self.MailHost
        try:
            host.send(mail_text, subject=subject)

            return self.mail_password_response( self, REQUEST )
        except SMTPRecipientsRefused:
            # Don't disclose email address on failure
            raise SMTPRecipientsRefused('Recipient address rejected by server')


    security.declarePublic('registeredNotify')
    def registeredNotify(self, new_member_id):
#    def registeredNotify(self):
        """ Wrapper around registeredNotify """
#        REQUEST = self.request
#        new_member_id = REQUEST['username']
#        context = aq_inner(self.context)
        membership = getToolByName( self, 'portal_membership' )
        utils = getToolByName(self, 'plone_utils')
        member = membership.getMemberById( new_member_id )

        if member and member.getProperty('email'):
            # add the single email address
            if not utils.validateSingleEmailAddress(member.getProperty('email')):
                raise ValueError, 'The email address did not validate'

        email = member.getProperty( 'email' )
        try:
            checkEmailAddress(email)
        except EmailAddressInvalid:
            raise ValueError, 'The email address did not validate'

        pwrt = getToolByName(self, 'portal_password_reset')
        reset = pwrt.requestReset(new_member_id)

        urltool = getToolByName(self, 'portal_url')
        portal = urltool.getPortalObject()
        encoding = ILangCharset(portal).effective_charset() or getUtility(ISiteRoot).getProperty('email_charset')

#        subject = _(
#            u'mailtemplate_user_account_info',
#            u"User Account Information for ${portal_name}",
#            mapping={'portal_name' : portal.Title()}
#        )
        subject = portal.translate(msgid=u'mailtemplate_user_account_info', domain='passwordresettool', mapping={'portal_name' : portal.Title()})
        subject = b64encode(subject.encode(encoding))
        subject = '=?%s?b?%s?=' %(encoding, subject)


#Subject: <span i18n:domain="passwordresettool" i18n:translate="mailtemplate_user_account_info" tal:omit-tag="">User Account Information for <span i18n:name="portal_name" tal:omit-tag="" tal:content="python:here.portal_url.getPortalObject().Title()" /></span>

        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).

        mail_text = self.registered_notify_template( self
                                                   , self.REQUEST
                                                   , member=member
                                                   , reset=reset
                                                   , email=email
                                                   , charset=encoding
                                                   )

        if isinstance(mail_text, unicode):
            mail_text = mail_text.encode(encoding, 'replace')

        host = self.MailHost

        host.send(mail_text, subject=subject)

        return self.mail_password_response( self, self.REQUEST )


_TESTS = ( ( re.compile("^[0-9a-zA-Z\.\-\_\+\']+\@[0-9a-zA-Z\.\-]+$")
           , True
           , "Failed a"
           )
         , ( re.compile("^[^0-9a-zA-Z]|[^0-9a-zA-Z]$")
           , False
           , "Failed b"
           )
         , ( re.compile("([0-9a-zA-Z_]{1})\@.")
           , True
           , "Failed c"
           )
         , ( re.compile(".\@([0-9a-zA-Z]{1})")
           , True
           , "Failed d"
           )
         , ( re.compile(".\.\-.|.\-\..|.\.\..|.\-\-.")
           , False
           , "Failed e"
           )
         , ( re.compile(".\.\_.|.\-\_.|.\_\..|.\_\-.|.\_\_.")
           , False
           , "Failed f"
           )
         , ( re.compile(".\.([a-zA-Z]{2,3})$|.\.([a-zA-Z]{2,4})$")
           , True
           , "Failed g"
           )
         )

def _checkEmail( address ):
    for pattern, expected, message in _TESTS:
        matched = pattern.search( address ) is not None
        if matched != expected:
            return False, message
    return True, ''

