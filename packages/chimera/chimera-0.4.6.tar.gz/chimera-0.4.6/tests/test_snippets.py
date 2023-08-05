import math
import os
import unittest
import chimera.pangocairo as pc
from codecs import open

class Test(unittest.TestCase):
    directory = "/tmp"
    format = "png"
    width = 256
    height = 256

    def getName(self):
        return self.id().rsplit(".")[-1]

    def setUp(self):
        self.im = pc.ImageSurface("argb", self.width, self.height)
        self.c  = pc.CairoContext(self.im)
        self.c.scale(self.width, self.height)
        self.c.linewidth = 0.04

        self.name = "%s.%s" %(self.getName(), self.format)
        self.fn = os.path.join(self.directory, self.name)

    def tearDown(self):
        pass
        #if self.fn and self.c:
        #    self.c.write(self.fn)

    def test_arc(self):
        cairo = self.c
        xc = 0.5
        yc = 0.5
        radius = 0.4;
        angle1 = 45.0  * (math.pi/180.0) #  /* angles are specified */
        angle2 = 180.0 * (math.pi/180.0) #  /* in radians           */

        cairo.arc(xc, yc, radius, angle1, angle2)
        cairo.stroke("black")

        cairo.arc(xc, yc, 0.05, 0, 2*math.pi)
        cairo.fill((1,0.2,0.2,0.6))
        cairo.linewidth = 0.03
        cairo.arc (xc, yc, radius, angle1, angle1)
        cairo.line_to(xc, yc)
        cairo.arc (xc, yc, radius, angle2, angle2)
        cairo.line_to (xc, yc)
        cairo.stroke((1,0.2,0.2,0.6))

    def test_arc_negative(self):
        cairo = self.c
        xc = 0.5
        yc = 0.5
        radius = 0.4;
        angle1 = 45.0  * (math.pi/180.0) #  /* angles are specified */
        angle2 = 180.0 * (math.pi/180.0) #  /* in radians           */

        cairo.arc_negative(xc, yc, radius, angle1, angle2)
        cairo.stroke("black")

        cairo.arc(xc, yc, 0.05, 0, 2*math.pi)
        cairo.fill((1,0.2,0.2,0.6))
        cairo.linewidth = 0.03
        cairo.arc (xc, yc, radius, angle1, angle1)
        cairo.line_to(xc, yc)
        cairo.arc (xc, yc, radius, angle2, angle2)
        cairo.line_to (xc, yc)
        cairo.stroke((1,0.2,0.2,0.6))

    def test_curve_to(self):
        x=0.1
        y=0.5
        x1=0.4
        y1=0.9
        x2=0.6
        y2=0.1
        x3=0.9
        y3=0.5
        c = self.c
        c.move_to(x, y)
        c.curve_to(x1, y1, x2, y2, x3, y3)
        c.stroke ((1,0.2,0.2,0.6))
        c.linewidth =  0.03
        c.move_to (x,y)
        c.line_to (x1,y1)
        c.move_to (x2,y2)
        c.line_to (x3,y3)
        c.stroke ("green")

    def test_fill_and_stroke(self):
        c = self.c
        c.move_to(0.5, 0.1)
        c.line_to(0.9, 0.9)
        c.rel_line_to (-0.4, 0.0)
        c.curve_to(0.2, 0.9, 0.2, 0.5, 0.5, 0.5)
        c.close_path()

        c.move_to(0.25, 0.1)
        c.rel_line_to(0.2, 0.2)
        c.rel_line_to(-0.2, 0.2)
        c.rel_line_to (-0.2, -0.2)
        c.close_path()

        c.fill_preserve((0,0,1))
        c.stroke((0,0,0))
        
    def test_gradient(self):
        cairo = self.c
        pat = pc.LinearGradient(0.0, 0.0, 0.0, 1.0)
        pat.add_color_stop(1, (1, 1, 1, 1))
        pat.add_color_stop(0, (0, 0, 0, 0.7))
        cairo.rectangle(0, 0, 1, 1)
        cairo.fill(pat)

        pat = pc.RadialGradient(0.45, 0.4, 0.1,
                                0.4, 0.4, 0.5)
        pat.add_color_stop(0, (1, 1, 1, 1))
        pat.add_color_stop(1, (0, 0, 0, 1))
        cairo.arc (0.5, 0.5, 0.3, 0, 2 * math.pi)
        cairo.fill(pat);

    def test_clip_image(self):
        cairo = self.c
        cairo.arc (0.5, 0.5, 0.3, 0, 2*math.pi)
        cairo.clip()
        cairo.new_path()

        im = pc.ImageSurface("kapow.png")
        w = im.width
        h = im.height
        cairo.scale (1.0/w, 1.0/h)
        cairo.paint (im)


    def test_image(self):
        cairo = self.c

        im = pc.ImageSurface("kapow.png")
        w = im.width
        h = im.height

        cairo.translate (0.5, 0.5)
        cairo.rotate (45* math.pi/180)
        cairo.scale  (1.0/w, 1.0/h)
        cairo.translate(-0.5*w, -0.5*h)

        cairo.paint(im)

    def test_image_pattern(self):
        cairo = self.c

        im = pc.ImageSurface("kapow.png")
        w = im.width
        h = im.height
        cairo.scale (1.0/w, 1.0/h)

        pattern  = pc.SurfacePattern(im)
        pattern.extend = "repeat"
        pattern.filter = "best"

        cairo.translate (0.5, 0.5)
        cairo.rotate (math.pi / 4.0)
        cairo.scale (1.0 / math.sqrt (2), 1.0 / math.sqrt (2))
        cairo.translate (- 0.5, - 0.5)

        cairo.paint(pattern)
        ## XXX: Broken...
        pattern.scale(w * 5.0, h * 5.0)

        cairo.rectangle (0, 0, 1.0, 1.0)
        cairo.fill(pattern)



    def test_path(self):
        cairo = self.c
        cairo.move_to (0.5, 0.1)
        cairo.line_to (0.9, 0.9)
        cairo.rel_line_to (-0.4, 0.0)
        cairo.curve_to (0.2, 0.9, 0.2, 0.5, 0.5, 0.5)
        cairo.stroke ("black")

    def test_text(self):
        self.im = pc.ImageSurface("argb", self.width, self.height)
        c = self.c  = pc.CairoContext(self.im)

        #c.rotate (45* math.pi/180)
        text = """This is a test of a block of text that will overflow the image"""
        l = c.Layout()
        t = l.Text(text)
        t.font = "Sans 24"

        l.width = 300
        l.single_paragraph = True
        l.ellipsize = "end"
        l.update()


        im2 = pc.ImageSurface("argb", *l.size)
        c2 = pc.CairoContext(im2)
        l.setContext(c2)
        #c2.rotate (45* math.pi/180)
        l.fill("black")
        self.c = c2
        self.im = im2

    def xtest_utf8(self):
        self.im = pc.ImageSurface("argb", self.width, self.height)
        c = self.c  = pc.CairoContext(self.im)

        data = open("HELLO.utf8", 'r', 'utf8').read()
        assert type(data) == unicode

        l = c.Layout()
        l.font = "Helvetica 12"
        l.Text(data.encode('utf-8'))
        l.antialias = "subpixel"
        l.hint_style = "strong"
        l.update()
        size = l.size
        im2 = pc.ImageSurface("argb", size[0], size[1])
        c2 = pc.CairoContext(im2)

        c2.paint("white")
        l.width = 750
        l.setContext(c2)
        l.fill("black")
        self.c = c2
        self.im = im2

    def test_fonts(self):
        import random
        self.im = pc.ImageSurface("argb", self.width, self.height)
        c = self.c  = pc.CairoContext(self.im)

        count = 3
        pick = []
        l = c.Layout()
        l.width = 100
        l.single_paragraph = False
        fonts = l.listFontFamilies()
        names = fonts.keys()
        for i in range(count):
            name = random.choice(names)
            face = fonts[name]
            pick.append("%s %s 14 " % ( name,
                                    random.choice(face)))

        for font in pick:
            t = l.Text("%s\n" % font)
            t.font =  font

        l.show()
        
    def test_composite(self):
        im2 = pc.ImageSurface("plus.png")
        for op in pc.cairo_operators:
            im = pc.ImageSurface("star.png")
            c = im.Context()
            c.operator = op
            c.paint(im2)
            l = c.Layout()
            t = l.Text(op, "Sans 12")
            c.operator = "source"
            l.fill((0,0,0,0.7))
            
    def test_watermark(self):
        im = pc.ImageSurface("logo.png")
        c = im.Context()
        l = c.Layout()
        t = l.Text("Copyright ObjectRealms, LLC 2006", "Helvetica 9")

        c.translate(im.width/2.0, im.height/2.0)
        l.fill((1,0,0,0.2))
        im2 = pc.ImageSurface("plus.png")
        c.paint(im2, alpha=0.3)
        
    def test_matrix(self):
        mt = (
            1.0, 0.0,
            -0.5, 1.0,
            0.0, 0.0
            )
        m = pc.CairoMatrix(mt)
        assert m.asTuple() == mt

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

if __name__ == "__main__":
    unittest.main()




