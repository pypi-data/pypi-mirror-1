"""
chimera
~~~~~~~~~~~~~~~~~~~~
adapt Chimera image to OFS.Images and back again

"""

__author__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright ObjectRealms LLC, 2005.'
__license__  = 'The GNU Public License V2+'


from OFS.Image import Image
import os.path
import md5

def hashKey(**kwargs):
    h = md5.new()
    for v in kwargs.itervalues():
        h.update(v)

    fmt = kwargs.get("format", "png")
    key = "%s.%s" % (h.hexdigest(), fmt)
    return key


def toOFSImage(name, font, aChimera):
    content_type = "image/%s" % aChimera.format
    id = hashKey(name=name, font=font, format=aChimera.format)
    image = Image(id, name, str(aChimera),  content_type)
    return id, image

def toOFSImage(name, aChimera, title=None):
    """Generate an image from a Chimera layer, the object will be
    named but will not have an aq context and must be set into a
    folder
    """
    try:
        ext = aChimera.format.lower()
    except:
        ext = "png"

    content_type = "image/%s" % ext
    if not title: title = name

    if hasattr(aChimera, "asPngBuffer"):
        data = aChimera.asPngBuffer()
    elif hasattr(aChimera, "read"):
        data = aChimera.read()
    else:
        data = str(aChimera)

    image = Image(name, title, data,  content_type)
    return image


