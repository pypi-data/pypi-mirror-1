#import re
from base64 import b64encode
#from AccessControl import Unauthorized#, allow_module
#from smtplib import SMTPRecipientsRefused
from zope.component import getUtility
#from Acquisition import aq_inner
from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from collective.langMailHost.interfaces import ILangCharset
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.RegistrationTool import RegistrationTool#, _checkEmail
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('shopinmall')

class LangRegistrationTool(RegistrationTool):

    security = ClassSecurityInfo()


    security.declarePublic('registeredNotify')
    def registeredNotify(self, new_member_id):
        """ Wrapper around registeredNotify """
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

        subject = portal.translate(msgid=u'mailtemplate_user_account_info', domain='passwordresettool', mapping={'portal_name' : portal.Title()})
        subject = b64encode(subject.encode(encoding))
        subject = '=?%s?b?%s?=' %(encoding, subject)

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


#_TESTS = ( ( re.compile("^[0-9a-zA-Z\.\-\_\+\']+\@[0-9a-zA-Z\.\-]+$")
#           , True
#           , "Failed a"
#           )
#         , ( re.compile("^[^0-9a-zA-Z]|[^0-9a-zA-Z]$")
#           , False
#           , "Failed b"
#           )
#         , ( re.compile("([0-9a-zA-Z_]{1})\@.")
#           , True
#           , "Failed c"
#           )
#         , ( re.compile(".\@([0-9a-zA-Z]{1})")
#           , True
#           , "Failed d"
#           )
#         , ( re.compile(".\.\-.|.\-\..|.\.\..|.\-\-.")
#           , False
#           , "Failed e"
#           )
#         , ( re.compile(".\.\_.|.\-\_.|.\_\..|.\_\-.|.\_\_.")
#           , False
#           , "Failed f"
#           )
#         , ( re.compile(".\.([a-zA-Z]{2,3})$|.\.([a-zA-Z]{2,4})$")
#           , True
#           , "Failed g"
#           )
#         )

#def _checkEmail( address ):
#    for pattern, expected, message in _TESTS:
#        matched = pattern.search( address ) is not None
#        if matched != expected:
#            return False, message
#    return True, ''

