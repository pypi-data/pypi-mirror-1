#!/usr/bin/python
#
# $Id: shortie.py 141 2009-01-29 12:31:42Z nsheridan@EVIL.IE $
#

""" Python library for short.ie API """

import sys
import urllib2
import xml.etree.ElementTree as etree

__author__ = 'nsheridan@gmail.com (Niall Sheridan)'
__license__ = 'Python'
__copyright__ = 'Copyright 2009, Niall Sheridan'


class shortie():
  """ short.ie client
  api: api url. default: http://short.ie/api
  """

  def __init__(self, api=None):
    if api is None:
      self.api = 'http://short.ie/api'
    else:
      self.api = api


  def shorturl(self, url, full=False, **kwargs):
    """ Request a short url
    url: The url which you would like shortened
    full: If True, return the complete response to the request
          If False, just return the shortened url
    Any other args will be appended to the api url in the form '&key=value'

    e.g. shorturl('http://www.google.com', format='json')
    becomes http://short.ie/api/?url=http://www.google.com&format=json
    """
    if full is False:
      # Force format to xml for later parsing
      kwargs['format'] = 'xml'
    url = '%s/?url=%s' % (self.api, url)
    for key in kwargs:
      url = '%s&%s=%s' % (url, key, kwargs[key])
    try:
      resp = urllib2.urlopen(url)
    except urllib2.URLError, error:
      sys.stderr.write(error)
      raise
    if full:
      # Return the full response in whatever format was requested
      return resp.read()
    else:
      # Just send back the shortened url
      short = etree.parse(resp).find('shortened').text
      return short


def main():
  if len(sys.argv) > 1:
    url = sys.argv[1]
    c = shortie()
    short = c.shorturl(url)
    print short
  else:
    sys.stderr.write('Argument required')


if __name__ == '__main__':
  main()
