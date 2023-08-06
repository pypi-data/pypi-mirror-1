from pyjaw.exc import RejawError, SessionRequired, SessionActive
import simplejson
from urllib2 import urlopen, Request
from urllib import urlencode
from random import randint

API_VERSION = 'v1'

class RejawClient(object):
    """This is a port of the Rejaw API client at:
        http://code.google.com/p/rejaw/source/browse/trunk/api/ruby/api_client.rb
    """
    
    def __init__(self, api_key, verbosity=0, hostname='localhost:3000'):
        self.api_key = api_key
        self.verbosity = verbosity
        self.host = hostname
        self.timeout = 120
        
        self.session = None
        
    def create_session(self):
        """Create a new API session"""
        if self.session:
            raise SessionActive("A session is already active")
            
        result = self._post('session/create', {'api_key': self.api_key}, False)
        if result['succeeded']:
            self.session = result['response']['session']
        return result
        
    def verify_session(self, session_id=None):
        """Verify a session id.  If no session id is passed, verifies the
        current session id for this RejawClient instance"""
        return self._get('session/verify', {'session': session_id or self.session}, False)
        
    def destroy_session(self):
        """Destroy the current API session"""
        result = self._post('session/destroy', {'session': self.session}, False)
        self.session = None
        return result
        
    def signin(self, user, password):
        """Authenticate a user within the current API session"""
        return self._post('auth/signin', {'user': user, 'password': password})
        
    def signout(self):
        """Log out the currently-authenticated user in the session, if any"""
        return self._post('auth/signout')
    
    def get_profile(self, username=None):
        """Get the Profile for the current user or the given username"""
        return self._get('user/get_profile', {'username': None})
        
    def set_profile(self, parameters):
        """Sets the Profile for the current user"""
        return self._post('user/set_profile', parameters)
        
    def set_guestname(self, guestname):
        """Sets the guestname"""
        return self._post('session/set_guestname', {'guestname':guestname})
        
    def get_user_info(self, username=None, which=None):
        # TODO: Find out exactly what user/get_info returns and update docstring        
        return self._get('user/get_info', {'username': username, 'which': which})
        
    def get_people(self, p_type):
        """Relationship lists: get people"""
        return self._get('user/get_people', {'type': p_type})
        
    def get_inbox(self, inbox_type='shouts_all'):
        """Relationship lists: get inbox"""
        return self._get('user/get_inbox', {'type':inbox_type})
        
    def add_to_inbox(self, conversation_id):
        """Add the specified conversation to inbox"""
        return self._post('user/add_to_inbox', {'cid': conversation_id})
        
    def start_following(self, username):
        """Start following the specified username"""
        return self._post('user/start_following', {'username': username})
        
    def stop_following(self, username):
        """Stop following the specified username"""
        return self._post('user/stop_following', {'username': username})
        
    def user_catch_up(self, u_type):
        # TODO: update docstring
        return self._post('user/catch_up', {'type': u_type})
        
    def get_conversation_info(self, conversation_id):
        return self._get('conversation/get_info', {'api_key': self.api_key, 'cid': conversation_id}, False)
        
    def shout(self, text):
        return self._post('conversation/shout', {'text': text})
        
    def whisper(self, text, users):
        return self._post('conversation/whisper', {'text': text, 'users': users})
        
    def reply(self, conversation_id, text, local_id=None):
        return self._post('conversation/reply', {'cid': conversation_id, 'text': text, 'local_id': local_id})
        
    def conversation_catch_up(self, conversation_id):
        return self._post('conversation/catch_up', {'cid': conversation_id})
        
    def delete_conversation(self, conversation_id):
        return self._post('conversation/delete', {'cid': conversation_id})
        
    def delete_reply(self, conversation_id, message_id):
        return self._post('conversation/delete_reply', {'cid': conversation_id, 'mid': message_id})
        
    def mute_conversation(self, conversation_id):        
        return self._post('conversation/mute', {'cid': conversation_id})
        
    def unmute_conversation(self, conversation_id):
        return self._post('conversation/unmute', {'cid': conversation_id})
        
    def subscribe(self, topic):
        """Subscribe to the given topic(s)"""
        return self._post('subscription/subscribe', {'topic': topic})
        
    def unsubscribe(self, topic):
        """Unsubscribe to the given topic(s)"""
        return self._post('subscription/unsubscribe', {'topic': topic})
        
    def public_timeline(self, page=1, filter=None):
        """Retrieve the public timeline"""
        return self._get('timeline/public', {'page': page, 'filter': filter})
        
    def user_timeline(self, page=1, username=None, filter=None):
        """Retrieve a user_timeline. If no username is passed the timeline for
        the current user is retrived"""
        return self._get('timeline/user', {'page': page, 'username': username, 'filter': filter})
        
    def observe(self, counter):
        # TODO: Update docstring
        path = "http://%d.%s/%s/%s.json" % (randint(1,100), self.host, API_VERSION, 'event/observe')
        parameters = {'counter': counter}
        self._session_check(parameters, True)
        self._clean_params(parameters)
        return self._do_api(Request("%s?%s" % (path, urlencode(parameters))))
        
    
    def _post(self, path, parameters, require_session=True):
        """calls self._do_api with the POST request"""
        self._session_check(parameters, require_session)
        self._clean_params(parameters)
        return self._do_api(Request(self._url_for(path), urlencode(parameters)))
    
    def _get(self, path, parameters, require_session=True):
        """calls self._do_api with a GET request"""
        self._session_check(parameters, require_session)
        self._clean_params(parameters)
        return self._do_api(Request("%s?%s" % (self._url_for(path), urlencode(parameters))))
    
    def _clean_params(self, parameters):
        """Cleans the parameters and converts lists/tuples to strings"""
        for k,v in parameters.items():
            if not v:
                parameters.pop(k)
                continue
                
            if isinstance(v, (list, tuple)):
                parameters[k] = ",".join(v)
                continue
    
    def _session_check(self, parameters, require_session):
        """Appends the session variable to the parameters if required"""
        if require_session:
            if not self.session:
                raise SessionRequired("An active session is required")
            
            # Append the session to the parameters for ease of use if it doesn't
            # already exist
            if not parameters.has_key('session'):
                parameters['session'] = self.session
    
    def _do_api(self, request):
        """Sends an api request via the given request object"""
        response = simplejson.loads(urlopen(request).read())
        
        if not isinstance(response, dict):
            raise RejawError("Unexpected Response: %s" % response)
            
        if not response.get('status', None) == 'ok':
            succeeded = False
        else:
            succeeded = True
            
        return dict(succeeded=succeeded, response=response)
        
    def _url_for(self, path):
        return "http://%s/%s/%s.json" % (self.host, API_VERSION, path)