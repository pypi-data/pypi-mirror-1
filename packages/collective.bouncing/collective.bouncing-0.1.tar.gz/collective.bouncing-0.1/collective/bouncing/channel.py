from zope import interface
from zope import component

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.sendmail.interfaces import IMailDelivery
from zope.annotation.interfaces import IAnnotations
import zope.app.component.hooks

import Products.CMFPlone.interfaces

from collective.singing.subscribe import SimpleSubscription, Subscriptions
from collective.singing.interfaces import IChannelLookup
from collective.singing.message import MessageQueues

from collective.bouncing import MessageFactory as _
from collective.dancing.utils import fix_request

from persistent.dict import PersistentDict

from interfaces import IMailingList

from Acquisition import Implicit

def annotation(name):
    def get(self):
        return self.annotations.get("%s:%s" % (
            self.name, name), getattr(self.__class__, name, None))
    def set(self, value):
        self.annotations["%s:%s" % (self.name, name)] = value
    return property(get, set)

class BaseList(Implicit):
    """Base mailinglist.

    Uses annotations to store additional subscriptions (for
    administration use) and channel data.
    """
    
    interface.implements(IMailingList)

    protocol = None
    subscriptions = {}

    title = annotation('title')
    description = annotation('description')
    
    @property
    def queue(self):
        return self.annotations.setdefault(
            '%s:queue' % self.name, MessageQueues())

    def _get_collector(self):
        return self.annotations.get('%s:collector' % self.name)
    
    def _set_collector(self, collector):
        self.annotations['%s:collector' % self.name] = collector

    collector = property(_get_collector, _set_collector)

    def _get_scheduler(self):
        return self.annotations.get('%s:scheduler' % self.name)

    def _set_scheduler(self, scheduler):
        self.annotations['%s:scheduler' % self.name] = scheduler

    scheduler = property(_get_scheduler, _set_scheduler)

    @property
    def annotations(self):
        return IAnnotations(self.portal).setdefault(
            'collective.bouncing', PersistentDict())
    
    @property
    def portal(self):
        root = component.queryUtility(Products.CMFPlone.interfaces.IPloneSiteRoot)
        return fix_request(root, 0)

    @property
    def email(self):
        raise NotImplementedError(
            "You must subclass and provide an ``email``-attribute.")

    def getPhysicalPath(self):
        return self.portal.restrictedTraverse('portal_newsletters/channels').\
               getPhysicalPath()+('++mailinglists++'+self.name,)

    def absolute_url(self):
        return self.portal.REQUEST.physicalPathToURL(self.getPhysicalPath())

class ListLookup(object):
    interface.implements(IChannelLookup)

    def __call__(self):
        mlists = component.getAllUtilitiesRegisteredFor(IMailingList)
        site = zope.app.component.hooks.getSite()
        if site is None:
            return []
        container = zope.app.component.hooks.getSite().\
               restrictedTraverse('portal_newsletters/channels')
        return [ml.__of__(container) for ml in mlists]

class ListVocabulary(object):
    interface.implements(IVocabularyFactory)

    lookup = ListLookup()
    
    def __call__(self, context):
        channels = self.lookup()
        items = [SimpleTerm(channel.email, channel.email, channel.title) \
                     for channel in channels]
        
        return SimpleVocabulary(items)

ListVocabulary = ListVocabulary()
