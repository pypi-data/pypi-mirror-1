import chimera

font = "irrep 32"
fg = "black"
bg = "transparent"


def renderLabel(**kwargs):
    title=kwargs['text']
    title = '<span weight="bold" stretch="ultracondensed" variant="smallcaps">%s</span>' % title

    text = chimera.ChimeraText(font, title, fg, bg, markup=True, maxwidth=600)
    return text


