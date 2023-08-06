# Python
import re

# Zope Imports
from zope.app.component.hooks import getSite
from ZODB.POSException import ConflictError

# Portal Transforms etc
from Products.PortalTransforms.interfaces import itransform
from htmlentitydefs import entitydefs
from Products.MimetypesRegistry.interfaces import IClassifier
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
from Products.MimetypesRegistry.common import MimeTypeException

# Internals
from openc.objectsfromlinks.interfaces import IMetadata
from types import InstanceType

# Externals
from BeautifulSoup import BeautifulSoup



class html_with_embeds(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "HTML with extra info on rich media"
    mimetypes  = ('text/html-with-embeds',)
    extensions = ('ebht',)
    binary     = 0


class HtmlToEmbedCodes:
    """Transform which replaces urls and email into hyperlinks"""

    __implements__ = itransform

    __name__ = "html_to_embed"
    output = "text/html-with-embeds"

    def __init__(self, name=None, inputs=('text/html',)):
        self.config = { 'inputs' : inputs }
        self.config_metadata = {
            'inputs' : ('list', 'Inputs', 
                            'Input(s) MIME type. Change with care.'),
            'tab_width' : ('string', 'Tab width', 
                            'Number of spaces for a tab in the input')
            }
        if name:
            self.__name__ = name
        self.trans = re.compile("<a .*?</a>")

    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr in self.config:
            return self.config[attr]
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        text = orig
        objects = self.trans.findall(text)
        try:
            context = getSite().REQUEST.PUBLISHED
        except:
            context = getSite()
        for obj in objects:
            soup = BeautifulSoup(obj)
            if soup.a['href'].startswith(u"http://"):
                continue
            try:
                try:
                    insite = context.unrestrictedTraverse(soup.a['href'].encode("ascii"))
                except ConflictError, EOFError:
                    raise
                except Exception, e:
                    continue
                metadata = IMetadata(insite)
                w, h, m, v = metadata.width, metadata.height, metadata.insertmethod, metadata.insertversion
                #soup.a['href'] = '%s?w=%s&h=%s&method=%s&version=%s' % (soup.a['href'], w, h, m, v)
                klass = soup.a.get('class', None)
                embedclass = u"%s_w%sh%sv%s" % (m, w, h, v)
                if klass:
                    klass += u" %s" % embedclass
                else:
                    klass = embedclass
                soup.a['class'] = klass
                text=text.replace(obj, soup.prettify())
            except ConflictError, EOFError:
                raise
            except Exception, e:
                continue
        data.setData(text)
        return data

def register():
    return HtmlToEmbedCodes()
