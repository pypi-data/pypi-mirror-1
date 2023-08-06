# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py 28119 2008-03-19 15:59:13Z sylvain $

import install
import Membership

from Products.Silva.ExtensionRegistry import extensionRegistry

def initialize(context):
    extensionRegistry.register(
        'silva.pas.base', 'Silva Pluggable Auth Service Support', context, [],
        install, depends_on='Silva')
    
    context.registerClass(
        Membership.MemberService,
        constructors = (Membership.manage_addMemberServiceForm,
                        Membership.manage_addMemberService),
        )

