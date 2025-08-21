# This code uses the __getattr__ magic method to dynamically import cli and stdin only
# when they are accessed. Importing them directly at the top of __init__.py interfere with
# the dependencies installation when huckle is installed via pip.
#
# If developing using pip editable installs on huckle and/or code referencing huckle
# as a library, an accidental working directory subfolder named huckle, anywhere you happen
# to be when executing related code, may prevent huckle from being imported properly as a library.
# This is a known side effect of PEP660 and import overshadowing on pip editable installs.
# This can be mitigated by ensuring no such subfolder exists where you are working, and may be by changing
# editable installs to # compability mode (e.g. pip install -e . --config-settings editable_mode=compat).
#
# See https://github.com/pypa/setuptools/issues/3548.

__all__ = ['cli', 'stdin']

def __getattr__(name):
    if name in __all__:
        from .huckle import cli, stdin
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
