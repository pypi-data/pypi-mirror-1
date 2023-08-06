"""Setup the environment for tests."""
from Products.PloneTestCase import PloneTestCase as ptc

BaseTestCase = ptc.PloneTestCase

ptc.setupPloneSite()
