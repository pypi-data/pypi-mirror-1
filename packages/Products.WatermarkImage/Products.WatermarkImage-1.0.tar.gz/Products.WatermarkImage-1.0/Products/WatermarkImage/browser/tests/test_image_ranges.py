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
""" WatermarkImage browser range request tests module

$Id: test_image_ranges.py 1763 2009-05-08 16:46:03Z jens $
"""

from cStringIO import StringIO
from mimetools import Message
from multifile import MultiFile
import re
import unittest
from webdav.common import rfc1123_date

from DateTime.DateTime import DateTime
from OFS.Image import Image as OFSImage
from Products.Five import zcml
from Testing import ZopeTestCase
from Testing.makerequest import makerequest
import transaction
from zExceptions import BadRequest

from Products.WatermarkImage.image import WatermarkImage
from Products.WatermarkImage.tests.test_image import LARGE_IMAGE
from Products.WatermarkImage.tests.test_image import SMALL_IMAGE
from Products.WatermarkImage.tests.test_image import WATERMARK_IMAGE

class WatermarkImageViewTestsBase(unittest.TestCase):

    def setUp(self):
        import Products.Five
        import Products.WatermarkImage

        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.WatermarkImage)

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _prepareRangeTest(self, range, if_range=None, draft=False):
        view = self._makeOne(self.image, self.request)
        if if_range is not None:
            self.request.environ['HTTP_IF_RANGE'] = if_range
        if draft:
            self.request.environ['HTTP_REQUEST_RANGE'] = range
        else:
            self.request.environ['HTTP_RANGE'] = range
        rendered = view()
        self.body = self.output.getvalue()
        if self.body.find('\n\n') != -1:
            self.body = self.body.split('\n\n', 1)[1]
        elif self.body.find('\r\n\r\n') != -1:
            self.body = self.body.split('\r\n\r\n', 1)[1]

    def _expectFailure(self, range):
        """ Helper to execute a range test based on a given range spec
        """
        self._prepareRangeTest(range)
        self.assertEquals(self.response.getStatus(), 416)
        self.assertEquals( self.response.getHeader('content-range')
                         , 'bytes */%d' % len(self.test_data)
                         )

    def _expectSuccess(self, range, if_range=None):
        """ Helper to execute a range test based on a given range spec
        """
        self._prepareRangeTest(range, if_range=if_range)
        self.assertEquals(self.response.getStatus(), 200)

    def _expectSingleRange(self, range, start, end, if_range=None):
        self._prepareRangeTest(range, if_range=if_range)
        self.assertEquals(self.response.getStatus(), 206)
        expected_range_hdr = 'bytes %d-%d/%d' % ( start
                                                , end-1
                                                , len(self.test_data)
                                                )
        self.assertEquals( self.response.getHeader('content-range')
                         , expected_range_hdr
                         )
        self.assertEquals( self.response.getHeader('content-length')
                         , str(len(self.body))
                         )
        self.assertEquals(self.test_data[start:end], self.body)

    def _expectMultipleRanges(self, range, sets, draft=False):
        rangeParse = re.compile('bytes\s*(\d+)-(\d+)/(\d+)')
        self._prepareRangeTest(range, draft=draft)
        self.assertEquals(self.response.getStatus(), 206)
        self.failIf(self.response.getHeader('content-range'))
        
        ct = self.response.getHeader('content-type').split(';')[0]
        draftprefix = draft and 'x-' or ''
        self.assertEquals(ct, 'multipart/%sbyteranges' % draftprefix)

        c_length = self.response.getHeader('content-length')
        if c_length:
            self.assertEquals(c_length, str(len(self.body)))

        # Decode the multipart message
        ct = self.response.getHeader('content-type')
        bodyfile = StringIO('Content-Type: %s\n\n%s' % (ct, self.body))
        bodymessage = Message(bodyfile)
        partfiles = MultiFile(bodyfile)
        partfiles.push(bodymessage.getparam('boundary'))

        partmessages = []
        while partfiles.next():
            partmessages.append(Message(StringIO(partfiles.read())))

        # Check the different parts
        returned_ranges = []
        for part in partmessages:
            range = part['content-range']
            start, end, size = rangeParse.search(range).groups()
            start, end, size = int(start), int(end), int(size)
            end = end + 1

            self.assertEquals(size, len(self.test_data))

            part.rewindbody()
            body = part.fp.read()
            # Bug in MultiFile; the CRLF that is part of the boundary
            # is returned as part of the body.
            if body[-2:] == '\r\n':
                body = body[:-2]

            self.assertEquals(len(body), end-start)
            self.assertEquals(body, self.test_data[start:end])

            returned_ranges.append((start, end))

        # Compare the ranges used with the expected range sets.
        self.assertEquals(returned_ranges, sets)




class WatermarkImageViewNoDBTestsBase(WatermarkImageViewTestsBase):

    def setUp(self):
        super(WatermarkImageViewNoDBTestsBase, self).setUp()

        wim = WatermarkImage('small', 'small title', '')
        wim.watermark_image = OFSImage('watermark_image', '', WATERMARK_IMAGE)
        wim.manage_upload(SMALL_IMAGE)
        self.image = wim

        self.output = StringIO()
        wrapped = makerequest(wim, stdout=self.output)
        self.request = wrapped.REQUEST
        self.response = self.request['RESPONSE']
        self.test_data = self._getTestData()

    def test_range_negative_zero(self):
        self._expectFailure('bytes=-0')

    def test_range_start_beyond_length(self):
        self._expectFailure('bytes=999999-')

    def test_range_multiple_unsatisfiable(self):
        self._expectFailure('bytes=999999-1000000,1000001-,-0')

    def test_range_garbage(self):
        # Garbage headers are silently ignored
        self._expectSuccess('kjhdkjhd = ew;jkj h eewh ew')

    def test_range_illegal_spec(self):
        # Garbage headers are silently ignored
        self._expectSuccess('notbytes=0-1000')

    def test_range_simple(self):
        self._expectSingleRange('bytes=3-7', 3, 8)

    def test_range_openended(self):
        self._expectSingleRange('bytes=3-', 3, len(self.test_data))

    def test_range_suffix(self):
        data_length = len(self.test_data)
        self._expectSingleRange('bytes=-3', data_length-3, data_length)

    def test_range_combine_single_and_invalid(self):
        # A satisfiable and an unsatisfiable range
        self._expectSingleRange('bytes=-0,3-23', 3, 24)

    def test_range_end_overflow(self):
        # A range that starts within the file, but ends beyond the file lenth
        data_length = len(self.test_data)
        start, end = data_length-10, data_length+10
        self._expectSingleRange('bytes=%d-%d' % (start, end), start, data_length)

    def test_range_bigfile_end_overflow(self):
        self.image.manage_upload(LARGE_IMAGE)
        self.test_data = self._getTestData()
        data_length = len(self.test_data)
        start, end = data_length-100, data_length+100
        self._expectSingleRange('bytes=%d-%d' % (start, end), start, data_length)

    def test_ranges_multiple(self):
        self._expectMultipleRanges( 'bytes=3-7,10-15'
                                  , [(3, 8), (10, 16)]
                                  )

    def test_ranges_multiple_reverse(self):
        self._expectMultipleRanges( 'bytes=21-25,10-20'
                                  , [(21, 26), (10, 21)]
                                  )

    def test_ranges_multiple_draft(self):
        self._expectMultipleRanges( 'bytes=3-7,10-15'
                                  , [(3, 8), (10, 16)]
                                  , draft=True
                                  )

    def test_ranges_multiple_bigfile(self):
        self.image.manage_upload(LARGE_IMAGE)
        self.test_data = self._getTestData()
        data_length = len(self.test_data)
        self._expectMultipleRanges( 'bytes=3-700,10-15,-10000'
                                  , [ (3, 701)
                                    , (10, 16)
                                    , (data_length-10000, data_length)
                                    ]
                                  )

    def test_ranges_multiple_bigfile_outoforder(self):
        self.image.manage_upload(LARGE_IMAGE)
        self.test_data = self._getTestData()
        data_length = len(self.test_data)
        self._expectMultipleRanges( 'bytes=10-15,-10000,70000-80000'
                                  , [ (10, 16)
                                    , (data_length-10000, data_length)
                                    , (70000, 80001)
                                    ]
                                  )

    def test_ranges_multiple_bigfile_overflow(self):
        self.image.manage_upload(LARGE_IMAGE)
        self.test_data = self._getTestData()
        data_length = len(self.test_data)
        start, end = data_length-100, data_length+100
        self._expectMultipleRanges( 'bytes=3-700,%d-%d' % (start, end)
                                  , [(3, 701), (start, data_length)]
                                  )


class WatermarkImageViewDBTestsBase(WatermarkImageViewTestsBase):

    def setUp(self):
        super(WatermarkImageViewDBTestsBase, self).setUp()

        try:
            self.app = ZopeTestCase.app()
        except BadRequest:
            self.app = ZopeTestCase.app()

        wim = WatermarkImage('small', 'small title', '')
        wim.watermark_image = OFSImage('watermark_image', '', WATERMARK_IMAGE)
        wim.manage_upload(SMALL_IMAGE)
        self.app.image = self.image = wim
        transaction.commit()

        self.output = StringIO()
        wrapped = makerequest(wim, stdout=self.output)
        self.request = wrapped.REQUEST
        self.response = self.request['RESPONSE']
        self.test_data = self._getTestData()

    def tearDown(self):
        self.app._delObject('image')
        transaction.commit()
        ZopeTestCase.close(self.app)

    def test_ranges_illegal_if_range(self):
        # We assume that an illegal if-range is to be ignored, just like an
        # illegal if-modified since.
        self._expectSingleRange('bytes=10-25', 10, 26, if_range='garbage')

    def test_ranges_if_range_same(self):
        if_range = rfc1123_date(self.image._p_mtime)
        self._expectSingleRange('bytes=10-25', 10, 26, if_range=if_range)

    def test_ranges_if_range_before(self):
        if_range = rfc1123_date(self.image._p_mtime - 100)
        self._expectSuccess('bytes=21-25,10-20', if_range=if_range)

    def test_ranges_if_range_after(self):
        if_range = rfc1123_date(self.image._p_mtime + 100)
        self._expectSingleRange('bytes=10-25', 10, 26, if_range=if_range)

    def test_ranges_if_range_same_etag(self):
        if_range = self.image.http__etag()
        self._expectSingleRange('bytes=10-25', 10, 26, if_range=if_range)

    def test_ranges_if_range_different_etag(self):
        if_range = self.image.http__etag() + 'bar'
        self._expectSuccess('bytes=10-25', if_range=if_range)


class WatermarkImageThumbnailViewNoDBTests(WatermarkImageViewNoDBTestsBase):

    def _getTargetClass(self):
        from Products.WatermarkImage.browser.image import ThumbnailView
        return ThumbnailView

    def _getTestData(self):
        return self.image.thumb_data

    def test_ranges_multiple_bigfile(self):
        pass # Makes no sense here

    def test_ranges_multiple_bigfile_outoforder(self):
        pass # Makes no sense here


class WatermarkImageOriginalViewNoDBTests(WatermarkImageViewNoDBTestsBase):

    def _getTargetClass(self):
        from Products.WatermarkImage.browser.image import OriginalView
        return OriginalView

    def _getTestData(self):
        return self.image.original_data


class WatermarkImageThumbnailViewDBTests(WatermarkImageViewDBTestsBase):

    def _getTargetClass(self):
        from Products.WatermarkImage.browser.image import ThumbnailView
        return ThumbnailView

    def _getTestData(self):
        return self.image.thumb_data


class WatermarkImageOriginalViewDBTests(WatermarkImageViewDBTestsBase):

    def _getTargetClass(self):
        from Products.WatermarkImage.browser.image import OriginalView
        return OriginalView

    def _getTestData(self):
        return self.image.original_data


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(WatermarkImageThumbnailViewNoDBTests),
        unittest.makeSuite(WatermarkImageOriginalViewNoDBTests),
        unittest.makeSuite(WatermarkImageThumbnailViewDBTests),
        unittest.makeSuite(WatermarkImageOriginalViewDBTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

