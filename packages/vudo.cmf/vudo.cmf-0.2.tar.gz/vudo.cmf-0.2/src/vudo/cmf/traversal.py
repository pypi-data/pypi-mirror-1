from zope import component
from repoze.bfg import traversal

import interfaces

_marker = object()

def step(ob, name, default):
    if name.startswith('@@'):
        return name[2:], default
    if name.startswith('++') and name.endswith('++'):
        name = name[2:-2]
        return name, getattr(ob, name)
    if not hasattr(ob, '__getitem__'):
        return name, default
    try:
        return name, ob[name]
    except KeyError:
        return name, default

class PageTraversal(traversal.ModelGraphTraverser):
    """This traverser extends the default model graph traverser with a
    handler to support `++` namespace segments."""
    
    component.adapts(interfaces.IPage)

    def __call__(self, environ):
        path = environ.get('PATH_INFO', '/')
        path = traversal.split_path(path)
        root = self.root

        ob = self.root
        name = ''

        while path:
            segment = path.pop(0)
            segment, next = step(ob, segment, _marker)
            if next is _marker:
                name = segment
                break
            if self.locatable:
                next = traversal.locate(next, ob, segment)
            ob = next

        return ob, name, path

