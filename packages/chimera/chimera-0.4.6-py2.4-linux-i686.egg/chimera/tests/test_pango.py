import unittest
import chimera.pangocairo as pangocairo

class TestChimeraPango(unittest.TestCase):

    def test_toPNG(self):
        # Generate an image
        i = pangocairo.ImageSurface("argb", 640, 256)
        p = pangocairo.CairoContext(i)
        c.antialias = "subpixel"
        c.hint_style = "strong"
        c.hint_metrics = "on"
        l, t = c.layout(text, font)
        l.show()
        assert i.toPngBuffer()

    def test_families(self):
        i = pangocairo.ImageSurface("argb", 640, 256)
        p = pangocairo.CairoContext(i)
        fonts = p.listFontFamilies()
        # These should be mapped on any system supporting pango
        assert "Sans" in fonts
        assert "Serif" in fonts
        assert "Monospace" in fonts

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestChimeraPango))
    return suite

if __name__ == "__main__":
    unittest.main()
