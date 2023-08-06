from zope.interface import implements
from zope.app.file.file import File
from interfaces import INamedFile

class NamedFile(File):
    implements(INamedFile)

    def __init__(self, data='', contentType='', filename=None):
        File.__init__(self, data, contentType)
        self.filename=filename
