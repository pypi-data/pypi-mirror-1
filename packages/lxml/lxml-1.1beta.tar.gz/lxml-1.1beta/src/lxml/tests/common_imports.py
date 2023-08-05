import unittest
import os.path
from StringIO import StringIO
import re

from lxml import etree

try:
    from xml.etree import ElementTree # Python 2.5
except ImportError:
    try:
        from elementtree import ElementTree # standard ET
    except ImportError:
        ElementTree = None

class HelperTestCase(unittest.TestCase):
    def parse(self, text):
        f = StringIO(text)
        return etree.parse(f)
    
    def _rootstring(self, tree):
        return etree.tostring(tree.getroot()).replace(' ', '').replace('\n', '')

class SillyFileLike:
    def __init__(self, xml_data='<foo><bar/></foo>'):
        self.xml_data = xml_data
        
    def read(self, amount=None):
        if self.xml_data:
            if amount:
                data = self.xml_data[:amount]
                self.xml_data = self.xml_data[amount:]
            else:
                data = self.xml_data
                self.xml_data = ''
            return data
        return ''

class LargeFileLike:
    def __init__(self, charlen=100, depth=4, children=5):
        self.data = StringIO()
        self.chars  = 'a' * charlen
        self.children = range(children)
        self.more = self.iterelements(depth)

    def iterelements(self, depth):
        yield '<root>'
        depth -= 1
        if depth > 0:
            for child in self.children:
                for element in self.iterelements(depth):
                    yield element
                yield self.chars
        else:
            yield self.chars
        yield '</root>'

    def read(self, amount=None):
        data = self.data
        append = data.write
        if amount:
            for element in self.more:
                append(element)
                if data.tell() >= amount:
                    break
        else:
            for element in self.more:
                append(element)
        result = data.getvalue()
        data.seek(0)
        data.truncate()
        if amount:
            self.data.write(result[amount:])
            result = result[:amount]
        return result

def fileInTestDir(name):
    _testdir = os.path.split(__file__)[0]
    return os.path.join(_testdir, name)

def canonicalize(xml):
    f = StringIO(xml)
    tree = etree.parse(f)
    f = StringIO()
    tree.write_c14n(f)
    return f.getvalue()

def unentitify(xml):
    for entity_name, value in re.findall("(&#([0-9]+);)", xml):
        xml = xml.replace(entity_name, unichr(int(value)))
    return xml
