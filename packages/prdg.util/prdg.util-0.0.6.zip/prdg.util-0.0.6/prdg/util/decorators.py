def collect_result(results):
    def decorate(f):
        def new_func(*args, **kwargs):
            result = f(*args, **kwargs)
            results.append(result)
            return result
        
        return new_func
    
    return decorate
    