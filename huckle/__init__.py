# This code uses the __getattr__ magic method to dynamically import cli and stdin only
# when they are accessed. Importing them directly at the top of __init__.py interfere with
# the dependencies installation when huckle is installed via pip.
__all__ = ['cli', 'stdin']

def __getattr__(name):
    if name in __all__:
        from .huckle import cli, stdin
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
