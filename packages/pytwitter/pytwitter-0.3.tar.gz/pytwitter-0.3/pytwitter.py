#!/usr/bin/python
#
# $Id: pytwitter.py 175 2009-05-10 00:29:23Z nsheridan@EVIL.IE $
#

""" Twitter api class.
See http://apiwiki.twitter.com/REST+API+Documentation for api docs

In short, converts 'method_action' to 'http://twitter.com/method/action.xml'
using the magic of __getattr__. Believe it!

Basic usage:
import pytwitter
twitter = pytwitter.pytwitter(username='username', password='password')
# Update status
twitter.statuses_update(status="<3 TWITTER!!1!")
# Follow biz
twitter.friendships_create(id="biz")

... and so on.

Unless an exception is raised, full output is returned in the requested format
Default: xml. Optional: json.
"""

import re
import urllib
import urllib2

__author__ = 'nsheridan@gmail.com (Niall Sheridan)'
__license__ = 'Python'
__copyright__ = 'Copyright 2008, Niall Sheridan'

class TwitterError(Exception):
  """ TwitterError exception
  Raised when the server returns something unexpected
  """
  def __init__(self, code, error):
    self.code = code
    self.error = error

  def __str__(self):
    return 'Error %s: %s' % (self.code, self.error)


class pytwitter:
  """ Twitter client:
  username:: twitter username
  password:: twitter account password
  url (optional):: alternate api url (ex. http://identi.ca/api)
  format:: xml or json (default: xml)
  """
  def __init__(
      self, username=None, password=None,
      url='http://twitter.com', format='xml'):
    self.url = url
    self.username = username
    self.password = password
    self.format = format

  def __getattr__(self, method):
    def method(_self=self, _method=method, **params):
      """ Dynamic api method constructor
      Takes: A valid twitter method
      Returns: xml or json output
      """
      # Exception case for 'direct_messages'
      # Can't just replace('_', '/') for this one
      if 'direct_messages' in _method:
        # _method should look like one of:
        #  direct_messages.format
        #  direct_messages/method.format
        _method = re.sub(r'^(direct_messages)_(.+)$', r'\1/\2', _method)
      else:
        # Everything else.
        _method = _method.replace('_', '/', 1)
      # Some methods are POST only. Default to sending a GET.
      use_post = False
      post_only_methods = ['statuses/update', 'statuses/delete',
          'account/endsession', 'friendships/destroy', 'friendships/create',
          'direct_messages/destroy', 'direct_messages/new',
          'account/update_delivery_service', 'account/update_profile_colors',
          'account/update_profile_image', 'favorites/create',
          'account/update_profile_background_image', 'account/update_profile',
          'notifications/follow', 'notifications/leave', 'blocks/create',
          'blocks/destroy', 'favorites/destroy']
      if _method in post_only_methods:
        use_post = True
      url = '%s/%s.%s' % (_self.url, _method, _self.format)
      for key in params.keys():
        params[key] = str(params[key])
      params = urllib.urlencode(params)
      resp = _self._send_data(url, params, use_post)
      return resp
    return method

  def _send_data(self, url, data, use_post=False):
    """ Authenticates with the server
    Sends the request and returns the xml or json response
    Raises TwitterError exception on urllib2.UrlError
    """
    try:
      pwdmanager = urllib2.HTTPPasswordMgrWithDefaultRealm()
      pwdmanager.add_password(
          None, self.url, self.username, self.password)
      opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(pwdmanager))
      if use_post:
        req = urllib2.Request(url, data)
      else:
        url = '%s?%s' % (url, data)
        req = urllib2.Request(url)
      resp = opener.open(req).read()
      try:
        return resp
      except:
        return None
    except urllib2.URLError, error:
      raise TwitterError(error.code, error.read())


def main():
  """ Test client """
  twitter = pytwitter()
  print twitter.help_test()

if __name__ == '__main__':
  main()
