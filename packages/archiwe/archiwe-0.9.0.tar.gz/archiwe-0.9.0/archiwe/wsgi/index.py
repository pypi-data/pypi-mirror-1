#!/usr/bin/env python
#****************************************************************
# File: ./archiwe/wsgi/index.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************

from hakmatak.w10n import W10n
from hakmatak.wsgi.index import Handler

from archiwe.constant import APP_NAME,APP_VERSION

import re

# for identifying those as webifiable
# this must be consistent with rewrite rules in {cgi,wsgi}.archiwe.conf
PATTERN = re.compile('^.*/[^/]+\.(zip|jar|egg|tar|tgz|tar\.(gz|bz2))$')

# wsgi entry point
def application(environ, start_response):
    w10n = W10n()
    w10n.application = "%s/%s-%s" % (w10n.application,APP_NAME,APP_VERSION)
    #handler = Handler(patterns=[],w10n=w10n)
    handler = Handler(w10n=w10n)
    handler.add_pattern(PATTERN)
    return handler.do(environ, start_response)

# cgi entry point
if __name__ == '__main__':
    import wsgiref.handlers
    wsgiref.handlers.CGIHandler().run(application)
