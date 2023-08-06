# -*- encoding: utf-8 -*-
'''
Useful tools for discovery
'''

import amara

from akara.services import simple_service
from akara.pipeline import register_pipeline

SERVICE_ID = 'http://purl.org/akara/services/demo/discovery.converter.txt'
@simple_service('POST', SERVICE_ID, 'discovery.converter.txt', 'text/xml')
def text_discovery(body, ctype):
    '''
    Discovery in text form.  Designed to be used in a pipeline.
    '''
    #curl http://localhost:8880/ | curl --request POST --data-binary "@-" http://localhost:8880/akara.discovery.text
    transformed = []
    doc = bindery.parse(body)
    for service in doc.services.service:
        transformed.append(service.ident)
        transformed.append(unicode(service.path))
        transformed.append(unicode(service.description))
        transformed.append('')
    
    return '\n'.join(transformed)


register_pipeline('http://purl.org/akara/services/demo/discovery.txt',
                 'discovery.txt',
                 stages = ['http://purl.org/xml3k/akara/services/registry',
                           'http://purl.org/akara/services/demo/discovery.converter.txt'])

