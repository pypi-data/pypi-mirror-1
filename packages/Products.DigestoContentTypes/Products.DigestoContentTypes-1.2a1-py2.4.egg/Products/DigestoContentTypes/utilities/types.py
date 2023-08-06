from persistent import Persistent
from zope.interface import implements
from interfaces import INormativaTypes

class NormativaTypes(Persistent):
    implements(INormativaTypes)
    types = []

    def get_types(self):
        return [a.encode('utf-8') for a in self.types]

