from zope import interface
from zope import schema

from collective.bouncing import MessageFactory as _

class ISubscribe(interface.Interface):
    email = schema.TextLine(
        title=_(u"E-mail address"),
        required=True)

class ISelection(interface.Interface):
    name = schema.Choice(
        title=_(u"Mailinglist"),
        vocabulary="collective.bouncing.vocabularies.ListVocabulary",
        required=True)

class IMailingListSubscription(interface.Interface):
    """Marker interface that represents a context should should include a
    subscribe form."""
