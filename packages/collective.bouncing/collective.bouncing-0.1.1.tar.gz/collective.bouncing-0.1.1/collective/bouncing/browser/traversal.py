from zope import interface
from zope import component

from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.http import IHTTPRequest

from Products.CMFPlone.interfaces import IPloneSiteRoot

from collective.singing.channel import channel_lookup
from collective.dancing.channel import IChannelContainer

class MailingListNamespace(object):
    interface.implements(ITraversable)
    component.adapts(IChannelContainer, IHTTPRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        for channel in channel_lookup():
            if channel.name == name:
                return channel
            
        raise ValueError("Channel not found: %s" % name)
