# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py 28748 2008-05-20 09:23:54Z sylvain $

from Products.Silva.ExtensionRegistry import extensionRegistry

import install

def initialize(context):
    extensionRegistry.register(
        'silva.captcha', 'Silva Captcha', context, [],
        install, depends_on='Silva')

