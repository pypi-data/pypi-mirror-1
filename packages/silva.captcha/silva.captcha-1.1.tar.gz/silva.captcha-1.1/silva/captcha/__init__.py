# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py 31899 2008-11-12 10:35:19Z sylvain $

from zope.component import getMultiAdapter
from AccessControl import ModuleSecurityInfo, allow_module
from Products.Silva.ExtensionRegistry import extensionRegistry

import install

def initialize(context):
    extensionRegistry.register(
        'silva.captcha', 'Silva Captcha', context, [],
        install, depends_on='Silva')

allow_module('silva.captcha')
module_security = ModuleSecurityInfo('silva.captcha')
module_security.declareProtected('View', 'validate')
def validate(context, request, input):
    """Validate a potential captcha entry for a Python Script.
    """
    captcha = getMultiAdapter((context, request), name='captcha')
    return captcha.verify(input)
