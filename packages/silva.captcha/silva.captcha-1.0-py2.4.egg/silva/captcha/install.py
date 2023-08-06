# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: install.py 28748 2008-05-20 09:23:54Z sylvain $

def install(root):
    """Install Captcha Support.
    """
    pass
    
from Products.Five.site.localsite import enableLocalSiteHook, FiveSite

from zope.app.component.hooks import setSite
from zope.component import queryUtility

from plone.keyring.interfaces import IKeyManager

from utility import SilvaKeyManager


def install(context):
    """Install Captcha Support.
    """
    enableLocalSiteHook(context)
    setSite(context)
    sm = context.getSiteManager()
    sm.registerUtility(IKeyManager, SilvaKeyManager())

def uninstall(context):
    """Uninstall Captcha Support.
    """
    sm = context.getSiteManager()
    sm.unregisterUtility(IKeyManager)
    
def is_installed(context):
    return not (queryUtility(IKeyManager) is None)



