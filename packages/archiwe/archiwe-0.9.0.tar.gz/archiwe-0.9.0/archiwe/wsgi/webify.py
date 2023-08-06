#!/usr/bin/env python
#****************************************************************
# File: ./archiwe/wsgi/webify.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************

from hakmatak.w10n import W10n
from hakmatak.wsgi.webify import Handler

from archiwe.constant import APP_NAME,APP_VERSION
from archiwe.store import ReaderClassFactory

# wsgi entry point
def application(environ, start_response):
    w10n = W10n()
    w10n.application = "%s/%s-%s" % (w10n.application,APP_NAME,APP_VERSION)
    handler = Handler(
        storeReaderClassFactory=ReaderClassFactory(),
        w10n=w10n
        )
    return handler.do(environ, start_response)

# cgi entry point
if __name__ == '__main__':
    import wsgiref.handlers
    wsgiref.handlers.CGIHandler().run(application)
