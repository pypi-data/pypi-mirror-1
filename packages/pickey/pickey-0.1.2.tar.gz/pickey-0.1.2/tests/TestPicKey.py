# -*- python -*-
# Copyright (C) 2008, Charles Wang <charlesw1234@163.com>
# Author: Charles Wang <charlesw1234@163.com>

import string
from paste.wsgilib import parse_querystring
from paste.request import construct_url

class application(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, environ, start_response):
        session = environ['beaker.session']
        key = dict(parse_querystring(environ)).get('key', None)
        status = '200 OK'
        pickeysrc = construct_url(environ, path_info = '/pickey.png')
        output = []
        output.append('<html><body>')
        output.append('<p>SCRIPT_NAME: %r</p>' % (environ['SCRIPT_NAME'],))
        output.append('<p>PATH_INFO: %r</p>' % (environ['PATH_INFO'],))
        output.append('<p>picture link: %r</p>' % pickeysrc)
        if key is None:
            output.append('<p>Not any key is inputted yet.</p>')
        elif not session.has_key('pickey.displayed_key'):
            output.append('<p>Not any key is displayed yet.</p>')
        elif key == session['pickey.displayed_key']:
            output.append('<p>Key Check successed: %r</p>' % (key,))
        else:
            output.append('<p>Key Check failed: %s != %s</p>' %\
                              (key, session['pickey.displayed_key']))
        output.append('<p>The Key is <img src="%s"/></p>' % pickeysrc)
        output.append('<form><input name="key"/><input type="submit"/></form>')
        output.append('</body></html>')
        output = string.join(output, '\n')
        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]
