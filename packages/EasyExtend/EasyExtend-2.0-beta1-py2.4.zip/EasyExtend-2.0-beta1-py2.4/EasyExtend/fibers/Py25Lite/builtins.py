def all(iterable):
    '''
    all(iterable) -> bool

    Return True if bool(x) is True for all values x in the iterable.
    '''
    for element in iterable:
        if not element:
            return False
    return True

def any(iterable):
    '''
    any(iterable) -> bool

    Return True if bool(x) is True for any x in the iterable.
    '''
    for element in iterable:
        if element:
            return True
    return False
