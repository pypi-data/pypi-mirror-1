from zope import interface

from collective.singing.interfaces import IChannel

class IMailingList(IChannel):
    """A mailinglist channel."""

    email = interface.Attribute(
        """List e-mail address.""")

    def subscribe(email):
        """Subscribe address to the list."""

    def unsubscribe(email):
        """Unsubscribe address from the list."""
