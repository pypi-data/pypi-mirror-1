# -*- coding: utf-8 -*-

# Copyright (c) 2009 Jonás Melián
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Common functions used in the main classes."""

__author__ = 'Jonás Melián <devel@jonasmelian.com>'
__copyright__ = '(c) 2009 Jonás Melián'
__license__ = 'Apache 2.0'
__date__ = '2009-05-30'  # yyyy-mm-dd

__all__ = ['Schema', 'Randomizer',]

import os
import random
import re
import sys

# For use random.SystemRandom()
if sys.version_info < (2, 4):
   raise AssertionError('Python 2.4 or later required')


class Schema:
   """Constants used in another classes."""
   SEPARATOR = u'$'  # Character used as separator.
   BASE64_CODE = r'[A-Za-z0-9\+\/=]+'
   HEXA_CODE = '[0-9a-f]{1,2}'

   HASH_SCHEMA = re.compile("^%s%s%s%s%s%s$" %
                            ('\\'+SEPARATOR, HEXA_CODE,
                             '\\'+SEPARATOR, BASE64_CODE,
                             '\\'+SEPARATOR, BASE64_CODE))

   CRYPT_SCHEMA = re.compile("^%s%s%s%s%s%s%s%s$" %
                             ('\\'+SEPARATOR, HEXA_CODE,
                              '\\'+SEPARATOR, HEXA_CODE,
                              '\\'+SEPARATOR, BASE64_CODE,
                              '\\'+SEPARATOR, BASE64_CODE))

   # Get visible ASCII characters --whose decimal value is in range
   # 33-126-- except the space --its decimal code is 32--; leaving
   # 94 characters.
   #ASCII_CHARS = [unichr(char) for char in range(33, 127)]
   #ASCII_CHARS = [x for x in string.printable.strip()]

   # The UTF-8 visible characters corresponding to ISO-8859-1 [1]_ that are
   # not in ASCII; whose decimal values go from 161 to 255, getting 95
   # characters.
   # .. [1] http://en.wikipedia.org/wiki/ISO/IEC_8859-1
   #LATIN1_CHARS = [unichr(char) for char in range(161, 256)]

   def valid(self, schema, crypter=True):
      """Check schema of a given hash or encrypted text.

      Arguments:

         ``schema``
            The schema.

         ``crypter``
            True if it is a crypt schema. False for a hash schema.

      Returns:
         ``True`` if it's valid.

      Raises:

         ``CryptError``: It is not a valid crypt schema.
         ``HashError``: It is not a valid hash schema.

      """
      if crypter:
         if not self.CRYPT_SCHEMA.search(schema):
            raise CryptError
      else:
         if not self.HASH_SCHEMA.search(schema):
            raise HashError

      return True


class Randomizer:
   """Generate random strings.

   Uses a pseudo random number generator with sources provided by the
   operating system (such as */dev/urandom* on Unix).

   """

   def __init__(self):
      """Initialize the PRNG of the operating system."""
      self.prng = random.SystemRandom()

   def generate(self, bytes):
      """Generate a random string.

      Each byte is randomly chosen from a domain of 256 possible values
      --range 0-255-- per character, thus a greater security is obtained.

      Keyword arguments:

      bytes
         Number of bytes, which are going to be translated to
         characters.

      Return a number of *n* characters.

      """
      rand = ''
      for x in range(bytes):
         rand += chr(self.prng.randrange(256))  # 0-255

      return rand


class Error(Exception):
   """Base class for exceptions in this module."""
   pass


class HashError(Error):
   def __init__(self):
      print('Invalid hash schema')


class CryptError(Error):
   def __init__(self):
      print('Invalid crypt schema')


def to_unicode(obj, decoding='utf-8'):
   """Decode *String* type to *Unicode*.

   Detect if object is a string and if so converts to unicode, if not
   already.

   http://farmdev.com/talks/unicode/

   Keyword arguments:

   obj
      String of ASCII characters to be decoded in the type defined in
      `decoding`.

   decoding
      It is used UTF-8 by default.

   Return an *Unicode* object.

   """
   if isinstance(obj, basestring) and not isinstance(obj, unicode):
      obj = unicode(obj, decoding)
   return obj


def to_string(obj, encoding='utf-8'):
   """Encode *Unicode* type to *String*.

   Detect if object is a unicode and if so converts to string, if not
   already.

   Keyword arguments:

   obj
      String of Unicode characters to be encoded to the type defined in
      `encoding`.

   encoding
      It is used UTF-8 by default.

   Return a *String* object.

   """
   if isinstance(obj, basestring) and not isinstance(obj, str):
      obj = obj.encode(encoding)
   return obj
