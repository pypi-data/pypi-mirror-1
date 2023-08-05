# -*- coding: utf-8 -*-
"""
    pocoo.utils.captcha
    ~~~~~~~~~~~~~~~~~~~

    Create Captcha images.

    Typical usage::

        >>> from pocoo.utils.captcha import Captcha
        >>> c = Captcha()
        >>> c
        <Captcha 'FGVZBS'>
        >>> c.code
        'FGVZBS'
        >>> fp = file('output.png', 'w')
        >>> fp.write(c.generate_image())
        >>> fp.close()
        >>> c == 'FGVZBS'
        True

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import pocoo
import os
import random
from PIL import Image, ImageFont, ImageDraw
from cStringIO import StringIO

# Aliases for a more pythonic usage ;-)
Image = Image.new
Canvas = ImageDraw.Draw
Font = ImageFont.truetype


CAPTCHA_CHARS = 'ABCDEFGHIKLMNPQRSTVWXYZ123456789'


def gen_captcha_key(length=6):
    """
    Generate a captcha key of ``length`` characters.
    """
    result = []
    for _ in xrange(length):
        result.append(random.choice(CAPTCHA_CHARS))
    return ''.join(result)


class Captcha(object):
    """
    Represents a captcha image.
    """

    def __init__(self, chars=6, code=None):
        if code is None:
            code = gen_captcha_key(chars)
        self.code = code

    def __eq__(self, other):
        if isinstance(other, Captcha):
            return self.code == other.code
        if isinstance(other, basestring):
            return self.code == other
        raise TypeError, 'Can\'t compare Captcha to %r' % other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.code)

    def __str__(self):
        return self.code

    def generate_image(self, width=200, height=70, font_size=50,
                       vlines=6, hlines=10, drawpoints=True, pointdeep=10,
                       bgcolor='#eeeeee', linecolor='#bbbbbb',
                       colors=('#222222', '#444444', '#666666', '#888888'),
                       pointcolor='#ffffff'):
        """
        Create a PNG version of the code image.

        Arguments:

        width
          width in pixel (default: 200)

        height
          height in pixel (default: 70)

        font_size
          font size in pixel (default: 50)

        vlines
          lines crossing the image vertically (default: 6)

        hlines
          lines crossing the image horizontally (default: 10)

        drawpoints
          should the background of the image be dotted? (default: True)

        pointdeep
          number defining amount of dots. (1 - many / 20 - few)
          if you define a number higher than 20 it's the same is setting
          drawpoints to False. (default: 10)

        bgcolor
          hex value of the background color (default: #eeeeee)

        linecolor
          hex value of the line color (default: #bbbbbb)

        colors
          list of colors used for the characters

        pointcolor
          color of the background dots if enabled (default: #ffffff)
        """
        font_path = os.path.dirname(pocoo.__file__) + '/res/captcha.ttf'

        img = Image('RGB', (width, height), bgcolor)
        c = Canvas(img)
        f = Font(font_path, font_size)
        max_len = len(self.code)

        # draw background points
        if drawpoints and pointdeep <= 20:
            limes = 20 - pointdeep
            for x in xrange(width):
                for y in xrange(height):
                    if random.randrange(0, 20) > limes:
                        c.point((x, y), fill=pointcolor)

        # draw letters
        for pos, char in enumerate(self.code):
            color = random.choice(colors)
            point = (int(width / max_len) * pos + 8,
                     random.randrange(-2, height - font_size - 4))
            c.text(point, char, fill=color, font=f)

        # draw lines
        for _ in xrange(vlines):
            c.line([(0, random.randrange(0, height + 1)),
                    (width, random.randrange(0, height + 1))],
                   fill=linecolor)
        for _ in xrange(hlines):
            c.line([(random.randrange(0, width + 1), 0),
                    (random.randrange(0, width + 1), height)],
                   fill=linecolor)

        out = StringIO()
        img.save(out, 'PNG')

        return out.getvalue()
