#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
'''

import goslate

__author__ = 'qiangz'
__date__ = '2015-04-08 16:26'
__version_info__ = (0, 1, 0)
__version__ = '.'.join(str(i) for i in __version_info__)


go = goslate.Goslate(debug=True, writing=goslate.WRITING_NATIVE_AND_ROMAN)

print(u'Translation: {}, Roman writing: {}'.format(*go.translate('hello', 'zh')))
