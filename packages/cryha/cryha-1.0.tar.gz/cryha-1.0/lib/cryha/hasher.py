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

"""Manages the hasher."""

__author__ = 'Jonás Melián <devel@jonasmelian.com>'
__copyright__ = '(c) 2009 Jonás Melián'
__license__ = 'Apache 2.0'
__date__ = '2009-05-30'  # yyyy-mm-dd

__all__ = ['Hasher',]

import base64
import sys

# In the first try load 'mhash'; if is not installed then try load 'hashlib'
# which is a standard library since Python 2.5, but it can be installed in older
# versions.
try:
   import mhash
   mhash_loaded = True
except ImportError:
   mhash_loaded = False

   try:  #compatible# < 2.5
      import hashlib
   except ImportError, err:
      module_name = err.args[-1].split()[-1]
      raise ImportError("%s\nTo install run: 'easy_install %s'"
                        % (err, module_name))

import common


class ID:
   """Dictionaries with identifiers."""
   # Identifiers with the same codes that are used in 'mhash' module.
   id_2_hasher = {
         42: 'bcrypt',
         1:  'md5',
         5:  'ripemd160',
         24: 'ripemd256',
         25: 'ripemd320',
         2:  'sha1',
         19: 'sha224',
         17: 'sha256',
         21: 'sha384',
         20: 'sha512',
         7:  'tiger',
         22: 'whirlpool',
   }
   hasher_2_id = {
         'bcrypt':    42,  # OpenBSD (2A)
         'md5':       1,   # Linux
         'ripemd160': 5,
         'ripemd256': 24,
         'ripemd320': 25,
         'sha1':      2,
         'sha224':    19,
         'sha256':    17,
         'sha384':    21,
         'sha512':    20,
         'tiger':     7,
         'whirlpool': 22,
   }


class Hasher:
   """Manage hash in password schemas.

   The schema used is:

   ``separator, the hash function identifier, separator, the salt,
   separator, the hash output``

   For the identifiers it is used a number in range 0-255, which will be
   converted to hexadecimal.

   """
   # Pre-deﬁned security levels by NIST, and its values pre-calculated to get
   # bytes from bits.
   VALID_SALT = {
         128: 16,
         192: 24,
         256: 32
   }

   # Only let use these hash functions and salt sizes.
   VALID_HASHLIB = ['sha224', 'sha256', 'sha384', 'sha512', 'ripemd160']
   VALID_MHASH = VALID_HASHLIB + ['ripemd256', 'ripemd320', 'tiger', 'whirlpool']

   def __init__(self, hasher=None, salt_size=128):
      """Get configuration and initialize object that create random
      strings.

      Keyword arguments:

      hasher
         Hash function to be used. It is only possible to use any
         functions by security.
         By default it is set to *ripemd256* or *ripemd160*.

      salt_size
         Size in bits of a random salt which will be added to the text
         to be hashed. Valid values are: 128, 192, 256.
         By default is 128.

      """
      self._randomize = common.Randomizer()  # Instance of PRNG.
      self._schema = common.Schema()
      self._separator = common.Schema.SEPARATOR  # Get the separator.

      # Get configuration values and check that they are correct.
      self.salt_size = salt_size
      if hasher is None:
         if mhash_loaded:
            self.hasher = 'ripemd256'
         else:
            self.hasher = 'ripemd160'
      else:
         self.hasher = hasher

      self._check_args()

      # Get hexadecimal identifier
      hasher_dec = ID.hasher_2_id[self.hasher]
      self._hasher_hexa = hex(hasher_dec)[2:]  # 0x deleted

   def _check_args(self):
      """Check that arguments are correct."""

      # Hash function.
      if mhash_loaded:
         if not self.hasher or not self.hasher in self.VALID_MHASH:
            try:
               raise ValueError('hash function not valid')
            except ValueError, err:
               print("Valid values: %s" % self.VALID_MHASH)
               raise
      else:
         if not self.hasher or not self.hasher in self.VALID_HASHLIB:
            try:
               raise ValueError('hash function not valid')
            except ValueError, err:
               print("Valid values: %s" % self.VALID_HASHLIB)
               raise

      # Salt size has to be an integer.
      if self.salt_size and isinstance(self.salt_size, basestring):
         try:
            self.salt_size = int(self.salt_size)
         except ValueError:
            print('integer argument required for salt size')
            raise

      # Salt size.
      valid_salt = self.VALID_SALT.keys()
      if not self.salt_size or not self.salt_size in valid_salt:
         try:
            raise ValueError('salt size not valid')
         except ValueError, err:
            print("Valid values: %s" % valid_salt)
            raise

   def _create_hash(self, hasher, salt, password):
      """Create a hash for the given password. The salt is inserted to
      the password.

      Return the hashed password.

      """
      # *Hashlib* does not works with Unicode, so encodes to *string*.
      password = common.to_string(password)

      # Look for the hash function choosen.
      if mhash_loaded:
         function = 'MHASH_' + hasher.upper()
         password_hash = mhash.MHASH(getattr(mhash, function),
                                     salt + password).digest()
      # Hashlib
      else:
         # Hash function used from OpenSSL.
         if 'ripemd160' == hasher:
            password_hash = hashlib.new('ripemd160')
            password_hash.update(salt + password)
            password_hash = password_hash.digest()
         # Functions implemented directly on *hashlib* module.
         else:
            password_hash = getattr(hashlib, hasher)(salt + password).digest()

      return password_hash

   def create(self, password):
      """Create the random salt, and built the schema with the hashed
      password.

      The password schema is built encoding to base-64 both salt and
      hash, and using the hexadecimal identifier.

      Return the password schema.

      """
      salt = self._randomize.generate(self.VALID_SALT[self.salt_size])
      password_hash = self._create_hash(self.hasher, salt, password)

      password_schema = (self._separator + self._hasher_hexa +
                         self._separator + base64.b64encode(salt) +
                         self._separator + base64.b64encode(password_hash))

      # Make sure return an UTF-8 object.
      return common.to_unicode(password_schema)

   def valid(self, login, schema):
      """Check a hash.

      Create a password hash with the `login` name and checks if is the
      same that is obtained from schema.

      Return a boolean.

      """
      self._schema.valid(schema, crypter=False)

      # The first split is empty beacuse the schema starts with a separator.
      hasher_hexa, schema_salt, schema_hash = schema.split(self._separator)[1:]

      # They are stored in base-64 so I decode them to bytes.
      schema_salt = base64.b64decode(schema_salt)
      schema_hash = base64.b64decode(schema_hash)

      # It is possible that it has been set another configuration.
      if hasher_hexa != self._hasher_hexa:
         hasher_dec = int(hasher_hexa, 16)  # From hexadecimal to decimal.
         new_hasher = ID.id_2_hasher[hasher_dec]
      else:
         new_hasher = self.hasher

      # Create a hash with the `login` given.
      password_hash = self._create_hash(new_hasher, schema_salt, login)

      # Compare bytes which is faster.
      return password_hash == schema_hash
