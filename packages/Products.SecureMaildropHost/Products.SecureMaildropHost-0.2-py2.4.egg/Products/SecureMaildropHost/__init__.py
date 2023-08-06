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
# SecureMaildropHost Initialization

from SecureMaildropHost import SecureMaildropHost
from SecureMaildropHost import addSecureMaildropHostForm
from SecureMaildropHost import manage_addSecureMaildropHost

def initialize( context ):
    context.registerClass(SecureMaildropHost,
                          permission='Add MailHost objects',
                          constructors=(addSecureMaildropHostForm,
                                        manage_addSecureMaildropHost),
                          icon='www/maildrop.gif')
