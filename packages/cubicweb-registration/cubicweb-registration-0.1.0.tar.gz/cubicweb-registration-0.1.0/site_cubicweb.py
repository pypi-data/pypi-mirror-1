# -*- coding: utf-8 -*-
from os.path import dirname, abspath, join
HERE = abspath(dirname(__file__))
options = (
    ('cypher-seed',
     {'type' : 'string',
      'default': u"this is my dummy registration cypher seed",
      'help': 'seed used to cypher registration data in confirmation email link',
      'group': 'registration', 'inputlevel': 2,
      }),
    ('captcha-font-file',
     {'type' : 'string',
      'default': join(HERE, 'data', 'porkys.ttf'),
      'help': 'True type font to use for captcha image generation',
      'group': 'registration', 'inputlevel': 2,
      }),
    ('captcha-font-size',
     {'type' : 'int',
      'default': 25,
      'help': 'Font size to use for captcha image generation',
      'group': 'registration', 'inputlevel': 2,
      }),
    )
