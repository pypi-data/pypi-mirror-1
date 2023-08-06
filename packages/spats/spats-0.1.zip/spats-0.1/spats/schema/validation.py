
class ValidationError(Exception):
    """ Validation Error """

def isInteger(value):
    try:
        if value != "False" and value:
            int(value)
    except ValueError:
        raise ValidationError('This field requires an integer')

def isFloat(value):
    try:
        if value != "False" and value:
            float(value)
    except ValueError:
        raise ValidationError('This field requires a float')

_registry = dict()

def registerValidator(id, callback):
    assert callable(callback), 'callback must be callable'
    _registry[id] = callback


def getValidator(id):
    v = _registry.get(id, None)
    assert v is not None, 'validator %s not found' % id
    return v

registerValidator('integer', isInteger)
registerValidator('float', isFloat)
