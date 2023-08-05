"""h2aproxy - WSGI app proxy for hAtom2Atom.xsl transformations.

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

from cgi import parse_qs
import urllib2

from kid import Template
try:
    import tidy
    has_tidy = True
except:
    has_tidy = False

from hatom2atom import settings, util


def h2a_proxy(environ, start_response):
    """WSGI app to proxy hAtom2Atom transformations of any URL."""
    messages = []
    response_status = '200 OK'
    qs = parse_qs(environ['QUERY_STRING'])
    url = qs.get('url', [''])[0]
    tidyme = qs.get('tidy', ['yes'])[0].lower()
    ctype = qs.get('ctype', [settings.default_ctype])[0]
    if url:
        try:
            f = util.url_opener(environ).open(url)
            url = f.geturl()
            response_text = f.read()
            try:
                if has_tidy and tidyme == 'yes':
                    tidydoc = tidy.parseString(response_text, 
                                               **settings.tidy_options)
                    response_text = str(tidydoc)
                atom = util.easy_transform(settings.stylesheet, 
                                          response_text,
                                          {'source-uri':"'%s'" % url})
                start_response(response_status, 
                               [('Content-Type', 
                                 '%s; charset=utf-8' % ctype)])
                return [atom]
            except Exception, e:
                response_status = "502 Bad Gateway"
                messages.append(str(e))
        except Exception, e:
            response_status = "500 Internal Server Error"
            messages.append(str(e))
    start_response(response_status, [('Content-Type', 'text/html')])
    t = Template(file=settings.kid_template, 
                 url=url, 
                 messages=messages, 
                 settings=settings,
                 has_tidy=has_tidy)
    return t.generate()


def run():
    """Run the proxy using flup's SCGI server."""
    settings.WSGIServer(h2a_proxy, 
                        bindAddress=(settings.host, settings.port), 
                        loggingLevel=settings.log_level).run()


if __name__ == '__main__':
    run()

