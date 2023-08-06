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

"""The 'repoze.what' group and permission adapters for Redis sources."""

__author__ = 'Jonás Melián <devel@jonasmelian.com>'
__copyright__ = '(c) 2009 Jonás Melián'
__license__ = 'Apache 2.0'
__date__ = '2009-05-16'  # yyyy-mm-dd

__all__ = ['RedisGroupAdapter', 'RedisPermissionAdapter']

from repoze.what import adapters


class _RedisAdapter(adapters.BaseSourceAdapter):
   """The base class for Redis database adapters."""
   EMPTY_STRING = ''
   EMPTY_STRING_SET = set([''])  # Returned in Redis.
   EMPTY_SET = set([])  # Used in repoze.what.

   def __init__(self, db_connection):
      """Creates a Redis source adapter.

      Arguments:

         db_connection
            The Redis authentication/authorization database connection.

      """
      super(_RedisAdapter, self).__init__(writable=True)

      self.db_connection = db_connection
      self.db_connection.select(self.DB_NAME)

   def _get_set(self, items):
      """Returns a set of the items."""
      set_items = set()

      if isinstance(items, basestring):
         set_items.add(items)
      else:
         for it in items:
            set_items.add(it)

      return set_items

   def _get_sections_of_item(self, item):
      """Returns the sections which have the item."""
      all_sections = self._get_all_sections()
      sections = []

      for value_key in all_sections.iteritems():
         # Searchs the group in the values.
         if item in value_key[1]:
            sections.append(value_key[0])

      return set(sections)

   def _save(self):
      """Synchronously save the data on disk."""
      self.db_connection.save(background=False)

   # ==== Methods for 'adapters.BaseSourceAdapter' ====

   # ==== Sections

   def _get_all_sections(self):
      sections = {}

      try:
         all_keys = self.db_connection.keys('*')
      except:
         msg = ('There was a problem with the source while retrieving the'
                ' sections')
         raise adapters.SourceError(msg)

      for key in all_keys:
         sections[key] = self._get_section_items(key)

      return sections

   def _create_section(self, section):
      try:
         self.db_connection.sadd(section, self.EMPTY_STRING)
      except:
         msg = "The %r section could not be added" % section
         raise adapters.SourceError(msg)

      self._save()

   def _edit_section(self, section, new_section):
      try:
         self.db_connection.rename(section, new_section)
      except:
         msg = "The %r section could not be edited" % section
         raise adapters.SourceError(msg)

      self._save()

   def _delete_section(self, section):
      try:
         self.db_connection.delete(section)
      except:
         msg = "The %r section could not be deleted" % section
         raise adapters.SourceError(msg)

      self._save()

   def _section_exists(self, section):
      try:
         value = self.db_connection.exists(section)
      except:
         msg = 'There was a problem with the source'
         raise adapters.SourceError(msg)

      if value:
         return True
      else:
         return False

   # ==== Items

   def _get_section_items(self, section):
      try:
         # Gets all members of the set.
         items = self.db_connection.smembers(section)
      except:
         msg = ("There was a problem with the source while retrieving the"
                " %r section") % section
         raise adapters.SourceError(msg)

      if items == self.EMPTY_STRING_SET:
         return self.EMPTY_SET
      else:
         return items

   def _include_items(self, section, items):
      set_items = self._get_set(items)
      section_items = self._get_section_items(section)

      for value in set_items:
         try:
            self.db_connection.sadd(section, value)
         except:
            msg = "The %r item could not be added to the %r section" % \
                  (value, section)
            raise adapters.SourceError(msg)

      if not section_items:
         self._exclude_items(section, self.EMPTY_STRING)

      self._save()

   def _exclude_items(self, section, items):
      set_items = self._get_set(items)

      for value in set_items:
         try:
            self.db_connection.srem(section, value)
         except:
            msg = "The %r item could not be removed from the %r section" % \
                  (value, section)
            raise adapters.SourceError(msg)

      self._save()

   def _item_is_included(self, section, item):
      try:
         value = self.db_connection.sismember(section, item)
      except:
         msg = 'There was a problem with the source'
         raise adapters.SourceError(msg)

      if value:
         return True
      else:
         return False


class RedisGroupAdapter(_RedisAdapter):
   DB_NAME = 1

   def _find_sections(self, credentials):
      """Returns the groups the authenticated user belongs to."""
      userid = credentials['repoze.what.userid']

      return self._get_sections_of_item(userid)


class RedisPermissionAdapter(_RedisAdapter):
   DB_NAME = 2

   def _find_sections(self, group):
      """Returns the name of the permissions granted to the group."""
      return self._get_sections_of_item(group)
