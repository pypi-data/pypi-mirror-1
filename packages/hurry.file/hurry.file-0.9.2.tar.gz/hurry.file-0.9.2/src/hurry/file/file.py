from StringIO import StringIO
from persistent import Persistent
from zope.interface import implements
from hurry.file import interfaces

class HurryFile(Persistent):
    implements(interfaces.IHurryFile)
    
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data
        self.headers = {}
        
    def _get_file(self):
        return StringIO(self.data)

    file = property(_get_file)

    def __eq__(self, other):
        try:
            return (self.filename == other.filename and
                    self.data == other.data)
        except AttributeError:
            return False
        
    def __neq__(self, other):
        try:
            return (self.filename != other.filename or
                    self.data != other.data)
        except AttributeError:
            return True

