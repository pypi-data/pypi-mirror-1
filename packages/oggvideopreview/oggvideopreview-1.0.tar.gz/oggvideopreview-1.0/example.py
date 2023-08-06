#!/usr/bin/python
#
# Usage: ./example.py path
#
# Run this script to display a video frame from an Ogg file.
#
# 2009 Fredrik Portstrom
#
# I, the copyright holder of this file, hereby release it into the
# public domain. This applies worldwide. In case this is not legally
# possible: I grant anyone the right to use this work for any
# purpose, without any conditions, unless such conditions are
# required by law.

try:
    import oggvideopreview
except ImportError:
    print "The oggvideopreview image module is not installed."
else:
    import Image
    import sys
    if len(sys.argv) < 2:
        print sys.argv[0] + ": missing file operand"
    else:
        size_x, size_y, aspect_numerator, aspect_denominator, image_data \
            = oggvideopreview.make_preview(sys.argv[1])
        image = Image.fromstring("RGB", (size_x, size_y), image_data)
        image.show()
