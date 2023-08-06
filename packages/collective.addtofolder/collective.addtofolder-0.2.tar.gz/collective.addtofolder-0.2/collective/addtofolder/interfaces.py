from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.addtofolder')

class IAddMenuConfiguration(Interface):
  """This interface defines the configlet.
  """
  allowAddToParent = schema.Bool(
                                title=_(u"Allow users to add items to the "
                                        "parent folder of a document?"),
                                description=_(u"Check this to allow users to add items to a document's "
                                              "parent folder, without having to leave the document. "
                                              "This used to be the default-behaviour in Plone 2.5."),
                                required=True
                                )

