# $Id
#

"""
The namespace module contains namespace classes that are used for
variable substitution within ModiPy.

Namespaces exist in a hierarchy, and a particular change will
use a namespace at some point in the hierarchy to find the
value to use for a keyword substitution. If the namespace doesn't
have an entry for that key, it will cascade upwards to its parent
namespace(s) all the way up to a global namespace to look for that
keyword, and will use the first one it finds.

In this way, you can define variables for use in your changes,
either globally (including some default keywords in the global
namespace) or specifically within just specific changes, or
for groups of changes.
"""

import logging
log = logging.getLogger('modipy')

class Namespace:
    """
    A cascading namespace object that can refer to items in
    parent namespaces to resolve names if they do not exist
    in the current namespace.
    """
    def __init__(self, name='', namespace={}, parent=None):

        self.parent = parent
        self.namespace = namespace

    def __getitem__(self, key):
        """
        Implement dictionary interface
        """
        try:
            return self.namespace[key]
        except KeyError:
            if self.parent is not None:
                return self.parent[key]
            else:
                raise

    def __setitem__(self, key, value):
        self.namespace[key] = value

    def keys(self):
        keys = self.namespace.keys()
        
        if self.parent is not None:
            pkeys = self.parent.keys()
            for pkey in pkeys:
                if pkey not in keys:
                    keys.append(pkey)
                    pass
                pass
            pass

        return keys

    def has_key(self, key):
        if self.namespace.has_key(key):
            return True
        else:
            if self.parent is not None:
                return self.parent.has_key(key)
            else:
                return False
            pass
        pass

    def update(self, dict):
        if dict is not None:
            for key in dict:
                self.namespace[key] = dict[key]

    def __iter__(self):
        log.debug("Creating a Namespace iterator")

        # initialise iterators
        if self.parent is not None:
            log.debug("started parent iterator")
            return self.parent.__iter__()

        self.namespace.__iter__()
        log.debug("started my iterator")
        return self

    def next(self):
        if self.parent is not None:
            try:
                return self.parent.next()
            except StopIteration:
                return self.namespace.next()
        else:
            try:
                return self.namespace.next()
            except AttributeError:
                raise StopIteration
            
    def items(self):
        log.debug("Using namespace.items()!")
        items = []
        if self.parent is not None:
            items.extend( self.parent.items() )
        items.extend( self.namespace.items() )

        return items

    def copy(self):
        return self.namespace.copy()

    def __repr__(self):
        return "<Namespace: %s>" % self.items()

def create_namespace(node):
    """
    Create a namespace from an element node
    """
    log.debug("Creating standard Namespace")
    ns = Namespace(node.tag)
    for entry in node.findall('entry'):
        item_name = entry.attrib['name']
        item_value = entry.text
        ns[item_name] = item_value
        pass

    return ns
