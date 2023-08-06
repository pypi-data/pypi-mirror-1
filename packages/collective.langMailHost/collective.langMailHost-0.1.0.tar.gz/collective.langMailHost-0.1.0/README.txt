Introduction
============

Character set of outgoing mail of Plone is defined in a portal property name "email_charset" and this 
charset set is globally used in the Plone site.
This is fine with monolingual site, however in multilingual site, there are cases you want to send mails with differernt character sets for different languages.

This package aims to provide language dependent character set for sending emails form Plone site.

There are five main default cases for sending e-mails from Plone site:

1. When new user registers to the site with password setting  disabled.
2. When a user forgets password and plone sends the user the guide to reset it.
3. When user contacts administrator form contact form.
4. When sending content to somebody from "Send this" link.
5. When content rules trigers sending mail, ex) when adding content to a certain folder.

All these five cases are supported by this package, however tests are only done with character set of iso-2022-jp for Japanese language and utf-8 for other languages.

Setting language and character set
----------------------------------

Once you installed this package from quickinstaller, go to ZMI of the plone site.
Within portal_properties, there is mailhost_properties where you can set two propeties.

* lang_charset
    'ja|iso-2022-jp' is default value.
    This means for Japanese language ('ja'), use character set 'iso-2022-jp'.
    To add other language and character set pair, add it line by line.
    Remenber to follow this syntax: language|charset

* is_member_lang_effective
    If this option is selected, logged in member receives e-mail with the character set of member's choice of languages.


Script example for your own code
--------------------------------

To use this feature in your own package, simply apply ILangCharset interface to portal object like:

    >>> from collective.langMailHost.interfaces import ILangCharset
    >>> email_charset = ILangCharset(portal).effective_charset() or portal.getProperty('email_charset', 'UTF-8')
    >>> mailhost.secureSend(message, email_recipient, source,
                                subject=subject, subtype='plain',
                                charset=email_charset, debug=False,
                                From=source)


