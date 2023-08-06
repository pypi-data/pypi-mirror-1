##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from Globals import DTMLFile

from Products.SecureMailHost.SecureMailHost import SecureMailHost
from Products.MaildropHost import MaildropHost

addSecureMaildropHostForm = DTMLFile('www/addSecureMaildropHost_form', globals())

def manage_addSecureMaildropHost(self, id, title='', REQUEST=None):
    """add a SecureMaildropHost"""
    smdh = SecureMaildropHost(id, title)
    self._setObject(id, smdh)

    if REQUEST is not None:
        ret_url = '%s/%s/manage_main' % (self.absolute_url(), id)
        REQUEST['RESPONSE'].redirect(ret_url)

class SecureMaildropHost(MaildropHost, SecureMailHost):
    meta_type = 'Secure Maildrop Host'
    def _send(self, mfrom, mto, messageText, debug=False):
        """Send a mail using the asynchronous maildrop handler"""
        if hasattr(messageText,'as_string'):
            # for MIMEText messages
            msg = messageText.as_string()
        else:
            # for other messages
            msg = str(messageText)
        MaildropHost._send(self, mfrom, mto, msg)
