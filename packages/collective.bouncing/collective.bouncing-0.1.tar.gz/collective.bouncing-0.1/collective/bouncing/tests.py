from zope import interface
from zope import component

from zope.testing import doctest

import unittest

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase import ptc

from Products.Five import zcml
from Products.Five import fiveconfigure

import collective.bouncing

OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE

ptc.setupPloneSite(products=['CMFPlacefulWorkflow'])
ptc.setupPloneSite(extension_profiles=['collective.bouncing:default'])

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.bouncing)
            fiveconfigure.debug_mode = False
	
        @classmethod
        def tearDown(cls):
            pass

def setup_error_log(site):
    site.error_log._ignored_exceptions = ()
    def print_error(index=0):
        logs = site.error_log.getLogEntries()
        if logs:
            print logs[index]['tb_text']
    return print_error

def test_suite():
    globs = dict(interface=interface, component=component)
    
    return ztc.FunctionalDocFileSuite(
        'README.txt',
        globs=globs,
        optionflags=OPTIONFLAGS,
        test_class=TestCase)
