from base_groupmanager import BaseGroupManagerTestCase
from collective.contentgroup.groupmanager import PortalGroupsGroupManager
import base
import unittest
        
class PortalGroupsGroupManagerTestCase(BaseGroupManagerTestCase):
    
    def create_group_manager(self):
        return PortalGroupsGroupManager()    
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PortalGroupsGroupManagerTestCase))
    return suite
