import re

from Products.validation.interfaces.IValidator import IValidator


class NormativaNumberValidator:
    """A validator for a normativa number.
    """
    __implements__ = IValidator

    def __init__(self,
                 name,
                 title='Normativa Number validator',
                 description='Check that a normativa number is valid'):
        self.name = name
        self.title = title or name
        self.description = description


    def __call__(self, value, *args, **kwargs):
        if isinstance(value, int):
          return 1
        elif not isinstance(value, str):
          return ("Validation failed(%s): value is %s" % (self.name, repr(value)))

        regex = r'^\d{1,}(bis)?$'
        compiled_re = re.compile(regex)

        m = compiled_re.match(value)
        if m is None:
            return ("Validation failed(%s): %s is not a valid normativa number" % (self.name, repr(value)))

        return 1
