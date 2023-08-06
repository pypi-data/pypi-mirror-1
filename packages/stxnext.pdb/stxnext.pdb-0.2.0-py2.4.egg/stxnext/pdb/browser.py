# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 STX Next Sp. z o.o. and Contributors.
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

from stxnext import pdb as p_d_b


IN_ZOPE_2 = False
IN_ZOPE_3 = False
BrowserView = object
DevelopmentMode = False

try:
    from zope.publisher.browser import BrowserView
    from zope.app.appsetup.appsetup import getConfigContext
    DevelopmentMode = getConfigContext().hasFeature('devmode')
    IN_ZOPE_3 = True
except:
    pass

try:
    from Products.Five import BrowserView
    from Globals import DevelopmentMode
    IN_ZOPE_2 = True
except ImportError:
    pass


class STXNextPdbView(BrowserView):
    """
    View class for STXNextPdb.
    
    @author: Wojciech Lichota <wojciech.lichota[at]stxnext.pl>
    """

    def __call__(self):
        """
        Open STXNextPdb.
        
        Usage:
          http://127.0.0.1:8080/plonesite/pdb        
        """
        if not DevelopmentMode:
            return "You must turn on debug-mode!"
        
        try:
            import rlcompleter, readline
            readline.parse_and_bind('tab: complete')
        except ImportError:
            pass        
                
        p_d_b.set_trace()
        
        return "stxnext.pdb stoped"
