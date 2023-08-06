from zope.component import getUtility
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from interfaces import IAddMenuConfiguration

from OFS.SimpleItem import SimpleItem

class AddMenuConfiguration(SimpleItem):
    implements(IAddMenuConfiguration)
    allowAddToParent = FieldProperty(IAddMenuConfiguration['allowAddToParent'])

def form_adapter(context):
    return getUtility(IAddMenuConfiguration, name='addmenuconfig', context=context)

