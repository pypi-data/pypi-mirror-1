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
""" WatermarkImage browser tests module

$Id: test_image.py 1761 2009-05-08 16:36:58Z jens $
"""

from cStringIO import StringIO
import unittest

from OFS.Image import Image as OFSImage
from OFS.Image import Pdata
from Products.Five import zcml
from Testing.makerequest import makerequest

from Products.WatermarkImage.image import WatermarkImage
from Products.WatermarkImage.tests.test_image import LARGE_IMAGE
from Products.WatermarkImage.tests.test_image import SMALL_IMAGE
from Products.WatermarkImage.tests.test_image import WATERMARK_IMAGE


class WatermarkImageViewTestsBase(unittest.TestCase):

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def setUp(self):
        import Products.Five
        import Products.WatermarkImage

        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.WatermarkImage)

        wim = WatermarkImage('small', 'small title', '')
        wim.watermark_image = OFSImage('watermark_image', '', WATERMARK_IMAGE)
        wim.manage_upload(SMALL_IMAGE)
        self.image = wim

        self.output = StringIO()
        wrapped = makerequest(wim, stdout=self.output)
        self.request = wrapped.REQUEST
        self.response = self.request['RESPONSE']

        self.test_data, self.test_ct, self.test_size = self._getImageData()

    def test_precondition_failure(self):
        def fake_precondition():
            raise RuntimeError

        self.image.precondition = 'fake_cond'
        self.image.fake_cond = fake_precondition
        view = self._makeOne(self.image, self.request)

        self.assertRaises(RuntimeError, view.__call__)

    def test_rendering_small_image(self):
        view = self._makeOne(self.image, self.request)

        rendered = view()

        self.assertEquals(self.response.getStatus(), 200)
        self.assertEquals( self.response.getHeader('content-length')
                         , str(self.test_size)
                         )
        self.assertEquals( self.response.getHeader('content-type')
                         , self.test_ct
                         )
        self.assertEquals(self.response.getHeader('accept-ranges'), 'bytes')
        self.assertEquals(rendered, self.test_data)
        self.assertEquals(len(rendered), self.test_size)

    def test_rendering_large_mage(self):
        self.image.manage_upload(LARGE_IMAGE)
        self.test_data, self.test_ct, self.test_size = self._getImageData()
        view = self._makeOne(self.image, self.request)

        rendered = view()

        # If the image data is large enough output is not resturned directly
        # The output contains headers and body, divided by "\n\n"
        if len(rendered) == 0:
            raw_output = self.output.getvalue()
            header_body = raw_output.split('\r\n\r\n', 1)
            if len(header_body) == 1:
                 # Zope < 2.12 still uses \n\n to split header and body
                 header_body = raw_output.split('\n\n', 1)
            rendered = header_body[1]

        self.assertEquals(self.response.getStatus(), 200)
        self.assertEquals( self.response.getHeader('content-length')
                         , str(self.test_size)
                         )
        self.assertEquals( self.response.getHeader('content-type')
                         , self.test_ct
                         )
        self.assertEquals(self.response.getHeader('accept-ranges'), 'bytes')
        self.assertEquals(rendered, str(self.test_data))
        self.assertEquals(len(rendered), self.test_size)



class WatermarkImageThumbnailViewTests(WatermarkImageViewTestsBase):

    def _getTargetClass(self):
        from Products.WatermarkImage.browser.image import ThumbnailView
        return ThumbnailView

    def _getImageData(self):
        return ( self.image.thumb_data
               , self.image.thumb_content_type
               , self.image.thumb_size
               )


class WatermarkImageOriginalViewTests(WatermarkImageViewTestsBase):

    def _getTargetClass(self):
        from Products.WatermarkImage.browser.image import OriginalView
        return OriginalView

    def _getImageData(self):
        return ( self.image.original_data
               , self.image.original_content_type
               , self.image.original_size
               )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(WatermarkImageThumbnailViewTests),
        unittest.makeSuite(WatermarkImageOriginalViewTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
