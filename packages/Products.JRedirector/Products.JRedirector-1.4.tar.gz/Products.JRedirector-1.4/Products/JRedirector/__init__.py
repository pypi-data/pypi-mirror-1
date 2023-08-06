##############################################################################
#
# Copyright (c) 2002-2009 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" JRedirector initialization

$Id: __init__.py 1810 2009-06-23 10:57:31Z jens $
"""

from JRedirector import addJRedirectorForm
from JRedirector import JRedirector 
from JRedirector import manage_addJRedirector

def initialize(context):
    context.registerClass( JRedirector
                         , permission='Add JRedirector'
                         , constructors=( addJRedirectorForm
                                        , manage_addJRedirector 
                                        )
                         , icon='www/jredirector.gif'
                         )

    context.registerHelp()
