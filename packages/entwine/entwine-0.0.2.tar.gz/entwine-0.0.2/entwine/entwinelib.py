
'''

entwinelib.py
==========

Desc: Library for querying twine.com

Author: Rob Cakebread <cakebread a t gmail .com>

License  : New BSD (See COPYING)

'''

__docformat__ = 'restructuredtext'

import urllib2

from rdflib import ConjunctiveGraph, Namespace

from entwine.utils import get_user_passwd

XMLNS = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
APP = Namespace('http://www.radarnetworks.com/shazam#')
BASIC = Namespace('http://www.radarnetworks.com/2007/09/12/basic#')
RADAR = Namespace('http://www.radarnetworks.com/core#')
WEB = Namespace('http://www.radarnetworks.com/web#')


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
    return opener.open("http://www.twine.com/user/%s" % profile_username)

def parse_profile(profile):
    """Parse RDF profile into triples"""
    
    store = ConjunctiveGraph()
    store.parse(profile, publicID=None, format="xml")
    print_profile_section(store, APP, ['status', 'wasInvitedBy', 'location'])
    print_profile_section(store, BASIC, ['url'])
    print_profile_section(store, RADAR, ['isPerson', 'createdDate', 'lastModifiedDate'])
    print_profile_section(store, WEB, ['views'])

def print_profile_section(store, namespace, elements):
    """Print the triples"""
    for predicate in elements:
        for subj, obj in store.subject_objects(namespace[predicate]):
            print predicate + u': %s' % obj

if __name__ == "__main__":
    print get_profile("cakebread")
    parse_profile(get_profile("cakebread"))
