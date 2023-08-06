#===============================================================================
# Copyright 2010 Matt Chaput
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

from array import array
from math import frexp, ldexp

import struct
si = struct.Struct(">i")
ipack = si.pack
iunpack = si.unpack


def int2blob(x):
    x+=(1<<(4<<2))-1 # 4 means 32-bits
    return ipack(x)

def blob2int(b):
    x=iunpack(b)[0]
    x-=(1<<(4<<2))-1
    return x

def long2blob(x):
    x+=(1<<(8<<2))-1 # 8 means 64-bits
    return struct.pack('>q',x)

def blob2long(b):
    x=struct.unpack('>q',b)[0]
    x-=(1<<(8<<2))-1
    return x

def double2blob(x):
    return long2blob(to_ulps(x))

def blob2double(b):
    return from_ulps(blob2long(b))

def to_ulps(x):
    n = struct.unpack('<q', struct.pack('<d', x))[0]
    if n < 0: n = ~(n+(2<<63))
    return n

def from_ulps(n):
    if n < 0: n = ~(n-(2<<63))
    x = struct.unpack('<d', struct.pack('<q', n))[0]
    return x

import time, random

r = range(-50000, 50000)
random.shuffle(r)

t = time.time()
r2 = [int2blob(n) for n in r]
print time.time() - t

r2.sort()
t= time.time()
r3 = [blob2int(n) for n in r2]
print time.time() - t
assert r3 == range(-50000, 50000)

o = [n/3.0 for n in xrange(-50000, 50000)]
r = o[:]
assert o == sorted(o)
random.shuffle(r)

t = time.time()
r2 = [double2blob(n) for n in r]
print time.time() - t

r2.sort()
t= time.time()
r3 = [blob2double(n) for n in r2]
print time.time() - t
assert r3 == o



