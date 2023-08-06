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

from simpleviewer_config import SimpleViewerConfig    

class AutoViewerConfig(SimpleViewerConfig):
    """
    View class for autoviewer XML configure data. 
    """
    
    def getImageCaption(self, image):
        """
        Return caption of given image.
        """
        return '<font size="14">%s</font>' % super(AutoViewerConfig, self).getImageCaption(image)
    
    def getImageWidth(self, image):
        """
        Return image_large width.
        """
        try:
            return self.context.restrictedTraverse('%s/image_preview' % image.getId).width
        except:
            return 0
    
    def getImageHeight(self, image):
        """
        Return image_large width.
        """
        try:
            return self.context.restrictedTraverse('%s/image_preview' % image.getId).height
        except:
            return 0