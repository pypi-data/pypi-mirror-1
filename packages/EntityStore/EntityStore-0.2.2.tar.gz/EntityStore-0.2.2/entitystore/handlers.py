#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from collections import defaultdict
from rdflib import Literal

# # If a fedora-like interface appears useful....
#browse_p = re.compile(r"""^(?P<store_name>[^/]+)   # for '/{store_name}/browse/{id}/parts/{path}
#                          /browse/
#                          (?P<id>[^/]+)
#                          ((?P<part>/parts[/]?)
#                          (?P<path>.*)
#                          )?""", re.VERBOSE|re.I)

objects_p = re.compile(r"""^(?P<store_name>[^/]+)   # for '/{store_name}/objects/{id}/{path}
                          /objects/
                          (?P<id>[^/]+)
                          (/(?P<path>.*))?""", re.VERBOSE|re.I)

patterns = {
            #'browse':browse_p,
            'objects':objects_p
            }
            

def parse_input(**kw):

    # Matches   "<---> <---> <--->. <---> <---> <--->. <---> <---> "---". " 
    # ntriples style, but . delimiter is enough - no newline char needed
    # also namespaces will be excepted eg "<foaf:name>"
    # each triple must end with a . however.
    faux_nt = re.compile(r"""   #  use faux_nt.finditer to work through all the matches
                          (
                          <               # < ...
                          (?P<s>[^>]+)    # get the subject as 's'
                          >               # >
                          \s+             # one or more space chars
                          <               # <
                          (?P<p>[^>]+)    # predicate as'p'
                          >               # >
                          \s+             # one or more space chars
                          )
                          ((
                          <
                          (?P<o>[^>]*)    # object as o - *can* be blank
                          >
                          \s*
                          \.             # *zero* or more space chars
                          )
                          |              #  <xxx> OR "xxx"
                          (
                          "
                          (?P<l>[^"]*)    # literal as l
                          "
                          \s*            # *zero* or more space chars
                          \.             # fullstop terminator
                          ))
                          """, re.UNICODE|re.VERBOSE)

    # Matches   "prefix:  namespace ;prefix: namespace;prefix:  namespace;"
    # namespace must end in # or / and there must be at least one ;
    namespace_p = re.compile(r"""
                          (?P<prefix>[A-z0-9]+)     # any prefix name
                          \s*                       # zero or more spaces
                          :                         #  :
                          \s*                       # zero or more spaces
                          (?P<namespace>
                          [^:/#?]+://               # 'scheme'://  (eg http://)
                          [^?#;]+                   # 'host/path/....'
                          [#/])                     # Must end with a # or a / 
                          \s*                       # zero or more spaces
                          ;                         # Delimiter ;
                          """, re.UNICODE|re.VERBOSE)
                          
    response = defaultdict(list)
    for verb in ['setnamespaces']:
        if verb in kw:
            for match in namespace_p.finditer(kw[verb]):
                if match.group('prefix') and match.group('namespace'):
                    response[verb].append((match.group('prefix'), match.group('namespace')))
    for verb in ['add','del']:
        if verb in kw:
            for match in faux_nt.finditer(kw[verb]):
                if match:
                    if match.group('l'):
                        response[verb].append((match.group('s'), 
                                               match.group('p'), 
                                               Literal(match.group('l'))))
                    elif match.group('o'):
                        response[verb].append((match.group('s'), 
                                               match.group('p'), 
                                               match.group('o')))
                    elif match.group('s') and match.group('p'):
                        response[verb].append((match.group('s'), 
                                               match.group('p'), 
                                               None))
    
    return response

def storeapi_parse(path):
    # Handle null
    if not path:
        return {'type':'empty'}
    fragments = path.split('/',1)
    if len(fragments) == 1 or (len(fragments)==2 and fragments[1] == ''):
        # store request
        return {'type':'store', 'store_name':fragments[0]}
    elif len(fragments) == 2:
        # stores/{store_name}/{access_type}
        store_name = fragments[0]
        fragments = fragments[1].split('/',1)
        if len(fragments)==1 or (len(fragments)==2 and fragments[1] == ''):
            api = fragments.pop(0)
            if api in patterns:
                return {'type':'root', 'store_name':store_name, 'api':api}
            else:
                raise Exception("Path not understood")
        else:
            api = fragments.pop(0)
            if api not in patterns:
                raise Exception("Path not understood")
            for api in patterns:
                m = patterns[api].match(path)
                if m != None:
                    d = {'api':api, 'type':'api'}
                    d.update(m.groupdict())
                    return d
    raise Exception("Path not understood")

