import re
import sys
import ttk
from codecs import BOM_UTF8, lookup
Tkinter = ttk.Tkinter

# Compatibility between Python 3.x and 2.x.
if sys.version_info[0] == 2:
    _source = open(__file__)
    # Code mostly taken from tokenize.detect_encoding
    _bom_found = False
    _cookie_re = re.compile("coding[:=]\s*([-\w.]+)")
    def _find_cookie(line):
        try:
            line_string = line.decode('ascii')
        except UnicodeDecodeError:
            return None

        matches = _cookie_re.findall(line_string)
        if not matches:
            return None
        encoding = matches[0]
        try:
            codec = lookup(encoding)
        except LookupError:
            # This behaviour mimics the Python interpreter
            raise SyntaxError("unknown encoding: " + encoding)

        if _bom_found and codec.name != 'utf-8':
            # This behaviour mimics the Python interpreter
            raise SyntaxError('encoding problem: utf-8')
        return encoding

    _first = _source.next()
    if _first.startswith(BOM_UTF8):
        _bom_found = True
        _first = _first[3:]

    _encoding = _find_cookie(_first)
    if _encoding:
        _source_enc = _encoding
    else:
        _second = _source.next()
        _encoding = _find_cookie(_second)
        _source_enc = _encoding if _encoding else 'utf-8'
    _source.close()

    text = lambda s: unicode(s, _source_enc)
    if sys.version_info[1] < 6:
        maxsize = sys.maxint
    else:
        maxsize = sys.maxsize
    import test.test_support as test_support
else:
    text = str
    maxsize = sys.maxsize
    from test import support as test_support
requires = test_support.requires
run_unittest = test_support.run_unittest

def get_tk_root():
    try:
        root = Tkinter._default_root
    except AttributeError:
        # it is possible to disable default root in Tkinter, although
        # I haven't seen people doing it (but apparently someone did it
        # here).
        root = None

    if root is None:
        # create a new master only if there isn't one already
        root = Tkinter.Tk()

    return root


def simulate_mouse_click(widget, x, y):
    """Generate proper events to click at the x, y position (tries to act
    like an X server)."""
    widget.event_generate('<Enter>', x=0, y=0)
    widget.event_generate('<Motion>', x=x, y=y)
    widget.event_generate('<ButtonPress-1>', x=x, y=y)
    widget.event_generate('<ButtonRelease-1>', x=x, y=y)
