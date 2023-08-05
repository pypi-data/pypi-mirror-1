import unittest
import chimera
import os
from math import sin, cos, pi, floor

class TestChimera(unittest.TestCase):

    def test_open(self):
        c = chimera.Image('logo.jpg')
        assert c.size == (274, 194)
        assert c.format == "png"

    def test_as_file(self):
        c = chimera.Image('logo.jpg')
        assert str(c)
        d = chimera.Image(c.asPngFile())
        assert d.size == c.size

    def test_scale(self):
        c = chimera.Image('logo.jpg')
        c.scale(2)
        assert c.size == (274*2, 194*2)

        c = chimera.Image('logo.jpg')
        c.scale("50%")
        assert c.size == (274/2, 194/2)

    def test_rotate(self):
        c = chimera.Image('logo.jpg')
        c.rotate(270.0)
        assert c.size == (194, 274)

    def test_clone(self):
        c = chimera.Image('logo.jpg')
        d = c.clone()
        assert c.size == (274, 194)
        assert d.size == (274, 194)
        c.rotate(270.0)
        # Verify there is no connection between the images surfaces
        assert c.size == (194, 274)
        assert d.size == (274, 194)

    def test_crop(self):
        c = chimera.Image('logo.jpg')
        c.crop((64, 64), (64, 64))
        assert c.size == (64,64)

    def test_resizeTo(self):
        c = chimera.ChimeraText("Comic Sans MS 20",
                                u"Chimera Rocks!")
        c.resizeTo(height=12)
        assert c.height == 12

    def test_mirror(self):
        c = chimera.Image('logo.jpg')
        c.mirror()
        c.flip()
        assert c

    def test_rotate_text(self):
        i = chimera.pangocairo.ImageSurface("argb", 1, 1)
        c = i.Context()

        angle = 15
        theta = angle * 0.017453293
        st, ct = sin(theta), cos(theta)

        l = c.Layout()
        l.antialias = "subpixel"
        l.hint_style = "strong"
        l.hint_metrics = "on"
        l.font = "1942 Report 12"
        t = l.Text("Chimera Rocks!", "1942 Report 16")
        w, h = l.size
        #c.scale(.5, .5)
        c.rotateDegrees(angle)
        c = l.contextFor(ctm=True)
        #print w, h
        #print  l.size
        #print st, ct
        #print c.image.size
        w, h = c.image.width, c.image.height
        l.fill('red')
        c.rectangle(0, 0, 2, 4)
        c.fill("blue")
        #c.image.show()

    def test_bounds(self):
        i = chimera.Image('logo.jpg')
        w, h = i.size
        c = i.Context()
        #print w, h
        for i in range(0, 360, 15):
            #print i
            c.identity()
            c.rotateDegrees(i)
            #print c.bounds


    def test_blit(self):
        c = chimera.Image('logo.jpg')
        c = chimera.ChimeraText("Helvetica 32", "Chimera Rocks!")
        c.rotate(90)
        #c.show()
        assert c

    def test_blend(self):
        c = chimera.Image('logo.jpg')
        f = chimera.ChimeraText("Comic Sans MS 24",
                                u"Chimera Rocks!")
        c.blend(f, (0,0), 0.5)

    def test_invert(self):
        c = chimera.Image('logo.jpg')
        c.invert()
        # just that its still sane
        assert c.size == (274, 194)

    def test_chimerasolid(self):
        c = chimera.ChimeraSolid((64, 128), "#ff6969")
        assert c.size == (64, 128)

    def test_chimeratransparent(self):
        c = chimera.ChimeraSolid((64, 128), "transparent")
        assert c.size == (64, 128)


    def test_chimeratext(self):
        c = chimera.ChimeraText("Comic Sans MS 96",
                                u'ChimeraRocks!',
                                "blue",
                                "red")
        assert c

        c = chimera.Image('logo.jpg')

        f = chimera.ChimeraText("1942 Report 10",
                                u'ChimeraRocks!',
                                "black",
                                "red")
        c.blend(f, (0,0), 0.2)

    def test_width_layout(self):
        from codecs import open
        text = open('text.utf8', 'r', 'utf-8').read()
        c = chimera.ChimeraText("Sans 24",
                                text,
                                "black",
                                "white",
                                512,
                                )
        c.rotate(90)
        assert c

    def test_withFontConfig(self):
        # Add a font from the test dir, the user won't have this one
        # and it shows that fontconfig is working
        chimera.addFontDir(os.path.abspath(os.curdir))
        c = chimera.ChimeraText("Barrakuda 24",
                                "Chimera Rocks!",
                                "red",
                                "white"
                                )
        assert c

    def test_listFontFamilies(self):
        assert "Sans" in chimera.listFontFamilies()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestChimera))
    return suite

if __name__ == "__main__":
    unittest.main()
