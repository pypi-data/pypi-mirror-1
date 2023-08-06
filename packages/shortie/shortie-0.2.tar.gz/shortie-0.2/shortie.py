#!/usr/bin/python
#
# $Id: shortie.py 145 2009-01-30 13:09:17Z nsheridan@EVIL.IE $
#

""" Python library for short.ie API """

import sys
import urllib
import urllib2

__author__ = 'nsheridan@gmail.com (Niall Sheridan)'
__license__ = 'Python'
__copyright__ = 'Copyright 2009, Niall Sheridan'


class ShortieError(Exception):

  def __init__(self, code, error):
    self.code = code
    self.error = error

  def __str__(self):
    return 'Error %s: %s' % (self.code, self.error)


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
    kwargs['url'] = url
    if full is False:
      # Force format to plain - returns only the shortened url
      kwargs['format'] = 'plain'
    params = urllib.urlencode(kwargs)
    url = '%s?%s' % (self.api, params)
    try:
      resp = urllib2.urlopen(url).read()
    except urllib2.URLError, error:
      raise ShortieError(error.code, error.code.read())
    return resp


def main():
  if len(sys.argv) > 1:
    url = sys.argv[1]
    c = shortie()
    short = c.shorturl(url)
    print short
  else:
    sys.stderr.write('Argument required')
    sys.exit(1)


if __name__ == '__main__':
  main()
