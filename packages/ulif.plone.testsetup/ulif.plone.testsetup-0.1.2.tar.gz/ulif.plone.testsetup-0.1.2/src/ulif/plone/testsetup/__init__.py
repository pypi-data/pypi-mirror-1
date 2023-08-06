from plonetesting import PloneTestCollector
from plonetesting import SimplePloneTestCase, SimpleFunctionalPloneTestCase

def register_all_plone_tests(*args, **kw):
    return PloneTestCollector(*args, **kw)

def initialize(context):
    """Initialization if used as a Zope 2 product.
    """
    pass

