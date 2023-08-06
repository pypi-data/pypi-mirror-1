import inspect

def callable_fixer(app, what, name, obj, options, signature, return_annotation):
    if what == 'attribute':
        print name
    if what == 'function' and signature is None and hasattr(obj, '__call__'):
        spec = inspect.getargspec(obj.__call__)
        spec[0].pop(0)
        signature = inspect.formatargspec(*spec)
    return (signature, return_annotation)

def setup(app):
    app.connect('autodoc-process-signature', callable_fixer)
