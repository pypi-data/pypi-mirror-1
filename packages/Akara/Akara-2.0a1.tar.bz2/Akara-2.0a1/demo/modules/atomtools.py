# -*- encoding: utf-8 -*-
'''

Requires a configuration section, for example:

[atomtools]

entries = /path/to/entry/files/*.atom
feed_envelope = <feed xmlns="http://www.w3.org/2005/Atom"><title>My feed</
title><id>http://example.com/myfeed</id></feed>

'''

import sys
from datetime import datetime, timedelta
import glob

import amara
from amara import bindery
from amara.tools import atomtools

from akara.services import simple_service


#text/uri-list from RFC 2483
SERVICE_ID = 'http://purl.org/akara/services/demo/atom.json'
@simple_service('GET', SERVICE_ID, 'akara.atom.json', 'application/json')
def atom_json(url=None):
    '''
    Convert Atom syntax to Exhibit JSON
    (see: http://www.ibm.com/developerworks/web/library/wa-realweb6/ ; this is based on listing 3)
    
    Sample request:
    * curl "http://localhost:8880/akara.atom.json?url=url=http://zepheira.com/feeds/news.atom"
    * curl "http://localhost:8880/akara.atom.json?url=http://picasaweb.google.com/data/feed/base/user/dysryi/albumid/5342439351589940049"
    * curl "http://localhost:8880/akara.atom.json?url=http://earthquake.usgs.gov/eqcenter/catalogs/7day-M2.5.xml"
    '''
    # From http://code.google.com/p/simplejson/
    import simplejson
    entries = atomtools.ejsonize(url)
    return simplejson.dumps({'items': entries}, indent=4)


# These come from the "[atomtools]" section of the Akara configuration file
ENTRIES = AKARA.module_config.get('entries')
FEED_ENVELOPE = AKARA.module_config.get('feed_envelope')

#print >> sys.stderr, "Entries:", ENTRIES
#print >> sys.stderr, "Feed envelope:", FEED_ENVELOPE

#FIXME: use stat to check dir and apply a cache otherwise
DOC_CACHE = None

SERVICE_ID = 'http://purl.org/akara/services/demo/aggregate.atom'
@simple_service('GET', SERVICE_ID, 'akara.aggregate.atom', str(atomtools.ATOM_IMT))
def aggregate_atom():
    '''
    Sample request:
    * curl "http://localhost:8880/akara.aggregate.atom"
    '''
    global DOC_CACHE
    refresh = False
    if DOC_CACHE is None:
        refresh = True
    else:
        expiration = DOC_CACHE[1] + timedelta(minutes=15)
        if datetime.now() > expiration:
            refresh = True
    if refresh:
        fnames = glob.glob(ENTRIES)
        doc, metadata = atomtools.aggregate_entries(FEED_ENVELOPE, fnames)
        DOC_CACHE = doc.xml_encode('xml-indent'), datetime.now()
    return DOC_CACHE[0]


#We love Atom, but for sake of practicality, here is a transform for general feeds
SERVICE_ID = 'http://purl.org/akara/services/demo/webfeed.json'
@simple_service('GET', SERVICE_ID, 'akara.webfeed.json', 'application/json')
def webfeed_json(url=None):
    '''
    Convert Web feed to Exhibit JSON
    
    Sample request:
    * curl "http://localhost:8880/akara.webfeed.json?url=http://feeds.delicious.com/v2/rss/recent%3Fmin=1%26count=15"
    '''
    # From http://www.feedparser.org/
    import feedparser
    # From http://code.google.com/p/simplejson/
    import simplejson

    if url is None:
        raise AssertionError("The 'url' query parameter is mandatory.")
    feed = feedparser.parse(url)
    # Note: bad URLs might mean the feed doesn't have headers
    #print >> sys.stderr, "Feed info:", url, feed.version, feed.encoding, feed.headers.get('Content-type')
    
    def process_entry(e):
        data = {
            u'id': e.link,
            u'label': e.link,
            u'title': e.title,
            u'link': e.link,
            u'updated': e.updated,
        }
        #Optional bits
        if 'content' in data:
            data[u'content'] = e.content
        if 'description' in data:
            data[u'description'] = e.description
        if 'author_detail' in data:
            data[u'author_name'] = e.author_detail.name
        return data

    entries = [ process_entry(e) for e in feed.entries ]
    return simplejson.dumps({'items': entries}, indent=4)

