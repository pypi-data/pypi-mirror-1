"""settings - settings for rdfa2rdf

This program is free software; you can redistribute it and/or
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

"""

import os
import logging
import sys

from pkg_resources import resource_filename, Requirement
from flup.server.scgi import WSGIServer


host = '127.0.0.5'
port = 4000
log_level = logging.INFO

stylesheet = 'http://ns.inria.fr/grddl/rdfa/2007/09/12/RDFa2RDFXML.xsl'

kid_template = 'proxypage.kid'
kid_dir = 'kid'
app_name = 'rdfa2rdf'
app_resource = Requirement.parse(app_name)
kid_dir = resource_filename(app_resource, kid_dir)
kid_template = os.sep.join([kid_dir, kid_template])

default_ctype = 'application/rdf+xml'

tidy_options = dict(output_xhtml=1, numeric_entities=1, doctype="omit")

"""
agent

Where your proxy is going to be served

agent = 'rdfa2rdf proxy (http://url.of_your.proxy/)'

"""
agent = 'rdfa2rdf proxy (http://tools.weborganics.co.uk/)'
accept = ','.join(['application/xhtml+xml',
		   'application/rdf+xml',
                   'application/xml',
                   'text/xml',
                   'text/html;q=0.9',
                   '*/*;q=0.8'])
