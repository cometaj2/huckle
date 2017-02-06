import config
import os
import errno

if not os.path.exists(config.dot_huck):
    os.makedirs(config.dot_huck)

if not os.path.exists(config.dot_bash_profile):
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

    try:
        file_handle = os.open(config.dot_bash_profile, flags)
    except OSError as e:
        if e.errno == errno.EEXIST:  # Failed as the file already exists.
            pass
        else:
            raise
    else:
        with os.fdopen(file_handle, 'w') as file_obj:
            file_obj.write("")
            file_obj.close
