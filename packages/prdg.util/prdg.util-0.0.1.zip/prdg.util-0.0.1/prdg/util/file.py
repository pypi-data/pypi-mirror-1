from tempfile import gettempdir, gettempprefix
from datetime import datetime
from os.path import join, splitext
from os import remove, access, F_OK

def get_temp_filename():
    return join(gettempdir(), gettempprefix() + str(datetime.now().microsecond)) 

def process_str_as_file(s, process_file, *args, **kwargs):
    """
    Suppose you have a function called process_file() that operates on a file on
    the filesystem. But, you have an string s, and you want to apply 
    process_file() on s. This function makes it possible. It creates a temporary
    file and calls, writes s to it and then call process_file().
    
    Arguments:
    s -- An string.
    process_file -- A callable that takes as the first argument a filesystem
        path.
    *args, **kwargs -- Additional arguments to pass to process_file.
    
    Return: the processed string.
    """
    filename = get_temp_filename()
    str_to_file(s, filename)
        
    process_file(filename, *args, **kwargs)
    f = open(filename, 'rb')
    result = f.read()
    f.close()
    remove(filename)    
    
    return result

def str_to_file(s, path, do_not_overwrite=True):
    """
    Write `s` to the file in the given `path`, creating it if necessary.
    If `do_not_overwrite` raise an error if the file already exists. Otherwise
    the file will be overwritten.
    """
    if do_not_overwrite and access(path, F_OK):
        raise RuntimeError('File "%s" already exists.' % path)
    
    f = open(path, 'w')
    f.write(s)
    f.close()
    
def replace_extension(path, new_extension):
    """
    Return: `path` with the file extension replaced. `new_extension` must NOT
        include a leading dot.
    """
    return splitext(path)[0] + '.' + new_extension
    
    