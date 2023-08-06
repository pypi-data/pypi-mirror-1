collective.bouncing
===================

Let's add English as a supported language and set it as default.

  >>> from Products.CMFCore.utils import getToolByName
  >>> ltool = getToolByName(portal, 'portal_languages')
  >>> ltool.addSupportedLanguage('en')
  >>> ltool.setDefaultLanguage('en')

Set up a test-browser:
  
  >>> from collective.bouncing.tests import setup_error_log
  >>> print_errors = setup_error_log(self.portal)
  
  >>> from Products.Five.testbrowser import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

Channels
--------

Mailinglists are registered as utilities providing ``IMailingList``. A
base class is provided for convenience.

Let's set up a list:

  >>> from collective.bouncing.channel import BaseList
  >>> from collective.bouncing.interfaces import IMailingList
  
  >>> class MyList(BaseList):
  ...     name = email = 'name@host'
  ...     protocol = 'Dummy'
  ...
  ...     title = u'My mailinglist'
  ...
  ...     def subscribe(self, email):
  ...         print "@mock: Subscribing %s" % email
  ...
  ...     def unsubscribe(self, email):
  ...         print "@mock: Unsubscribing %s" % email
  
We'll instantiate and provide this channel as a utility. It's expected
that the utility is registered with the list email address as name.

  >>> list = MyList()
  >>> component.provideUtility(list, IMailingList, name='name@host')

We can list the available channels:

  >>> from collective.bouncing.channel import ListLookup

  >>> lookup = ListLookup()
  >>> lookup() # doctest: +ELLIPSIS
  [...<MyList object at ...>]

A vocabulary is also provided:

  >>> from zope.app.schema.vocabulary import IVocabularyFactory
  >>> factory = component.getUtility(
  ...     IVocabularyFactory,
  ...     name="collective.bouncing.vocabularies.ListVocabulary")

  >>> 'name@host' in [term.value for term in factory(None)]
  True

Collector
---------

We can assign a collector.

  >>> from collective.dancing.collector import Collector

  >>> collector = Collector("test", u"Test")
  >>> list.collector = collector
  
Portlet
-------

A portlet is provided that allows users to subscribe/unsubscribe to a list.

Let's first add the portlet programmatically. We'll get a hold of the
portlet manager for the left column in the portal.

  >>> from plone.portlets.interfaces import IPortletManager
  >>> manager = component.getUtility(
  ...     IPortletManager, name=u'plone.leftcolumn', context=portal)

  >>> from plone.portlets.interfaces import IPortletAssignmentMapping
  >>> mapping = component.getMultiAdapter(
  ...     (portal, manager), IPortletAssignmentMapping, context=portal)

  >>> from collective.bouncing.browser.portlet import Assignment
  >>> assignment = mapping[u'mylist'] = Assignment('name@host')

Verify that our assignment is able to lookup the channel.

  >>> assignment.channel # doctest: +ELLIPSIS
  <MyList object at ...>

Let's try and add it using the add form. First we log in as the portal
owner.

  >>> from Products.PloneTestCase.setup import portal_owner, default_password

  >>> browser.open('http://nohost/plone/login_form')
  >>> browser.getControl(name='__ac_name').value = portal_owner
  >>> browser.getControl(name='__ac_password').value = default_password
  >>> browser.getControl(name='submit').click()
  
Then add a portlet to the right portlet manager. We browse directly to
the add-form.

  >>> browser.open(
  ...    'http://nohost/plone/++contextportlets++plone.rightcolumn/+/portlets.Mailinglist') 

Choose the list and save.

  >>> browser.getForm(id='zc.page.browser_form')\
  ...        .getControl(name='form.name').value = ('name@host',)
  >>> browser.getControl(u'Save').click()

Let's look at the right portlet column mapping. We expect our
assignment to be there.

  >>> manager = component.getUtility(
  ...     IPortletManager, name=u'plone.rightcolumn', context=portal)
  >>> mapping = component.getMultiAdapter(
  ...     (portal, manager), IPortletAssignmentMapping, context=portal)
  >>> 'dummy-my-mailinglist' in mapping.keys()
  True
  
Now we can load up the front page and verify that our portlet is being
rendered.

  >>> browser.open('http://nohost/plone')
  >>> 'portletMailinglist' in browser.contents
  True
  
We should be able to enter an e-mail address and hit subscribe.

  >>> input = browser.getControl(name='mailinglist.dummy-my-mailinglist.email')
  >>> input.value = 'dummy@host'
  >>> submit = browser.getControl(name='mailinglist.dummy-my-mailinglist.actions.subscribe')
  >>> submit.click()
  @mock: Subscribing dummy@host
  
Cleanup
-------

  >>> for i in range(10):
  ...     try: print_errors(i)
  ...     except: break
