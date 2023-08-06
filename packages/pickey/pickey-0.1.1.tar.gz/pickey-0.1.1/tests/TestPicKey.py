# -*- python -*-
# Copyright (C) 2008, Charles Wang <charlesw1234@163.com>
# Author: Charles Wang <charlesw1234@163.com>

import string
from paste.wsgilib import parse_querystring
import _pickey

class application(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, environ, start_response):
        session = environ['beaker.session']
        key = dict(parse_querystring(environ)).get('key', None)
        status = '200 OK'
        output = []
        output.append('<html><body>')
        output.append('<p>SCRIPT_NAME: %s</p>' % repr(environ['SCRIPT_NAME']))
        output.append('<p>PATH_INFO: %s</p>' % repr(environ['PATH_INFO']))
        if key is None:
            output.append('<p>Not any key is inputted yet.</p>')
        elif not session.has_key('pickey.displayed_key'):
            output.append('<p>Not any key is displayed yet.</p>')
        elif key == session['pickey.displayed_key']:
            output.append('<p>Key Check successed: %s</p>' % repr(key))
        else:
            output.append('<p>Key Check failed: %s != %s</p>' %\
                              (repr(key),
                               repr(session['pickey.displayed_key'])))
        output.append('<p>The Key is <img src="pickey.png"/></p>')
        output.append('<form><input name="key"/><input type="submit"/></form>')
        output.append('</body></html>')
        output = string.join(output, '\n')
        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]
