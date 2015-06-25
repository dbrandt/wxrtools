from .wxr import fast_iter, wxr_context, WXRObject


def printer(element):
    we = WXRObject(element)
    import pdb; pdb.set_trace()

    print element

def printer_app(fname):
    with open(fname) as f:
        context = wxr_context(f)
        fast_iter(context, printer)

