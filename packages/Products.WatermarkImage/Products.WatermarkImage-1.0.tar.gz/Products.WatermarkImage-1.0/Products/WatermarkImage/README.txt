=========================
 Products.WatermarkImage
=========================

.. contents::

This package provides a Zope 2 Image content type with thumbnail and 
watermarking support. It aims to be fully API-compatible with the 
standard Zope Image type.

Data storage
------------
WatermarkImage instances take the original image data, store it on 
the instance, and generate a watermarked image as well as a thumbnail, 
which are stored on the instance as well. The watermarked image is 
stored as the main image, so all normal image access will return 
the watermarked image. The thumbnail is a scaled-down copy of the 
watermarked image.

Thumbnail support
-----------------
Whenever a WatermarkImage is created or updated, a thumbnail is 
generated as well. Thumbnail data can be viewed using the ZMI 
(Zope Management Interface) on the `Thumbnail` tab. Its data 
can be accessed by adding `/thumbnail.jpg` to the WatermarkImage 
URL. A new method `tag_thumbnail` can be used to generate a HTML
`img` tag for the thumbnail image, its arguments are the same as 
the standard Zope Image's `tag` method.

The following WatermarkImage properties affect thumbnail 
generation:

- Maximum thumbnail height (pixels): The maximum height for the
  generated thumbnail. Thumbnails retain the original image's 
  height/width ratio, so the actual thumbnail height may be less
  than the maximum height specified here.

- Maximum thumbnail width (pixels): The maximum width for the
  generated thumbnail. Thumbnails retain the original image's 
  height/width ratio, so the actual thumbnail width may be less
  than the maximum width specified here.

If you change any of these properties through the ZMI `Properties` 
tab, the thumbnail will be regenerated automatically to reflect 
the new values.

Watermarking support
--------------------
If the user specifies that a watermarked image should be created, 
any image upload to the WatermarkImage instance as well as 
property updates on the ZMI `Properties` tab will generate a 
watermarked copy of the original image. The original image data 
can be viewed using the ZMI  on the `Edit Original` tab. Its data 
can be accessed by adding `/original` to the WatermarkImage 
URL. A new method `tag_original` can be used to generate a HTML
`img` tag for the original image, its arguments are the same as 
the OFS.Image's `tag` method.

Access to the original image is protected by a new Zope Permission 
named `WatermarkImage: View original`. This permission is only 
granted to the Zope `Manager` role by default. You can use the 
ZMI `Security` tab to change this default setting.

The following WatermarkImage properties affect the watermarking 
support:

- Watermark ID: The Zope Id of a standard Zope Image instance 
  containing the actual watermark to be placed onto the image.

- Watermark opacity: The opacity value determines how opaque the 
  watermark will appear on the watermarked image. Its value must 
  be betwen 0 and 1. Opacity 0 will create a transparent watermark, 
  while opacity 1 will apply the watermark image without any 
  transparency manipulation.

- Watermark use: Select whether to create no watermark at all 
  (`none`), position a single watermark in a specific place on 
  the image (`position`), tile as many copies of the watermark 
  image onto the image as possible (`tile`), or place a single 
  watermark onto the image, scaled to the original image size 
  (`scale`).

- Watermark position on X-axis: Only applicable if `position` has 
  been selected under `Watermark use`. The watermark's top left 
  corner will be placed further to the right by the number of 
  pixels set here. If you specify a negative value, placement will 
  be determined by subtracting the provided value from the original 
  image's width in order to allow right-aligned positioning.

- Watermark position on Y-axis: Only applicable if `position` has 
  been selected under `Watermark use`. The watermark's top left 
  corner will be placed lower by the number of pixels set here. If 
  you specify a negative value, placement will be determined by 
  subtracting the provided value from the original image's height 
  in order to allow bottom-aligned positioning.

If you change any of these properties through the ZMI `properties` 
tab, the watermarked image and the thumbnail will be regenerated 
automatically to reflect the new values.


Changing configuration defaults
-------------------------------
A user can configure several settings on a per-instance basis 
which influence thumbnail and watermarked image generation. 
However, doing so for every WatermarkImage instance is tedious.
Instead, a set of configuration defaults can be defined in your 
Zope instance's `zope.conf` configuration file. Simply add a stanza 
named `product-config watermarkimage` and define new defaults::

<product-config watermarkimage>
  watermark_use position
  watermark_position_x 100
  watermark_position_y -100
  thumbmail_max_height 100
  thumbnail_max_width 100
</product-config>

The following keys and their corresponding setting on the ZMI 
`Properties` tab are recognized:

- watermark_use: corresponds to `Watermark use`

- watermark_position_x: corresponds to `Watermark position on X axis`

- watermark_position_y: corresponds to `Watermark position on Y axis`

- watermark_opacity: corresponds to `Watermark opacity`

- watermark_id: corresponds to `Watermark ID`

- thumbnail_max_height: corresponds to `Maximum thumbnail height (pixels)`

- thumbnail_max_width: corresponds to `Maximum thumbnail width (pixels)`

Please note: When you set a default in `zope.conf`, it will be applied 
to the WatermarkImage instance at creation time. Subsequent changes in 
the `zope.conf` default values will not influence existing instances.


Bug tracker
===========
If you have suggestions, bug reports or requests please use the issue
tracker at http://www.dataflake.org/tracker/

SVN version
===========
You can retrieve the latest code from Subversion using setuptools or
zc.buildout via this URL:

http://svn.dataflake.org/svn/Products.WatermarkImage/trunk#egg=Products.WatermarkImage


