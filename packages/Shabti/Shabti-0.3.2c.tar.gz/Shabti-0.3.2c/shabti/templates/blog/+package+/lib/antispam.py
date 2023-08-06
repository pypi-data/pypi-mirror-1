from PIL import  ImageFont
from PIL.PngImagePlugin import  Image
from PIL import  ImageDraw
# This function is (c) Jesus Roncero Franco <jesus at roncero.org>.
# Modified to support old and new PIL versions by Steven Armstrong.
_xstep = 5 
_ystep = 5 
_imageSize = (61,21)
_bgColor = (255,255,255) # White
_gridInk = (200,200,200)
_fontInk = (130,130,130)
_fontSize = 14
_fontPath = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
def generateImage(number):
    try:
        # recent PIL version with support for truetype fonts
        font = ImageFont.truetype(_fontPath, _fontSize)
    except AttributeError:
        # old PIL version, fallback to pil fonts
        font = ImageFont()#.load(_fontPath)
        font._load_pilfont(_fontPath)

    img = Image.new("RGB", _imageSize, _bgColor)
    draw = ImageDraw.Draw(img)
    
    xsize, ysize = img.size

    # Do we want the grid start at 0,0 or want some offset?
    x, y = 0,0
    
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
        draw.text((10, 2), number, font=font, fill=_fontInk)
    except TypeError:
        draw.setink(_fontInk)
        draw.text((10, 2), number, font=font)

    return img


def writeImage(number):
    img = generateImage(number)
    import StringIO
    s=StringIO.StringIO()
    img.save(s,'PNG')
    return s.getvalue()
