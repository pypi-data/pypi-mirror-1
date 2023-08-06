"""Define CMFNotification specific exceptions.

$Id: exceptions.py 111643 2010-02-24 15:01:39Z jcbrand $
"""

class MailHostNotFound(Exception):
    """Could not send notification: no mailhost found"""

class DisabledFeature(Exception):
    """Cannot use this feature: it is disabled"""

class InvalidEmailAddress(Exception):
    """The given email address is not valid"""
