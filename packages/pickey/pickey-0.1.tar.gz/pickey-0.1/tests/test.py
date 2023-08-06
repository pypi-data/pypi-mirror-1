#!/usr/bin/python

import random
import string

import _pickey

keychars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
key = map(lambda idx:
              keychars[int(random.random() * len(keychars))],
          range(4))
key = string.join(key, '')
s = _pickey.GetPNG(key, 160, 48, dot_limit = 32)
f = file('x.png', 'w')
f.write(s)
f.close()
