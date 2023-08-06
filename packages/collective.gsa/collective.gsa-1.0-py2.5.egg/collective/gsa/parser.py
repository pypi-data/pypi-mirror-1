from zope.interface import implements
from elementtree.ElementTree import iterparse
from StringIO import StringIO
from xml.parsers.expat import ExpatError

from collective.gsa.interfaces import IGSAFlare
from collective.gsa.utils import remove_html_tags
from logging import getLogger


logger = getLogger(__name__)


class GSAFlare(object):
    """ a sol(a)r brain, i.e. a data container for search results """
    implements(IGSAFlare)

    __allow_access_to_unprotected_subobjects__ = True


class GSAResults(list):
    """ a list of results returned from solr, i.e. sol(a)r flares """

class GSAResponse(object):
    """ a gsa search response; TODO: this should get an interface!! """

    def __init__(self, data=None):
        if data is not None:
            self.parse(data)

    def parse(self, data):
        """ parse a gsa response contained in a string or file-like object """
        if not data:
            logger.warning('No data reveceived.')
            return []
        if isinstance(data, basestring):
            data = StringIO(data)
        results = []
        try:
            elements = iterparse(data, events=('start','end'))
            for action, elem in elements:
                tag = elem.tag
                if action == 'start':
                    if tag == 'R':
                        obj = GSAFlare()
                    if tag in ['U','UE','T','S','RK']:
                        if elem.text:
                            setattr(obj, tag, elem.text)
                    if tag == 'MT':
                        if elem.attrib['N'] not in ['Title','Description']:
                            setattr(obj, elem.attrib['N'], elem.attrib['V'])
                    
                elif action == 'end':
                    if tag == 'R':
                        results.append(obj)
                    if tag in ['U','UE','T','S','RK']:
                        if elem.text:
                            setattr(obj, tag, elem.text)
                
            
        except ExpatError, e:
            logger.error('Could not parse received data. Reason: %s' % e)
            
        return results

def setter(item, name, value):
    """ sets the named value on item respecting its type """
    if isinstance(item, list):
        item.append(value)      # name is ignored for lists
    elif isinstance(item, dict):
        item[name] = value
    else:                       # object is assumed...
        setattr(item, name, value)


class AttrDict(dict):
    """ a dictionary with attribute access """

    # look up attributes in dict
    def __getattr__(self, name):
        marker = []
        value = self.get(name, marker) 
        if value is not marker:
            return value
        else:
            raise AttributeError, name
