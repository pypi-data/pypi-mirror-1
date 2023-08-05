import unittest
import chimera
import cairo
import math

def warpPath(ctx, function):
    first = True

    for type, points in ctx.copy_path():
        if type == cairo.PATH_MOVE_TO:
            if first:
                ctx.new_path()
                first = False
            x, y = function(*points)
            ctx.move_to(x, y)

        elif type == cairo.PATH_LINE_TO:
            x, y = function(*points)
            ctx.line_to(x, y)

        elif type == cairo.PATH_CURVE_TO:
            x1, y1, x2, y2, x3, y3 = points
            x1, y1 = function(x1, y1)
            x2, y2 = function(x2, y2)
            x3, y3 = function(x3, y3)
            ctx.curve_to(x1, y1, x2, y2, x3, y3)

        elif type == cairo.PATH_CLOSE_PATH:
            ctx.close_path()

def spiral(x, y):
    theta0 = -math.pi * 3 / 4
    theta = x / 256 * math.pi * 2 + theta0
    radius = y + 100 - x/7
    xnew = radius*math.cos(theta)
    ynew = radius*math.sin(-theta)
    return xnew + 128, ynew + 128

class Test(unittest.TestCase):

    def test_toPNG(self):
        # Create a cairo surface and manipulate it using the
        # pycairo API
        c = chimera.ChimeraCairo(256, 256)
        assert c.width <= 256
        assert c.height <= 256

        ctx = c.context

        pat = cairo.LinearGradient (0.0, 0.0, 0, 256)
        pat.add_color_stop_rgba (1, 0, 0, 0, 1)
        pat.add_color_stop_rgba (0, 1, 1, 1, 1)

        ctx.rectangle (0,0, 256,256)
        ctx.set_source (pat)
        ctx.fill ()

        solidpattern = ctx.get_source()
        ctx.set_source (solidpattern)
        ctx.set_source_rgb (1,0,0)

        ctx.select_font_face("Sans")
        ctx.set_font_size(24)


        ctx.move_to(0,0)
        ctx.new_path()
        ctx.text_path("Chimera with Cairo Rocks!")
        warpPath(ctx, spiral)
        ctx.fill()
        c.save("/tmp/text.png")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

if __name__ == "__main__":
    unittest.main()
