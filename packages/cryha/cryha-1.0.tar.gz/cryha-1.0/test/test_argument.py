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

"""Test suite for the Cryha arguments."""

__author__ = 'Jonás Melián <devel@jonasmelian.com>'
__copyright__ = '(c) 2009 Jonás Melián'
__license__ = 'Apache 2.0'

import os

from nose import tools

import cryha


class TestHasher:
   """Check arguments passed to Hasher."""

   def test_hasher(self):
      # Hash function
      for hasher in [None, 'non_exist']:
         yield self.check_hasher, hasher, None

      hasher = 'tiger'

      # Salt size
      for salt_size in [None, '10', '10s']:
         yield self.check_hasher, hasher, salt_size

   def check_hasher(self, hasher, salt_size):
      tools.assert_raises(
            ValueError, cryha.Hasher,
            hasher=hasher, salt_size=salt_size)

      # To show the error messages.
      #assert cryha.Hasher(hasher=hasher, salt_size=salt_size)


class TestCrypter:
   """Check arguments passed to Crypter."""

   def test_crypter(self):
      # Cipher
      for cipher in [None, 'non_exist']:
         yield self.check_crypter, cipher, None, None, None

      cipher = 'serpent'

      # Mode
      for mode in [None, 'non_exist']:
         yield self.check_crypter, cipher, mode, None, None

      mode = 'cbc'

      # Key size
      for key_size in [None, '10s', 10]:
         yield (self.check_crypter, cipher, mode, key_size, None)

      key_size = 16

      # Sub-directory for key file.
      yield (self.check_crypter, cipher, mode, key_size, None, None)

      # Root of key file.
      file_path = os.path.abspath(os.path.dirname(__file__))
      yield (self.check_crypter, cipher, mode, key_size, file_path, __file__)

   def check_crypter(self, cipher, mode, key_size, root_keyfile,
                     dir_keyfile='test-0'):
      tools.assert_raises(
            ValueError, cryha.Crypter,
            cipher=cipher, mode=mode, key_size=key_size,
            root_keyfile=root_keyfile, dir_keyfile=dir_keyfile)

      # To show the error messages.
      #assert cryha.Crypter(cipher=cipher, mode=mode, key_size=key_size,
      #                     root_keyfile=root_keyfile, dir_keyfile=dir_keyfile)
