"""
PangoCairo frontends the Pango Layout and Cairo Rendering systems with
a simple, convenience API. To use it you first create a drawing
surface.

>>> import chimera.pangocairo as pangocairo

Lets create a surface from an existing resource and write it out to
another name.

>>> im = pangocairo.ImageSurface("logo.png")
>>> assert 'PNG' in im.asPngBuffer()[:128]

Great. Now lets create an empty image we will use for testing

>>> im = pangocairo.ImageSurface('argb', 256, 256)
>>> assert im.height == 256
>>> assert im.width == 256
>>> repr(im)
'<ImageSurface 256x256>'

Now that we have a surface to draw on we can construct a CairoContext.
This object is our entry point to all the warm Cairo gooeyness.

>>> c = pangocairo.CairoContext(im)

We expose a good portion of the Cairo API (but not all of it). While
our focus is around properly laid out text with high quality rendering
we can still draw on the canvas.

>>> c.rectangle((10,10), (150, 125))
>>> c.fill_preserve((1, 0, 0, 0.7))
>>> c.linewidth = 2.0
>>> c.stroke("green")
>>> c.rotateDegrees(45.0)
>>> c.rectangle((150,0), (100,100))
>>> c.stroke("blue")

>>> assert c.asPngBuffer()


What we really want all this for though is control over text layout, fonts
and rendering.


>>> l = c.Layout()
>>> l.hint_style = "slight"
>>> l.hint_metrics = "on"
>>> l.antialias = "subpixel"
>>> t = l.Text("Chimera Rocks", "Times New Roman 24")
>>> c.move_to(100,100)
>>> c.rotateDegrees(-45.0)
>>> t.underline = "double"
>>> t.weight = "heavy"
>>> t.style = "italic"
>>> t.letter_spacing = 2500
>>> assert l + t
>>> assert l.fill((1.0, 0.0, 1.0, 1.0))

>>> l = c.Layout()
>>> t = l.Text("Python", "Helvetica 32")
>>> t.underline = "none"
>>> t.letter_spacing = -2500
>>> t.foreground = "blue"
>>> c.move_to(25, 25)
>>> t = l.Text(" Love", "Helvetica 24")
>>> t.letter_spacing = 2000
>>> t.foreground = "red"
>>> t.underline = "single"
>>> t.style= "oblique"
>>> extents = l.show()

What follows is an example of doing a high quality drop shadow
text image. A layout is generated, a shadow is rendered, and the the
same layout is rendered over it at an offset.

>>> im = pangocairo.ImageSurface("argb", 256, 256)
>>> c = pangocairo.CairoContext(im)
>>> l = c.Layout()
>>> l.antialias = "subpixel"
>>> l.hint_style = "strong"
>>> l.hint_metrics = "on"

>>> text = "ARTIST CLIENT LOGIN"
>>> font = "Helvetica-11:bold"
>>> t = l.Text(text, font)
>>> t.letter_spacing = 200
>>> t.weight = "bold"
>>> c.move_to(10,100)
>>> ext1 = l.fill("#2b001899")

Reuse the same layout for the top layer with a different fill

>>> c.move_to(11, 99)
>>> ext2 = l.fill("#ffffffff")

Here we want to extract it to a properly sized area. Given the
bounding rect imageFromRect will do just that. This is like
traditional Chimera clipping.
#>>> r = ext1 + ext2
#>>> im2 = im.create_similar('color_alpha', r.width, r.height)
#>>> c2 = pangocairo.CairoContext(im2)
#>>> im2 = c2.scaleImage(2,2)
#>>> assert im2.width == r.width *2



We have bi-directional interoperatbility with PNGs. Here we pass a
file object into ImageSurface
>>> png = open("logo.png", "r")
>>> im = pangocairo.ImageSurface(png)
>>> assert im.size == (274, 194)

"""


import doctest

def test_suite():
    suite = doctest.DocTestSuite()
    return suite

if __name__ == "__main__":

    doctest.testmod()
