# -*- encoding: utf-8 -*-
'''
'''

import sys, time, re
import urllib2
import httplib
import datetime
from itertools import *

# http://pypi.python.org/pypi/simplejson
import simplejson

from amara.tools.atomtools import feed, ATOM_IMT
from akara.services import simple_service

from amara.lib import U
from amara.writers.struct import structwriter, E, NS, ROOT, RAW

#SERVICE_ID = 'http://purl.org/akara/services/demo/exhibit2atom.json'
#@simple_service('POST', SERVICE_ID, 'akara.wwwlog.json', 'application/json')

ATOM_ENVELOPE = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>%s</title>
  <id>%s</id>
</feed>
'''

#curl --request POST --data-binary "@-" "http://localhost:8880/exhibit.atom?title=hello+world&id=xyz" < /Users/uche/old/tmp/partners.json

SERVICE_ID = 'http://purl.org/akara/services/demo/exhibit.atom'
@simple_service('POST', SERVICE_ID, 'exhibit.atom', ATOM_IMT)
def exhibit2atom(body, ctype, id, title):
    '''
    Convert Exhibit JSON to Atom
    (see: http://www.ibm.com/developerworks/web/library/wa-realweb6/ )

    Sample request:
    * curl --request POST --data-binary "@foo.js" "http://localhost:8880/exhibit.atom"

    '''
    env = ATOM_ENVELOPE%(title, id)
    #f = feed(env, title=title, id=id.decode('utf-8'))
    f = feed(env, title=title, id=id)
    #FIXME: Need a link
    #f.feed.xml_append(E((ATOM_NAMESPACE, u'link'), {u'rel': u'self', u'type': u'application/atom+xml', u'href': self_link.decode('utf-8')}))

    #for item in doc.xml_select(u'//*[@class="result_table"]//*[@class="article_title"]'):
    items = simplejson.loads(body)[u'items']
    for item in items:
        f.append(
            item[u'id'],
            title=item[u'label'],
            updated=item.get(u'updated', '2010-01-01'),
            summary=item.get(u'description', ''),
            #authors=authors,
            #links=links,
            #categories=categories,
            #elements=elements,
        )

        #Retrieve the DSpace page
        #authors = [ (a, None, None) for a in resource.get(u'creator', '') ]
        #links = [
        #    (DSPACE_ARTICLE_BASE + rel_id, u'alternate'),
        #    (u'dspace?id=' + dspace_id, u'self'),
        #]
        #elements = [
        #    E((ATOM_NAMESPACE, u'content'), {u'src': alt_link}),
        #]

    #FIXME: indent
    return f.xml_encode()

