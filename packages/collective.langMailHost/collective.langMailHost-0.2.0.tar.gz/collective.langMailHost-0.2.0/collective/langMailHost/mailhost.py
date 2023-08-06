from copy import deepcopy
import email
from email.Utils import getaddresses
from email.Utils import formataddr
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import use_mailhost_services
from Products.CMFCore.utils import getToolByName
from Products.MailHost.MailHost import MailHostError#, _encode, _mungeHeaders
from Products.SecureMailHost.SecureMailHost import SecureMailHost, encodeHeaderAddress
from Products.SecureMailHost.config import BAD_HEADERS
from collective.langMailHost.interfaces import ILangCharset

class LangMailHost(SecureMailHost):

    security = ClassSecurityInfo()

    security.declareProtected(use_mailhost_services, 'secureSend')
    def secureSend(self, message, mto, mfrom, subject='[No Subject]',
                   mcc=None, mbcc=None, subtype='plain', charset='us-ascii',
                   debug=False, **kwargs):
        """A more secure way to send a message

        message:
            The plain message text without any headers or an
            email.Message.Message based instance
        mto:
            To: field (string or list)
        mfrom:
            From: field
        subject:
            Message subject (default: [No Subject])
        mcc:
            Cc: (carbon copy) field (string or list)
        mbcc:
            Bcc: (blind carbon copy) field (string or list)
        subtype:
            Content subtype of the email e.g. 'plain' for text/plain (ignored
            if message is a email.Message.Message instance)
        charset:
            Charset used for the email, subject and email addresses
        kwargs:
            Additional headers
        """
        mto  = self.emailListToString(mto)
        mcc  = self.emailListToString(mcc)
        mbcc = self.emailListToString(mbcc)
        # validate email addresses
        # XXX check Return-Path
        for addr in mto, mcc, mbcc:
            if addr:
                result = self.validateEmailAddresses(addr)
                if not result:
                    raise MailHostError, 'Invalid email address: %s' % addr
        result = self.validateSingleEmailAddress(mfrom)
        if not result:
            raise MailHostError, 'Invalid email address: %s' % mfrom
        urltool = getToolByName(self, "portal_url")
        portal = urltool.getPortalObject()
        charset = ILangCharset(portal).effective_charset() or portal.getProperty('email_charset', 'UTF-8')

        # create message
        if isinstance(message, email.Message.Message):
            # got an email message. Make a deepcopy because we don't want to
            # change the message
            msg = deepcopy(message)
        else:
            if isinstance(message, unicode):
                message = message.encode(charset)
            msg = email.MIMEText.MIMEText(message, subtype, charset)

        mfrom = encodeHeaderAddress(mfrom, charset)
        mto = encodeHeaderAddress(mto, charset)
        mcc = encodeHeaderAddress(mcc, charset)
        mbcc = encodeHeaderAddress(mbcc, charset)

        # set important headers
        self.setHeaderOf(msg, skipEmpty=True, From=mfrom, To=mto,
#                 Subject=str(email.Header.Header(subject, charset)),
                 Subject=str(email.Header.Header(subject.decode('utf-8'), charset)),
                 Cc=mcc, Bcc=mbcc)

        for bad in BAD_HEADERS:
            if bad in kwargs:
                raise MailHostError, 'Header %s is forbidden' % bad
        self.setHeaderOf(msg, **kwargs)

        # we have to pass *all* recipient email addresses to the
        # send method because the smtp server doesn't add CC and BCC to
        # the list of recipients
        to = msg.get_all('to', [])
        cc = msg.get_all('cc', [])
        bcc = msg.get_all('bcc', [])
        #resent_tos = msg.get_all('resent-to', [])
        #resent_ccs = msg.get_all('resent-cc', [])
        recipient_list = getaddresses(to + cc + bcc)
        all_recipients = [formataddr(pair) for pair in recipient_list]

        # finally send email
        return self._send(mfrom, all_recipients, msg, debug=debug)
