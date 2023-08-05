"""settings - settings for hatom2atom

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

import os
import logging

from pkg_resources import resource_filename, Requirement
from flup.server.scgi import WSGIServer


host = 'localhost'
port = 4000
log_level = logging.INFO

stylesheet = 'http://rbach.priv.at/hAtom2Atom/hAtom2Atom.xsl'

kid_template = 'proxypage.kid'
kid_dir = 'kid'
app_name = 'hatom2atom'
app_resource = Requirement.parse(app_name)
kid_dir = resource_filename(app_resource, kid_dir)
kid_template = os.sep.join([kid_dir, kid_template])

default_ctype = 'application/atom+xml'

tidy_options = dict(output_xhtml=1, numeric_entities=1, doctype="omit")

agent = 'hAtom2Atom proxy (http://lukearno.com/projects/hatom2atom/)'
accept = ','.join(['application/xhtml+xml',
                   'application/xml',
                   'text/xml',
                   'text/html;q=0.9',
                   '*/*;q=0.8'])
