# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: install.py 31899 2008-11-12 10:35:19Z sylvain $

from Products.Five.site.localsite import enableLocalSiteHook, FiveSite

from zope.app.component.interfaces import ISite
from zope.app.component.hooks import setSite
from zope.component import queryUtility

from plone.keyring.interfaces import IKeyManager

from utility import SilvaKeyManager


def install(context):
    """Install Captcha Support.
    """
    if not ISite.providedBy(context):
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



