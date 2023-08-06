from zope.interface import implements
from pydataportability.microformats.base.interfaces import IMicroformatsParser

from config import XFN_TAGS, FLAT_XFN_TAGS

class IXFNParser(IMicroformatsParser):
    """a xfn parser implementation"""
    
    
class XFNRelationships(object):
    """models the xfn relationships for a noce"""
    
    def __init__(self, url):
        self.url = url
        self.data = {}
        self.link = {}
        for category in XFN_TAGS.keys():
            self.data[category]=set()    
    
    def __setitem__(self,name,value):
        """store an item in the dict"""
        if name not in self.data.keys():
            raise KeyError, "'%s' is not a valid key, please use one of %s" %(name,", ".join(self.data.keys()))
        self.data[name]=value
        
    def __getitem__(self,name):
        """return an item from the dict"""
        if name not in self.data.keys():
            raise KeyError, "'%s' is not a valid key, please use one of %s" %(name,", ".join(self.data.keys()))
        return self.data.get(name,u'')
        
    def getAllRelationships(self):
        """return a flat list of the relationships found"""
        return frozenset(reduce(lambda x,y: x|y,[item for item in self.data.values()]))
        

    def __str__(self):
        """return a texture representation"""
        return """XFN Relationships for %s: %s""" %(self.url,", ".join(self.getAllRelationships()))
        


class XFNParser(object):
    """parses HCards"""
    implements(IXFNParser)
    
    def checkNode(self,node):
        """check a node if some microformat might be inside"""
        # we check if there is an intersection between the tags in the rel attribute and the known tags
        tag = node.tag.split('}')[-1].lower()   # more a hack to get rid of the namespace
        if tag!="a":
            return False
        rel = set(node.attrib.get('rel','').split())
        return len(rel.intersection(FLAT_XFN_TAGS))!=0
    
    def parseNode(self,node):
        """parse a subtree"""
        # extract URL
        url = node.attrib.get('href',None)
        self.rels = XFNRelationships(url)
        self.consume_xfn(node)
        return self.rels

    def consume_xfn(self, node):
        rel = set(node.attrib.get('rel','').split())
        
        for category, tags in XFN_TAGS.items():
            self.rels[category] = rel.intersection(tags)
        
