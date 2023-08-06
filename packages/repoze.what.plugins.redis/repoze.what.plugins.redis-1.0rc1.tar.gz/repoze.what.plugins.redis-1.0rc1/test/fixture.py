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

"""Setups the test database."""

__author__ = 'Jonás Melián <devel@jonasmelian.com>'
__copyright__ = '(c) 2009 Jonás Melián'
__license__ = 'Apache 2.0'


import redis
from repoze.what.plugins.redis import adapters


class Conf():
   #l_users = ['rms', 'linus', 'sballmer']

   #user = redis.Redis(db=0)
   group = redis.Redis(db=adapters.RedisGroupAdapter.DB_NAME)
   permission = redis.Redis(db=adapters.RedisPermissionAdapter.DB_NAME)
   databases = [group, permission]  # user


def setup():
   # Creates users with empty values.
   #for u in Conf.l_users:
      #Conf.user.set(u, '')

   # Sets groups to users.
   Conf.group.sadd('admins', 'rms')
   Conf.group.sadd('developers', 'rms')
   Conf.group.sadd('developers', 'linus')
   Conf.group.sadd('trolls', 'sballmer')
   Conf.group.sadd('python', '')  # The value would be: set([''])
   Conf.group.sadd('php', '')

   # Sets permissions to groups.
   Conf.permission.sadd('see-site', 'trolls')
   Conf.permission.sadd('edit-site', 'admins')
   Conf.permission.sadd('edit-site', 'developers')
   Conf.permission.sadd('commit', 'developers')

   # Save data.
   # 'save' is global to the server. It is not required to call 'save'
   # against all instances.
   Conf.group.save()


def teardown():
   """Removes all the keys of the selected databases."""
   for db in Conf.databases:
      db.flush()
