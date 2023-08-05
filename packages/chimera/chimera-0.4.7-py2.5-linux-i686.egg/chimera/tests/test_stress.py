"""
Run the problamatic text generation paths many, many times
Taking samples at even intervals

"""
import os
import unittest
import time
import sys
import subprocess


# only valid with the default ouput format, but key, this is a debug toy
column_desc = ['sample', 'delta', 'total', 'stack', 'shared', 'code', 'note']

class NanoProf:
    """ A small memory profiler """
    def __init__(self):
        self.data = []
        self.counter = 0

    def sample(self, note=None):
        data = [int(d) for d in open("/proc/self/statm",
                                     "r").read().split()]
        self.counter += 1

        self.data.append({'timestamp' : time.time(),
                          'total'     : data[0],
                          'shared'    : data[2],
                          'code'      : data[3],
                          'stack'     : data[5],
                          'sample'    : self.counter,
                          'note'      : note,
                          })
    def _process(self):
        orig = self.data[0]['timestamp']
        self.data[0]['delta'] = 0
        delta = 0
        for row in self.data[1:]:
            row['delta'] = delta + (row['timestamp'] - orig)
            orig = row['timestamp']
            delta = row['delta']

    def plot(self,
             fmt="%(sample)s %(delta)s %(total)s %(stack)s %(shared)s %(code)s # %(note)s",
             fp=sys.stdout):
        self._process()
        for row in self.data:
            print >>fp, fmt % row

    def _render(self, **kw):
        fn = "/tmp/memplot"
        fp = open(fn , "w")
        self.plot(fp=fp, **kw)
        fp.close()
        return fn

    def _graph(self, fn, columns=[(1,2), (1,3), (1,4), (1,5)]):
        output = "/tmp/memplot.svg"
        try: os.remove(output)
        except: pass

        p = subprocess.Popen('gnuplot',
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             close_fds=True)
        (child_stdout, child_stdin) = (p.stdout, p.stdin)
        print >>child_stdin, "set term svg dynamic"
        print >>child_stdin, 'set output "%s"' % output

        for index, pair in enumerate(columns):
            verb = "plot"
            if index > 0:verb = "replot"
            title = column_desc[pair[1]]
            print >>child_stdin, '%s  "%s" using ($%d):($%d) title "%s" with line palette' % (
                verb, fn, pair[0], pair[1], title)
        print >>child_stdin, 'quit'
        p.wait()
        return output

    def _view(self, output):
        subprocess.call(['inkscape', output])

    def show(self, **kw):
        fn = self._render()
        output = self._graph(fn)
        self._view(output)

    def status(self):
        self._process()
        tot = len(self.data) -1
        first = self.data[1]
        last = self.data[-1]
        delta = last['delta']
        delta -= first['delta']

        if first != last:
            print "\n%s in %0.2f seconds =  %0.2f per second" %(
                tot, delta,
                tot / delta)
        else:
            print "\n%0.2f seconds" % last['delta']

def regraph(args):
    columns = []
    # pivot linear args into int tuples
    while args:
        pair = args[:2]
        columns.append(( int(pair[0]), int(pair[1])))
        del args[:2]

    prof = NanoProf()
    output = prof._graph("/tmp/memplot", columns=columns)
    prof._view(output)

def dropshadow(basec, text, font, color, shadow, offset, operator="dest_over"):
    l = basec.Layout()
    l.resolution = options.dpi
    t = l.Text(text, font)
    t.letter_spacing = -500

    # Render
    c = l.contextFor(4,4)
    c.move_to(2,2)
    l.antialias = options.antialias
    l.hint_style = options.hint_style
    l.hint_metrics = options.hint_metrics

    ext1 = l.fill(color, preserve=True)
    if options.use_shadow:
        c.move_to(2 + offset[0], 2 + offset[1])
        if operator: c.operator = operator
        ext2 = l.fill(shadow, preserve=True)
    return c.image


def do_chimera():
    baseim = pc.ImageSurface("argb", 1, 1)
    basec = pc.CairoContext(baseim)

    fontspec="%s %s" % (options.font, options.pointsize)

    for i in range(options.iterations):
        text = options.text or \
               "Render test %s %s" % (options.operator, i)
        im = dropshadow(basec,
                        text,
                        fontspec,
                        options.color,
                        options.shadow,
                        (1, 1),
                        options.operator)
        #report
        if 1:
            if i % 25 == 0 and i != 0: print
            sys.stdout.write('.')
            sys.stdout.flush()

        prof.sample()

    # visually check the last one for corruption
    if options.output:
        im.writePng(os.path.expanduser(options.output))
    else:
        im.show()


def main():
    global prof
    prof = NanoProf()
    #prof.sample()

    do_chimera()
    prof.sample()
    if options.show:
        prof.show()
    prof.status()


if __name__ ==  "__main__":
    from chimera import pangocairo as pc
    import optparse
    global options
    parser = optparse.OptionParser()
    parser.add_option("-n", "--iterations",
                      dest="iterations",
                      action="store",
                      type="int",
                      default=10,
                      help="number of runs")

    parser.add_option("-d", "--dpi",
                      dest="dpi",
                      action="store",
                      type="int",
                      default=72,
                      help="dots per inch")

    parser.add_option("-q", "--quiet",
                      action="store_false",
                      dest="show", default=True,
                      help="to graph or not to graph")

    parser.add_option("-o", "--opertator",
                      dest="operator",
                      default="dest_over",
                      help="operator to use [%s]" %(','.join(pc.cairo_operators.keys())))


    parser.add_option("-f", "--font",
                      dest="font",
                      default="Helvetica",
                      help="font to use -- see fc-list" )

    parser.add_option("-p", "--pointsize",
                      dest="pointsize",
                      type="int",
                      default=32,
                      help="font size in points")

    parser.add_option("-c", "--color",
                      dest="color",
                      default="red",
                      help="font color")

    parser.add_option("-s", "--shadow",
                      dest="shadow",
                      default="black",
                      help="shadow color")

    parser.add_option("-t", "--text",
                      dest="text",
                      help="text to render")

    parser.add_option("-a", "--antialias",
                      dest="antialias",
                      default="subpixel",
                      help="antialias mode [default, off, grey, subpixel]")

    parser.add_option("--hint-style",
                      dest="hint_style",
                      default="strong",
                      help="hint style")

    parser.add_option("--hint-metrics",
                      dest="hint_metrics",
                      default="on",
                      help="hint style")

    parser.add_option("--no-shadow",
                      action="store_false",
                      dest="use_shadow",
                      default=True,
                      help="disable drop shadow")


    parser.add_option("--output",
                      dest="output",
                      help="filename for output as png")

    (options, args) = parser.parse_args()

    if not args:
        main()
    else:
        regraph(args)
