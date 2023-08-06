from zope.interface import implements
from pydataportability.microformats.base.interfaces import IMicroformatsParser, IHTMLNode

class IHCardParser(IMicroformatsParser):
    """a hcard implementation"""
    
    
class VCard(object):
    """models a VCard"""
    
    FIELDS = ['fn','nickname','sort-string','url','email','label','tel','geo','photo','bday','logo','sound','title','role','org','category','note','class','key','mailer','uid','rev']
    ADR_FIELDS = ['post-office-box', 'extended-address', 'street-address', 'locality', 'region', 'postal-code', 'country-name', 'type', 'value']

    def __init__(self, **kwargs):
        self.data = {}
        self.adr = {}
        for field in self.FIELDS:
            self.data[field] = kwargs.get(field,u'')
        for field in self.ADR_FIELDS:
            self.adr[field] = kwargs.get(field,u'')
    
    
    def __setitem__(self,name,value):
        """store an item in the dict"""
        if name not in self.FIELDS:
            raise KeyError, "'%s' is not a valid key, please use one of %s" %(name,", ".join(self.FIELDS))
        self.data[name]=value
        
    def __getitem__(self,name):
        """return an item from the dict"""
        if name not in self.FIELDS:
            raise KeyError, "'%s' is not a valid key, please use one of %s" %(name,", ".join(self.FIELDS))
        return self.data.get(name,u'')
        
    def setAdrAttribute(self,name,value):
        if name not in self.ADR_FIELDS:
            raise KeyError, "'%s' is not a valid adr key, please use one of %s" %(name,", ".join(self.FIELDS))
        self.adr[name] = value
            
    def getAdrAttribute(self,name):
        """return an item from the dict"""
        if name not in self.ADR_FIELDS:
            raise KeyError, "'%s' is not a valid adr key, please use one of %s" %(name,", ".join(self.FIELDS))
        return self.adr.get(name,u'')

    def __str__(self):
        """return a texture representation"""
        l=[]
        for field in self.FIELDS:
            if self[field]!=u'':
                l.append("%s=%s" %(field,self[field]))
        al = []
        for field in self.ADR_FIELDS:
            if self.adr[field]!=u'':
                al.append("%s=%s" %(field,self.adr[field]))
        
        return """VCard for %s (%s), Adr: %s""" %(self.data['fn'],", ".join(l),", ".join(al))
        


class HCardParser(object):
    """parses HCards"""
    implements(IHCardParser)
    
    FIELDS = ['fn','nickname','sort-string','url','adr','email','label','tel','geo','photo','bday','logo','sound','title','role','org','category','note','class','key','mailer','uid','rev']
    ADR_FIELDS = ['post-office-box', 'extended-address', 'street-address', 'locality', 'region', 'postal-code', 'country-name', 'type', 'value']
    
    
    def checkNode(self,node):
        """check a node if some microformat might be inside"""
        classes = node.attrib.get('class','').split()
        classes = [c.lower() for c in classes]
        return 'vcard' in classes
    
    def parseNode(self,node):
        """parse a subtree"""
        self.vcard=VCard()
        self.consume_vcard(node)
        return self.vcard

    def consume_vcard(self, node):
        # note: for nested hcards getiterator() is probably not the way to go.
        for inode in node.getiterator():
            node = IHTMLNode(inode)
            classes = node.attrib.get('class','').split()
            classes = [c.lower() for c in classes]
            if 'vcard' in classes:
                # vcard in vcard, ignore for now
                pass
            for field in self.FIELDS:
                if field in classes:
                    # try to find a method to handle it
                    method = getattr(self,'handle_%s' %field,self.handlefield)
                    method(field,node)

    def handlefield(self,field,node):
        """generic field handler"""
        self.vcard[field]=node.text
        
    def handle_photo(self,field,node):
        """for photos we use the URL in the href"""
        url=node.attrib.get('href',None)
        if url is None:
            url = node.attrib.get('src',None)
        if url is not None:
            self.vcard['photo'] = url

    def handle_url(self,field,node):
        """extract the URL"""
        url=node.attrib.get('href',None)
        if url is not None:
            self.vcard['url'] = url

    def handle_email(self,field,node):
        """extract the email address"""
        url=node.attrib.get('href','').lower()
        if url.startswith('mailto:'):
            self.vcard['email'] = url[7:]
        else:
            self.vcard['email'] = node.text
        
    def handle_adr(self, field, node):
        for inode in node.getiterator():
            node = IHTMLNode(inode)
            classes = node.attrib.get('class','').split()
            classes = [c.lower() for c in classes]
            for field in self.ADR_FIELDS:
                if field in classes:
                    self.vcard.setAdrAttribute(field,node.text)
