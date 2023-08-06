from zope import interface
from zope import component

from zope.formlib import form
from zope.i18n import translate

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.formlib import formbase

from collective.bouncing import MessageFactory as _
from collective.bouncing.browser.interfaces import ISubscribe
from collective.bouncing.browser.interfaces import ISelection
from collective.bouncing.interfaces import IMailingList

def subscribe(channel, request, email):
    channel.subscribe(email)    

def unsubscribe(channel, request, email):
    channel.unsubscribe(email)    

class SubscribeForm(formbase.PageForm):
    template = ViewPageTemplateFile("form.pt")
    form_fields = form.Fields(ISubscribe)

    @property
    def description(self):
        return self.context.data.channel.title

    @property
    def prefix(self):
        return 'mailinglist.%s' % self.context.data.__name__
    
    @form.action(_(u"Subscribe"))
    def handle_subscribe(self, action, data):
        email = data['email']
        subscribe(self.context.data.channel, self.request, email)

class ViewletSubscribeForm(formbase.PageForm):
    template = ViewPageTemplateFile("form.pt")
    form_fields = form.Fields(ISelection, ISubscribe)

    description = None
    prefix = 'mailinglist.viewlet'
    status = None
    
    @form.action(_(u"Subscribe"))
    def handle_subscribe(self, action, data):
        email = data['email']
        name = data['name']
        channel = component.getUtility(IMailingList, name=name)        
        subscribe(channel, self.request, email)        
        self.status = translate(
            _(u"A request to subscribe was sent to ${email}.", mapping={'email': email}))

    @form.action(_(u"Unsubscribe"))
    def handle_unsubscribe(self, action, data):
        email = data['email']
        name = data['name']
        channel = component.getUtility(IMailingList, name=name)        
        unsubscribe(channel, self.request, email)        
        self.status = translate(
            _(u"A request to unsubscribe was sent to ${email}.", mapping={'email': email}))

class SubscribeViewlet(object):
    def render(self):
        context = self.context.aq_inner
        form = ViewletSubscribeForm(context, self.request).__of__(context)
        return form()
