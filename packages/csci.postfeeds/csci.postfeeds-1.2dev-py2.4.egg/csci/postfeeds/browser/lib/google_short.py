#!/usr/bin/python2.4
#
# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Example script.

   Connects to an installation of Google Short Links and submits an
   API request.

   Example commands:
     Get the details of the short link 'foo':
       python api_sample.py
           --details
           --server=shortlinks.example.com
           --hmac=foobar
           --email=anything
           --url=anything
           --shortcut_name=foo
     Create a new short link 'bar' that points to www.google.com and
     is owned by owner@example.com:
       python api_sample.py
           --create
           --server=shortlinks.example.com
           --hmac=foobar
           --email=owner@example.com
           --url=http://www.google.com
           --shortcut_name=bar
     Create a new public HASHED short link that points to www.google.com and
     is owned by owner@example.com:
       python api_sample.py
           --hash
           --server=shortlinks.example.com
           --hmac=foobar
           --email=owner@example.com
           --url=http://www.google.com
           --shortcut_name=anything
           --is_public
"""


import base64
import datetime
import hmac
import optparse
import sha
import sys
import time
import urllib
import urllib2


def make_request_uri(hostname, api_method, secret, **parameters):
    """Constructs a signed api request.

       Contains a miniature implementation of an oauth signing mechanism.
       Not complete, but enough for this use case.

    Args:
      hostname: the name of the domain that short links is installed at
      api_method: the api method to be called, like get_or_create_hash
      secret: the api (hmac) secret to be used
      parameters: additional arguments that should be passed to the api-method
    Returns:
      A signed URL that the short links server would understand.
    """
    # What is the url (without parameters)?
    base_url = 'http://%s/js/%s' % (hostname.lower(), api_method)

    # What is the base query string?
    parameters['oauth_signature_method'] = 'HMAC-SHA1'
    parameters['timestamp'] = str(
        time.mktime(datetime.datetime.now().timetuple()))
    param_array = [(k, v) for k, v in parameters.items()]
    param_array.sort()
    keyvals = ['%s=%s' % (urllib.quote(a, ''), urllib.quote(str(b), ''))
               for a, b in param_array]
    unsecaped = '&'.join(keyvals)
    signature_base_string = 'GET&%s&%s' % (
        urllib.quote(base_url, ''), urllib.quote(unsecaped, ''))

    # Create oauth secret
    signature = urllib.quote(base64.b64encode(
        hmac.new(secret, signature_base_string, sha).digest()), '')

    # Return the result
    return '%s?%s&oauth_signature=%s' % (base_url, unsecaped, signature)


if __name__ == '__main__':
    main()

