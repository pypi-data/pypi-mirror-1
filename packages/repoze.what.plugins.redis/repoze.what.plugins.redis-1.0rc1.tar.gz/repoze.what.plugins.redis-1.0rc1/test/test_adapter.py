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

"""Test suite for the adapters."""

__author__ = 'Jonás Melián <devel@jonasmelian.com>'
__copyright__ = '(c) 2009 Jonás Melián'
__license__ = 'Apache 2.0'

import unittest

import redis
from repoze.what.adapters import testutil
from repoze.what.plugins.redis import adapters

import fixture


class _BaseRedisAdapterTester(unittest.TestCase):
    """Base class for the test suite."""

    def tearDown(self):
        fixture.teardown()


class TestGroupsAdapterTester(testutil.GroupsAdapterTester,
                              _BaseRedisAdapterTester):
   db = redis.Redis()

   def setUp(self):
      super(TestGroupsAdapterTester, self).setUp()
      fixture.setup()
      self.adapter = adapters.RedisGroupAdapter(self.db)


class TestPermissionsAdapterTester(testutil.PermissionsAdapterTester,
                                   _BaseRedisAdapterTester):
   db = redis.Redis()

   def setUp(self):
      super(TestPermissionsAdapterTester, self).setUp()
      fixture.setup()
      self.adapter = adapters.RedisPermissionAdapter(self.db)
