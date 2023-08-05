from toscawidgets.api import JSLink, js_function

__all__ = ['prototype_js', 'S']

prototype_js = JSLink(modname=__name__, filename='static/prototype.js')

S = js_function('$')

