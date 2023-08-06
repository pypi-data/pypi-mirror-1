"""
MochiKit 1.4 widget for ToscaWidgets

To download and install::

  easy_install twMochiKit

"""

from tw.api import JSLink, js_function

__all__ = [
    "mochikit",
    "packed",
    "base",
    "iter",
    "async",
    "dom",
    "signal",
    "datetime",
    "format",
    "style",
    ]

base = JSLink(
    modname = __name__, 
    filename = 'static/Base.js',
    )

datetime = JSLink(
    modname = __name__, 
    filename = 'static/DateTime.js',
    )

format = JSLink(
    modname = __name__, 
    filename = 'static/Format.js',
    )

async = JSLink(
    modname = __name__, 
    filename = 'static/Async.js',
    javascript = [base]
    )

iter = JSLink(
    modname = __name__, 
    filename = 'static/Iter.js',
    javascript = [base]
    )

dom = JSLink(
    modname = __name__, 
    filename = 'static/DOM.js',
    javascript = [base]
    )

signal = JSLink(
    modname = __name__, 
    filename = 'static/Signal.js',
    javascript = [base, dom]
    )

style = JSLink(
    modname = __name__, 
    filename = 'static/Style.js',
    javascript = [base, dom]
    )


packed = JSLink(
    modname = __name__, 
    filename = 'static/packed/MochiKit.js',
    )

mochikit = JSLink(
    modname = __name__, 
    filename = 'static/MochiKit.js',
    )

connect = js_function('MochiKit.Signal.connect')
