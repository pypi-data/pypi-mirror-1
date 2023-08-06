"""
Conventions:
- paths are tuples of strings.
"""

def relativize(base_path, full_path):
    """
    Arguments:
    base_path, full_path -- Tuples representing paths.
    
    Return: full_path relative to base_path.
    """
    return full_path[len(base_path):]

def change_base(old_base_path, new_base_path, full_path):
    return new_base_path + relativize(old_base_path, full_path)

def join(*paths):
    if not paths:
        return tuple()
    
    joined = list(strip_end(paths[0]))
    
    for p in paths[1:]:
        joined.extend(strip_begin(p))
    
    return tuple(joined)
    
def strip(path):
    return strip_begin(strip_end(path)) 
    
def strip_begin(path):
    len_path = len(path)    
    first_non_empty = len_path - 1
    for i in xrange(len_path):
        if path[i]:
            first_non_empty = i
            break
    
    return path[first_non_empty:]

def strip_end(path):
    last_non_empty = len(path) - 1
    for i in xrange(last_non_empty, -1, -1):
        if path[i]:
            last_non_empty = i
            break
    
    return path[:last_non_empty + 1]

def contains(base, path):
    return path[:len(base)] == base
