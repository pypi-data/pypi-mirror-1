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
""" WatermarkImage main module

$Id: image.py 1764 2009-05-09 12:32:19Z jens $
"""

from cgi import escape
import copy
from cStringIO import StringIO
from tempfile import NamedTemporaryFile

from PIL import Image as PILImage
from PIL import ImageEnhance as PILImageEnhance

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import change_images_and_files
from AccessControl.Permissions import manage_properties
from AccessControl.Permissions import view
from App.config import getConfiguration
from App.special_dtml import DTMLFile
from OFS.Image import cookId
from OFS.Image import getImageInfo
from OFS.Image import Image as OFSImage
from OFS.Image import Pdata
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent

from Products.WatermarkImage.interfaces import IWatermarkImage

wim_config = getConfiguration().product_config.get('watermarkimage', {})
config_watermark_use = wim_config.get('watermark_use')
config_watermark_position_x = int(wim_config.get('watermark_position_x', 0))
config_watermark_position_y = int(wim_config.get('watermark_position_y', 0))
config_watermark_opacity = float(wim_config.get('watermark_opacity', 0))
config_watermark_id = wim_config.get('watermark_id')
config_thumbnail_max_height = int(wim_config.get('thumbnail_max_height', 0))
config_thumbnail_max_width = int(wim_config.get('thumbnail_max_width', 0))

manage_addWatermarkImageForm = PageTemplateFile('www/add.pt', globals())

def manage_addWatermarkImage( self
                            , id
                            , file
                            , title=''
                            , precondition=''
                            , content_type=''
                            , description=''
                            , REQUEST=None
                            ):
    """ Add a new WatermarkImage object
    """
    id, title = cookId(id, title, file)
    self = self.this()

    # First, we create the image without data:
    self._setObject(id, WatermarkImage(id,title,'',content_type, precondition))
    img = self._getOb(id)
    img.description = description

    # Now we "upload" the data.  By doing this in two steps, we
    # can use a database trick to make the upload more efficient.
    if file:
        img.manage_upload(file)
    if content_type:
        img.content_type = content_type

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect('%s/manage_main' % REQUEST['URL1'])
    return id


class WatermarkImage(OFSImage):
    """ A Zope 2 image with thumbnail and watermarking support
    """
    implements(IWatermarkImage)
    meta_type = 'Watermark Image'
    security = ClassSecurityInfo()
    watermark_uses = ('none', 'position', 'tile', 'scale')

    manage_thumbnailForm = DTMLFile('www/thumbnail', globals())
    manage_watermarkedForm = DTMLFile('www/watermarked', globals())
    manage_editForm = DTMLFile('www/edit', globals())
    manage_editForm._setName('manage_editForm')
    manage = manage_main = manage_editForm
    manage_options = ( ( { 'label': 'Edit Original'
                         , 'action': 'manage_main'
                         }
                       , { 'label': 'Watermarked'
                         , 'action': 'manage_watermarkedForm'
                         }
                       , { 'label': 'Thumbnail'
                         , 'action': 'manage_thumbnailForm'
                         }
                       )
                     + OFSImage.manage_options[2:]
                     )

    _properties = ( { 'id': 'title'
                    , 'label': 'Title'
                    , 'type': 'ustring'
                    , 'mode': 'w'
                    }
                  , { 'id': 'alt'
                    , 'label': 'Text alternative'
                    , 'type': 'ustring'
                    , 'mode': 'w'
                    }
                  , { 'id': 'description'
                    , 'label': 'Description'
                    , 'type': 'utext'
                    , 'mode': 'w'
                    }
                  , { 'id': 'watermark_id'
                    , 'label': 'Watermark ID'
                    , 'type': 'string'
                    , 'mode': 'w'
                    }
                  , { 'id': 'watermark_opacity'
                    , 'label': 'Watermark opacity (between 0 and 1)'
                    , 'type': 'float'
                    , 'mode': 'w'
                    }
                  , { 'id': 'watermark_use'
                    , 'label': 'Watermark use'
                    , 'type': 'selection'
                    , 'select_variable': 'watermark_uses'
                    , 'mode': 'w'
                    }
                  , { 'id': 'watermark_position_x'
                    , 'label': 'Watermark position on X-axis'
                    , 'type': 'int'
                    , 'mode': 'w'
                    }
                  , { 'id': 'watermark_position_y'
                    , 'label': 'Watermark position on Y-axis'
                    , 'type': 'int'
                    , 'mode': 'w'
                    }
                  , { 'id': 'thumbnail_max_height'
                    , 'label': 'Maximum thumbnail height (pixels)'
                    , 'type': 'int'
                    , 'mode': 'w'
                    }
                  , { 'id': 'thumbnail_max_width'
                    , 'label': 'Maximum thumbnail width (pixels)'
                    , 'type': 'int'
                    , 'mode': 'w'
                    }
                  )

    def __init__(self, id, title, file, content_type='', precondition=''):
        self.alt = title
        self.description = ''
        self.watermark_id = config_watermark_id or 'watermark_image'
        self.thumbnail_max_height = config_thumbnail_max_height or 100
        self.thumbnail_max_width = config_thumbnail_max_width or 100
        self.watermark_opacity = config_watermark_opacity or 1
        self.watermark_use = config_watermark_use or 'position'
        self.watermark_position_x = config_watermark_position_x or 0
        self.watermark_position_y = config_watermark_position_y or 0
        self.data = ''
        self.height = self.width = self.size = 0
        self.thumb_content_type = 'text/x-unknown-content-type'
        self.thumb_height = self.thumb_width = self.thumb_size = 0
        self.thumb_data = ''
        self.original_content_type = 'text/x-unknown-content-type'
        self.original_size = 0
        self.original_data = ''
        OFSImage.__init__(self, id, title, file, content_type, precondition)

    security.declareProtected(manage_properties, 'manage_editProperties')
    def manage_editProperties(self, REQUEST):
        """ Edit object properties via the web

        Must override this method because PropertyManager does not
        support events yet - some property changes could require 
        regeneration of watermarked image or thumbnail or both.
        """
        old_properties = copy.deepcopy(self.propertyItems())
        for prop in self._propertyMap():
            name=prop['id']
            if 'w' in prop.get('mode', 'wd'):
                if prop['type'] == 'multiple selection':
                    value=REQUEST.get(name, [])
                else:
                    value=REQUEST.get(name, '')
                self._updateProperty(name, value)
        notify(ObjectModifiedEvent(self, *old_properties))
        if REQUEST:
            message="Saved changes."
            return self.manage_propertiesForm(self,REQUEST,
                                              manage_tabs_message=message)

    security.declareProtected(change_images_and_files, 'manage_edit')
    def manage_edit(self, title, content_type, precondition='',
                    filedata=None, REQUEST=None):
        """ Change the title and/or content type attribute

        Overridden to change the original image content type
        """
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"

        self.title=str(title)
        self.original_content_type=str(content_type)
        if precondition: self.precondition=str(precondition)
        elif self.precondition: del self.precondition
        if filedata is not None:
            self.update_data(filedata, content_type, len(filedata))
        else:
            self.ZCacheable_invalidate()
        if REQUEST:
            message="Saved changes."
            return self.manage_main(self,REQUEST,manage_tabs_message=message)

    security.declarePrivate('update_data')
    def update_data(self, data, content_type=None, size=None):
        """ Update the stored image

        - self.data contains watermarked image
        - original image data is saved in self.original_data
        - incoming value for data can be either str or pData
        """
        if isinstance(data, unicode):
            raise TypeError('Data can only be str or file-like.  '
                            'Unicode objects are expressly forbidden.')

        # Save the original image data and metadata
        if isinstance(data, Pdata):
            self.original_data = data
        else:
            ( self.original_data
            , self.original_size
            ) = self._read_data(data)

        ct, width, height = getImageInfo(data)
        if ct:
            self.original_content_type = ct

        if size is not None:
            self.original_size = size
        if content_type is not None: 
            self.original_content_type = self.content_type = content_type

        notify(ObjectModifiedEvent(self))

        self.ZCacheable_invalidate()
        self.ZCacheable_set(None)
        self.http__refreshEtag()


    #################################################################
    # Watermark handling
    #################################################################

    security.declarePrivate('update_watermarked')
    def update_watermarked(self):
        """ Regenerate watermarked image
        """
        watermark_id = self.getProperty('watermark_id')
        watermark_use = self.getProperty('watermark_use')

        if not watermark_id or not watermark_use or watermark_use == 'none':
            self.data = self.original_data
            self.size = self.original_size
            self.content_type = self.original_content_type
            ignored, self.width, self.height = getImageInfo(self.data)
            return

        if len(self.original_data) == 0:
            self.data = self.original_data
            self.content_type = self.original_content_type
            self.size = self.width = self.height = 0
            return

        mark_data = str(getattr(self, self.getProperty('watermark_id')).data)
        x_pos = self.getProperty('watermark_position_x', 0)
        y_pos = self.getProperty('watermark_position_y', 0)
        watermark_use = self.getProperty('watermark_use')

        pil_img = PILImage.open(StringIO(str(self.original_data)))
        original_format = pil_img.format
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')

        if x_pos < 0:
            x_pos = pil_img.size[0] - abs(x_pos)
        if y_pos < 0:
            y_pos = pil_img.size[1] - abs(y_pos)

        pil_mark = PILImage.open(StringIO(mark_data))
        if pil_mark.mode != 'RGBA':
            pil_mark = pil_mark.convert('RGBA')

        opacity = getattr(self, 'watermark_opacity', 1)
        if 0 <= opacity < 1:
            pm = pil_mark.copy()
            alpha = pm.split()[3]
            alpha = PILImageEnhance.Brightness(alpha).enhance(opacity)
            pil_mark.putalpha(alpha)

        layer = PILImage.new('RGBA', pil_img.size, (0,0,0,0))

        if watermark_use == 'tile':
            for y in range(0, pil_img.size[1], pil_mark.size[1]):
                for x in range(0, pil_img.size[0], pil_mark.size[0]):
                    layer.paste(pil_mark, (x, y))
        elif watermark_use == 'scale':
            # scale, but preserve the aspect ratio
            ratio = min( float(pil_img.size[0]) / pil_mark.size[0]
                       , float(pil_img.size[1]) / pil_mark.size[1]
                       )
            w = int(pil_mark.size[0] * ratio)
            h = int(pil_mark.size[1] * ratio)
            pil_mark = pil_mark.resize((w, h))
            layer.paste( pil_mark
                       , ( (pil_img.size[0] - w) / 2
                         , (pil_img.size[1] - h) / 2
                         )
                       )
        else:
            layer.paste(pil_mark, (x_pos, y_pos))
        
        out_file = StringIO()
        composite = PILImage.composite(layer, pil_img, layer)
        composite.save(out_file, original_format or 'JPEG')
        out_file.reset()

        self.data, self.size = self._read_data(out_file)

        ct, width, height = getImageInfo(self.data)
        if ct:
            self.content_type = ct
        if width >= 0 and height >= 0:
            self.width = width
            self.height = height


    #################################################################
    # Thumbnail handling
    #################################################################

    security.declarePrivate('update_thumbnail')
    def update_thumbnail(self, width=None, height=None):
        """ Generate a thumbnail from the stored image data
        """
        if width is None:
            width = self.thumbnail_max_width

        if height is None:
            height = self.thumbnail_max_height

        if self.size > 0:
            data_file = StringIO(str(self.data))
            pil_img = PILImage.open(data_file)

            if pil_img.mode != 'RGBA':
                pil_img = pil_img.convert('RGBA')

            if not ( width and height ):
                original_width, original_height = pil_img.size
                original_ratio = float(original_width) / float(original_height)
                
                if width and not height:
                    height = int( width * original_ratio )
                else:
                    width = int( height * original_ratio )

            pil_img.thumbnail((width, height))
            out_file = StringIO()
            pil_img.save(out_file, 'JPEG')
            out_file.reset()

            self.thumb_data, self.thumb_size = self._read_data(out_file)
            ( self.thumb_content_type
            , self.thumb_width
            , self.thumb_height
            ) = getImageInfo(self.thumb_data)

        else:
            self.thumb_data = ''
            self.thumb_content_type = 'text/x-unknown-content-type'
            self.thumb_size = 0
            self.thumb_height = 0
            self.thumb_width = 0

    security.declareProtected(view, 'tag_thumbnail')
    def tag_thumbnail(self, height=None, width=None, alt=None,
            scale=0, xscale=0, yscale=0, css_class=None, title=None, **args):
        """ Generate a HTML img tag for the thumbnail

        Adapted from OFS.Image.Image.tag

        Arguments can be any valid attributes of an IMG tag.
        'src' will always be an absolute pathname, to prevent redundant
        downloading of images. Defaults are applied intelligently for
        'height', 'width', and 'alt'. If specified, the 'scale', 'xscale',
        and 'yscale' keyword arguments will be used to automatically adjust
        the output height and width values of the image tag.

        Since 'class' is a Python reserved word, it cannot be passed in
        directly in keyword arguments which is a problem if you are
        trying to use 'tag()' to include a CSS class. The tag() method
        will accept a 'css_class' argument that will be converted to
        'class' in the output tag to work around this.
        """
        if height is None: height=self.thumb_height
        if width is None:  width=self.thumb_width

        # Auto-scaling support
        xdelta = xscale or scale
        ydelta = yscale or scale

        if xdelta and width:
            width =  str(int(round(int(width) * xdelta)))
        if ydelta and height:
            height = str(int(round(int(height) * ydelta)))

        result='<img src="%s/thumbnail.jpg"' % (self.absolute_url())

        if alt is None:
            alt=getattr(self, 'alt', '')
        result = '%s alt="%s"' % (result, escape(alt, 1))

        if title is None:
            title=getattr(self, 'title', '')
        result = '%s title="%s"' % (result, escape(title, 1))

        if height:
            result = '%s height="%s"' % (result, height)

        if width:
            result = '%s width="%s"' % (result, width)

        if css_class is not None:
            result = '%s class="%s"' % (result, css_class)

        for key in args.keys():
            value = args.get(key)
            if value:
                result = '%s %s="%s"' % (result, key, value)

        return '%s />' % result


    #################################################################
    # Original handling
    #################################################################

    security.declareProtected(view, 'tag_original')
    def tag_original(self, height=None, width=None, alt=None,
            scale=0, xscale=0, yscale=0, css_class=None, title=None, **args):
        """ Generate a HTML img tag for the original image

        Adapted from OFS.Image.Image.tag

        Arguments can be any valid attributes of an IMG tag.
        'src' will always be an absolute pathname, to prevent redundant
        downloading of images. Defaults are applied intelligently for
        'height', 'width', and 'alt'. If specified, the 'scale', 'xscale',
        and 'yscale' keyword arguments will be used to automatically adjust
        the output height and width values of the image tag.

        Since 'class' is a Python reserved word, it cannot be passed in
        directly in keyword arguments which is a problem if you are
        trying to use 'tag()' to include a CSS class. The tag() method
        will accept a 'css_class' argument that will be converted to
        'class' in the output tag to work around this.
        """
        if height is None: height=self.height
        if width is None:  width=self.width

        # Auto-scaling support
        xdelta = xscale or scale
        ydelta = yscale or scale

        if xdelta and width:
            width =  str(int(round(int(width) * xdelta)))
        if ydelta and height:
            height = str(int(round(int(height) * ydelta)))

        result='<img src="%s/original"' % (self.absolute_url())

        if alt is None:
            alt=getattr(self, 'alt', '')
        result = '%s alt="%s"' % (result, escape(alt, 1))

        if title is None:
            title=getattr(self, 'title', '')
        result = '%s title="%s"' % (result, escape(title, 1))

        if height:
            result = '%s height="%s"' % (result, height)

        if width:
            result = '%s width="%s"' % (result, width)

        if css_class is not None:
            result = '%s class="%s"' % (result, css_class)

        for key in args.keys():
            value = args.get(key)
            if value:
                result = '%s %s="%s"' % (result, key, value)

        return '%s />' % result

