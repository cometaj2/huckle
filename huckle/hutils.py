from __future__ import absolute_import, division, print_function

import os
import sys
import errno

# creates a folder at "path"
def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

# creates a file at "path"
def create_file(path):
    if not os.path.exists(path):
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

        try:
            file_handle = os.open(path, flags, 0o0600)
        except OSError as e:
            if e.errno == errno.EEXIST:  # Failed since the file already exists.
                pass
            else:
                raise
        else:
            with os.fdopen(file_handle, 'w') as file_obj:
                file_obj.write("")
                file_obj.close

# helps with printing error messages to STDERR
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
