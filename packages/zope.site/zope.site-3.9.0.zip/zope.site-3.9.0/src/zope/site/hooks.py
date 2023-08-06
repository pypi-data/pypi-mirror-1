##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Hooks for getting and setting a site in the thread global namespace.

$Id: hooks.py 105534 2009-11-09 07:37:17Z tlotze $
"""
__docformat__ = 'restructuredtext'

from zope.component.hooks import (read_property,
                                  SiteInfo,
                                  siteinfo,
                                  setSite,
                                  getSite,
                                  getSiteManager,
                                  adapter_hook,
                                  setHooks,
                                  resetHooks,
                                  setSite,
                                  clearSite) # BBB
