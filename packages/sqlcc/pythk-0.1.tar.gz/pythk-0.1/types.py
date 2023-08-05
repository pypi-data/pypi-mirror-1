
def is_lambda(o):
    return callable(o) and o.__name__ == '<lambda>'

def is_subclass(o, clazzes):
    return isinstance(o, type) and issubclass(o, clazzes)

def is_descriptor(o):
    return hasattr(o, '__get__')
