##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from netsight.caseinsensitivefieldindex import CaseInsensitiveFieldIndex

def initialize(context):

    context.registerClass(
        CaseInsensitiveFieldIndex.CaseInsensitiveFieldIndex,
        permission = 'Add Pluggable Index',
        constructors = (CaseInsensitiveFieldIndex.manage_addCaseInsensitiveFieldIndexForm,
                        CaseInsensitiveFieldIndex.manage_addCaseInsensitiveFieldIndex,),
        icon='www/index.gif',
        visibility=None
    )

manage_addCaseInsensitiveFieldIndexForm = CaseInsensitiveFieldIndex.manage_addCaseInsensitiveFieldIndexForm
manage_addCaseInsensitiveFieldIndex = CaseInsensitiveFieldIndex.manage_addCaseInsensitiveFieldIndex
