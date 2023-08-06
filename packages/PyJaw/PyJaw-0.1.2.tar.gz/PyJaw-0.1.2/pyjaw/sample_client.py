from pyjaw import RejawClient
from threading import Thread
from random import randint

import re
import sys
import traceback

try:
    set
except NameError: # Python 2.3
    from sets import Set as set
    
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

USER_TOPIC_PATTERN = re.compile(r'/user/(.+?)/(profile|followers|followees|conversations)/?$')
CONVERSATION_TOPIC_PATTERN = re.compile(r'/conversation/(\w{11})/?$')

class ObserverThread(Thread):
    def __init__(self, client):
        self.client = client
        self.counter = None
        self.stop_observing = False
        super(ObserverThread, self).__init__()
        
    def run(self):
        while not self.stop_observing:
            try:
                response = self.client.observe(self.counter)
                if response.get('succeeded'):
                    if response.get('response', {}).get('counter'):
                        self.counter = response['response']['counter']
                    if response['response'].get('events') and not self.client.process_events(response['response']['events']):
                        print "Event processing failed: %s" % str(response)
                        self.client.print_prompt()
                else:
                    print "observe failed: %s" % str(response)
            except Exception, e:
                buf = StringIO()
                traceback.print_exc(file=buf)
                print "Caught exception in observe loop: %s - %s" % (str(type(e)), str(e))
                print buf.getvalue()

class SampleClient(object):
    prompt = "> "
    def __init__(self, key, username, password, hostname='localhost:3000'):
        self.client = RejawClient(key, 0, hostname)
        self.client.create_session()
        self.username = username
        response = self.client.signin(self.username, password)
        
        self.infos = dict()
        self.rosters = dict()
        self.conversations = dict()
        
        self.observer = None
        
        if response['succeeded']:
            topics = [
                "/user/%s/profile",
                "/user/%s/followers",
                "/user/%s/followees",
                "/user/%s/conversations",
                "/user/%s/conversation_replies"
            ]
            topics = [t % self.username for t in topics]
            
            self.client.subscribe(topics)
            
            # init the rosters
            self.rosters["followees"] = self.gather_roster("followees")
            self.rosters["followers"] = self.gather_roster("followers")
            
            # init the user info
            users = list()
            for k, v in self.rosters.iteritems():
                users.extend(v)
            # Make sure we only have unique items
            users = list(set(users))
            response = self.client.get_user_info(users, ["fullname", "blurb"])
            if response.get("succeeded"):
                for u in response["response"]["users"]:
                    self.infos[u['username']] = u
            
            self.observer = ObserverThread(self)
            self.observer.start()
            
            # init the inbox
            response = self.client.get_inbox('shouts_all')
            if response.get('succeeded'):
                self.update_conversation_info(",".join(response['response']['conversations']))
                    
            # Show a summary
            self.show_user_summary()
                    
    def gather_roster(self, roster_type):
        response = self.client.get_people(roster_type)
        return response.get("succeeded") and response["response"]["users"] or []
        
    def update_conversation_info(self, conversations):
        response = self.client.get_conversation_info(conversations)
        if response.get('succeeded'):
            for conversation in response['response']['conversations']:
                self.conversations[conversation['cid']] = conversation
        
    def get_user_info(self, user):
        response = self.client.get_user_info(user, ["fullname", "blurb"])
        return response.get("succeeded") and response["response"]["users"][0] or {}
        
    def show_roster(self, which, label):
        print "%s: %s" % (label, ", ".join(self.rosters[which]))
        
    def update_roster(self, which, additions, deletions):
        self.rosters[which].extend(additions)
        [self.rosters.remove(u) for u in deletions]
        # Make sure we have a unique list
        self.rosters[which] = list(set(self.rosters[which]))
        
    def show_rosters(self):
        self.show_roster("followees", "You are following")
        self.show_roster("followers", "You are followed by")
        
    def show_conversations(self):
        print "Your conversaitions: "
        for c in self.conversations.values():
            print "%(text)s, created by %(username)s (%(cid)s)" % c
            
    def show_user_summary(self):
        self.show_rosters()
        print ""
        self.show_conversations()
        print ""
        
    def show_profile(self, username=None):
        response = self.client.get_profile(username)
        if response.get("succeeded"):
            for items in response["response"]["user"].iteritems():
                print "%s: %s" % items
            
    def process_events(self, events):
        if not events:
            return False
        
        for event in events:
            if USER_TOPIC_PATTERN.match(event["topic"]):
                user, subtopic = USER_TOPIC_PATTERN.match(event["topic"]).groups()
                
                if subtopic == "profile":
                    print "%s's profile changed" % user
                    self.print_prompt()
                    if "username" in event["changes"] and user == self.username:
                        self.username = event["new_username"]
                        
                elif subtopic in ["followers", "followees"]:
                    if user == self.username:
                        self.update_roster(subtopic, event.get("additions", []), event.get("deletions", []))

                        for u in event.get("additions", []):
                            print "%s added to %s" % (u, subtopic)
                            
                            # Get the user info if we don't already have it
                            if not u in self.infos.keys():
                                self.infos[u] = self.get_user_info(u)
                        
                        for u in event.get("deletions", []):
                            print "%s removed from %s" % (u, subtopic)
                            
                            # remove the unneeded info
                            try:
                                del self.infos[u]
                            except KeyError:
                                pass
                                
                        self.print_prompt()
                                
                elif subtopic == "conversations":
                    if event.get("joined"):
                        if not event["joined"]["cid"] in self.conversations.keys():
                            self.conversations[event["joined"]["cid"]] = event["joined"]
                            print "You joined %(text)s (%(cid)s)" % event["joined"]
                            self.print_prompt()
                        
                    elif event.get("moved") and not event["destination"] == "active":
                        print "%(text)s (%(cid)s) was removed from your active conversations" % event["moved"]
                        self.print_prompt()
                        try:
                            del self.conversations[event["moved"]["cid"]]
                        except KeyError:
                            pass
                            
            elif CONVERSATION_TOPIC_PATTERN.match(event["topic"]):
                conversation = CONVERSATION_TOPIC_PATTERN.match(event["topic"]).group(1)
                if not conversation in self.conversations.keys():
                    self.update_conversation_info(conversation)
                print "[%s] %s says %s" % (self.conversations[conversation]["cid"], event["fullname"], event["text"])
                self.print_prompt()
            else:
                print "Unknown event detected: %s" % str(event)
                self.print_prompt()
            # TODO: Implement the public topic pattern when announced
        return True
        
    def observe(self, *args, **kw):
        """Proxy through to self.client.observe"""
        return self.client.observe(*args, **kw)
        
    def quit(self):
        if self.observer:
            print "Shutting down observer..."
            self.observer.stop_observing = True
            self.observer.join()
            self.observer = None
        self.client.destroy_session()
        
    def print_prompt(self):
        print ""
        sys.stdout.write(self.prompt)
        sys.stdout.flush()
        
    def print_help(self):
        print "show"
        print "get_profile [username]"
        print "set_profile <attribute> <value>"
        print "start_following <username>"
        print "stop_following <username>"
        print "add_to_inbox <id>"
        print "shout <text>"
        print "whisper <user> <text>"
        print "reply <conversation_id> <text>"
        print "exit"
        print "verbose"
        print "quiet"
        print "quit"
        
    def main(self, *args, **kw):
        while True:
            cmd = raw_input(self.prompt).split(" ")
            
            if cmd[0] in ["help", "?"]:
                self.print_help()
                
            elif cmd[0] == "show":
                self.show_user_summary()
                
            elif cmd[0] == "get_profile":
                self.show_profile(cmd[1])
            
            elif cmd[0] == "set_profile":
                self.client.set_profile({cmd[1]: " ".join(cmd[2:])})
                
            elif cmd[0] == "start_following":
                self.client.start_following(cmd[1])
            
            elif cmd[0] == "stop_following":
                self.client.stop_following(cmd[1])
                
            elif cmd[0] == "add_to_inbox":
                self.client.add_to_inbox(cmd[1])
                
            elif cmd[0] == "shout":
                self.client.shout(" ".join(cmd[1:]))
                
            elif cmd[0] == "whisper":
                if len(cmd) < 3:
                    print "whisper <user> <text>"
                else:
                    self.client.whisper(" ".join(cmd[2:]), cmd[1])
                    
            elif cmd[0] == "reply":
                self.client.reply(cmd[1], " ".join(cmd[2:]))
                
            elif cmd[0] == "stop_observing":
                if self.observer:
                    self.observer.stop_observing = True
                    self.observer.join()
                    self.observer = None
                    
            elif cmd[0] == "verbose":
                self.client.verbosity = 2
                
            elif cmd[0] == "quiet":
                self.client.verbosity = 0
                
            elif cmd[0] == "dump":
                print "my username: %s" % self.username
                print "rosters: %s" % str(self.rosters)
                print "infos: %s" % str(self.infos)
                print "conversations: %s" % str(self.conversations)
                
            elif cmd[0] in ["exit", "quit"]:
                self.quit()
                break
            
            else:
                print "unrecognised command: %s" % cmd[0]
                
if __name__=="__main__":
    args = sys.argv
    if len(args) < 3:
        print "usage: sample_client <api_key> <email> <password> [host]"
    else:
        try:
            host = args[4]
        except IndexError, e:
            host = "api.rejaw.com"
        
        try:
            c = SampleClient(args[1], args[2], args[3], host)
            c.main()
        finally:
            c.quit()