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
""" WatermarkImage browser views

$Id: image.py 1758 2009-05-07 18:43:37Z jens $
"""

from mimetools import choose_boundary

from DateTime.DateTime import DateTime
from Products.Five import BrowserView
from webdav.common import rfc1123_date
from ZPublisher import HTTPRangeSupport


class WatermarkImageViewBase(BrowserView):
    """ Base view class for Products.WatermarkImage instances

    Code adapted from OFS.Image.Image class, with one exception: 
    ZCacheable caching is not supported by this view class, since only
    the watermarked image is to be cached, and that image is handled
    by the code in OFS.Image only.
    """

    def __call__(self):
        """ Render the view
        """
        REQUEST = self.request
        RESPONSE = REQUEST['RESPONSE']

        # If-modified-since handling: If the instance has not been modified 
        # as a whole, then the thumbnail image is the same as well.
        if self.context._if_modified_since_request_handler(REQUEST, RESPONSE):
            return ''

        # Apply the same precondition handling as used for the whole instance
        precondition = self.context.precondition
        if precondition and getattr(self.context, str(precondition)):
            # Grab whatever precondition was defined and then
            # execute it.  The precondition will raise an exception
            # if something violates its terms.
            c=getattr(self.context, str(precondition))
            if hasattr(c,'isDocTemp') and c.isDocTemp:
                c(REQUEST['PARENTS'][1],REQUEST)
            else:
                c()

        if self._range_request_handler( self.file_content_type
                                      , self.file_size
                                      , self.file_data
                                      ):
            # we served a chunk of content in response to a range request.
            return ''

        RESPONSE.setHeader('Last-Modified', rfc1123_date(self.context._p_mtime))
        RESPONSE.setHeader('Content-Type', self.file_content_type)
        RESPONSE.setHeader('Content-Length', self.file_size)
        RESPONSE.setHeader('Accept-Ranges', 'bytes')

        data = self.file_data
        if isinstance(data, str):
            RESPONSE.setBase(None)
            return data

        while data is not None:
            RESPONSE.write(data.data)
            data = data.next

        return ''

    def _range_request_handler( self
                              , file_content_type
                              , file_size
                              , file_data
                              ):
        REQUEST = self.request
        RESPONSE = REQUEST['RESPONSE']
        # HTTP Range header handling: return True if we've served a range
        # chunk out of our data.
        range = REQUEST.get_header('Range', None)
        request_range = REQUEST.get_header('Request-Range', None)
        if request_range is not None:
            # Netscape 2 through 4 and MSIE 3 implement a draft version
            # Later on, we need to serve a different mime-type as well.
            range = request_range
        if_range = REQUEST.get_header('If-Range', None)
        if range is not None:
            ranges = HTTPRangeSupport.parseRange(range)

            if if_range is not None:
                # Only send ranges if the data isn't modified, otherwise send
                # the whole object. Support both ETags and Last-Modified dates!
                if len(if_range) > 1 and if_range[:2] == 'ts':
                    # ETag:
                    if if_range != self.context.http__etag():
                        # Modified, so send a normal response. We delete
                        # the ranges, which causes us to skip to the 200
                        # response.
                        ranges = None
                else:
                    # Date
                    date = if_range.split( ';')[0]
                    try: mod_since=long(DateTime(date).timeTime())
                    except: mod_since=None
                    if mod_since is not None:
                        if self.context._p_mtime:
                            last_mod = long(self.context._p_mtime)
                        else:
                            last_mod = long(0)
                        if last_mod > mod_since:
                            # Modified, so send a normal response. We delete
                            # the ranges, which causes us to skip to the 200
                            # response.
                            ranges = None

            if ranges:
                # Search for satisfiable ranges.
                satisfiable = 0
                for start, end in ranges:
                    if start < file_size:
                        satisfiable = 1
                        break

                if not satisfiable:
                    RESPONSE.setHeader('Content-Range',
                        'bytes */%d' % file_size)
                    RESPONSE.setHeader('Accept-Ranges', 'bytes')
                    RESPONSE.setHeader('Last-Modified',
                        rfc1123_date(self.context._p_mtime))
                    RESPONSE.setHeader('Content-Type', file_content_type)
                    RESPONSE.setHeader('Content-Length', file_size)
                    RESPONSE.setStatus(416)
                    return True

                ranges = HTTPRangeSupport.expandRanges(ranges, file_size)

                if len(ranges) == 1:
                    # Easy case, set extra header and return partial set.
                    start, end = ranges[0]
                    size = end - start

                    RESPONSE.setHeader('Last-Modified',
                        rfc1123_date(self.context._p_mtime))
                    RESPONSE.setHeader('Content-Type', file_content_type)
                    RESPONSE.setHeader('Content-Length', size)
                    RESPONSE.setHeader('Accept-Ranges', 'bytes')
                    RESPONSE.setHeader('Content-Range',
                        'bytes %d-%d/%d' % (start, end - 1, file_size))
                    RESPONSE.setStatus(206) # Partial content

                    data = file_data
                    if isinstance(data, str):
                        RESPONSE.write(data[start:end])
                        return True

                    # Linked Pdata objects. Urgh.
                    pos = 0
                    while data is not None:
                        l = len(data.data)
                        pos = pos + l
                        if pos > start:
                            # We are within the range
                            lstart = l - (pos - start)

                            if lstart < 0: lstart = 0

                            # find the endpoint
                            if end <= pos:
                                lend = l - (pos - end)

                                # Send and end transmission
                                RESPONSE.write(data[lstart:lend])
                                break

                            # Not yet at the end, transmit what we have.
                            RESPONSE.write(data[lstart:])

                        data = data.next

                    return True

                else:
                    boundary = choose_boundary()

                    # Calculate the content length
                    size = (8 + len(boundary) + # End marker length
                        len(ranges) * (         # Constant lenght per set
                            49 + len(boundary) + len(file_content_type) +
                            len('%d' % file_size)))
                    for start, end in ranges:
                        # Variable length per set
                        size = (size + len('%d%d' % (start, end - 1)) +
                            end - start)


                    # Some clients implement an earlier draft of the spec, they
                    # will only accept x-byteranges.
                    draftprefix = (request_range is not None) and 'x-' or ''

                    RESPONSE.setHeader('Content-Length', size)
                    RESPONSE.setHeader('Accept-Ranges', 'bytes')
                    RESPONSE.setHeader('Last-Modified',
                        rfc1123_date(self.context._p_mtime))
                    RESPONSE.setHeader('Content-Type',
                        'multipart/%sbyteranges; boundary=%s' % (
                            draftprefix, boundary))
                    RESPONSE.setStatus(206) # Partial content

                    data = file_data
                    # The Pdata map allows us to jump into the Pdata chain
                    # arbitrarily during out-of-order range searching.
                    pdata_map = {}
                    pdata_map[0] = data

                    for start, end in ranges:
                        RESPONSE.write('\r\n--%s\r\n' % boundary)
                        RESPONSE.write('Content-Type: %s\r\n' %
                            file_content_type)
                        RESPONSE.write(
                            'Content-Range: bytes %d-%d/%d\r\n\r\n' % (
                                start, end - 1, file_size))

                        if isinstance(data, str):
                            RESPONSE.write(data[start:end])

                        else:
                            # Yippee. Linked Pdata objects. The following
                            # calculations allow us to fast-forward through the
                            # Pdata chain without a lot of dereferencing if we
                            # did the work already.
                            first_size = len(pdata_map[0].data)
                            if start < first_size:
                                closest_pos = 0
                            else:
                                closest_pos = (
                                    ((start - first_size) >> 16 << 16) +
                                    first_size)
                            pos = min(closest_pos, max(pdata_map.keys()))
                            data = pdata_map[pos]

                            while data is not None:
                                l = len(data.data)
                                pos = pos + l
                                if pos > start:
                                    # We are within the range
                                    lstart = l - (pos - start)

                                    if lstart < 0: lstart = 0

                                    # find the endpoint
                                    if end <= pos:
                                        lend = l - (pos - end)

                                        # Send and loop to next range
                                        RESPONSE.write(data[lstart:lend])
                                        break

                                    # Not yet at the end, transmit what we have.
                                    RESPONSE.write(data[lstart:])

                                data = data.next
                                # Store a reference to a Pdata chain link so we
                                # don't have to deref during this request again.
                                pdata_map[pos] = data

                    # Do not keep the link references around.
                    del pdata_map

                    RESPONSE.write('\r\n--%s--\r\n' % boundary)
                    return True


class ThumbnailView(WatermarkImageViewBase):
    """ Thumbnail view for Products.WatermarkImage instances
    """

    def __init__(self, context, request):
        super(ThumbnailView, self).__init__(context, request)
        self.file_content_type = self.context.thumb_content_type
        self.file_size = self.context.thumb_size
        self.file_data = self.context.thumb_data
    

class OriginalView(WatermarkImageViewBase):
    """ Originals view for Products.WatermarkImage instances
    """

    def __init__(self, context, request):
        super(OriginalView, self).__init__(context, request)
        self.file_content_type = self.context.original_content_type
        self.file_size = self.context.original_size
        self.file_data = self.context.original_data

