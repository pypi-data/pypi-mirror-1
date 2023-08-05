"""
chimera
~~~~~~~~~~~~~~~~~~~~
Simple Image Generation

Chimera is a higher level graphics abstraction than is commonly
available for Python. Taking advantage of the power of the Pango
library (http://www.pango.org/) we are able to render beautiful
subpixel rendered, anti-aliased text in the fonts of your choice.

Chimera doesn't expose all the funtionality of its underlying
systems. In particular its not about drawing, pixel manipulation or
other low level operations on a surface. Chimera attempts to deal with
handling all its operations in a uniform, simple way so that you can
focus on the output you want to generate, now how to generate it.

"""

__author__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright ObjectRealms, LLC. 2005'
__license__  = 'The GNU Public License V2+'

import pangocairo
import fontconfig
import chimera_svg
import colors, utils
import PIL.Image
from cStringIO import StringIO
import math



class Image(object):
    def __init__(self, *args):
        self.image = None
        if args: self._parse(*args)

    def _parse(self, *args):
        """Be flexible in what you accept...
        Chimera can be initialized with
              (width:int, height:int)
              filelike with image data
              string of filename to load
        """
        w, h = 0,0
        if len(args) == 2:
            w, h = args
            args = ((w, h), )

        if len(args) == 1:
            arg = args[0]
            # either (w,h) tuple or
            # string to filename
            # or filelike with image data
            if isinstance(arg, tuple):
                w, h = arg
                if not isinstance(w, int) or not isinstance(h, int):
                    raise ValueError("must pass w,h as ints")
                self.image = pangocairo.ImageSurface("argb", w, h)
            elif isinstance(arg, pangocairo.ImageSurface):
                self.image = arg
            elif hasattr(arg, 'read'):
                # PIL handles more formats than just PNG
                # but we already have an explicit SVG loaded
                # I will pass on doing conversion of file objects
                # for now
                self.image = pangocairo.ImageSurface(arg)
            elif isinstance(arg, basestring):
                if not arg.lower().endswith(".png"):
                    # use PIL to load the image and convert it to a
                    # PNG filelike
                    pimg = PIL.Image.open(arg)
                    pimg.convert('RGBA')
                    # Buffer the image in memory to create a PNG
                    # filelike
                    output = StringIO()
                    pimg.save(output, 'png')
                    output.seek(0)
                    self.image = pangocairo.ImageSurface(output)
                else:
                    # directly load PNGs
                    self.image = pangocairo.ImageSurface(arg)
        if not self.image:
            raise ValueError("cannot create unspecified image")


    def getSize(self): return self.image.size
    def getWidth(self): return self.image.width
    def getHeight(self): return self.image.height

    size = property(getSize)
    width = property(getWidth)
    height = property(getHeight)

    def get_format(self):
        # later this will support other surfaces, pdf, svg, ps
        return "png"
    format = property(get_format)

    def Image(self):
        """return a clone of the image. The clone will have no canvas
        associated with it
        """
        size = self.image.size
        return Image(self.image.create_similar("color_alpha", *size ))

    def Layout(self):
        return self.Context().Layout()

    def Context(self):
        """Create and return a new Cairo canvas for this image
        """
        c = pangocairo.CairoContext(self.image)
        # return a context mapped to the projected size of the image,
        # not 1.0 space
        #c.scale(1.0/self.width, 1.0/self.height)
        return c
    
    # method alias
    Canvas = Context


    def save(self, filename=None):
        """save png to filename if one is passed in. otherwise return
        a filelike object with the object in memory
        """
        if isinstance(filename, basestring):
            if not filename.lower().endswith('.png'):
                # load a PNG buffer into PIL
                img = PIL.Image.open(self.image.asPngBuffer())
                utils.save(img, filename)
            else:
                self.image.writePng(filename)
        else:
            return self.image.asFile()

    def show(self): self.image.show()

    def composite(self, other, offset=(0,0), mode="over", alpha=1.0, canvas=None):
        """compose two images, this is a convenience method, canvas
        also exposes this. In this case a new default canvas is
        created.
        """
        if canvas is None:
            canvas = self.Context()

        canvas.save()
        canvas.translate(offset[0], offset[1])
        canvas.operator = mode
        canvas.paint(other, alpha=alpha)
        canvas.restore()
        
    blit = composite
    blend = composite
        

    def clone(self):
        img = self.image.clone()
        return Image(img)

    def similar(self):
        img = self.image.create_similar()
        return Image(img)


    def asPngFile(self): return self.image.asFile()

    def __str__(self): return self.image.asPngBuffer()

    def resizeTo(self, width=None, height=None, retainAspect=True):
        """Resize to a given size. Omitting either height or width
        will cause it to be sized along with the other dimension to
        keep the aspect ration. If retainAspect is set to False
        the size is left alone
        """
        if width and not height and isinstance(width, tuple):
            width, height =  width

        # If both are passed in then we know the size
        if width and height: retainAspect = False

        if width and retainAspect:
            ratio = float(width)/float(self.size[0])
            height = round(ratio * self.size[1])
        elif height and retainAspect:
            ratio = float(height)/float(self.size[1])
            width = round(ratio * self.size[0])

        if not width: width = self.size[0]
        if not height: height = self.size[1]

        im = pangocairo.ImageSurface("argb", width, height)
        canvas = pangocairo.CairoContext(im)
        w, h = self.size
        c = im.Context()
        spec = width/float(w), height/float(h)
        c.scale(*spec)
        c.paint(self.image)
        self.image = im

    def scale(self, size):
        """Scale an image to a new size. In specifying the size you
        have a number of options. see utils.parseSizeSpec for details.

        This throws out any settings currently on the image
        """
        spec = utils.parseSizeSpec(size)
        new_size = (int(self.size[0] * spec[0]),
                    int(self.size[1] * spec[1]))
        im = self.image.create_similar("color_alpha", *new_size)
        c = im.Context()
        c.scale(*spec)
        c.paint(self.image)
        self.image = im

    def rotate(self, angle=0.0):
        """Counter clockwise rotation of the image"""
        # XXX: this is currently broken 
        matrix = pangocairo.CairoMatrix()
        matrix.rotateDegrees(angle)
        w = self.image.width
        h = self.image.height
        # we are doing a clockwise rotation
        # so we can map the image corners using the
        # matrix
        nw, dy = matrix.transform_point(w, h)
        dx, nh = matrix.transform_point(w, 0)
        niw = abs(int(nw))
        nih = abs(int(nh))
        im = self.image.create_similar("color_alpha", niw, nih)
        c = im.Context()
        M = pangocairo.CairoMatrix
        c.matrix = M().translate(-w/2, -h/2).rotateDegrees(angle)
        c.paint(self.image, x=-w/2, y=-w/2)
        self.image = im


    def mirror(self):
        im = self.image.create_similar("color_alpha", *self.size)
        c = im.Context()
        c.scale(-1, 1)
        c.translate(-self.width, 0)
        c.paint(self.image)
        self.image = im

    def flip(self):
        im = self.image.create_similar("color_alpha", *self.size)
        c = im.Context()
        c.scale(1, -1)
        c.translate(0, -self.height)
        c.paint(self.image)
        self.image = im

    def invert(self):
        pass

    def crop(self, size, offset):
        r = pangocairo.Rect(offset[0], offset[1],
                            size[0], size[1])
        im = self.image.create_similar("color_alpha",
                                       r.width,
                                       r.height)
        c = im.Context()
        c.operator = "source"
        c.translate(-r.x, -r.y)
        c.paint(self.image)
        self.image = im



class ChimeraSolid(Image):
    """Produce a solid surface.

    >>> c = ChimeraSolid((64, 128), '#ff6969')

    """
    __allow_access_to_unprotected_subobjects__ = 1
    def __init__(self, size, color):
        i = pangocairo.ImageSurface("argb", *size)
        p = pangocairo.CairoContext(i)
        rect = pangocairo.Rect(0, 0, *size)
        p.rectangle(rect)
        p.fill(color)
        self.image = i


class ChimeraText(Image):
    """
    >>> c = ChimeraText("Sans 12", "test")


    Using the fill and stroke parameters you can do things that are
    even more fun.
    >>> p = Image("../tests/logo.jpg")
    >>> c = ChimeraText("Sans 48", "test", fill=p, stroke="black")

    Which would stroke the outside of the font in black and fill the
    inside of the font with the image
    
    """
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, fontspec, text, fg="black", bg="white",
                 maxwidth=False, fill=None, stroke=None):
        i = pangocairo.ImageSurface("argb", 1, 1)
        c = i.Context()
        c.paint(fg)
        l = c.Layout()
        l.antialias = "subpixel"
        l.hint_style = "strong"
        l.hint_metrics = "on"
        if maxwidth: l.width = maxwidth
        t = l.Text(text, fontspec)
        c = l.contextFor()
        if stroke: l.stroke(stroke)
        if fill: l.fill(fill)
        else: l.fill(fg)
        self.image = c.image
        self.context = c
        
class ChimeraSvg(Image):
    """Load a normal Chimera Image from an SVG source. Because SVG art
    is vector based it should be sized to something reasonable for use.
    """
    ## We could retain the svg source to use for resize operations
    ## rather than simply resize the raster output, but this would
    ## require a change to the subclassing model.
    def __init__(self, filename, width=None, height=None):
        """Load an image at a fixed size, or at the size recorded in
        the svg source image.

        Invoking this with either width or height as -1 will retain
        the default size for the entity along that dimension. This can
        distort the aspect ratio though.
        """
        svg = chimera_svg.ChimeraSvg()
        if not width and not height:
            fp = svg.load(filename)
        else:
            # we need to acutally probe the size here
            # passing 0 doesn't work
            if width is None: width = height
            if height is None: height = width

            fp = svg.load_at_size(filename, width, height)
        self._parse(fp)

    @staticmethod
    def atMaxSize(filename, max_width=None, max_height=None):
        """ An alternative consturctor, this will clamp the max size
        along width and/or height. The smaller value will take
        priority if both width and height are specified, passing -1
        should allow the image to scale primary along the other
        dimension.
        """
        svg = chimera_svg.ChimeraSvg()
        # we need to acutally probe the size here
        # passing 0 doesn't work
        if max_width is None: max_width   =  max_height
        if max_height is None: max_height =  max_width
        fp = svg.load_at_maxsize(filename, max_width, max_height)
        return Image(fp)

    @staticmethod
    def atZoomWithMaxSize(filename, widthratio, heightratio,
                          max_width, max_height):
        """Retain aspect ratio while clamping the max size of the
        image"""
        svg = chimera_svg.ChimeraSvg()
        fp = svg.load_at_zoom_with_max(filename,
                                       widthratio, heightratio,
                                       max_width, max_height)
        return Image(fp)




_fontconfig = fontconfig.FontConfig()
addFontDir = _fontconfig.addFontDir
addFontFile = _fontconfig.addFontFile
_i = pangocairo.ImageSurface("argb", 1, 1)
_p = pangocairo.CairoContext(_i)
_l = _p.Layout()
listFontFamilies = _l.listFontFamilies


__all__ = ('Image', 
           'ChimeraSolid',
           'ChimeraSvg',
           'ChimeraText',
           'addFontFile', 'addFontDir', 'listFontFamilies')
