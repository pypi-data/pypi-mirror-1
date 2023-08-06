#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python Bindings for libLZMA
#
# Copyright (c) 2008 Per Øyvind Karlsen <peroyvind@mandriva.org>
# liblzma Copyright (C) 2007-2008  Lasse Collin
# LZMA SDK Copyright (C) 1999-2007 Igor Pavlov
# Based on regressions tests by Joachim Bauch <mail@joachim-bauch.de>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import sys, md5, random
import lzma
import unittest
from binascii import unhexlify
from cStringIO import StringIO
from StringIO import StringIO as PyStringIO

ALL_CHARS = ''.join([chr(x) for x in xrange(256)])

# cache random strings to speed up tests
_random_strings = {}
def generate_random(size, choice=random.choice, ALL_CHARS=ALL_CHARS):
    global _random_strings
    if _random_strings.has_key(size):
        return _random_strings[size]
        
    s = ''.join([choice(ALL_CHARS) for x in xrange(size)])
    _random_strings[size] = s
    return s

class TestlibLZMA(unittest.TestCase):
    
    def setUp(self):
        self.plain = 'This is our mighty test string :o)'
        self.plain_with_eopm = unhexlify('5d00008000ffffffffffffffff002a1a0927641c878e0f81d29e8b130ffeb07336fd10fd6bfacf3d4c90f947b8d07bce7dffffecb00000')
        self.plain_without_eopm = unhexlify('5d000080002200000000000000002a1a0927641c878e0f81d29e8b130ffeb07336fd10fd6bfacf3d4c90f947b8d04af75600')
        self.data_large = "kosogklem"*(1<<18)


    def test_compression_eopm(self):
        # test compression with end of payload marker
        compressed = lzma.compress(self.plain, eopm=True)
        self.assertEqual(compressed, self.plain_with_eopm)

    def test_compression_noeopm(self):
        # test compression without end of payload marker
        compressed = lzma.compress(self.plain, eopm=False)
        self.assertEqual(compressed, self.plain_without_eopm)

    def test_decompression_eopm(self):
        # test decompression with end of payload marker
        decompressed = lzma.decompress(self.plain_with_eopm)
        self.assertEqual(decompressed, self.plain)
        
    def test_decompression_noeopm(self):
        # test decompression without end of payload marker
        decompressed = lzma.decompress(self.plain_without_eopm)
        self.assertEqual(decompressed, self.plain)

    def test_compression_decompression_eopm(self, dictionary_size=1<<23):
        # call compression and decompression on random data of various sizes
        for i in xrange(18):
            size = 1 << i
            original = generate_random(size)
            result = lzma.decompress(lzma.compress(original, eopm=True, dictionary_size=dictionary_size))
            self.assertEqual(len(result), size)
            self.assertEqual(md5.new(original).hexdigest(), md5.new(result).hexdigest())

    def test_compression_decompression_noeopm(self, dictionary_size=1<<23):
        # call compression and decompression on random data of various sizes
        for i in xrange(18):
            size = 1 << i
            original = generate_random(size)
            result = lzma.decompress(lzma.compress(original, eopm=False, dictionary_size=dictionary_size))
            self.assertEqual(len(result), size)
            self.assertEqual(md5.new(original).hexdigest(), md5.new(result).hexdigest())

    def test_multi(self):
        # call compression and decompression multiple times to detect memory leaks...
        for x in xrange(4):
            self.test_compression_decompression_eopm(dictionary_size=1<<26)
            self.test_compression_decompression_noeopm(dictionary_size=1<<26)

    def test_decompression_stream(self):
        # test decompression object in one steps
        decompress = lzma.LZMADecompressor()
        data = decompress.decompress(self.plain_without_eopm)
        data += decompress.flush()
        self.assertEqual(data, self.plain)
    
    def test_decompression_stream_two(self):
        # test decompression in two steps
        decompress = lzma.LZMADecompressor()
        data = decompress.decompress(self.plain_without_eopm[:10])
        data += decompress.decompress(self.plain_without_eopm[10:])
        data += decompress.flush()
        self.assertEqual(data, self.plain)

    def test_decompression_stream_props(self):
        # test decompression with properties in separate step
        decompress = lzma.LZMADecompressor()
        data = decompress.decompress(self.plain_without_eopm[:5])
        data += decompress.decompress(self.plain_without_eopm[5:])
        data += decompress.flush()
        self.assertEqual(data, self.plain)

    def test_decompression_stream_reset(self):
        # test reset
        decompress = lzma.LZMADecompressor()
        data = decompress.decompress(self.plain_without_eopm[:10])
        decompress.reset()
        data = decompress.decompress(self.plain_without_eopm[:15])
        data += decompress.decompress(self.plain_without_eopm[15:])
        data += decompress.flush()
        self.assertEqual(data, self.plain)

    def test_decompression_streaming_eopm(self):
        # test decompressing with one byte at a time...
        decompress = lzma.LZMADecompressor()
        infile = StringIO(self.plain_with_eopm)
        outfile = StringIO()
        while 1:
            data = infile.read(1)
            if not data: break
            outfile.write(decompress.decompress(data, 2)) # why do we need to read two bytes in stead of just one??
        outfile.write(decompress.flush())
        self.assertEqual(outfile.getvalue(), self.plain)

    def test_decompression_streaming_noeopm(self):
        # test decompressing with one byte at a time...
        decompress = lzma.LZMADecompressor()
        infile = StringIO(self.plain_without_eopm)
        outfile = StringIO()
        while 1:
            data = infile.read(1)
            if not data: break
            outfile.write(decompress.decompress(data, 2)) # why do we need to read two bytes in stead of just one??
        outfile.write(decompress.flush())
        self.assertEqual(outfile.getvalue(), self.plain)
    
    def test_compression_stream(self):
        # test compression object in one steps
        compress = lzma.LZMACompressor()
        data = compress.compress(self.plain)
        data += compress.flush()
        self.assertEqual(data, self.plain_with_eopm)
    
    def test_compression_stream_two(self):
        # test compression in two steps
        compress = lzma.LZMACompressor()
        data = compress.compress(self.plain[:10])
        data += compress.compress(self.plain[10:])
        data += compress.flush()
        self.assertEqual(data, self.plain_with_eopm)

    def test_compression_stream_props(self):
        # test compression with properties in separate step
        compress = lzma.LZMACompressor()
        data = compress.compress(self.plain[:5])
        data += compress.compress(self.plain[5:])
        data += compress.flush()
        self.assertEqual(data, self.plain_with_eopm)

    def test_compression_stream_reset(self):
        # test reset
        compress = lzma.LZMACompressor()
        data = compress.compress(self.plain[:10])
        compress.reset()
        data = compress.compress(self.plain[:15])
        data += compress.compress(self.plain[15:])
        data += compress.flush()
        self.assertEqual(data, self.plain_with_eopm)

    def test_compression_streaming_noeopm(self):
        # test compressing with one byte at a time...
        compress = lzma.LZMACompressor()
        infile = StringIO(self.plain)
        outfile = StringIO()
        while 1:
            data = infile.read(1)
            if not data: break
            outfile.write(compress.compress(data))
        outfile.write(compress.flush())
        self.assertEqual(outfile.getvalue(), self.plain_with_eopm)

    def test_compress_large_string(self):
        # decompress large block of repeating data, string version
        compressed = lzma.compress(self.data_large)
        self.failUnless(self.data_large == lzma.decompress(compressed))

    def test_decompress_large_stream(self):
        # decompress large block of repeating data, stream version
        decompress = lzma.LZMADecompressor()
        infile = StringIO(lzma.compress(self.data_large))
        outfile = StringIO()
        while 1:
            tmp = infile.read(1)
            if not tmp: break
            outfile.write(decompress.decompress(tmp))
        outfile.write(decompress.flush())
        self.failUnless(self.data_large == outfile.getvalue())

    def test_decompress_large_stream_bigchunks(self):
        # decompress large block of repeating data, stream version with big chunks
        decompress = lzma.LZMADecompressor()
        infile = StringIO(lzma.compress(self.data_large))
        outfile = StringIO()
        while 1:
            tmp = infile.read(1024)
            if not tmp: break
            outfile.write(decompress.decompress(tmp))
        outfile.write(decompress.flush())
        self.failUnless(self.data_large == outfile.getvalue())

    def test_compress_large_stream(self):
        # compress large block of repeating data, stream version
        compress = lzma.LZMACompressor()
        infile = StringIO(self.data_large)
        outfile = StringIO()
        while 1:
            tmp = infile.read(1)
            if not tmp: break
            outfile.write(compress.compress(tmp))
        outfile.write(compress.flush())
        self.failUnless(lzma.compress(self.data_large, eopm=True) == outfile.getvalue())

    def test_compress_large_stream_bigchunks(self):
        # compress large block of repeating data, stream version with big chunks
        compress = lzma.LZMACompressor()
        infile = StringIO(self.data_large)
        outfile = StringIO()
        while 1:
            tmp = infile.read(1024)
            if not tmp: break
            outfile.write(compress.compress(tmp))
        outfile.write(compress.flush())
        self.failUnless(lzma.compress(self.data_large, eopm=True) == outfile.getvalue())

    def test_decompress_new_format(self):
        infile = open('tests/data/teststring-newformat.lzma')
        outstring = lzma.decompress(infile.read())
        infile.close()
        self.assertEqual(self.plain, outstring)

class TestlibLZMAOptions(unittest.TestCase):
    def setUp(self):
        self.data = "kosogklem"*(1<<10)
    def test_preset_levels(self):
        for lvl in xrange(lzma.options.level[0], lzma.options.level[1]+1):
            result = lzma.compress(self.data, level=lvl)
            self.assertEqual(self.data, lzma.decompress(result))
        self.failUnlessRaises(ValueError, lzma.compress, self.data, level=lzma.options.level[1]+1)
        self.failUnlessRaises(ValueError, lzma.compress, self.data, level=lzma.options.level[0]-1)

    def test_dictionary_size(self):
        dict = lzma.options.dictionary_size[0]
        while dict <= 1<<26: # lzma.options.dictionary_size[1]: Since using very large dictionaries requires
                             # very large amount of memory, let's not go beyond 64mb for testing..
            result = lzma.compress(self.data, dictionary_size=dict)
            self.assertEqual(self.data, lzma.decompress(result))
            dict = dict * 2
        self.failUnlessRaises(ValueError, lzma.compress, self.data, dictionary_size=lzma.options.dictionary_size[1]+1)
        self.failUnlessRaises(ValueError, lzma.compress, self.data, dictionary_size=lzma.options.dictionary_size[0]-1)

    def test_fast_bytes(self):
        for fb in xrange(lzma.options.fast_bytes[0], lzma.options.fast_bytes[1]+1):
            result = lzma.compress(self.data, fast_bytes=fb)
            self.assertEqual(self.data, lzma.decompress(result))
        self.failUnlessRaises(ValueError, lzma.compress, self.data, fast_bytes=lzma.options.fast_bytes[1]+1)
        self.failUnlessRaises(ValueError, lzma.compress, self.data, fast_bytes=lzma.options.fast_bytes[0]-1)

    def test_literal_context_bits(self):
        for lcb in xrange(lzma.options.literal_context_bits[0], lzma.options.literal_context_bits[1]+1):
            result = lzma.compress(self.data, literal_context_bits=lcb)
            self.assertEqual(self.data, lzma.decompress(result))
        self.failUnlessRaises(ValueError, lzma.compress, self.data, literal_context_bits=lzma.options.literal_context_bits[0]-1)
        self.failUnlessRaises(ValueError, lzma.compress, self.data, literal_context_bits=lzma.options.literal_context_bits[1]+1)

    def test_literal_pos_bits(self):
        for lpb in xrange(lzma.options.literal_pos_bits[0], lzma.options.literal_pos_bits[1]+1):
            result = lzma.compress(self.data, literal_pos_bits=lpb)
            self.assertEqual(self.data, lzma.decompress(result))
        self.failUnlessRaises(ValueError, lzma.compress, self.data, literal_pos_bits=lzma.options.literal_pos_bits[0]-1)
        self.failUnlessRaises(ValueError, lzma.compress, self.data, literal_pos_bits=lzma.options.literal_pos_bits[1]+1)

    def test_pos_bits(self):
        for pb in xrange(lzma.options.pos_bits[0], lzma.options.pos_bits[1]+1):
            result = lzma.compress(self.data, pos_bits=pb)
            self.assertEqual(self.data, lzma.decompress(result))
        self.failUnlessRaises(ValueError, lzma.compress, self.data, pos_bits=lzma.options.literal_pos_bits[0]-1)
        self.failUnlessRaises(ValueError, lzma.compress, self.data, pos_bits=lzma.options.literal_pos_bits[1]+1)

    def test_mode(self):
        for md in lzma.options.mode:
            result = lzma.decompress(lzma.compress(self.data, mode=md))
            self.assertEqual(self.data, result)
        self.failUnlessRaises(ValueError, lzma.compress, self.data, mode='foo')

    def test_matchfinder(self):
        for mf in lzma.options.match_finder:
            result = lzma.decompress(lzma.compress(self.data, match_finder=mf))
            self.assertEqual(self.data, result)
        self.failUnlessRaises(ValueError, lzma.compress, self.data, match_finder='1234')

    def test_matchfinder_cycles(self):
        for mfc in xrange(lzma.options.match_finder_cycles, 20):
            result = lzma.decompress(lzma.compress(self.data, match_finder_cycles=mfc))
            self.assertEqual(self.data, result)
        self.failUnlessRaises(ValueError, lzma.compress, self.data, match_finder_cycles=-1)

    def test_format(self):
        for format in lzma.options.format:
            result = lzma.decompress(lzma.compress(self.data, format=format))
            self.assertEqual(self.data, result)
        self.failUnlessRaises(ValueError, lzma.compress, self.data, format='foo')
        
class ChecksumTestCase(unittest.TestCase):
    # checksum test cases
    def test_crc32start(self):
        self.assertEqual(lzma.crc32(""), lzma.crc32("", 0))
        self.assert_(lzma.crc32("abc", 0xffffffff))

    def test_crc32empty(self):
        self.assertEqual(lzma.crc32("", 0), 0)
        self.assertEqual(lzma.crc32("", 1), 1)
        self.assertEqual(lzma.crc32("", 432), 432)

    def assertEqual32(self, seen, expected):
        # 32-bit values masked -- checksums on 32- vs 64- bit machines
        # This is important if bit 31 (0x08000000L) is set.
        self.assertEqual(seen & 0x0FFFFFFFFL, expected & 0x0FFFFFFFFL)

    def test_penguins32(self):
        self.assertEqual32(lzma.crc32("penguin", 0), 0x0e5c1a120L)
        self.assertEqual32(lzma.crc32("penguin", 1), 0x43b6aa94)

        self.assertEqual(lzma.crc32("penguin"), lzma.crc32("penguin", 0))

    # These crc64 tests needs to be reviewed..
    def test_crc64start(self):
        self.assertEqual(lzma.crc64(""), lzma.crc64("", 0))
        self.assert_(lzma.crc64("abc", 0xffffffff))

    def test_crc64empty(self):
        self.assertEqual(lzma.crc64("", 0), 0)
        self.assertEqual(lzma.crc64("", 1), 1)
        self.assertEqual(lzma.crc64("", 432), 432)

    def assertEqual64(self, seen, expected):
        self.assertEqual(seen & 0xFFFFFFFFFFFFFFFFL, expected & 0xFFFFFFFFFFFFFFFFL)

    def test_penguins64(self):
        self.assertEqual64(lzma.crc64("penguin", 0), 0x9285a18e774b3258)
        self.assertEqual64(lzma.crc64("penguin", 1), 0xb06aacd743b256b4L)

        self.assertEqual(lzma.crc64("penguin"), lzma.crc64("penguin", 0))

def test_main():
    from test import test_support
    test_support.run_unittest(TestlibLZMA)
    test_support.run_unittest(TestlibLZMAOptions)
    test_support.run_unittest(ChecksumTestCase)

if __name__ == "__main__":
    unittest.main()
