from lxml import etree


def wxr_parser(f_obj):
    return etree.iterparse(f_obj, events=("start", "end", "start-ns"), recover=True)

def fast_iter(parser):
    # See http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    # for more on this. This module will be subjected to huge files
    # and can't risk filling up RAM.
    for event, element in parser:
        yield event, element
        if event in ("start-ns", "start"):
            continue
        element.clear()
        while element.getprevious() is not None:
            try:
                del element.getparent()[0]
            except TypeError:
                break
    del parser
