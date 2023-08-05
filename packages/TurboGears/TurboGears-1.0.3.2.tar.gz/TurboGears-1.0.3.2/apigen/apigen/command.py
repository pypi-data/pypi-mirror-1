import sys
import os
import optparse

from apigen.pythondoc import ModuleParser, CompactHTML, ElementTree
from apigen.element_colorizer import ElementColorizer

from apigen import release

ET = ElementTree

def myparse(file, output):

    basename = os.path.basename(file)
    basename = os.path.splitext(basename)[0]
    sourcefile = "%s-source.html" % basename
    parser = ModuleParser(file)
    module = parser.parse(docstring=1)

    for elem in module.getiterator():

        lineno = elem.get("lineno")
        if not lineno:
            continue

        description = elem.find("info/description")
        if description is None:
            description = ET.SubElement(elem, "p")
        if len(description) == 0 and description.text:
            # wrap it in a paragraph
            p = ET.SubElement(description, "p")
            p.text = description.text
            description.text = None

        # insert hyperlink
        href = sourcefile + "#" + lineno
        p = ET.SubElement(description, "p")
        a = ET.SubElement(p, "a", href=href)
        a.set("class", "sourcelink")
        a.text = "View source code..."

    # ET.ElementTree(module).write("out.xml")

    formatter = CompactHTML()
    print formatter.save(module, os.path.join(output, basename)), "ok"
    c = ElementColorizer(open(file).read())
    pre = c.colorize()
    sourceoutput = os.path.join(output, sourcefile)
    root = ET.Element("html")
    head = ET.SubElement(root, "head")
    style = ET.SubElement(head, "style")
    style.attrib["type"] = "text/css"
    style.text = """
    .class {color:firebrick;font-weight:bold;}
    .comment {color:darkolivegreen;font-style:italic;}
    .decorator {color:firebrick;}
    .function {color:firebrick;font-weight:bold;}
    .keyword {color:firebrick;}
    .lineno {color:gray;border-right:1px solid gray;padding-right:5px;}
    .string {color:navy;}
    """
    body = ET.SubElement(root, "body")
    body.append(pre)
    tree = ET.ElementTree(root)
    tree.write(sourceoutput)
    print sourceoutput, "ok"

def generate_index(package, packages, files, output):
    html = ET.Element("html")
    tree = ET.ElementTree(html)
    body = ET.SubElement(html, "body")
    h1 = ET.SubElement(body, "h1")
    h1.text = package
    if packages:
        h2 = ET.SubElement(body, "h2")
        h2.text = "Subpackages"
        dl = ET.SubElement(body, "dl")
        
        for p in packages:
            dt = ET.SubElement(dl, "dt")
            a = ET.SubElement(dt, "a")
            a.attrib["href"] = "%s/index.html" % (p)
            a.text = p
            dd = ET.SubElement(dl, "dd")
            # add package description here... will require cooperation
            # and aggregation
    files.sort()
    if files:
        h2 = ET.SubElement(body, "h2")
        h2.text = "Modules"
        dl = ET.SubElement(body, "dl")
        
        for f in files:
            f = os.path.splitext(f)[0]
            dt = ET.SubElement(dl, "dt")
            a = ET.SubElement(dt, "a")
            a.attrib["href"] = "%s.html" % (f)
            a.text = f
            dd = ET.SubElement(dl, "dd")
            # add module description here... will require cooperation
            # and aggregation
    indexfile = os.path.join(output, "index.html")
    tree.write(indexfile)
    print indexfile, "ok"

def process_files(roots, output, ignore):
    splitext = os.path.splitext
    for thisroot in roots:
        for root, dirs, files in os.walk(thisroot):
            if root in ignore:
                continue
            if ".svn" in dirs:
                dirs.remove(".svn")
            files = filter(lambda file: splitext(file)[1] == ".py", files)
            if "__init__.py" in files:
                packages = []
                for dir in dirs:
                    subdir = os.path.join(root, dir)
                    if os.path.exists(os.path.join(subdir,
                            "__init__.py")):
                        if not subdir in ignore:
                            packages.append(dir)
                initiallen = len(os.path.commonprefix([thisroot, root]))
                remainder = root[initiallen:]
                if remainder.startswith("/"):
                    remainder = remainder[1:]
                currentoutput = os.path.join(output, remainder)
                if not os.path.exists(currentoutput):
                    os.makedirs(currentoutput)
                package = os.path.basename(root)
                generate_index(package, packages, files, currentoutput)
            for file in files:
                myparse(os.path.join(root, file), currentoutput)

def main():
    parser = optparse.OptionParser(
        usage="%prog [-o]", version="%prog " + release.version)
    parser.add_option("-o", "--output",
             help="output directory (will be created)",
             dest="output")
    parser.add_option("-i", "--ignore",
        help="ignore this path/file", dest="ignore", action="append")
    (options, args) = parser.parse_args()
    process_files(args, options.output, options.ignore)