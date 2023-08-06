# -*- python -*-
# Copyright (C) 2008, Charles Wang <charlesw1234@163.com>
# Author: Charles Wang <charlesw1234@163.com>

from random import random
from string import join as strjoin

from paste.request import path_info_split
from paste.fileapp import DataApp
from paste.deploy.converters import asbool

from _pickey import GetPNG

def str2kcs(kcsname):
    kcsarr = kcsname.split(',')
    mark_digit = False; mark_lower = False; mark_upper = False
    for kcs in kcsarr:
        if kcs.lower() == 'digit': mark_digit = True
        elif kcs.lower() == 'lower': mark_lower = True
        elif kcs.lower() == 'upper': mark_upper = True
        elif kcs.lower() == 'letter': mark_lower = True; mark_upper = True
    result = ''
    if mark_digit: result = result + '0123456789'
    if mark_lower: result = result + 'abcdefghijklmnopqrstuvwxyz'
    if mark_upper: result = result + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return result

def str2clr(clrname, rgb = None):
    """
    Three formats of color are accepted:
     * #RRGGBB
     * #RGB
     * Color name: Which is defined in the rgb file.
    """
    lcn = clrname.lower()
    if lcn[0] == '#' and len(lcn) == 4:
        r = int(lcn[1], 16)
        g = int(lcn[2], 16)
        b = int(lcn[3], 16)
        return ((r << 4) | r, (g << 4) | g, (b << 4) | b)
    elif lcn[0] == '#' and len(lcn) == 7:
        return (int(lcn[1:3], 16), int(lcn[3:5], 16), int(lcn[5:7], 16))
    elif rgb is not None:
        try:
            f = file(rgb)
            for ln in f:
                ln = ln.strip()
                if ln[0] == ';': continue
                r, g, b, cn = ln.split(None, 3)
                if lcn != cn.lower(): continue
                return (int(r), int(g), int(b))
            f.close()
        except IOError:
            pass
    raise ValueError, 'Unrecognized color name: %s' % clrname

class PicKey(object):
    """Picture confirmation code generation class.

    "PicKey" use "gd" to render the output picture.

    PicKey accept many options to control the generation of key picture.

    ``suffix``
    The appended url to show the generated key picture. The default
    value is 'pickey'.

    ``keylen``
    The length of the generated key, The default value is 6.

    ``keycharset``
    Decide which characters can be used in the generated key. It can
    be any combination of digit, lower, upper, letter. The default
    value is 'digit,letter'.

    ``charwidth``
    The width of a single character. Used to control the width of the
    generated picture. The default value is 24.

    ``charheight``
    The height of a single character. Used to control the height of the
    generated picture. The default value is 40.

    ``rgbpath``
    The name of the rgb file. rgb.txt provided by X11/xorg can be used
    directly. If not provided, not any named color can be recognized.
    For the system with X11/xorg, /usr/share/X11/rgb.txt might be usable.

    ``monochrome``
    Whether use different color to render characters in key or not.
    The default value is false.

    ``monofont``
    Whether use different font to render characters in key or not.
    The default value is true.

    ``background``
    Provide the background color of the generated picture. The default
    value is #FFFFFF. The value of background can be #FFF or #FFFFF.
    If rgbpath is provided, the color name in that file is valid too.

    ``minptsize``
    The minimum percentage of the full size character. The default
    value is 60.

    ``maxptsize``
    The maximum percentage of the full size character. The default
    value is 100. Render all choose ptsize between minptsize and
    maxptsize randomly, so we get the result with different font size.

    ``dot_limit``
    The maximum number of noise point per character. The default value is 32.

    ``line_limit``
    The maximum number of noise line per character. The default value is 2.

    ``fontpathes``
    The list of ttf font files which can be used to render characters.
    If more then one font files are provided and monofont is set too
    Trie, so the different font might be shown in a single generated
    picture. The font file path is separated by space. Now, there is
    no way to include file pathes which contain space...

    """
    def __init__(self, configs, cfglist):
        self.configs = configs
        self.cfglist = cfglist
        self.keylen = int(self.config_get('keylen', '6'))
        self.keycset = str2kcs(self.config_get('keycharset', 'digit,letter'))
        self.charwidth = int(self.config_get('charwidth', '24'))
        self.charheight = int(self.config_get('charheight', '40'))
        self.rgbpath = self.config_get('rgbpath', None)
        self.render_kwargs = {}
        self.render_kwargs_get('monochrome', asbool)
        self.render_kwargs_get('monofont', asbool)
        self.render_kwargs_get('background', str2clr, rgbpath = self.rgbpath)
        self.render_kwargs_get('minptsize', int)
        self.render_kwargs_get('maxptsize', int)
        self.render_kwargs_get('dot_limit', int)
        self.render_kwargs_get('line_limit', int)
        self.render_kwargs_get('fontpathes', str)

    def config_get(self, name, defvalue):
        for cfg in self.cfglist:
            if cfg + name in self.configs: return self.configs[cfg + name]
        return defvalue

    def render_kwargs_get(self, name, func, **kwargs):
        for cfg in self.cfglist:
            if cfg + name in self.configs:
                self.render_kwargs[name] = func(self.configs[cfg + name],
                                                **kwargs)

    def get_png(self):
        key = strjoin(map(lambda idx:
                              self.keycset[int(random() * len(self.keycset))],
                          xrange(self.keylen)), '')
        png = GetPNG(key, self.keylen * self.charwidth,
                     self.charheight, ** self.render_kwargs)
        return (key, png)

class application(object):
    def __init__(self, app, global_conf, **kwargs):
        """Initialize the Authentication Picture Key Middleware

        This WSGI application use "Beaker" to do session management and save
        the key value into environ['beaker.session']['pickey.displayed_key'],
        so the wrapped application can use it. If session type is cookie, it
        must be encrypted to avoid hack.
        """
        self.app = app
        self.pickey = PicKey(kwargs, ['pickey.'])
        self.pathinfo = kwargs.get('pickey.pathinfo', '/pickey.png')

    def __call__(self, environ, start_response):
        session = environ['beaker.session']
        if environ['PATH_INFO'] != self.pathinfo:
            return self.app(environ, start_response)
        key, png = self.pickey.get_png()
        session['pickey.displayed_key'] = key
        session.save()
        app = DataApp(png, content_type = "image/png")
        return app(environ, start_response)

def pickey_filter_factory(global_conf, **kwargs):
    def filter(app):
        return application(app, global_conf, **kwargs)
    return filter
