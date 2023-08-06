#!/usr/bin/env python

'''Unittest for the AnobiiAPI.

Far from complete, but it's a start.
'''

import unittest
import sys
import urllib
import StringIO
import exceptions
import logging
import pkg_resources

# Make sure the anobii.api module from the source distribution is used
sys.path.insert(0, '..')

import anobii.api
anobii.api.set_log_level(logging.FATAL)
#anobii.api.set_log_level(logging.DEBUG)

print "Testing AnobiiAPI version %s" % anobii.api.__version__

# Some useful constants
EURO_UNICODE = u'\u20ac'
EURO_UTF8 = EURO_UNICODE.encode('utf-8')
U_UML_UNICODE = u'\u00fc'
U_UML_UTF8 = U_UML_UNICODE.encode('utf-8')


key = '7e862a70e1844f136ab2ab8ab07cc2c8'
secret = '09zugc4v9y'

#key = '34c8c38039b4acfdabf8cfb3184b6743'
#secret = 'au8tt0ieg7'

logging.basicConfig()
LOG = logging.getLogger(__name__)

def etree_package():
    '''Returns the name of the ElementTree package for the given
    Python version.'''

    current_version = sys.version_info[0:3]
    if current_version < (2, 5, 0):
        # For Python 2.4 and earlier, we assume ElementTree was
        # downloaded and installed from pypi.
        return 'elementtree.ElementTree'

    return 'xml.etree.ElementTree'


class SuperTest(unittest.TestCase):
    '''Superclass for unittests, provides useful methods.'''
    
    def setUp(self):
        super(SuperTest, self).setUp()
        self.a = anobii.api.AnobiiAPI(key, secret)
        # It's me
        self.user_id = 'massimoazzolini'
        # the "Shutendoji vol. 1" manga 
        self.item_id ='BmhaaQhvBDJWYgg2V2I='

        # Remove/prevent any unwanted tokens
        self.a.token_cache.forget()

    def assertUrl(self, expected_protocol, expected_host, expected_path,
                  expected_query_arguments, actual_url):
        '''Asserts that the 'actual_url' matches the given parts.'''
            
        # Test the URL part by part
        (urltype, rest) = urllib.splittype(actual_url)
        self.assertEqual(expected_protocol, urltype)
        
        (hostport, path) = urllib.splithost(rest)
        self.assertEqual(expected_host, hostport)
        
        (path, query) = urllib.splitquery(path)
        self.assertEqual(expected_path, path)
        
        attrvalues = query.split('&')
        attribs = dict(av.split('=') for av in attrvalues)
        self.assertEqual(expected_query_arguments, attribs)

        
class AnobiiApiTest(SuperTest):
    def test_repr(self):
        '''Class name and API key should be in repr output'''

        r = repr(self.a)
        self.assertTrue('AnobiiAPI' in r)
        self.assertTrue(key in r)
        
    def test_user_id(self):
        '''Test if the user is correctly returned'''
        result = self.a.shelf_getSimpleShelf(user_id=self.user_id)
        self.assertTrue(result['user_id']  == self.user_id)
        
    def test_limit(self):
        '''Test the nr of elements returned'''
        result = self.a.shelf_getSimpleShelf(user_id=self.user_id, limit='3')
        self.assertTrue(len(result.items[0].item) == 3)
    
    def test_less_than_limit(self):
        '''Anobii returns al max 10 elements'''
        result = self.a.shelf_getSimpleShelf(user_id=self.user_id, limit='11')
        self.assertTrue(len(result.items[0].item) == 10)
        
    def test_item_getInfo(self):
        '''test if we get the right infos:
         <item   id="BmhaaQhvBDJWYgg2V2I=" 
                 title="Shutendoji vol. 1" 
                 subtitle="" 
                 format="" 
                 language="it" 
                 cover="http://image.anobii.com/anobi/image_book.php?type=3&amp;item_id=01e35cf654903782eb&amp;time=1219596403">
                 <contributors>
                     <contributor id="Bm4POVUyVWVQZFph"></contributor>
                 </contributors>
         </item>
        
        '''
        book = self.a.item_getInfo(item_id=self.item_id)
        self.assertTrue(book.item[0]['id'] == self.item_id)
        self.assertTrue(book.item[0]['title'] == "Shutendoji vol. 1")
        self.assertTrue(book.item[0]['subtitle'] == "")
        self.assertTrue(book.item[0]['format'] == "")
        self.assertTrue(book.item[0]['language'] == "it")
        self.assertTrue(book.item[0]['cover'] != "")
        
    def test_contributor_getInfo(self):
        book = self.a.item_getInfo(item_id=self.item_id)
        contributor = self.a.contributor_getInfo(contributor_id = book.item[0].contributors[0].contributor[0]['id'],
                                                 item_id        = self.item_id)
        
        self.assertTrue(contributor.roles[0].role[0]['role'] == 'Author')
        self.assertTrue(contributor.roles[0].role[0]['name'] == 'Go Nagai')
        
if __name__ == '__main__':
    unittest.main()
