from lxml import etree

def wxr_context(f_obj):
    return etree.iterparse(f_obj, events=('end',), tag='item')

def fast_iter(context, func):
    # See http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    # for more on this. This module will be subjected to huge files
    # and can't risk filling up RAM.
    for event, elem in context:
        func(elem)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context


