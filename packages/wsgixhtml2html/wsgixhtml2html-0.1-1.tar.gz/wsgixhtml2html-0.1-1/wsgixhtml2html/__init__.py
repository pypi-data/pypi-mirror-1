"""WSGI middleware to serve XHTML pages as HTML for old browsers, while keeping them in standards mode.

Uses Sune Kirkeby's middleware for Django.

Usage (in Pylons, put this in controllers/middleware.py)::

    from wsgixhtml2html import AppWrapper
    app = AppWrapper(app)
"""

import re
from .xhtml import xhtml_to_html, re_ct_xhtml, re_accept_xhtml
import xml.sax
import logging

vary_delim_re = re.compile(r',\s*')
def patch_vary_headers(headers, newheaders):
    """Add newheaders to WSGI headers list (like in Django)"""
    vary = set()
    for existingvary in  [(k,v) for (k,v) in headers if k.lower() == "vary"]: # more of an if
        vary.update(el.lower() for el in vary_delim_re.split(existingvary[1]))
        headers.remove(existingvary)
    for newheader in newheaders:
        vary.add(newheader.lower())
    headers.append(("Vary", ", ".join(vary)))

class AppWrapper(object):
    """Wrapper around an application that changes output XHTML to HTML and sets headers accordingly."""
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        modify_me = [] # transport by reference. i am very open to better suggestsions.

        def _start_response(status, headers, *args, **kwords):
            hd = dict((k.lower(), v) for (k, v) in headers) # don't write -- conversion is one-way

            if status.startswith("206"):
                raise Exception, "Can not translate partial XHTML to HTML." # this is too important to only show up in logs!

            if not status.startswith("304"): # see pylons ticket #313 (http://pylonshq.com/project/pylonshq/ticket/313)
                if not "content-encoding" in hd and re_ct_xhtml.match(hd['content-type']):
                    # we could replace if required

                    patch_vary_headers(headers, ["Accept"]) # tell that we would if we should

                    if not re_accept_xhtml.search(environ.get("HTTP_ACCEPT", "*/*")):
                        # really replace
                        for header in [header for header in headers if header[0].lower() == "content-type"]: # think of it as headers["Content-Type"] = headers["Content-Type"].replace(...)
                            headers.remove(header)
                            headers.append(("Content-Type", header[1].replace("application/xhtml+xml", "text/html")))

                        modify_me.append(True)
                        return start_response(status, headers, *args, **kwords)

            modify_me.append(False)
            return start_response(status, headers, *args, **kwords)

        data = self.application(environ, _start_response)
        assert len(modify_me) == 1, "Application sent data before start_response."
        if modify_me[0]:
            try:
                data = [xhtml_to_html("".join(data))]
            except xml.sax.SAXParseException:
                logging.warn("document served as application/xhtml+xml is not valid.")
        return data
