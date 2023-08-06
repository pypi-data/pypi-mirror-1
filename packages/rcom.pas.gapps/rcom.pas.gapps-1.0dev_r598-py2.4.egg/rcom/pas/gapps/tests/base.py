import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from rcom.pas.gapps.config import *

ptc.setupPloneSite()

import rcom.pas.gapps

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             rcom.pas.gapps)
            fiveconfigure.debug_mode = False
            # XXX monkey patch everytime (until we figure out the problem where
            #   monkeypatch gets overwritten somewhere)
            try:
                from Products.Five import pythonproducts
                pythonproducts.setupPythonProducts(None)
                ztc.installProduct(PROJECTNAME)
            except ImportError:
                # Not needed in Plone 3
                ztc.installPackage(PROJECTNAME)

        @classmethod
        def tearDown(cls):
            pass
