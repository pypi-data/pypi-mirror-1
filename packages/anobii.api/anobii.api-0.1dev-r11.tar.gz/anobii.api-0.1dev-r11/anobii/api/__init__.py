#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''A AnobiiAPI interface.
See `the AnobiiAPI homepage`_ for more info.

.. _`the AnobiiAPI homepage`: http://code.google.com/p/anobiiapi/

Since the behaviour is very similar to FlickrAPI I get the code from http://flickrapi.sf.net/
and I adapted it to Anobii API.
thanks to Sybren Stuvel for his work.
'''

__version__ = '0.1'
__all__ = ('AnobiiAPI','__version__')
__author__ = u'Massimo Azzolini'

# Copyright (c) 2007 by the respective coders, see
# http://code.google.com/p/anobiiapi/
#
# This code is subject to the Python licence, as can be read on
# http://www.python.org/download/releases/2.5.2/license/
#
# For those without an internet connection, here is a summary. When this
# summary clashes with the Python licence, the latter will be applied.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import md5
import urllib
import urllib2
import mimetools
import os.path
import logging
import copy
import webbrowser

from anobii.api.tokencache import TokenCache, SimpleTokenCache
from anobii.api.xmlnode import XMLNode
from anobii.api.exceptions import IllegalArgumentException, AnobiiError
from anobii.api.cache import SimpleCache

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

def make_utf8(dictionary):
    '''Encodes all Unicode strings in the dictionary to UTF-8. Converts
    all other objects to regular strings.
    
    Returns a copy of the dictionary, doesn't touch the original.
    '''
    
    result = {}

    for (key, value) in dictionary.iteritems():
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        else:
            value = str(value)
        result[key] = value
    
    return result
        
def debug(method):
    '''Method decorator for debugging method calls.

    Using this automatically sets the log level to DEBUG.
    '''

    LOG.setLevel(logging.DEBUG)

    def debugged(*args, **kwargs):
        LOG.debug("Call: %s(%s, %s)" % (method.__name__, args,
            kwargs))
        result = method(*args, **kwargs)
        LOG.debug("\tResult: %s" % result)
        return result

    return debugged

parsers = {}

def parser(format):
    '''Function decorator, use this to mark a function as the parser for REST as
    returned by Anobii.
    '''

    def decorate_parser(method):
        LOG.debug(method)
        parsers[format] = method
        return method

    return decorate_parser

class AnobiiAPI:
    """Encapsulates Anobii functionality.
    """
    
    anobii_host = 'api.anobii.com'
    
    def __init__(self, api_key, secret, token=None, fail_on_error=None, format='xmlnode', store_token=True, cache=False):
        """
        api_key 
            The API key obtained by anobii
            
        api_secret
            The API secret key obtained by anobii
        """
        self.api_key = api_key
        self.api_secret = secret
        self.default_format = format
        self.fail_on_error=fail_on_error
        self.__handler_cache = {}
        self.api_sig = self.__get_sig()
        
        if token:
            # Use a memory-only token cache
            self.token_cache = SimpleTokenCache()
            self.token_cache.token = token
        elif not store_token:
            # Use an empty memory-only token cache
            self.token_cache = SimpleTokenCache()
        else:
            # Use a real token cache
            self.token_cache = TokenCache(api_key)

        if cache:
            self.cache = SimpleCache()
        else:
            self.cache = None
    
    def __get_sig(self):
        return md5.new(self.api_key+self.api_secret).hexdigest()

    def __repr__(self):
        '''Returns a string representation of this object.'''
        return '[AnobiiAPI for key "%s"]' % (self.api_key, )

    __str__ = __repr__

    @parser('xmlnode')
    def parse_xmlnode(self, xml):
        '''Parses a REST XML response from Anobii into an XMLNode object.'''
        rsp = XMLNode.parse(xml, store_xml=True)
        try:
            err = rsp.error[0]
            if not self.fail_on_error:
                return rsp
            else:
                err = rsp.err[0]
                raise AnobiiError(u'Error: %(code)s: %(msg)s' % err)
        except:
            return rsp
        

    @parser('etree')
    def parse_etree(self, xml):
        '''Parses a REST XML response from Anobii into an ElementTree object.'''

        # Only import it here, to maintain Python 2.4 compatibility
        import xml.etree.ElementTree

        rsp = xml.etree.ElementTree.fromstring(xml)
        if rsp.attrib['stat'] == 'ok' or not self.fail_on_error:
            return rsp
        
        err = rsp.find('err')
        raise AnobiiError(u'Error: %s: %s' % (
            err.attrib['code'], err.attrib['msg']))

    def sign(self, dictionary):
        """Calculate the Anobii signature for a set of params.
        
        data
            a hash of all the params and values to be hashed, e.g.
            ``{"api_key":"AAAA", "auth_token":"TTTT", "key":
            u"value".encode('utf-8')}``

        """

        data = [self.api_secret]
        for key in sorted(dictionary.keys()):
            data.append(key)
            datum = dictionary[key]
            if isinstance(datum, unicode):
                raise IllegalArgumentException("No Unicode allowed, "
                        "argument %s (%r) should have been UTF-8 by now"
                        % (key, datum))
            data.append(datum)
        
        md5_hash = md5.new()
        md5_hash.update(''.join(data))
        return md5_hash.hexdigest()

    def encode_and_sign(self, dictionary):
        '''URL encodes the data in the dictionary, and signs it using the
        given secret, if a secret was given.
        '''
        
        dictionary = make_utf8(dictionary)
        if self.api_secret:
            dictionary['api_sig'] = self.sign(dictionary)
        return urllib.urlencode(dictionary)
        
    def __getattr__(self, attrib):
        """Handle all the regular Anobii API calls.
        
        Example::

            anobii.getSimpleShelf(api_key="AAAAAA", api_sig="BBBBBB", user_id="misterx")
            
            see api.anobii.com for more API
        """

        # Refuse to act as a proxy for unimplemented special methods
        if attrib.startswith('_'):
            raise AttributeError("No such attribute '%s'" % attrib)

        # Construct the method name and see if it's cached
        method = attrib.replace("_", ".")
        if method in self.__handler_cache:
            return self.__handler_cache[method]
        
        def handler(**args):
            '''Dynamically created handler for a Anobii API call'''

            if self.token_cache.token and not self.api_secret:
                raise ValueError("Auth tokens cannot be used without "
                                 "API secret")

            # Set some defaults
            defaults = {'method': method,
                        'api_key': self.api_key,
                        'api_sig': self.api_sig,
                        'format': self.default_format}

            args = self.__supply_defaults(args, defaults)

            return self.__wrap_in_parser(self.__anobii_call,
                    parse_format=args['format'], **args)

        handler.method = method
        self.__handler_cache[method] = handler
        return handler
    
    def __supply_defaults(self, args, defaults):
        '''Returns a new dictionary containing ``args``, augmented with defaults
        from ``defaults``.

        Defaults can be overridden, or completely removed by setting the
        appropriate value in ``args`` to ``None``.

        >>> f = AnobiiAPI('123')
        >>> f._AnobiiAPI__supply_defaults(
        ...  {'foo': 'bar', 'baz': None, 'token': None},
        ...  {'baz': 'foobar', 'room': 'door'})
        {'foo': 'bar', 'room': 'door'}
        '''

        result = args.copy()
        for key, default_value in defaults.iteritems():
            # Set the default if the parameter wasn't passed
            if key not in args:
                result[key] = default_value

        for key, value in result.copy().iteritems():
            # You are able to remove a default by assigning None, and we can't
            # pass None to Anobii anyway.
            if result[key] is None:
                del result[key]
        
        return result

    def __anobii_call(self, **kwargs):
        '''Performs a Anobii API call with the given arguments. The method name
        itself should be passed as the 'method' parameter.
        
        Returns the unparsed data from Anobii::

            data = self.__anobii_call(method='shelf.getSimpleShelf',user_id='massimoazzolini', limit='30')
        '''

        LOG.debug("Calling %s" % kwargs)
        
        obj, method = kwargs['method'].split('.') 
        del(kwargs['format'])
        del(kwargs['method'])

        post_data = self.encode_and_sign(kwargs)

        # Return value from cache if available
        if self.cache and self.cache.get(post_data):
            return self.cache.get(post_data)

        params = urllib.urlencode(kwargs)
        
        url = 'http://%(url)s/%(obj)s/%(method)s?%(params)s' % {'url': AnobiiAPI.anobii_host, 'obj': obj, 'method':method,'params': params}
 
        LOG.debug('url %s' % url)
        socket = urllib.urlopen(url, post_data)
        reply = socket.read()
        socket.close()

        # Store in cache, if we have one
        if self.cache is not None:
            self.cache.set(post_data, reply)

        return reply
    
    def __wrap_in_parser(self, wrapped_method, parse_format, *args, **kwargs):
        '''Wraps a method call in a parser.

        The parser will be looked up by the ``parse_format`` specifier. If there
        is a parser and ``kwargs['format']`` is set, it's set to ``rest``, and
        the response of the method is parsed before it's returned.
        '''

        # Find the parser, and set the format to rest if we're supposed to
        # parse it.
        if parse_format in parsers and 'format' in kwargs:
            kwargs['format'] = 'rest'

        LOG.debug('Wrapping call %s(self, %s, %s)' % (wrapped_method, args,
            kwargs))
        data = wrapped_method(*args, **kwargs)

        # Just return if we have no parser
        if parse_format not in parsers:
            return data

        # Return the parsed data
        parser = parsers[parse_format]
        return parser(self, data)
        
        
        
def set_log_level(level):
    '''Sets the log level of the logger used by the AnobiiAPI module.
    
    >>> import anobii.api
    >>> import logging
    >>> anobii.api.set_log_level(logging.INFO)
    '''
    
    import anobii.api.tokencache

    LOG.setLevel(level)
    anobii.api.tokencache.LOG.setLevel(level)


if __name__ == "__main__":
    print "Running doctests"
    import doctest
    doctest.testmod()
    print "Tests OK"
