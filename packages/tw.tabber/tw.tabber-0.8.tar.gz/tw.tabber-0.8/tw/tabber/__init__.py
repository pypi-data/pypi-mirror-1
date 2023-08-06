from tw.api import JSLink, JSSource, CSSLink, js_function, Widget, Link

_manual_startup = JSSource("""var tabberOptions = {"manualStartup": true};""")

tabberAutomatic = js_function('tabberAutomatic')

css = CSSLink(
    modname = __name__,
    filename = 'static/tabber.css',
    )

packed = JSLink(
    modname = __name__,
    filename = 'static/tabber-minimized.js',
    javascript = [_manual_startup],
    css = [css],
    )

tabber = JSLink(
    modname = __name__,
    filename = 'static/tabber.js',
    javascript = [_manual_startup],
    css = [css],
    )

cookie = JSLink(
    modname = __name__,
    filename = 'static/tabber_cookie.js',
    )

class Tabber(Widget):
    javascript = [tabber]
    params = ["options"]
    options = {}

    def __init__(self, *args, **kw):
        super(Tabber, self).__init__(*args, **kw)
        self.add_call(tabberAutomatic(self.options))

__all__ = ['tabberAutomatic', 'Tabber']

for name, value in locals().items():
    if isinstance(value, Link) and not name.startswith('_'):
        __all__.append(name)
