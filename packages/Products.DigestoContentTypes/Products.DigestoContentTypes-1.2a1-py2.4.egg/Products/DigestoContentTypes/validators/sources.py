import re
from Products.validation.interfaces.IValidator import IValidator


class AreaSourceValidator:
    """A validator for a sources in a 'AT Extensions' record filed.
    """
    __implements__ = IValidator

    def __init__(self,
                 name,
                 title='Source validator',
                 description='Check the source item'):
        self.name = name
        self.title = title or name
        self.description = description


    def __call__(self, value, *args, **kwargs):
        if isinstance(value, str):
            source = value
        else:
          return ("Validation failed(%s): value is %s" % (self.name, repr(value)))

        if re.match(r'[\w ]+', source, re.UNICODE) is None:
            return ("Validation failed(%s): %s is not a valid source name" % (self.name, repr(source)))

        return 1


class AreaKindsValidator:
    """A validator for a kind in a 'AT Extensions' record filed.
    """
    __implements__ = IValidator

    def __init__(self,
                 name,
                 title='Kind validator',
                 description='Check the Kind item is not an empty list'):
        self.name = name
        self.title = title or name
        self.description = description


    def __call__(self, value, *args, **kwargs):

        if not isinstance(value, list):
            return ("Validation failed(%s): value is %s" % (self.name, repr(    value)))
        elif len(value) <= 0:
            return ("Validation failed(%s): kinds list is empty" % self.name)

        return 1
