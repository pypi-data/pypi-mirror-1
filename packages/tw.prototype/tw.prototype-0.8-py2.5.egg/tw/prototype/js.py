from tw.api import JSLink, js_function

__all__ = ['prototype_js', 'S', 'Event']

prototype_js = JSLink(modname=__name__, filename='static/prototype.js')

S = js_function('$')

class Event:
    observe = js_function('Event.observe')

