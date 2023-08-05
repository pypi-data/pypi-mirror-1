class CannotResolve(Exception):
    pass

class Collect(Exception):
    pass

def all(sequence):
    for element in sequence:
        if not element:
            return False
    return True

def any(sequence):
    for element in sequence:
        if element:
            return True
    return False
