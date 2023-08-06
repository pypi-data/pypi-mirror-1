##############################################################################
#
# Copyright (c) 2008-2009 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Interfaces for the Products.WatermarkImage package

$Id: interfaces.py 1756 2009-05-05 21:00:18Z jens $
"""

from zope.interface import Interface


class IWatermarkImage(Interface):
    """ A Zope 2 image with thumbnail and watermarking support
    """

    def index_html(REQUEST, RESPONSE):
        """ Return the watermarked contents of the image.
        
        o Sets the Content-Type HTTP header to the objects content type.

        o Handle If-Modified-Since requests appropriately.
        """

