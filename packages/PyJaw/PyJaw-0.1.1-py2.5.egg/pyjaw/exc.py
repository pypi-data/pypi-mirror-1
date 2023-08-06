"""Contains all the exceptions that can be raised by the Rejaw API"""

class RejawError(Exception):
    """The base exception raised by the RejawClient class"""
    
class SessionRequired(RejawError):
    """Raised when a session is required but not active"""
    
class SessionActive(RejawError):
    """Raised when a session is already active"""