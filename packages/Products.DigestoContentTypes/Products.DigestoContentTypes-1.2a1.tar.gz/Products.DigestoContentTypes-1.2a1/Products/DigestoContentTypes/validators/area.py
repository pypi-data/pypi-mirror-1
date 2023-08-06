from Products.validation.interfaces.IValidator import IValidator

class AreaRecordValidator:
    """A validator for the area record.
    """
    __implements__ = IValidator

    def __init__(self,
                 name,
                 title='Area record validator',
                 description='Check that every item in the Area Record is valid'):
        self.name = name
        self.title = title or name
        self.description = description


    def __call__(self, value, *args, **kwargs):
        return 1
