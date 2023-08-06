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

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

class SimpleViewerView(BrowserView):
    """
    SimpleViewer view class.
    """
    
    def getThumb(self):
        """
        Return thumb.
        """
        image_id = self.request.get('id', '')
        size = self.request.get('size', '')
        
        try:
            return self.context.restrictedTraverse('%s/image_%s' %(image_id, size)).data
        except:
            return
