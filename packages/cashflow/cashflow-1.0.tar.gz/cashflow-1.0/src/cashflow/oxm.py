"""Object-XML mapper.

These base classes and descriptors can be used to wrap ElementTree nodes
and make them behave like normal Python objects.  Think of this as being
like an ORM but for XML data.

"""
class XMLWrapper(object):
    """A class that wraps an XML object to expose its sub-elements."""

    def __init__(self, element):
        self.element = element

class XMLChild(object):
    """Descriptor returning a single XML child element."""

    def __init__(self, tag, cls):
        self.tag = tag
        self.cls = cls

    def __get__(self, instance, owner):
        return self.cls(instance.element.find(self.tag))

class XMLChildText(object):
    """Descriptor for a text attribute in a child XML element."""

    def __init__(self, *tags):
        self.tags = tags

    def __get__(self, instance, owner):
        e = instance.element
        for tag in self.tags:
            e = e.find(tag)
        return e.text

class XMLChildren(object):
    """Descriptor returning an iterator over XML child elements."""

    def __init__(self, tag, cls):
        self.tag = tag
        self.cls = cls

    def __get__(self, instance, owner):
        cls = self.cls
        return ( cls(e) for e in instance.element.findall(self.tag) )
