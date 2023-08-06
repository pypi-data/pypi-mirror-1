#
# Utility functions
#
from twisted.internet import reactor, defer

import logging
import debug
log = logging.getLogger('modipy')

def substituteVariables(str, namespace={}):
    """
    Perform variable substitution, given a string and a namespace.
    """
    try:
        str = str % namespace
        return str
    except KeyError, e:
        log.error("Cannot perform substitution on string. KeyError on: %s, %s", str, e)
        raise

def build_dict(node):
    """
    Create a dictionary representing an XML tree. Assumes
    the XML tree is only one layer deep.
    """
    result = {}
    for child in node:
        name = str(child.tag)
        result[name] = str(child.text)
        pass
    return result

def run_after_delay(delay, func, *args):
    """
    Run a function after some arbitrary delay
    """
    d = defer.Deferred()
    log.debug("In %d seconds, I'll run %s with args: %s", delay, func, args)
    reactor.callLater(delay, run_delayed_function, d, func, *args)
    return d

def run_delayed_function(d, func, *args):
    """
    Run a function that was called after a delay via reactor.callLater
    Chains the original deferred with whatever is run after
    the delay.
    """
    #log.debug("Calling %s with args: %s", func, args)
    newd = func(*args)
    newd.chainDeferred(d)
