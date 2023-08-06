# -*- coding: utf-8 -*-

__version__ = '0.1'

from functools import wraps

from django.conf import settings
from django.utils.decorators import decorator_from_middleware


class Notice(tuple):
    """A simple wrapper for managing notices."""
    
    level = property(lambda self: self[0])
    message = property(lambda self: self[1])
    
    def __new__(cls, level, message):
        return tuple.__new__(cls, (level, message))
    
    def __repr__(self):
        return 'Notice(%r, %r)' % (self.level, self.message)
    
    def __unicode__(self):
        return self.message


## Middleware

class AttentionMiddleware(object):
    """Middleware that attaches an `AttentionHandler` to each request."""
    
    def __init__(self):
        self.attribute = getattr(settings, 'ATTENTION_REQUEST_ATTR', 'attn')
    
    def process_request(self, request):
        setattr(request, self.attribute, AttentionHandler(request.session))

attention = decorator_from_middleware(AttentionMiddleware)


## Handler

def modifies_session(method):
    """Declare that a method modifies `self.session`."""
    
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        finally:
            if hasattr(self.session, 'modified'):
                self.session.modified = True
            else:
                self.session.save()
    return wrapper


class AttentionHandler(object):
    
    """A handler which manages adding/removing messages to/from the client."""
    
    def __init__(self, session):
        self.session = session
        self.session_key = getattr(settings, 'ATTENTION_SESSION_KEY', '_attn')
    
    @modifies_session
    def __iter__(self):
        messages = self.session.get(self.session_key, ())
        while messages:
            yield Notice(*messages.pop())
    
    def __len__(self):
        return len(self.session.get(self.session_key, ()))
    
    @modifies_session
    def add(self, message, level='notice'):
        """Add a notice to the session (where `level` defaults to 'notice')."""
        
        self.session.setdefault(self.session_key, []).append((level, message))
    
    def get(self):
        """Retrieve all current notices."""
        
        return [Notice(*args) for args in self.session.get(self.session_key, ())]
    
    @modifies_session
    def pop(self):
        """Retrieve all current notices, clearing them from the session."""
        
        return list(self)
    
    # `request.attn.info('message')` => `request.attn.add('message', level='info')`
    def __getattr__(self, level):
        def add_message(message):
            self.add(message, level)
        return add_message
