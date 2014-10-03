import tempfile
import subprocess
from tempfile import TemporaryFile

from lxml import etree


def preprocess_wxr_file(fname):
    # Not proud of this one, but I haven't dared to dig into the xmllint
    # sources yet. A lxml implementation would probably make sense, both
    # to spare IO and not having to fork...
    out = TemporaryFile()
    with TemporaryFile() as err:
        if subprocess.call(("xmllint", "--recover", fname),
                           stdout=out, stderr=err, close_fds=False) != 0:
            # Handle files so broken even xmllint --recover cant handle them.
            return err
            # err.seek(0)
            # for line in err:
            #     print

    out.seek(0)
    return out


def fast_iter(context, func):
    for event, elem in context:
        func(elem)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context


def printer(element):
    print element

def wxr_open(fname):
    f = preprocess_wxr_file(fname)
    context = etree.iterparse(f, events=('end',), tag='item')

    fast_iter(context, printer)

if __name__ == "__main__":
    import sys
    wxr_open(sys.argv[1])

