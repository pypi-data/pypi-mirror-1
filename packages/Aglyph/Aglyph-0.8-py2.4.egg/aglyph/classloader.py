"""A simple class loader that mimics the Python __import__ function."""

import os
import sys


class ClassLoader:

    """A class providing basic import functionality.

    Classes expected to be loaded by instances of this class MUST be
    available in sys.path.

    """

    def find_resource(self, name):
        """Return the absolute path to a filesystem resource.

        Arguments:
        name -- the name of a resource (usually a filename or directory)

        """
        for prefix in sys.path:
            path = os.path.normpath(os.path.join(prefix, name))
            if (os.path.exists(path)):
                return path
        return None


    def load_class(self, classpath):
        """Return the class object identified by classpath.

        Arguments:
        classpath -- a Python classpath

        """
        (modulename, classname) = classpath.rsplit('.', 1)
        module = __import__(modulename, globals(), locals(), [classname])
        return getattr(module, classname)

