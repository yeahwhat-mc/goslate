#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''Unit test for goslate module
'''

from __future__ import unicode_literals
import sys
import os
import unittest
import doctest        
import goslate
import types
import itertools
import io

from goslate import *
from goslate import _main

__author__ = 'ZHUO Qiang'
__date__ = '2013-05-14'

gs = Goslate(debug=False)

class UnitTest(unittest.TestCase):
    if sys.version < '3':
        pass
    else:
        assertRaisesRegexp = unittest.TestCase.assertRaisesRegex
    
    def assertIsGenerator(self, generator):
        if not isinstance(generator, types.GeneratorType) and not isinstance(generator, itertools.chain):
            raise self.failureException('type is not generator: %s, %s' % (type(generator), generator))
        
    
    def assertGeneratorEqual(self, expectedResult, generator):
        self.assertIsGenerator(generator)
        self.assertListEqual(list(expectedResult), list(generator))
        
    def test_translate_space(self):
        self.assertEqual(u'hallo\n welt', gs.translate('hello\n world', 'de', 'en').lower())
        
    def test_translate_roman(self):
        gs = Goslate(writing=WRITING_ROMAN)
        self.assertEqual(u'', gs.translate(b'\n \n\t\n', 'en'))
        self.assertEqual(u'N\u01d0 h\u01ceo sh\xecji\xe8.'.lower(), gs.translate(b'hello world.', 'zh').lower())
        self.assertEqual(u'heˈlō,həˈlō', gs.translate(b'hello', 'de'))        
        self.assertGeneratorEqual([u'Nín h\u01ceo', u'sh\xecji\xe8'], gs.translate([b'hello', 'world'], 'zh'))

        
    def test_translate_native_and_roman(self):
        gs = Goslate(WRITING_NATIVE_AND_ROMAN)
        self.assertEqual((u'', u''), gs.translate(b'\n \n\t\n', 'en'))
        self.assertEqual((u'你好世界。', u'N\u01d0 h\u01ceo sh\xecji\xe8.'),
                         gs.translate(b'hello world.', 'zh'))
        self.assertEqual((u'Hallo', u''),
                         gs.translate(b'Hello', 'de'))
        
        self.assertGeneratorEqual([(u'您好', u'Nín h\u01ceo'), (u'世界', u'sh\xecji\xe8')],
                                  gs.translate([b'hello', 'world'], 'zh'))
        
        
    def test_translate(self):
        self.assertEqual(u'', gs.translate(b'\n \n\t\n', 'en'))
        
        self.assertEqual(u'你好世界。', gs.translate(b'hello world.', 'zh'))
        self.assertEqual(u'Hello World.', gs.translate(u'你好世界。', 'en', 'zh'))
        self.assertEqual(u'Hello World.', gs.translate(u'你好世界。'.encode('utf-8'), 'en'))
        self.assertEqual(u'你好世界。', gs.translate(b'hello world.', 'zh-cn', u'en'))
        self.assertEqual(u'你好世界。', gs.translate(b'hallo welt.', u'zh-CN'))
        self.assertEqual(u'你好世界。', gs.translate(u'hallo welt.', 'zh-CN', 'de'))
        
        self.assertRaisesRegexp(Error, 'invalid target language', gs.translate, '', '')
        
        self.assertNotEqual(u'你好世界。', gs.translate(b'hallo welt.', u'zh-CN', 'en'))

        test_string = b'helloworld'
        exceed_allowed_times = int(gs._MAX_LENGTH_PER_QUERY / len(test_string) + 10)
        self.assertRaisesRegexp(Error, 'input too large', gs.translate, test_string*exceed_allowed_times, 'zh')

        self.assertRaisesRegexp(Error, 'invalid target language', gs.translate, 'hello', '')
        
        self.assertEqual(u'你好世界。\n\n您好', gs.translate(u'\n\nhello world.\n\nhello\n\n', 'zh-cn'))

        test_string = u'hello!    '
        exceed_allowed_times = int(gs._MAX_LENGTH_PER_QUERY / len(test_string) + 10)
        self.assertEqual(u'您好！'*exceed_allowed_times, gs.translate(test_string*exceed_allowed_times, 'zh'))
        

    def test_translate_batch_input(self):
        self.assertGeneratorEqual([], gs.translate((), 'en'))        
        self.assertGeneratorEqual([u''], gs.translate([b'\n \n\t\n'], 'en'))
        self.assertGeneratorEqual([u'你好世界。'], gs.translate([u'hello world.'], 'zh-cn'))
        self.assertGeneratorEqual([u'你好世界。'], gs.translate([b'hello world.'], 'zh-CN', u'en'))
        self.assertGeneratorEqual([u'你好世界。'], gs.translate([b'hallo welt.'], u'zh-CN'))
        self.assertGeneratorEqual([u'你好世界。\n\n您好'], gs.translate([b'\n\nhello world.\n\nhello\n\n'], 'zh-cn'))
        self.assertNotEqual([u'你好世界。'], gs.translate([b'hallo welt.'], 'zh-CN', 'en'))
        self.assertRaisesRegexp(Error, 'invalid target language', gs.translate, [''], u'')
        
        test_string = b'hello!    '
        exceed_allowed_times = int(gs._MAX_LENGTH_PER_QUERY / len(test_string) + 10)
        self.assertGeneratorEqual([u'您好！'*exceed_allowed_times]*3, gs.translate((test_string*exceed_allowed_times,)*3, 'zh'))
        self.assertGeneratorEqual([u'你好世界。', u'您好'], gs.translate([b'\n\nhello world.\n', b'\nhello\n\n'], 'zh-cn'))
        

    def test_translate_batch_input_exceed(self):
        test_string = b'helloworld'
        exceed_allowed_times = int(gs._MAX_LENGTH_PER_QUERY / len(test_string) + 1)        
        self.assertRaisesRegexp(Error, 'input too large', list, gs.translate((u'hello', test_string*exceed_allowed_times, ), 'zh'))
        
        
    def test_translate_batch_input_with_empty_string(self):
        self.assertGeneratorEqual([u'你好世界。', u''], gs.translate([u'hello world.', u''], 'zh-cn'))
        self.assertGeneratorEqual([u'你好世界。', u'', u'您好'], gs.translate([u'hello world.', u'', u'hello'], 'zh-cn'))
        self.assertGeneratorEqual([u'', u'你好世界。'], gs.translate([u'', u'hello world.'], 'zh-cn'))        
        
        
    def test_detect(self):
        self.assertEqual('en', gs.detect(b''))
        self.assertEqual('en', gs.detect(b'\n\r  \n'))
        self.assertEqual('en', gs.detect(b'hello world'))
        self.assertEqual('zh-CN', gs.detect(u'你好世界'.encode('utf-8')))
        self.assertEqual('de', gs.detect(u'hallo welt.'))
        
        self.assertEqual('zh-CN', gs.detect(u'你好世界'.encode('utf-8')*1000))
        
    def test_detect_batch_input(self):
        times = 10
        self.assertGeneratorEqual(['en', 'zh-CN', 'de', 'en']*10,
                                  gs.detect((u'hello world', u'你好世界'.encode('utf-8'), u'hallo welt.', '')*10))

        self.assertGeneratorEqual(['en', 'zh-CN', 'de', 'en']*10,
                                  gs.detect([b'hello world'*10, u'你好世界'*100, b'hallo welt.'*times, u'\n\r \t'*times]*10))


    def test_translate_massive_input(self):
        times = 10
        source = (u'hello world. ' for i in range(times))
        result = gs.translate((i.encode('utf-8') for i in source), 'zh-cn')
        self.assertGeneratorEqual((u'你好世界。' for i in range(times)), result)

        
    def test_main(self):
        encoding = sys.getfilesystemencoding()
        # sys.stdout = StringIO()
        
        sys.stdout = io.BytesIO()
        sys.stdin = io.BytesIO(b'hello world')
        sys.stdin.buffer = sys.stdin
        _main([sys.argv[0], '-t', 'zh-CN'])
        self.assertEqual(u'你好世界\n'.encode(encoding), sys.stdout.getvalue())
        
        sys.stdout = io.BytesIO()
        sys.stdin = io.BytesIO(u'你好'.encode(encoding))
        sys.stdin.buffer = sys.stdin
        _main([sys.argv[0], '-t', 'en'])
        self.assertEqual(u'Hello\n'.encode(encoding), sys.stdout.getvalue())
        
        sys.stdout = io.BytesIO()
        sys.stdin = io.BytesIO(b'hello world')
        sys.stdin.buffer = sys.stdin        
        _main([sys.argv[0], '-t', 'zh-CN', '-o', 'utf-8'])
        self.assertEqual(u'你好世界\n'.encode('utf-8'), sys.stdout.getvalue())
        
        sys.stdout = io.BytesIO()        
        sys.stdin = io.BytesIO(u'你好'.encode('utf-8'))
        sys.stdin.buffer = sys.stdin                
        _main([sys.argv[0], '-t', 'en', '-i', 'utf-8'])
        self.assertEqual(u'Hello\n'.encode(encoding), sys.stdout.getvalue())
        
        sys.stdout = io.BytesIO()        
        with open('for_test.tmp', 'w') as f:
            f.write('hello world')
        _main([sys.argv[0], '-t', 'zh-CN', f.name])
        self.assertEqual(u'你好世界\n'.encode(encoding), sys.stdout.getvalue())
        
        sys.stdout = io.BytesIO()        
        with open('for_test.tmp', 'w') as f:
            f.write('hello world')
        _main([sys.argv[0], '-t', 'zh-CN', '-o', 'utf-8', f.name])
        self.assertEqual(u'你好世界\n'.encode('utf-8'), sys.stdout.getvalue())
        
        sys.stdout = io.BytesIO()
        with io.open('for_test.tmp', 'w', encoding=encoding) as f:
            f.write(u'你好')
        _main([sys.argv[0], '-t', 'en', f.name])
        self.assertEqual(u'Hello\n'.encode(encoding), sys.stdout.getvalue())
        
        sys.stdout = io.BytesIO()
        with io.open('for_test.tmp', 'w', encoding='utf-8') as f:
            f.write(u'你好')
        _main([sys.argv[0], '-t', 'en', '-i', 'utf-8', f.name])
        self.assertEqual(u'Hello\n'.encode(encoding), sys.stdout.getvalue())

        sys.stdout = io.BytesIO()        
        with io.open('for_test.tmp', 'w', encoding='utf-8') as f:
            f.write(u'你好')
        with io.open('for_test_2.tmp', 'w', encoding='utf-8') as f2:
            f2.write(u'世界')
            
        _main([sys.argv[0], '-t', 'en', '-i', 'utf-8', f.name, f2.name])
        self.assertEqual(u'Hello\nWorld\n'.encode(encoding), sys.stdout.getvalue())
        

    def test_get_languages(self):
        expected = {
            'el': 'Greek',
            'eo': 'Esperanto',
            'en': 'English',
            'zh': 'Chinese',
            'af': 'Afrikaans',
            'sw': 'Swahili',
            'ca': 'Catalan',
            'it': 'Italian',
            'iw': 'Hebrew',
            'cy': 'Welsh',
            'ar': 'Arabic',
            'ga': 'Irish',
            'cs': 'Czech',
            'et': 'Estonian',
            'gl': 'Galician',
            'id': 'Indonesian',
            'es': 'Spanish',
            'ru': 'Russian',
            'nl': 'Dutch',
            'pt': 'Portuguese',
            'mt': 'Maltese',
            'tr': 'Turkish',
            'lt': 'Lithuanian',
            'lv': 'Latvian',
            'tl': 'Filipino',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'ro': 'Romanian',
            'is': 'Icelandic',
            'pl': 'Polish',
            'yi': 'Yiddish',
            'be': 'Belarusian',
            'fr': 'French',
            'bg': 'Bulgarian',
            'uk': 'Ukrainian',
            'sl': 'Slovenian',
            'hr': 'Croatian',
            'de': 'German',
            'ht': 'Haitian Creole',
            'da': 'Danish',
            'fa': 'Persian',
            'hi': 'Hindi',
            'fi': 'Finnish',
            'hu': 'Hungarian',
            'ja': 'Japanese',
            'zh-TW': 'Chinese (Traditional)',
            'sq': 'Albanian',
            'no': 'Norwegian',
            'ko': 'Korean',
            'sv': 'Swedish',
            'mk': 'Macedonian',
            'sk': 'Slovak',
            'zh-CN': 'Chinese (Simplified)',
            'ms': 'Malay',
            'sr': 'Serbian',}
        
        result = gs.get_languages()
        expected_keys = set(expected.keys())
        result_keys = set(result.keys())
        self.assertLessEqual(expected_keys, result_keys)
        for key, value in expected.items():
            self.assertEqual(value, result.get(key, None))
            
        # self.assertDictEqual(expected, gs.get_languages())
        
        
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(goslate))
    return tests        
        

if __name__ == '__main__':
    unittest.main()
