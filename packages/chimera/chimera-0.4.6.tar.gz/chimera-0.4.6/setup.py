import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
from setuptools.extension import Extension
from subprocess import Popen, PIPE
from distext.pkgconfig import pkgconfig
from distext import *
import __pkginfo__
import os

classifiers = [
"Development Status :: 4 - Beta",
"Intended Audience :: Developers",
"Natural Language :: English",
"Operating System :: OS Independent",
"Programming Language :: Python",
"Topic :: Multimedia :: Graphics :: Editors",
"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
]

includes, libs = pkgconfig("pangocairo cairo freetype2 fontconfig librsvg-2.0")

setup(
      name = __pkginfo__.modname,
      version = __pkginfo__.version,
      author = "Benjamin Saller",
      author_email = "bcsaller@objectrealms.net",
      url = "http://projects.objectrealms.net/projects/chimera",
      description = """ Simple Image Generation """,
      license = "GPL",
      platforms = ["Python >= 2.4"],

      install_requires = [  "setuptools >= 0.6a11", ],
      packages = [ "chimera",
                   "chimera.tests"],
      package_dir = {'chimera' : "src",
                     'chimera.tests' : "tests",
                     },
      package_data={'chimera.tests': ['*.TTF', '*.utf8', '*.svg',
                                      '*.jpg'],
                    'chimera' : ['ez_setup.py'],
                    },

      classifiers = classifiers,
      long_description = """
      Simple image generation of beautiful anti-aliases text in the
      fonts of your choice. Supports fully internationalize text and
      automatic layout of text within graphic elements. Can easily
      combine and manipute graphics from a vareity of sources.
      """,

      ext_modules=[
            Extension("chimera.pangocairo",
                      ["src/pangocairo.pyx", ],
                      include_dirs = includes,
                      libraries = libs,
                      ),
            Extension("chimera.chimera_svg",
                      ["src/chimera_svg.pyx",],
                      include_dirs = includes,
                      libraries = libs,
                      ),
            Extension("chimera.fontconfig",
                      ["src/fontconfig.pyx"],
                      include_dirs = includes,
                      libraries = libs,
                      )
            ],

      cmdclass = {
              'test' : TestCommand,
              'doc' : DocCommand,
      }
      )
