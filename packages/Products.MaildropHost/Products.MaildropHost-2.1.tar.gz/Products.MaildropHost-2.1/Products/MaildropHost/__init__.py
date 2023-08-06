##############################################################################
#
# Copyright (c) Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" MaildropHost initialization

$Id: __init__.py 1648 2008-10-31 18:22:44Z jens $
"""

from AccessControl.Permissions import add_mailhost_objects
from MaildropHost import addMaildropHostForm
from MaildropHost import MaildropHost
from MaildropHost import manage_addMaildropHost

def initialize( context ):
    try:
        context.registerClass( MaildropHost
                             , permission=add_mailhost_objects
                             , constructors=( addMaildropHostForm
                                            , manage_addMaildropHost
                                            )
                             , icon='www/maildrop.gif'
                            )

        context.registerHelp()
        context.registerHelpTitle('MaildropHost')

    except:
        import traceback; traceback.print_exc()

