import test_temp01
import sys, locale
from codecs import EncodedFile

#locale.setlocale(locale.LC_CTYPE, '')
#encoding = locale.getlocale(locale.LC_CTYPE)[1]
encoding = 'big5'
stdout = EncodedFile(sys.stdout, encoding, encoding)
out = {'test': {'data': [], 'foo': '393j', 'boo': 'g99'}}
cur = out['test']['data']
cur.append({'foo': 'mamami', 'boo': 'what?'})
cur.append({'foo': 'luke', 'boo': 'use force'})
cur.append({'foo': 'john', 'boo': 'read book'})

test_temp01.template(out, stdout)
