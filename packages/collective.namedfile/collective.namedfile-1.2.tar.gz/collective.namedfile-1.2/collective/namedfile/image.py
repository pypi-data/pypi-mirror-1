from zope.interface import implements
from file import NamedFile
from interfaces import INamedImage

class NamedImage(NamedFile):
    implements(INamedImage)
