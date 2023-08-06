"""Module for listing directories"""
import commands
import os


class BaseLister(object):
    """Base class for listers"""

    def __init__(self, location, ignore=[]):
        self.location = location
        self.ignore = ignore
        self.contents = sorted(
            [item for item in sorted(self._calculate_contents())
             if item not in self.ignore])

    def _calculate_contents(self):
        """Return list of contents"""
        raise NotImplementedError('Implement in subclass')

    def fullpath(self, item=None):
        """Return full path of item"""
        raise NotImplementedError('Implement in subclass')

    def traverse(self, subdir):
        """Return similar instance for subdir"""
        return self.__class__(self.fullpath(subdir), ignore=self.ignore)

    @property
    def is_project(self):
        """Return whether this location is something with trunk/tags"""
        return 'trunk' in self.contents

    def is_dir(self, item):
        """Return whether item is a directory"""
        raise NotImplementedError('Implement in subclass')

    @property
    def head(self):
        """Return head/trunk when we're a project, if found"""
        if 'trunk' in self.contents:
            return self.traverse('trunk')

    def cat(self, item):
        """Return content of item as lines (assumption: text file)"""
        raise NotImplementedError('Implement in subclass')

    def __cmp__(self, other):
        """Sort by location"""
        if other == None:
            # Special case...
            return -1
        return cmp(self.location, other.location)


class DirLister(BaseLister):
    """List filesystem directories"""

    def _calculate_contents(self):
        return os.listdir(self.location)

    def fullpath(self, item):
        return os.path.join(self.location, item)

    def cat(self, item):
        return open(self.fullpath(item)).read().splitlines()

    def is_dir(self, item):
        return os.path.isdir(self.fullpath(item))


class SvnLister(BaseLister):
    """List svn directory contents"""

    def _calculate_contents(self):
        output = commands.getoutput('svn list %s' % self.location)
        lines = [line.strip() for line in output.splitlines()]
        # Directories are svn-listed as 'directoryname/', so store them first
        # in a list of directories (for is_dir()) and strip the slash
        # afterwards.
        self._directories = [line.rstrip('/') for line in lines
                             if line.endswith('/')]
        lines = [line.rstrip('/') for line in lines]
        return [line for line in lines if line]

    def fullpath(self, item):
        # svn always uses forward slashes.
        return '/'.join([self.location, item])

    def cat(self, item):
        output = commands.getoutput('svn cat %s' % self.fullpath(item))
        return output.splitlines()

    def is_dir(self, item):
        return item in self._directories
