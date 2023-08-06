from zope.interface import implements
from zope.component import adapts

from hexagonit.swfheader import parse
from hachoir_core.error import HachoirError
from hachoir_parser.guess import guessParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.stream import StringInputStream

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from Products.ATContentTypes.interface import IFileContent
from openc.objectsfromlinks.interfaces import IMetadata

from zope.annotation import IAnnotations

class ATFileToMetadata(object):
    
    adapts(IFileContent)
    implements(IMetadata)
    
    def __init__(self, context):
        anno = IAnnotations(context)
        key = "richmediametadata%s"%(context.schema['modification_date'].get(context).ISO())
        try:
            self.metadata = anno.get(key, parse(StringIO(str(context.getRawFile().aq_base))))
            self.metadata['type'] = ".swf"
        except ValueError: # Not a SWF hexagonit can parse
            self.metadata = {}
        if not self.metadata:
            data = str(context.getRawFile().aq_base)
            stream = StringInputStream(data)
            parser = guessParser(stream)
            metadata = extractMetadata(parser)
            self.metadata['type'] = parser.filename_suffix
            if not self.metadata.has_key('height'):
                self.metadata['height'] = metadata.get("height")
            if not self.metadata.has_key('width'):
                self.metadata['width'] = metadata.get("width")
            if not self.metadata.has_key('version'):
                try:
                    self.metadata['version'] = metadata.get("version")
                except ValueError:
                    self.metadata['version'] = '0'
        anno[key] = self.metadata
        
    @property
    def width(self):
        return self.metadata['width']
            
    @property
    def height(self):
        return self.metadata['height']
    
    @property
    def insertmethod(self):
        return self.metadata['type'][1:]
    
    @property
    def insertversion(self):
        return self.metadata['version']