from Products.CMFCore.utils import getToolByName

from openc.objectsfromlinks.html_to_embed import html_with_embeds

from StringIO import StringIO
from types import InstanceType

def registerTransform(self, out, name, module):
    transforms = getToolByName(self, 'portal_transforms')
    transforms.manage_addTransform(name, module)
    print >> out, "Registered transform", name

def unregisterTransform(self, out, name):
    transforms = getToolByName(self, 'portal_transforms')
    try:
        transforms.unregisterTransform(name)
        print >> out, "Removed transform", name
    except AttributeError:
        print >> out, "Could not remove transform", name, "(not found)"

def registerMimeType(self, out, mimetype):
    if type(mimetype) != InstanceType:
        mimetype = mimetype()
    mimetypes_registry = getToolByName(self, 'mimetypes_registry')
    mimetypes_registry.register(mimetype)
    print >> out, "Registered mimetype", mimetype

def unregisterMimeType(self, out, mimetype):
    if type(mimetype) != InstanceType:
        mimetype = mimetype()
    mimetypes_registry = getToolByName(self, 'mimetypes_registry')
    mimetypes_registry.unregister(mimetype)
    print >> out, "Unregistered mimetype", mimetype

def install(self):

    out = StringIO()

    print >> out, "Installing text/web-intelligent mimetype and transform"
    
    registerMimeType(self, out, html_with_embeds)
    registerTransform(self, out, 'html_to_embed', 'openc.objectsfromlinks.html_to_embed')
    shtml = self.portal_transforms.safe_html
    params = dict([(a, shtml.get_parameter_value(a)) for a in shtml.get_parameters()])
    params['inputs'] = list(html_with_embeds.mimetypes)
    for k in list(params):
        if isinstance(params[k], dict):
            v = params[k]
            params[k+'_key'] = v.keys()
            params[k+'_value'] = [str(s) for s in v.values()]
            del params[k]
    self.portal_transforms.safe_html.set_parameters(**params)
    self.portal_transforms.safe_html._p_changed = True
    return out.getvalue()

def uninstall(self):

    out = StringIO()
    self.portal_transforms.safe_html.set_parameters(inputs=['text/html'])
    unregisterTransform(self, out, 'html_to_embed')
    unregisterMimeType(self, out, html_with_embeds)

    return out.getvalue()
