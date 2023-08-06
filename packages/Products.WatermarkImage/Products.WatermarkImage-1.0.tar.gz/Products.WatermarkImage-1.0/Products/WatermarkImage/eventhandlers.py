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
""" WatermarkImage evant handlers

$Id: eventhandlers.py 1764 2009-05-09 12:32:19Z jens $
"""

def handleImageModifiedEvent(obj, event):
    thumbnail_update = True
    watermarked_update = True

    if event.descriptions:
        old_props = dict(event.descriptions)

        if ( old_props['watermark_id'] == obj.watermark_id and
             old_props['watermark_opacity'] == obj.watermark_opacity and
             old_props['watermark_use'] == obj.watermark_use and
             old_props['watermark_position_x'] == obj.watermark_position_x and
             old_props['watermark_position_y'] == obj.watermark_position_y ):
            watermarked_update = False

            if ( old_props['thumbnail_max_height'] == obj.thumbnail_max_height and
                 old_props['thumbnail_max_width'] == obj.thumbnail_max_width ):
                thumbnail_update = False
                 
    if watermarked_update:
        obj.update_watermarked()
        obj.update_thumbnail()
    elif thumbnail_update:
        obj.update_thumbnail()
