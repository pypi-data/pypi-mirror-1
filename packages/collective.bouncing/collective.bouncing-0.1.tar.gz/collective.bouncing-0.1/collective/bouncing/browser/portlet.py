from zope import interface
from zope import component
from zope import schema

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import get_language

from plone.app.portlets.portlets import base
from zope.formlib import form

from Acquisition import aq_inner
from AccessControl import getSecurityManager

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.formlib import formbase
from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

from collective.bouncing import MessageFactory as _
from collective.bouncing.interfaces import IMailingList

from collective.bouncing.browser.interfaces import ISubscribe
from collective.bouncing.browser.interfaces import ISelection
from collective.bouncing.browser.form import SubscribeForm

class IListPortlet(IPortletDataProvider, ISelection):
    pass

class Assignment(base.Assignment):
    interface.implements(IListPortlet)

    def __init__(self, name=u""):
        self.name = name

    @property
    def title(self):
        channel = self.channel
        return u"%s: %s" % (channel.protocol, channel.title)
        
    @property
    def channel(self):
        return component.getUtility(IMailingList, name=self.name)
        
class AddForm(base.AddForm):
    form_fields = form.Fields(IListPortlet)

    label = _(u"Add Mailinglist Portlet")
    description = _(u"This portlet displays a mailinglist subscription form.")

    def create(self, data):
        return Assignment(name=data.get('name'))

class Renderer(base.Renderer):
    template = ViewPageTemplateFile("portlet.pt")

    label = _(u"Subscribe")

    def __init__(self, *args):
        super(Renderer, self).__init__(*args)
        form = SubscribeForm(self.context, self.request)
        self.form = form.__of__(self.context)

    render = template
    
    @property
    def title(self):
        return self.data.title
    
    @property
    def available(self):
        return True
