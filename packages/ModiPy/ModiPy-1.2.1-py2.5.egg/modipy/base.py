# $Id: base.py 98 2009-07-04 07:35:19Z daedalus $

"""
Some base level classes and definitions.
"""

class XMLConfigurable:
    """
    Something that is XML configurable, i.e.: pretty much
    all the classes in the system, has some common functions
    and attributes that we define here.
    """
    # These lists are used to perform some checking of
    # the configuration that is passed in to make sure
    # that it has all the right parts defined, and no
    # extras.

    # A list if tags that MUST be found in the element
    # definition in the configuration stack
    required_tags = []

    # Other tags that are merely optional
    optional_tags = []

    def get_required_tags(self):
        return self.required_tags

    def get_optional_tags(self):
        return self.optional_tags

    def get_supported_tags(self):
        return self.required_tags + self.optional_tags
