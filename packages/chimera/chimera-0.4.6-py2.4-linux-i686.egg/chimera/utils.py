import PIL
from cStringIO import StringIO
import tempfile
import os


# dict tools
def invert(d):
    return dict((v,k) for k,v in d.iteritems())

def twoway(d, inplace=False):
    # when we know we have a dict with a stable one way mapping
    # we can update it so that it will translate keys both directions
    # this return a new dict unless inplace is True
    n = invert(d)
    if inplace:
        d.update(n)
        return d
    else:
        n.update(d)
        return n


JPEG_OPTIONS = {'quality'  : 100,
              'optimize' : 1
              }

FORMAT_DEFAULT_OPTIONS = {
    'png'  : {'optimize' : 1},
    'jpg' : JPEG_OPTIONS,
    'jpeg' : JPEG_OPTIONS,
    'gif' : {},
    }

## PIL Image manipulation
## lower level
def pngBufferToPIL(buffer):
    fp = StringIO(buffer)
    return PIL.Image.open(fp)

def normalizeImage(image):
    return image.convert('RGBA')


def save(image, filename, format=None):
    if not format:
        format = os.path.splitext(filename)[1]
        if format.startswith('.'):
            format = format[1:]

    image.save(filename, **FORMAT_DEFAULT_OPTIONS.get(format, {}))

def show(image, title):
    fd, fn = tempfile.mkstemp(".png", title)
    image.save(fn)
    os.system("gnome-open %s &> /dev/null &" % fn)
    return fn

def createImage(size):
    return PIL.Image.new('RGBA', size)

## Size manipulation
def parseSizeSpec(size):
    """Convert a size spec to a tuple of floating point ratio numbers
    used to calcuate a different size
    always returns (float, float) or raises ValueError

    >>> parseSizeSpec(2)
    (2.0, 2.0)
    >>> parseSizeSpec("50%")
    (0.5, 0.5)
    >>> parseSizeSpec(("50%", 0.5))
    (0.5, 0.5)
    >>> parseSizeSpec(("50%", "150%"))
    (0.5, 1.5)

    """
    try:
        if isinstance(size, float): return (f, f)
        if not isinstance(size, tuple) and not isinstance(size, list):
            size = [size, size]

        size = [size[0], size[1]]
        if isinstance(size[0], basestring):
            size[0] = percentToFloat(size[0])
        if isinstance(size[1], basestring):
            size[1] = percentToFloat(size[1])
        size = (float(size[0]), float(size[1]))
        return size
    except:
        pass

    raise ValueError("invalid size spec %r" % size)



def percentToFloat(string):
    if string.endswith("%"): string = string[:-1]
    return float(string)/100.0



