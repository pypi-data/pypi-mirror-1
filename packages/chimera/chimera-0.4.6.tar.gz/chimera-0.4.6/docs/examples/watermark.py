#!/usr/bin/python
# Example of how to do a logo watermark on an image
# useful to protect digital assets from brand diversion
from chimera import *
import sys, os

COPYRIGHT = u'\xa9 Me 2005'

# Load the image to watermark <taken from the cmdline>
base = Image(sys.argv[1])
# Load the logo to water mark with 
logo = ChimeraSvg(os.path.abspath('tests/logo.svg'), base.width/4)

# Center the logo
base.composite(logo,
               offset=((base.width - logo.width)/2.0,(base.height-logo.width)/2.0),
               alpha=0.35,
               )

if COPYRIGHT:
    # Add a drop shadow for the copyright
    text = ChimeraText("sans 9 bold", COPYRIGHT, 'white', 'black',)
    shadow = ChimeraText("sans 9 bold", COPYRIGHT, 'black', 'black',)
    shadow.composite(text, offset=(-1, -1))
    
    # and stick it in the bottom left
    base.composite(shadow, offset=(5, base.height - (text.height + 9)))

base.show()
