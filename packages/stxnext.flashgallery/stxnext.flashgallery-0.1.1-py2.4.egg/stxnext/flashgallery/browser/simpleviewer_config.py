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

class SimpleViewerConfig(BrowserView):
    """
    Base view class for simpleviewer and autoviewer XML configure data. 
    """
    
    def getImagesInFolder(self):
        """
        Return list of images.
        """
        pc = getToolByName(self.context, 'portal_catalog')
        return pc(object_provides='Products.ATContentTypes.interface.image.IATImage', 
                  path={'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
                  sort_on='getObjPositionInParent')
    
    def getImageCaption(self, image):
        """
        Return caption of given image.
        """
        result = []
        
        if image.Title:
            result.append('<B>%s</B><BR />' % image.Title)
        
        if image.Description:
            result.append(image.Description.replace('\r', ''))
            result.append('<BR />')
        
        result.append('<A href="%s" target="_blank"><U>Original size</U></A>' % image.getURL())
        
        return '<BR />'.join(result)
    