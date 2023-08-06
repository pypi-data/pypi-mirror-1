import re

from Products.validation.interfaces.IValidator import IValidator


class DossierNumberListValidator:
    """A validator for a tuple of dossier numbers.
    """
    __implements__ = IValidator

    def __init__(self,
                 name,
                 title='Dossier Number list validator',
                 description='Check that every item in a tuple is a valid dossier number'):
        self.name = name
        self.title = title or name
        self.description = description


    def __call__(self, value, *args, **kwargs):

        if isinstance(value, str):
            numbers = (value,)
        elif hasattr(value, '__iter__'):
            numbers = value
        else:
          return ("Validation failed(%s): value is %s" % (self.name, repr(value)))

        dossier_re = re.compile(r'^\d{2}-\d{2}-\d{5}$')
        cudap_re = re.compile(r'^[A-Z]+-[A-Z]{3}:\d{7}/\d{4}$')

        for number in numbers:
            if dossier_re.match(number) is None and cudap_re.match(number) is None:
                return ("Validation failed(%s): %s is not a valid DD-DD-DDDDD dossier number or CUDAP: TypeDoc-server:number/year (A[1..n]-A[3]:D[7]/D[4])" % (self.name, repr(number)))

        return 1
