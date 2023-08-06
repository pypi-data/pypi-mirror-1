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
""" Products.WatermarkImage Zope2 initialization code

$Id: __init__.py 1757 2009-05-07 10:20:09Z jens $
"""

# Make sure the registrations take place
import eventhandlers

def initialize(context):
    """ initializer called when used as a zope2 product """
    from Products.WatermarkImage import image

    context.registerClass(
        image.WatermarkImage,
        constructors=(image.manage_addWatermarkImageForm,
                      image.manage_addWatermarkImage
                      ),
        icon='www/watermarkimage.gif',
        )

