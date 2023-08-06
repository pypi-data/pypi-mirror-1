from Products.PortalTransforms.libtransforms.utils import MissingBinary
modules = [
    'html_to_embed',
    ]

g = globals()
transforms = []
for m in modules:
    try:
        ns = __import__(m, g, g, None)
        transforms.append(ns.register())
    except ImportError, e:
        print "Problem importing module %s : %s" % (m, e)
    except MissingBinary, e:
        print e
    except:
        import traceback
        traceback.print_exc()

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    pass
    #for transform in transforms:
    #
    #     context.registerTransform(transform)

