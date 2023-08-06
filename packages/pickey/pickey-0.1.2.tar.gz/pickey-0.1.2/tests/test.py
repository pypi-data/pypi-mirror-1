#!/usr/bin/python

import random
import string

import _pickey

keychars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
key = map(lambda idx:
              keychars[int(random.random() * len(keychars))],
          range(4))
key = string.join(key, '')
fontpathes = ['/usr/share/fonts/corefonts/arialbd.ttf',
              '/usr/share/fonts/corefonts/courbd.ttf',
              '/usr/share/fonts/corefonts/timesbd.ttf']
s = _pickey.GetPNG(key, 160, 48, dot_limit = 32,
                   fontpathes = string.join(fontpathes, '  \t\n'))
f = file('x.png', 'w')
f.write(s)
f.close()
