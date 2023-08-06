from base import BaseTestCase

class BaseGroupManagerTestCase(BaseTestCase):
    
    def create_group_manager(self):
        pass

    def test_exercise(self):
        gm = self.create_group_manager()
        
        g1 = gm.create_group('g1')
        self.failUnless(gm.group_exists('g1'))        
        gm.set_group_title('g1', 'Title G1')
        self.failUnlessEqual('Title G1', gm.get_group_title('g1'))
        gm.remove_group('g1')
        self.failIf(gm.group_exists('g1'))