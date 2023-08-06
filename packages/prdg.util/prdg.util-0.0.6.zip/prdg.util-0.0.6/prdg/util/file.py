from tempfile import gettempdir, gettempprefix
from datetime import datetime
from os.path import join, splitext, dirname
from os import remove, access, F_OK, chdir

def exists(path):
    return access(path, F_OK)

def get_temp_filename():
    return join(gettempdir(), gettempprefix() + str(datetime.now().microsecond)) 

def process_str_as_file_both(s, process_file, *args, **kwargs):
    """
    Suppose you have a function called `process_file()` that operates on a file
    on the filesystem. But, you have an string `s`, and you want to apply 
    `process_file()` on `s`. This function makes it possible. It creates a 
    temporary file and calls, writes `s` to it and then call `process_file()`.
    
    Arguments:
    s -- An string.
    process_file -- A callable that takes as the first argument a filesystem
        path.
    *args, **kwargs -- Additional arguments to pass to process_file.
    
    Return: a 2-tuple. The first value is the value returned by 
    `process_file`. The second value is the content of the processed file,
    after processing.
    """    
    filename = get_temp_filename()
    str_to_file(s, filename)
        
    return_value = process_file(filename, *args, **kwargs)
    f = open(filename, 'rb')
    file_contents = f.read()
    f.close()
    remove(filename)    
    
    return (return_value, file_contents)  

def process_str_as_file_out(s, process_file, *args, **kwargs):
    return process_str_as_file_both(s, process_file, *args, **kwargs)[0]


def process_str_as_file(s, process_file, *args, **kwargs):
    return process_str_as_file_both(s, process_file, *args, **kwargs)[1]

def str_to_file(s, path, do_not_overwrite=True):
    """
    Write `s` to the file in the given `path`, creating it if necessary.
    If `do_not_overwrite` raise an error if the file already exists. Otherwise
    the file will be overwritten.
    """
    if do_not_overwrite and exists(path):
        raise RuntimeError('File "%s" already exists.' % path)
    
    f = open(path, 'w')
    f.write(s)
    f.close()
    
def file_to_str(path):
    """Return: the content of the file pointed by `path`."""
    f = open(path)
    s = f.read()    
    f.close()
    
    return s
    
def get_extension(path):
    """
    Return: the extension of the file pointed by `path` or an empty string. The
        leading dot is not included.
    """
    return splitext(path)[1][1:]
    
def remove_extension(path):
    """
    Return: `path` without the extension of the last component of the path. If
        there's no such extension then `path` is returned without any change.
        The dot is removed together with the extension.
    """
    return splitext(path)[0] 
    
def replace_extension(path, new_extension):
    """
    Return: `path` with the file extension replaced. `new_extension` must NOT
        include a leading dot.
    """
    return splitext(path)[0] + '.' + new_extension
    
def change_to_file_dir(path):
    target_dir = dirname(path)
    if target_dir:
        chdir(target_dir)        
    
