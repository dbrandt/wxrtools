from lxml import etree

class WXRObject(object):
    # Base functionality, like unravelling element into members
    # named after tags.
    def __init__(self, start_elem):
        for e in start_elem.iterchildren():
            if e.text and e.text.strip():
                setattr(self, e.tag, e.text)
            else:
                setattr(self, e.tag, WXRObject(e))

class WXRAuthor(WXRObject):
    # User data such as names and email addesses.
    pass

class WXRBlog(WXRObject):
    # Blog information; URLs, names, descriptions, categories, tags...
    pass

class WXREntry(WXRObject):
    # Entry and meta data + links to image attachments.
    pass

class WXRAttachment(WXRObject):
    # Entry and meta data + links to image attachments.
    pass

class WXRComment(WXRObject):
    # Comment info and spam checks.
    pass

def wxr_context(f_obj):
    return etree.iterparse(f_obj, events=('end',), tag='item', recover=True)

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


