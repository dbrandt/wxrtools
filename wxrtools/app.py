from .wxr import fast_iter, wxr_context
from .reader import wxr_open

def printer(element):
    print element

def printer_app(fname):
    with open(fname) as f:
        context = wxr_context(f)
        fast_iter(context, printer)

