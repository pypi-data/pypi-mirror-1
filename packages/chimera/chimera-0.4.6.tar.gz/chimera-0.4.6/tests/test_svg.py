import unittest
import chimera

class TestChimeraSvg(unittest.TestCase):

    def test_toPNG(self):
        # Generate an image
        c = chimera.ChimeraSvg("logo.svg", 100, 100)
        assert c.width <= 100
        assert c.height <= 100

        # Here we specify the "rectangular" size
        c = chimera.ChimeraSvg("logo.svg", 512)
        assert c.width  == 512
        assert c.height == 512

        # auto size
        c = chimera.ChimeraSvg("logo.svg")

    def test_maxSize(self):
        c = chimera.ChimeraSvg.atMaxSize("logo.svg", 512)
        assert c.width <= 512 and c.width > 500
        assert c.height <= 512

    def test_zoomMax(self):
        c = chimera.ChimeraSvg.atZoomWithMaxSize("logo.svg",
                                                 3,3,
                                                 512, 100)
        assert c.width <= 512
        assert c.height <= 100




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestChimeraSvg))
    return suite

if __name__ == "__main__":
    unittest.main()
