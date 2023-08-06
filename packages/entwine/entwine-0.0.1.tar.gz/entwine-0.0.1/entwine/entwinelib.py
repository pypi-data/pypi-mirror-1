
'''

entwinelib.py
==========

Desc: Library for querying twine.com

Author: Rob Cakebread <cakebread a t gmail .com>

License  : New BSD (See COPYING)

'''

__docformat__ = 'restructuredtext'

import urllib2
from entwine.utils import get_user_passwd


def get_profile(profile_username):
    """Returns RDF for a given username"""
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    username, password = get_user_passwd()

    top_level_url = "http://www.twine.com/user/%s" % profile_username
    password_mgr.add_password(None, top_level_url, username, password)

    handler = urllib2.HTTPBasicAuthHandler(password_mgr)

    opener = urllib2.build_opener(handler)
    opener.addheaders = [('Accept', 'application/rdf+xml'), 
        ('Content-Type',  'application/rdf+xml'), 
        ('User-agent',
         'Mozilla/5.0 (compatible; entwine ' +
         'http://code.google.com/p/entwine)')]

    # use the opener to fetch a URL
    return opener.open("http://www.twine.com/user/%s" % profile_username).read()


if __name__ == "__main__":
    print get_profile("cakebread")
