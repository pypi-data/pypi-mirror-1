#!/usr/bin/env python
#
# Copyright (c) 2008 Daniel Holth <dholth@fastmail.fm>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# Geohash implementation using bit manipulation techniques instead
# of iteration, with a permissive license.
#
# See http://graphics.stanford.edu/~seander/bithacks.html#InterleaveBMN

# TODO: round decoded coord according to length of hash
from math import log10

ALPHABET = "0123456789bcdefghjkmnpqrstuvwxyz"
TEBAHPLA = dict((c, ALPHABET.index(c)) for c in ALPHABET)

def ungeohash(g):
    # Trailing 's' (0b11000) provides Geohash's implied +0.5, +0.5
    z = unhash(g + 's')
    return decode(z)

def unhash(g):
    z = 0
    for c in g:
        z = (z << 5) + TEBAHPLA[c]
    z = z << (64 - (5*len(g)))
    return z

def enhash(z):
    out = ""
    for n in range(64-5, 0, -5):
        out = out + ALPHABET[(z >> n) & 31]
    return out

def encode(lat, lon):
    x, y = enc(lat, range=90.0), enc(lon, range=180.0)
    z = interleave(x, y)
    return z

def decode(z):
    x, y = deinterleave(z)
    lat, lon = dec(x, range=90.0), dec(y, range=180.0)
    return lat, lon

def enc(c, range=90.0, bits=32):
    # Alternatively, we could derive x from the mantissa bits of an
    # IEEE754 floating point number between 1 and 2. In Python that
    # would require using the struct module so we do this instead.
    clamp = (1<<bits) - 1
    x = min(int((c + range) * (1<<bits)) // int(2*range), clamp)
    return x

def dec(x, range=90.0, bits=32):
    return ((x * 2 * range) / float(1<<bits)) - range

def interleave(x, y):
    B = [0x5555555555555555, 0x3333333333333333, 0x0F0F0F0F0F0F0F0F, 0x00FF00FF00FF00FF, 0x0000FFFF0000FFFF]
    S = [1, 2, 4, 8, 16]

    x = (x | (x << S[4])) & B[4]
    x = (x | (x << S[3])) & B[3]
    x = (x | (x << S[2])) & B[2]
    x = (x | (x << S[1])) & B[1]
    x = (x | (x << S[0])) & B[0]

    y = (y | (y << S[4])) & B[4]
    y = (y | (y << S[3])) & B[3]
    y = (y | (y << S[2])) & B[2]
    y = (y | (y << S[1])) & B[1]
    y = (y | (y << S[0])) & B[0]

    z = x | (y << 1)

    return z

def deinterleave(z):
    # Someone should find the faster algorithm that puts x and y into
    # the tap and bottom half of the same 64-bit number, instead of this.
    B = [0x5555555555555555, 0x3333333333333333, 0x0F0F0F0F0F0F0F0F, 0x00FF00FF00FF00FF, 0x0000FFFF0000FFFF, 0x00000000FFFFFFFF]
    S = [1, 2, 4, 8, 16]

    x = z & B[0]
    x = (x | (x >> S[0])) & B[1]
    x = (x | (x >> S[1])) & B[2]
    x = (x | (x >> S[2])) & B[3]
    x = (x | (x >> S[3])) & B[4]
    x = (x | (x >> S[4])) & B[5]

    y = (z>>1) & B[0]
    y = (y | (y >> S[0])) & B[1]
    y = (y | (y >> S[1])) & B[2]
    y = (y | (y >> S[2])) & B[3]
    y = (y | (y >> S[3])) & B[4]
    y = (y | (y >> S[4])) & B[5]

    return x, y

if __name__ == "__main__":
    tests = ((22., 22.), (0., 0.), (-90, -180.), (42.6, -5.6))
    for x, y in tests:
        print x, dec(enc(x))
        print y, dec(enc(y))
        print enhash(encode(x, y))
        print encode(x, y)
        print unhash(enhash(encode(x, y)))
        g = enhash(encode(x, y))
        for i in range(1, len(g)):
            print g[:i], ungeohash(g[:i])
        print
