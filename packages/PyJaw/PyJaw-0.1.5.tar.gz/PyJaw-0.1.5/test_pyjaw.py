import pyjaw.base
from pyjaw import RejawClient
import os
from nose import tools

def mock_urlopen(request):
    """A mock urlopen function
    request should be a urllib2.Request instance"""
    
    # find the test data directory
    test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testdata')
    
    # get the filename we're looking for from the request
    filename = "_".join(request.get_full_url().split("/")[3:])
    
    # ditch any 'get' parameters for now
    # TODO: find a way of using the get/post data to find different files
    filename = filename.split("?")[0]
    
    # return the file object as .read() is used by the API
    return open(os.path.join(test_data_dir, filename))
    
# monkeypatch pyjaw.base.urlopen
pyjaw.base.urlopen = mock_urlopen
    
class TestSession(object):
    
    def setUp(self):
        self.client = pyjaw.RejawClient('ABc1dEf23gH', 'api.rejaw.com')
        resp = self.client.create_session()
        tools.assert_true(resp['succeeded'])
        
    def test_verify(self):
        resp = self.client.verify_session()
        tools.assert_true(resp['succeeded'])
        
    def test_destroy(self):
        resp = self.client.destroy_session()
        tools.assert_true(resp['succeeded'])

    def test_set_guestname(self):
        resp = self.client.set_guestname('pyjawtester')
        tools.assert_true(resp['succeeded'])
        
class TestUser(object):
    
    def setUp(self):
        self.client = pyjaw.RejawClient('ABc1dEf23gH', 'api.rejaw.com')
        self.client.create_session()
        
    def test_get_info(self):
        resp = self.client.get_user_info('pyjawtester')
        tools.assert_true(resp['succeeded'])
        
    def test_get_profile(self):
        resp = self.client.get_profile('pyjawtester')
        tools.assert_true(resp['succeeded'])
        
    def test_set_profile(self):
        resp = self.client.set_profile({'fullname': 'PyJaw Tester'})
        tools.assert_true(resp['succeeded'])
        
    def test_get_inbox(self):
        resp = self.client.get_inbox()
        tools.assert_true(resp['succeeded'])
        
    def test_get_people(self):
        resp = self.client.get_people('followers')
        tools.assert_true(resp['succeeded'])