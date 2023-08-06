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
""" WatermarkImage tests module

$Id: test_image.py 1758 2009-05-07 18:43:37Z jens $
"""

from cStringIO import StringIO
import unittest

from PIL import Image as PILImage

from OFS.Image import Image as OFSImage
from OFS.Image import Pdata
from Products.Five import zcml
from Testing.makerequest import makerequest


def makeImageData(width, height, format='PNG', color='black'):
    out = StringIO()
    img = PILImage.new('RGBA', (width, height), color)
    img.save(out, format)
    return out.getvalue()
LARGE_IMAGE = makeImageData(3000, 3000)
SMALL_IMAGE = makeImageData(200, 200, format='JPEG')
WATERMARK_IMAGE = makeImageData(50, 50, format='GIF', color='red')


class SimpleWatermarkImageTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.WatermarkImage.image import WatermarkImage
        return WatermarkImage

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_conformance(self):
        from zope.interface.verify import verifyClass
        from Products.WatermarkImage.interfaces import IWatermarkImage
        verifyClass(IWatermarkImage, self._getTargetClass())

    def test_defaults(self):
        # Test default values for an empty instance
        wim = self._makeOne('wim', '', '')

        self.assertEquals(wim.getId(), 'wim')
        self.assertEquals(wim.title, '')
        self.assertEquals(wim.alt, '')
        self.assertEquals(wim.description, '')
        self.assertEquals(len(wim.data), 0)
        self.assertEquals(wim.watermark_id, 'watermark_image')
        self.assertEquals(wim.watermark_opacity, 1)
        self.assertEquals(wim.watermark_use, 'position')
        self.assertEquals(wim.watermark_position_x, 0)
        self.assertEquals(wim.watermark_position_y, 0)
        self.assertEquals(wim.content_type, 'text/x-unknown-content-type')
        self.assertEquals(wim.height, 0)
        self.assertEquals(wim.width, 0)
        self.assertEquals(wim.size, 0)
        self.assertEquals(wim.thumb_content_type, 'text/x-unknown-content-type')
        self.assertEquals(wim.thumb_height, 0)
        self.assertEquals(wim.thumb_width, 0)
        self.assertEquals(wim.thumb_size, 0)
        self.assertEquals(len(wim.thumb_data), 0)
        self.assertEquals( wim.original_content_type
                         , 'text/x-unknown-content-type'
                         )
        self.assertEquals(wim.original_size, 0)
        self.assertEquals(len(wim.original_data), 0)

    def test_manage_edit(self):
        wim = self._makeOne('wim', '', '')

        wim.manage_edit( 'test title'
                       , 'application/octet-stream'
                       , precondition='foo'
                       )

        self.assertEquals(wim.title, 'test title')
        self.assertEquals(wim.original_content_type, 'application/octet-stream')
        self.assertEquals(wim.precondition, 'foo')

    def test_manage_editProperties(self):
        def fake_form(*args, **kw):
            return None
        wim = self._makeOne('wim', '', '')
        wim.manage_propertiesForm = fake_form
        wrapped = makerequest(wim)

        request = wrapped.REQUEST
        # Fill in the form with default data
        for prop_id in wim.propertyIds():
            request[prop_id] = getattr(wim, prop_id)
        request['title'] = 'new title'
        request['description'] = 'some description'
        
        wim.manage_editProperties(request)

        self.assertEquals(wim.title, 'new title')
        self.assertEquals(wim.description, 'some description')


class EventWatermarkImageTests(unittest.TestCase):

    def setUp(self):
        import Products.Five
        import Products.WatermarkImage

        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.WatermarkImage)

    def _getTargetClass(self):
        from Products.WatermarkImage.image import WatermarkImage
        return WatermarkImage

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_update_data_small(self):
        wim = self._makeOne('wim', '', '')
        wim.watermark_id = 'watermark_file'
        wim.watermark_file = OFSImage('watermark_file', '', WATERMARK_IMAGE)
        wim.thumb_width = 100
        wim.thumb_height = 100

        wim.update_data(SMALL_IMAGE)

        self.assertEquals(str(wim.original_data), SMALL_IMAGE)
        self.assertEquals(wim.original_size, len(SMALL_IMAGE))
        self.failUnless(isinstance(wim.original_data, str))
        self.assertEquals(wim.original_content_type, 'image/jpeg')

        self.assertNotEquals(str(wim.data), SMALL_IMAGE)
        self.failUnless(str(wim.data))
        self.failUnless(isinstance(wim.data, str))
        self.failUnless(wim.size)
        self.assertEquals(wim.content_type, 'image/jpeg')

        self.assertNotEquals(str(wim.thumb_data), SMALL_IMAGE)
        self.failUnless(str(wim.thumb_data))
        self.failUnless(isinstance(wim.thumb_data, str))
        self.failUnless(wim.thumb_size)
        self.assertEquals(wim.thumb_content_type, 'image/jpeg')

    def test_update_data_large(self):
        wim = self._makeOne('wim', '', '')
        wim.watermark_id = 'watermark_file'
        wim.watermark_file = OFSImage('watermark_file', '', WATERMARK_IMAGE)
        wim.thumb_width = 100
        wim.thumb_height = 100

        wim.update_data(LARGE_IMAGE)

        self.assertEquals(str(wim.original_data), LARGE_IMAGE)
        self.assertEquals(wim.original_size, len(LARGE_IMAGE))
        self.failUnless(isinstance(wim.original_data, Pdata))
        self.assertEquals(wim.original_content_type, 'image/png')

        self.assertNotEquals(str(wim.data), LARGE_IMAGE)
        self.failUnless(str(wim.data))
        self.failUnless(isinstance(wim.data, Pdata))
        self.failUnless(wim.size)
        self.assertEquals(wim.content_type, 'image/png')

        self.assertNotEquals(str(wim.thumb_data), LARGE_IMAGE)
        self.failUnless(str(wim.thumb_data))
        self.failUnless(isinstance(wim.thumb_data, str))
        self.failUnless(wim.thumb_size)
        self.assertEquals(wim.thumb_content_type, 'image/jpeg')

    def test_tag_original(self):
        wim = self._makeOne('wim', '', '')
        wim.watermark_id = 'watermark_file'
        wim.watermark_file = OFSImage('watermark_file', '', WATERMARK_IMAGE)
        wim.thumb_width = 100
        wim.thumb_height = 100
        wim.update_data(SMALL_IMAGE)

        got = wim.tag_original()
        expected = '<img src="/original" alt="" title="" height="200" width="200" />'
        self.assertEquals(got, expected)

    def test_tag_thumbnail(self):
        wim = self._makeOne('wim', '', '')
        wim.watermark_id = 'watermark_file'
        wim.watermark_file = OFSImage('watermark_file', '', WATERMARK_IMAGE)
        wim.thumb_width = 100
        wim.thumb_height = 100
        wim.update_data(SMALL_IMAGE)

        got = wim.tag_thumbnail()
        expected = '<img src="/thumbnail.jpg" alt="" title="" height="100" width="100" />'
        self.assertEquals(got, expected)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SimpleWatermarkImageTests),
        unittest.makeSuite(EventWatermarkImageTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
