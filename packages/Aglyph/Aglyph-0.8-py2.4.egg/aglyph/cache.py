"""A simple cache class that uses a last-modified (TTL) caching strategy."""

import logging
import sys
import time
import UserDict


class Cache(UserDict.DictMixin):

    """A mapping class that can invalidate items based on a TTL."""

    class __Value:

        def __init__(self, value):
            self.__value = value
            self.__last_accessed = time.time()

        def get_value(self):
            self.touch()
            return self.__value

        def get_last_accessed(self):
            return self.__last_accessed

        def touch(self):
            self.__last_accessed = time.time()

    MINUTES = 60

    HOURS = MINUTES * 60

    NEVER_EXPIRE = sys.maxint

    ALWAYS_EXPIRE = -1

    logger = logging.getLogger("aglyph")

    def __init__(self, ttl=NEVER_EXPIRE):
        """Create a new cache with an optional TTL (time-to-live).

        Arguments:
        ttl -- the time (in seconds) between accesses that cache entries will
               be permitted to live (default: entries never expire)

        If instantiated without a TTL, Cache objects behave as regular
        dictionaries.

        """
        self.__ttl = ttl
        self.__map = {}

    def get_ttl(self):
        """Return the TTL for this cache's entries."""
        return self.__ttl

    def set_ttl(self, value):
        """Assign the TTL for this cache's entries.

        Arguments:
        value -- a numeric value specifying the TTL (in seconds)

        """
        self.__ttl = value

    def keys(self):
        """Return a list of the component IDs in this cache."""
        return self.__map.keys()

    def __getitem__(self, name):
        """Return a cached instance if it's TTL has not been exceeded."""
        value = self.__map[name]
        if ((time.time() - value.get_last_accessed()) <= self.__ttl):
            return value.get_value()
        else:
            self.logger.info("%r has expired" % name)
            del self.__map[name]
            raise KeyError(name)

    def __setitem__(self, name, value):
        """Cache the named component instance.

        Do not cache the value unless this instance has a TTL greater than
        zero.  This allows other operations to fail early.

        """
        if (self.__ttl > 0.0):
            self.__map[name] = self.__Value(value)

    def __delitem__(self, name):
        """Remove the named component instance from this cache."""
        del self.__map[name]

