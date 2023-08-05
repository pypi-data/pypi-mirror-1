from Pyrex.Distutils import build_ext as build_rex
import re


class build_ext(build_rex):
    # we have "special needs" because libpng is a bad citizen and
    # demands that its headers be included first (before PyRex would
    # place them)
    def swig_sources (self, sources, ext=None):
        sources = build_rex.swig_sources(self, sources)
        # now do our fixup
        for source in sources:
            self._pngPatch(source)
        return sources

    def _pngPatch(self, source):
        data = open(source, 'r').read()
        match = re.search('(?m)^#include\s+"png.h"', data)
        if not match: return

        # we have the dreaded header
        data = data[:match.start()] + data[match.end():]
        data = data.split('\n')
        data.insert(1, '#include "png.h"')

        f = open(source, 'w')
        f.write('\n'.join(data))
        f.close()

