# 
#  flash.py
#  rum
#  
#  Created by Michael Brickenstein on 2008-11-28.
#  Copyright 2008 Michael Brickenstein/Alberto Valverde
#   

class DummyFlash(object):
    messages = None
    def __call__(*args, **kw):
        pass

    def pop_messages(self):
        return []

class Flash(object):
    key = 'rum.flash.messages'
    def __init__(self, session):
        self.session = session

    @property
    def messages(self):
        if self.session.has_key(self.key):
            messages = self.session[self.key]
        else:
            self.session[self.key] = messages = []
        return messages

    def __call__(self, msg, status='info'):
        self.messages.append({'msg':unicode(msg), 'status':status})
        self.session.save()

    def pop_messages(self):
        messages = self.messages[:]
        del self.messages[:]
        self.session.save()
        return messages
