import chimera.pangocairo as pangocairo
import chimera.fontconfig as fontconfig

fc = fontconfig.FontConfig()
#fc.addFontFile("/home/bcsaller/.fonts/Helvetica.dfont")


DPI = 72

base_font = "Helvetica %s"
#base_font = "Agent Orange %s"
menu_size = 11
menu_font =  base_font % menu_size
menu_color = "#2b0018ff"
menu_shadow = "#ffffff99"
menu_offset = (-1, -1)

over_color = "white"
over_shadow = "#00000033"

photo_size = 10
photo_font = base_font % photo_size
photo_color = "#797979"
photo_shadow = "white"

def dropshadow(text, font, color, shadow, offset, hint="strong"):
    origin = (10, 100)
    im = pangocairo.ImageSurface("argb", 800, 256)
    # Context
    c = pangocairo.CairoContext(im, DPI)
    c.antialias = "subpixel"
    c.hint_style = hint
    c.hint_metrics = "on"
    # Layout
    l, t = c.layout(text, font)
    l.single_paragraph = True
#    t.stretch = "condensed"
    t.weight = "bold"
    l += t
    c.move_to(*origin)
    ext1 = l.fill(shadow)
    c.move_to(origin[0] + offset[0], origin[1] + offset[1])
    ext2 = l.fill(color)
    # Extract rendered image
    bounds = ext1 + ext2
    im2 = c.imageFromRect(bounds)
    return im2

def menu(text,
         font=menu_font,
         color=menu_color,
         shadow=menu_shadow,
         offset=menu_offset, **kw):
    return dropshadow(text, font, color, shadow, offset)


def menu_over(text,
         font=menu_font,
         color=over_color,
         shadow=over_shadow,
         offset=menu_offset, **kw):
    return dropshadow(text, font, color, shadow, offset)


def photo(text,
         font=photo_font,
         color=photo_color,
         shadow=photo_shadow,
         offset=menu_offset, **kw):
    return dropshadow(text, font, color, shadow, offset, hint="medium")

if __name__ == "__main__":
    text = "ARTISTS AWIST  Bg Gb"

    for method in menu, menu_over, photo:
        img = method(text)
        img.writePng("/tmp/%s.png" % method.__name__)

