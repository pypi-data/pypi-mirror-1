#!/usr/bin/python
#
# Usage: ./example.py [word]
#
# Run this script to generate and display an image with any word of
# your choice.
#
# 2008 Fredrik Portstrom
#
# I, the copyright holder of this file, hereby release it into the
# public domain. This applies worldwide. In case this is not legally
# possible: I grant anyone the right to use this work for any
# purpose, without any conditions, unless such conditions are
# required by law.

try:
    import captchaimage
except ImportError:
    print "The captcha image module is not installed."
else:
    import random
    import Image
    import sys
    size_y = 32
    image_data = captchaimage.create_image(
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf" if len(sys.argv) < 3
        else sys.argv[2], 28, size_y,
        "EMACS" if len(sys.argv) < 2 else sys.argv[1])
    image = Image.fromstring(
        "L", (len(image_data) / size_y, size_y), image_data)
    image.show()
