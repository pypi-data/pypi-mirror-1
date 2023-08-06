## (c) peter@fry-it.com, Aug, 2008
import re
import os
from cStringIO import StringIO
from urllib import urlopen
from copy import deepcopy

import lxml.html
from lxml.cssselect import CSSSelector
from lxml import etree


class DOMStripper(object):
    """ DOMStripper takes a URL/filename/fileobject, downloads the HTML and 
    strips away everything from the body tag except those CSS selectors provided. 
    
    NB. This is not a working doc test (I couldn't be asked to get the syntax 
    and colour highlighting right) so this docstring just shows how the class
    would work:
        
        >>> file = '/tm/foo.html'
        >>> stripper = DOMStripper(file, ['#main','table'])
        >>> print stripper
        '<html>...<body><div id="main">...<table></body></html>'
    
    
    
    """
    # ' # needed comment to prevent 
    
    
    
    
    def __init__(self, file_or_url, selectors_to_keep, 
                 pretty_print=True
                 ):
        self.file_or_url = file_or_url
        assert isinstance(selectors_to_keep, (tuple, list))
        self.selectors_to_keep = selectors_to_keep
        self.pretty_print = pretty_print
        self._new_html = None
        
    def __str__(self):
        if self._new_html is None:
            self._generate_new_html()
        return self._new_html
    
    def __unicode__(self):
        return unicode(self.__str__())
    
    def __repr__(self):
        return repr(self.__str__())
        
    def _get_file(self):
        if hasattr(self.file_or_url, 'read'):
            return self.file_or_url
        elif os.path.isfile(self.file_or_url):
            return open(self.file_or_url)
        else:
            return urlopen(self.file_or_url)

    def _discover_doctype(self, html):
        _doctype_regex = re.compile(r'<!doctype .*?>', re.I)
        try:
            return _doctype_regex.findall(html)[0]
        except IndexError:
            # not found
            return ''
        
    def _generate_new_html(self):
            
        parser = etree.HTMLParser()
        tree   = etree.parse(self._get_file(), parser)
        
        doctype = self._discover_doctype(self._get_file().read())
        
        new_tree = deepcopy(tree)
        _body_selector = CSSSelector('body')
        new_root = new_tree.getroot()
        _body = _body_selector(new_root)[0]
        _body_items = _body.items()
        new_root.remove(_body)
        
        new_body = etree.Element("body", **dict(_body_items))
        for selector in self.selectors_to_keep:
            sel = CSSSelector(selector)
            for element in sel(tree.getroot()):
                new_body.append(element)
                #htmlchunk = etree.tostring(element, pretty_print=True)
                #print htmlchunk
                #print ""
                #print "*" * 80
                #print ""
            
        new_root.append(new_body)

        # Since the doctype is stripped from the root ('html' node)
        # we put it back in again.
        self._new_html = '\n'.join([
          doctype,
          etree.tostring(new_root, pretty_print=self.pretty_print)
        ])
        
            
        return self._new_html
    
    def regenerate(self):
        self._new_html = None
        
    def getvalue(self):
        return self.__str__()



def domstripper(file_or_url, selectors_to_keep, pretty_print=True):
    
    if isinstance(selectors_to_keep, basestring):
        selectors_to_keep = [selectors_to_keep]
        
    return DOMStripper(file_or_url, selectors_to_keep, 
                       pretty_print=pretty_print).getvalue()
        