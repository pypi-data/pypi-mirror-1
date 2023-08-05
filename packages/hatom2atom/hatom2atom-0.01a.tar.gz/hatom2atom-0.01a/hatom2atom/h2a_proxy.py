"""h2a_proxy - WSGI app proxy for hAtom2Atom.xsl transformations.

this file is part of the hatom2atom package.

created and maintained by luke arno <luke.arno@gmail.com>

copyright (c) 2006  Luke Arno  <luke.arno@gmail.com>

this program is free software; you can redistribute it and/or
modify it under the terms of the gnu general public license
as published by the free software foundation; either version 2
of the license, or (at your option) any later version.

this program is distributed in the hope that it will be useful,
but without any warranty; without even the implied warranty of
merchantability or fitness for a particular purpose.  see the
gnu general public license for more details.

you should have received a copy of the gnu general public license
along with this program; if not, write to:

the free software foundation, inc., 
51 franklin street, fifth floor, 
boston, ma  02110-1301, usa.

luke arno can be found at http://lukearno.com/
"""
import settings
from util import *
#import kid; kid.enable_import(); from proxy_page import Template
from kid import Template
from pkg_resources import resource_filename, resource_string
from cgi import parse_qs
from urllib2 import urlopen, URLError

def h2a_proxy(environ, start_response):
    """WSGI app to proxy hAtom2Atom transformations of any URL."""
    messages = []
    url = parse_qs(environ['QUERY_STRING']).get('url', [""])[0]
    if url:
        try:
            # this line is just to get setuptools to put to put a 
            # supporting files on the filesystem for the engine:
            [resource_filename(__name__, f) for f in settings.xslt_support]
            xsl_file = resource_filename(__name__, settings.xslt)
            atom = easy_transform(xsl_file, urlopen(url))
            start_response('200 OK', [('Content-Type', 'text/xml')])
            return [atom]
        except Exception, e:
            messages.append(str(e))
    start_response('200 OK', [('Content-Type', 'text/html')])
    #t = Template(url=url, messages=messages)# settings=settings)
    t = Template(source=resource_string(__name__, settings.template), 
                 url=url, 
                 messages=messages, 
                 settings=settings)
    return [t.serialize()]

def run():
    """Run the proxy using flup's SCGI server."""
    settings.WSGIServer(h2a_proxy, 
                        bindAddress=(settings.host, settings.port), 
                        loggingLevel=settings.log_level).run()

if __name__ == '__main__':
    run()
