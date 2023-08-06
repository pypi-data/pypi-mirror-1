# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: install.py 28983 2008-06-04 10:18:12Z sylvain $

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
    utility = sm.queryUtility(IKeyManager)
    parent = utility.aq_parent
    parent.manage_delObjects(['IKeyManager'])
    
def is_installed(context):
    return not (queryUtility(IKeyManager) is None)



