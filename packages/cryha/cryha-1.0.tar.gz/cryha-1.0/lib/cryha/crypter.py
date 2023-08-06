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

"""Manages the crypter."""

__author__ = 'Jonás Melián <devel@jonasmelian.com>'
__copyright__ = '(c) 2009 Jonás Melián'
__license__ = 'Apache 2.0'
__date__ = '2009-05-30'  # yyyy-mm-dd

__all__ = ['Crypter',]

import base64
import os
import sys

try:
   import mcrypt
except ImportError, err:
   module_name = err.args[-1].split()[-1]
   raise ImportError("%s\nInstall 'python-%s'." % (err, module_name))

import common


class ID:
   """Dictionaries with identifiers."""
   # Identifiers in range 0-255.
   id_2_cipher = {
         3: 'rijndael-128',
         4: 'rijndael-192',
         5: 'rijndael-256',
         1: 'serpent',
         2: 'twofish',
   }
   cipher_2_id = {
         'rijndael-128': 3,
         'rijndael-192': 4,
         'rijndael-256': 5,
         'serpent': 1,
         'twofish': 2,
   }

   # Identifiers for cipher modes.
   id_2_mode = {
         1: 'cbc',  # file
         2: 'cfb',  # string
         3: 'ctr',
         4: 'ecb',  # password
         5: 'ncfb',  # stream-block
         6: 'nofb',
         0: 'ofb',
         7: 'stream',  # stream
   }
   mode_2_id = {
         'cbc':  1,
         'cfb':  2,
         'ctr':  3,
         'ecb':  4,
         'ncfb': 5,
         'nofb': 6,
         'ofb':  0,
         'stream': 7,
   }


class Base:
   """Creates the keystore if it does not exist."""
   KEY_DIRNAME = 'mongo'
   KEY_PATH = os.path.join(os.path.expanduser('~'), '.cryha', KEY_DIRNAME)

   def create():
      if not os.path.exists(Conf.KEY_PATH):
         os.makedirs(Conf.KEY_PATH, 0750)
      elif not os.path.isdir(Conf.KEY_PATH):
         print("There is a file named %r. You have to delete it or rename it"
               " to create a directory with that name." % Conf.KEY_PATH)
         sys.exit(1)

      #keyczart.Create(loc=Conf.KEY_PATH, name='sign', asymmetric='dsa',
                      #purpose=keyinfo.SIGN_AND_VERIFY,)

      keyczart.Create(loc=Conf.KEY_PATH, name='cryp',
                      purpose=keyinfo.DECRYPT_AND_ENCRYPT)

      #ciphertext = crypter.Encrypt("Secret message")


class Crypter:
   """Manage cipher text into a schema.

   The schema used is:

   ``separator, the cipher identifier, separator, the mode identifier,
   separator, the IV parameter, separator, the ciphertext``

   For the identifiers it is used a number in range 0-255, which will be
   converted to hexadecimal.

   """
   _ROOT_KEYFILE = os.path.join(os.path.expanduser('~'), '.cryha')
   _KEYFILE_NAME = 'meta'

   # Only let use the next ciphers.
   # The number of bits on rijndael-128, rijndael-192, rijndael-256, refers to
   # block sizes.
   VALID_CIPHER = ['rijndael-128', 'twofish', 'serpent']

   # Information about cryptography modes.
   STREAM_MODES_FOR_BLOCK = ['ctr', 'ncfb', 'nofb']
   INSECURE_MODES = ['ofb']

   def __init__(self, cipher='twofish', mode='cfb', key_size=24,
                dir_keyfile=None, root_keyfile=None, warning=True):
      """Get configuration and initialize object that create random strings.

      Keyword arguments:

      cipher
         Cipher algorithm to be used. It is only possible to use any
         ciphers by security.
         By default it is set to *twofish*.

      mode
         Cipher mode of operation.
         By default is *cfb* (to encrypt strings).

      key_size
         Size in bytes of the key used to encrypt a text.
         By default is 24.

      root_keyfile
         Root base for directory of the key file.
         By default is *~/HOME/.cryha/*.

      dir_keyfile
         Sub-directory of the key file.

      """
      self._randomize = common.Randomizer()  # Instance of PRNG.
      self._schema = common.Schema()
      self._separator = common.Schema.SEPARATOR  # Get the separator.

      # Get configuration values and check that they are correct.
      self.cipher = cipher
      self.mode = mode
      self.key_size = key_size
      self.root_keyfile = root_keyfile
      self.dir_keyfile = dir_keyfile

      self._get_info_mcrypt()
      self._check_args()
      self._check_crypto(warning=warning)
      self._read_keyfile()

      # Get hexadecimal identifiers
      cipher_dec = ID.cipher_2_id[self.cipher]
      mode_dec = ID.mode_2_id[self.mode]
      self._cipher_hexa = hex(cipher_dec)[2:]  # 0x deleted
      self._mode_hexa = hex(mode_dec)[2:]  # 0x deleted

      # This instance offer encryption and decryption functionality.
      self._context = mcrypt.MCRYPT(self.cipher, self.mode)

   def _get_info_mcrypt(self):
      list_algorithms = mcrypt.list_algorithms()
      self.list_modes = mcrypt.list_modes()

      # Information about algoritm types.
      self.ciphers_block_64 = []
      self.ciphers_block_128 = []
      self.ciphers_block_192 = []
      self.ciphers_block_256 = []
      ciphers_stream = []

      for x in list_algorithms:
         # Look for algorithms with a certain block in bytes.
         if mcrypt.is_block_algorithm(x):
            if mcrypt.get_block_size(x) == 8:  # Block size of 64 bits.
               self.ciphers_block_64.append(x)
            elif mcrypt.get_block_size(x) == 16:  # Block size of 128 bits.
               self.ciphers_block_128.append(x)
            elif mcrypt.get_block_size(x) == 24:  # Block size of 192 bits.
               self.ciphers_block_192.append(x)
            elif mcrypt.get_block_size(x) == 32:  # Block size of 256 bits.
               self.ciphers_block_256.append(x)
         else:
            ciphers_stream.append(x)

      # Information about cryptography modes.
      block_modes = []
      self.stream_modes = []

      for x in self.list_modes:
         if mcrypt.is_block_algorithm_mode(x):
            block_modes.append(x)
         else:
            self.stream_modes.append(x)

      # Get block exclusive modes, discarding the stream modes for block.
      _set_block = set(block_modes)
      _set_stream = set(self.STREAM_MODES_FOR_BLOCK)
      self.only_block_modes = [i for i in _set_block.difference(_set_stream)]

   def _check_args(self):
      """Check that arguments are correct."""

      # Cipher.
      if not self.cipher or not self.cipher in self.VALID_CIPHER:
         try:
            raise ValueError('cipher not valid')
         except ValueError, err:
            print("Valid values: %s" % self.VALID_CIPHER)
            raise

      # Mode.
      if not self.mode or not self.mode in self.list_modes:
         try:
            raise ValueError('mode not valid')
         except ValueError, err:
            print("Valid values: %s" % self.list_modes)
            raise

      # Key size has to be an integer.
      if self.key_size and isinstance(self.key_size, basestring):
         try:
            self.key_size = int(self.key_size)
         except ValueError:
            print('integer argument required for key size')
            raise

      # Key size.
      if not self.key_size:
         raise ValueError('key size not found')

      # Key file directory.
      if not self.dir_keyfile:
         raise ValueError('keyfile directory not found')

   def _check_crypto(self, warning):
      """Check that cryptographic values are correct."""

      # Get the cipher key sizes (MCrypt works with bytes).
      list_key_sizes = mcrypt.get_key_sizes(self.cipher)

      # The maximum key size.
      max_key_size = mcrypt.get_key_size(self.cipher)

      # Insecure cipher mode
      if warning and self.mode in self.INSECURE_MODES:
         print("Warning: %r is an insecure cipher mode\n" % self.mode)

      # Cipher
      # ----------------------------

      # If it is a stream algorithm
      if not mcrypt.is_block_algorithm(self.cipher):

         # check if the mode is for stream.
         if mcrypt.is_block_algorithm_mode(self.mode):
            try:
               raise ValueError("%r is not a stream mode" % self.mode)
            except ValueError, err:
               print("%r cipher works with stream modes\n"
                     "Valid values for mode: %s"
                     % (self.cipher, self.stream_modes))
               raise
      # If it is a block algorithm
      else:
         # If the mode of operation is not for use with block algorithms.
         if not mcrypt.is_block_algorithm_mode(self.mode):
            try:
               raise ValueError("%r is not a block mode" % self.mode)
            except ValueError, err:
               print("%r cipher works with block modes\n"
                     "Valid values for mode: %s\n\n"
                     "Or to turn a block cipher into stream cipher"
                     " using any mode between: %s"
                     % (self.cipher, self.only_block_modes,
                        self.STREAM_MODES_FOR_BLOCK))
               raise

         # Check if the block is lesser than 128 bits.
         if warning and self.cipher in self.ciphers_block_64:
            print("Warning: %r cipher has a block size lesser than 128 bits\n"
                  "Use it for the encryption of a few hundred megabytes,"
                  " else would start to leak information about the message"
                  " contents.\n\n"
                  "Ciphers with block size of 128 bits: %s\n\n"
                  "Ciphers with block size greater than 128 bits: %s\n"
                  % (self.cipher, self.ciphers_block_128,
                     self.ciphers_block_192 + self.ciphers_block_256))

      # Key size
      # ----------------------------

      # If 'MCRYPT.get_key_sizes()' returns any value, then it is only
      # possible to choose a key size of that list.
      if list_key_sizes:
         if not self.key_size in list_key_sizes:
            try:
               raise ValueError("key size not valid for %r cipher"
                                % self.cipher)
            except ValueError, err:
               print("Valid values: %s" % list_key_sizes)
               raise
      # If returns an empty list, then is possible to choose any length up to
      # the maximum key size 'MCRYPT.get_key_size()'.
      else:
         # Chek the range
         if self.key_size > max_key_size:
            try:
               raise ValueError("key size out of range for %r cipher"
                                % self.cipher)
            except ValueError, err:
               print("Valid values: up to %d bytes\n" % max_key_size)
               raise

         # Minimum size
         if warning and self.key_size < 14:  # 112 bits
            print('Warning: key size must be of 14 bytes (112 bits) like'
                  ' minimum for security.\n')

   def _read_keyfile(self):
      """Reads the key from a file.

      The sub-directory is created if it doesn't exist. And if doesn't
      exist the file then generates a random key for the key file.

      """
      if self.root_keyfile is None:
         _root_keyfile = self._ROOT_KEYFILE
      else:
         _root_keyfile = self.root_keyfile

      self._dirname_keyfile = os.path.join(_root_keyfile, self.dir_keyfile)

      # The directory is created if it does not exist.
      if not os.path.exists(self._dirname_keyfile):
         os.makedirs(self._dirname_keyfile, 0750)
      elif not os.path.isdir(self._dirname_keyfile):
         try:
            raise ValueError(
                  "There is a file named %r. You have to delete it or rename it"
                  " to create a directory with that name." % self._dirname_keyfile)
         except ValueError:
            raise

      self._keyfile = os.path.join(self._dirname_keyfile, self._KEYFILE_NAME)

      # If the key file does not exist, then is created with a random key
      # and is encoded to base-64.
      if os.path.isfile(self._keyfile):
         self._key = open(self._keyfile).readline().rstrip()
         self._key = base64.b64decode(self._key)
      else:
         self._key = self._randomize.generate(self.key_size)
         open(self._keyfile, 'w').write(base64.b64encode(self._key))
         os.chmod(self._keyfile, 0400)  # Only read for User.

   def encrypt(self, plain_text):
      """Main encryption function.

      Built the schema encoding to base-64 both IV and text encrypted,
      and using the hexadecimal identifiers.

      Return the schema.

      """
      # Identifiers for the schema.
      cipher_dec = ID.cipher_2_id[self.cipher]
      mode_dec = ID.mode_2_id[self.mode]

      # The IV parameter needs to be random and unique (but not secret).
      if self._context.has_iv():
         iv = self._randomize.generate(self._context.get_iv_size())
         self._context.init(self._key, iv)
      else:
         self._context.init(self._key)
         iv = ''

      # *python-mcrypt* does not works with Unicode.
      plain_text = common.to_string(plain_text)

      # Here is where plain text is encrypted.
      encrypted_data = self._context.encrypt(plain_text, fixlength=1)

      # The schema is built encoding to base-64 both IV and encrypted data,
      # and using the hexadecimal identifiers.
      schema = (self._separator + self._cipher_hexa +
                self._separator + self._mode_hexa +
                self._separator + base64.b64encode(iv) +
                self._separator + base64.b64encode(encrypted_data))

      # Make sure returns an UTF-8 object.
      return common.to_unicode(schema)

   def decrypt(self, schema):
      """Main decryption function.

      Get data from schema, decode to bytes, and decrypt.

      Return the decrypted text.

      """
      self._schema.valid(schema)

      # The first split is empty beacuse the schema starts with a separator.
      cipher_hexa, mode_hexa, schema_iv, cipher_text = schema.split(
         self._separator)[1:]

      # They are stored in base-64 so I decode them to bytes.
      schema_iv = base64.b64decode(schema_iv)
      cipher_text = base64.b64decode(cipher_text)

      # It's possible that it has been set another configuration.
      if cipher_hexa != self._cipher_hexa or mode_hexa != self._mode_hexa:
         # Convert from hexadecimal to decimal.
         cipher_dec = int(cipher_hexa, 16)
         mode_dec = int(mode_hexa, 16)
         # Get names from identifier.
         new_cipher = ID.id_2_cipher[cipher_dec]
         new_mode = ID.id_2_mode[mode_dec]
         # Initialize a new class of MCRYPT with new values.
         context = mcrypt.MCRYPT(new_cipher, new_mode)
      else:
         context = self._context

      if schema_iv:
         context.init(self._key, schema_iv)
      else:
         context.init(self._key)

      decrypted_data = context.decrypt(cipher_text, fixlength=1)

      # If it is not an instance of String then it has not been decrypted
      # because the key is incorrect.
      try:
         return common.to_unicode(decrypted_data)
      except:
         print('Decryption key is incorrect.')
         sys.exit(1)
