'''
This function is (c) Jesus Roncero Franco <jesus at roncero.org>.
Modified to support old and new PIL versions by Steven Armstrong.
Modified to add distortion effect by Florent AIDE
        <florent d-o-t aide a-t gmail.com>.
'''

import os
import random
import StringIO
from PIL import ImageFont
from PIL.PngImagePlugin import Image
from PIL import ImageDraw
from PIL import ImageOps

_xstep = 5 
_ystep = 5 
width = 90
height = 35
text_pos_x = 25 
text_pos_y = 11
_imageSize = (width, height)
_bgColor = (255,255,255) # White
_gridInk = (200,200,200)
_fontInk = (130,130,130)
_fontSize = 14
_fontPath = os.path.abspath(
        os.path.join('turboblog', 'data', 'freesans.ttf'))

distortion_max = 15
distortion_min = 8 

def generateImage(number):
    # corner co-ordinates, anticlockwise from top left
    x1 = width - width + random.randrange(distortion_min, distortion_max)
    y1 = height - height + random.randrange(distortion_min, distortion_max)
    x2 = width - width + random.randrange(distortion_min, distortion_max)
    y2 = height - random.randrange(distortion_min, distortion_max)
    x3 = width - random.randrange(distortion_min, distortion_max)
    y3 = height - random.randrange(distortion_min, distortion_max)
    x4 = width - random.randrange(distortion_min, distortion_max)
    y4 = height - height + random.randrange(distortion_min, distortion_max)
    corners = (x1, y1, x2, y2, x3, y3, x4, y4)

    try:
        # recent PIL version with support for truetype fonts
        font = ImageFont.truetype(_fontPath, _fontSize)
    except AttributeError:
        # old PIL version, fallback to pil fonts
        font = ImageFont()
        font._load_pilfont(_fontPath)

    img = Image.new("RGB", _imageSize, _bgColor)
    draw = ImageDraw.Draw(img)
    
    xsize, ysize = img.size

    # Do we want the grid start at 0,0 or want some offset?
    x, y = 0, 0
    
    while x <= xsize:
        try:
            # recent PIL version
            draw.line(((x, 0), (x, ysize)), fill=_gridInk)
        except TypeError:
            # old PIL version
            draw.setink(_gridInk)
            draw.line(((x, 0), (x, ysize)))
        x = x + _xstep 

    while y <= ysize:
        try:
            draw.line(((0, y), (xsize, y)), fill=_gridInk)
        except TypeError:
            draw.setink(_gridInk)
            draw.line(((0, y), (xsize, y)))
        y = y + _ystep 
    
    try:
        draw.text((text_pos_x, text_pos_y), number, font=font, fill=_fontInk)
    except TypeError:
        draw.setink(_fontInk)
        draw.text((text_pos_x, text_pos_y), number, font=font)

    return img.transform(img.size, Image.QUAD, corners,
            Image.BICUBIC)

def write_image(number):
    img = generateImage(number)
    s = StringIO.StringIO()
    img.save(s, 'PNG')
    return s.getvalue()

# vim: expandtab tabstop=4 shiftwidth=4:
