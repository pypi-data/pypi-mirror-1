# $Id$
# experimental element colorizer.

try:
    import cElementTree as ET
except ImportError:
    import elementtree.ElementTree as ET

import colorizer
import cStringIO

##
# A colorizer that converts a code snippet to a colorized XHTML element
# tree.

class ElementColorizer(colorizer.Colorizer):

    def __init__(self, text):
        self.readline = cStringIO.StringIO(text).readline
        self.elem_root = ET.Element("pre")
        self.elem_style = None

    def colorize(self):
        colorizer.Colorizer.colorize(self)
        return self.elem_root

    def make_span(self, class_):
        e = ET.SubElement(self.elem_root, "span")
        e.set("class", class_)
        return e

    def lineno(self, lineno):
        e = self.make_span("lineno")
        e = ET.SubElement(e, "a")
        e.attrib["name"] = str(lineno)
        e.text = "%05d" % lineno
        e.tail = " "

    def write(self, text):
        if self.elem_style is not None:
            elem = self.elem_style
        elif len(self.elem_root):
            elem = self.elem_root[-1]
            elem.tail = (elem.tail or "") + text
            return
        else:
            elem = self.elem_root
        elem.text = (elem.text or "") + text

    def style(self, style, token):
        if self.elem_style is not None:
            current = self.elem_style.get("class")
        else:
            current = None
        if style != current:
            if style:
                self.elem_style = self.make_span(style)
            else:
                self.elem_style = None
        return current

if __name__ == "__main__":
    import sys
    PYTHONWORKS_STYLE = """
    .class {color:firebrick;font-weight:bold;}
    .comment {color:darkolivegreen;font-style:italic;}
    .decorator {color:firebrick;}
    .function {color:firebrick;font-weight:bold;}
    .keyword {color:firebrick;}
    .lineno {color:gray;border-right:1px solid gray;padding-right:5px;}
    .string {color:navy;}
    """
    try:
        file = sys.argv[1]
    except IndexError:
        file = "pythondoc.py"
    c = ElementColorizer(open(file).read())
    import time
    t0 = time.clock()
    tree = c.colorize()
    t0 = time.clock() - t0
    print "<style>", PYTHONWORKS_STYLE, "</style>"
    ET.dump(tree)
    print >>sys.stderr, t0
