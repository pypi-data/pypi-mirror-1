#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

r"""Components reusing the Secure Hash Algorithms already found in 
Python stdlib.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

from trac.core import Component, implements

from api import IHashLibrary, GVizInvalidConfigError

import hashlib
from zlib import adler32, crc32

__all__ = 'HashLib', 'ZLibChecksum'

__metaclass__ = type

class HashLib(Component):
  r"""Secure Hash Algorithms supported by `hashlib` standard module.
  
  Supports the following methods:
    - sha1, sha224, sha256, sha384, sha512 : as defined in FIPS 180-2 
    - md5 : RSA's MD5 algorithm (defined in Internet RFC 1321)
    - Additional algorithms may also be available depending upon the 
      OpenSSL library that Python uses on your platform.
  """
  implements(IHashLibrary)
  
  # IHashLibrary methods
  def get_hash_properties(self, method_name):
    r"""Determine whether the requested method is a standard hash 
    algorithm (i.e. md5, sha1, sha224, sha256, sha384, and sha512), or 
    is implemented by the OpenSSL library that Python uses on your 
    platform, or is not supported by `hashlib` module.
    
    @param method_name  the name identifying the hash method
    @return             `None` if the method is not supported by 
                        `hashlib` module, a tuple of the form 
                        (priority, source) otherwise.
                        
                        priority: 0   - OpenSSL, 
                                  199 - standard hash algorithms.
                        source:   0   - OpenSSL. 
                                  100 - standard hash algorithms
    """
    if (not method_name.startswith('_')) and \
        method_name != 'new' and \
        hasattr(hashlib, method_name):
      return (199, 100)
    else:
      try:
        hashlib.new(method_name)
        return (0, 0)
      except ValueError:
        return None
    
  def new_hash_obj(self, method_name, data=None):
    r"""Create a new hash object.
    """
    try:
      meth = getattr(hashlib, method_name)
      if data is None:
        return meth()
      else:
        return meth(data)
    except AttributeError:
      try:
        return hashlib.new(method_name)
      except ValueError:
        raise GVizInvalidConfigError("Unsupported hash algorithm '%s'" \
                                  % (method_name,))
    else:
      raise

class ZLibChecksum(Component):
  r"""Checksum Algorithms supported by `zlib` standard module.
  
  Supports the following methods:
    - adler32 : Adler-32 checksum of string.
    - crc32   : Compute a CRC (Cyclic Redundancy Check) checksum of 
                string. 
  """
  implements(IHashLibrary)
  
  # IHashLibrary methods
  def get_hash_properties(self, method_name):
    r"""Determine whether the requested method is defined by `zlib` 
    standard module.
    
    @param method_name  the name identifying the hash method
    @return             (199, 100) if `method_name` is either 
                        `adler32` or `crc32`, or `None` otherwise.
    """
    if method_name in ['adler32', 'crc32']:
      return (199, 100)
    else:
      return None
    
  class ZLibChecksumObject:
    r"""Hash objects for zlib checksum methods.
    """
    digest_size = 4
    block_size = 4 # FIX : Dont remember now
    def __init__(self, method_name):
      self.args = ()
      self.chksum_method = {'adler32': adler32,
                            'crc32': crc32}.get(method_name)
      if self.chksum_method is None:
        raise ValueError("Unsupported checkum method '%s'" % \
                          (method_name,))
    def update(self, data):
      r"""Update the hash object with the string arg. Repeated calls 
      are equivalent to a single call with the concatenation of all 
      the arguments: m.update(a); m.update(b) is equivalent to 
      m.update(a+b). .
      """
      self.args = (self.chksum_method(data, *self.args),)
    def digest(self):
      r"""Return the digest of the strings passed to the update() 
      method so far. This is a string of 4 bytes which may contain 
      non-ASCII characters, including null bytes.
      """
      try:
        chksum, digest = self.args[0], []
      except ValueError:
        return None
      else:
        for x in xrange(4):
          digest.append(chr(chksum & 0xFF))
          chksum >>= 8
        return ''.join(reversed(digest))
    def hexdigest(self):
      r"""Like digest() except the digest is returned as a string of 
      double length, containing only hexadecimal digits. This may be 
      used to exchange the value safely in email or other non-binary 
      environments. 
      """
      try:
        return hex(self.args[0])[2:]
      except ValueError:
        return None
    def copy(self):
      new_obj = ZLibChecksumObject(self.chksum_method.func_name)
      new_obj.args = tuple(self.args)
      return new_obj
  
  def new_hash_obj(self, method_name, data=None):
    r"""Create a new hash object.
    """
    try:
      ho = self.ZLibChecksumObject(method_name)
    except ValueError:
      raise GVizInvalidConfigError("Unsupported hash algorithm '%s'" \
                                  % (method_name,))
    else:
      if data is not None:
        ho.update(data)
      return ho

