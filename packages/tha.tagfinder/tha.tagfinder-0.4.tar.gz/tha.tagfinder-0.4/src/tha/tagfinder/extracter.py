"""Extracter that extract info from a project"""
from distutils.version import LooseVersion
import re


NAME_PATTERN = re.compile(r"""
    name\W*=\W*    # 'name =  ' with possible whitespace
    [\"\']         # Opening (double) quote.
    (?P<name>.+?)  # Something, but match non-greedy, store in 'name'
    [\"\']         # Closing (double) quote.
    """, re.VERBOSE)


class TagNotFoundError(Exception):
    pass


class BaseExtracter(object):
    """Basic info extracter"""

    def __init__(self, lister):
        """Just return the location info"""
        self.directory = lister
        self._tags = None

    @property
    def location(self):
        """Root of the project (so dir that contains trunk/tags)"""
        return self.directory.location

    @property
    def trunk(self):
        """Trunk location"""
        return self.directory.fullpath('trunk')

    @property
    def tags(self):
        if self._tags is None:
            self._tags = self._calculate_tags()
        return self._tags

    def _calculate_tags(self):
        """Return dict of tag/directory"""
        if 'tags' not in self.directory.contents:
            return []
        tagdir = self.directory.traverse('tags')
        tags = tagdir.contents
        # Filter out everything not starting with a number
        tags = [tag for tag in tags
                if isinstance(LooseVersion(tag).version[0], int)]
        # Not handled yet: tags that don't match setup.py.
        # Is that still needed?
        tags.sort(key=version_key)
        return tags

    def tag_location(self, tag):
        """Return location of tag"""
        if 'tags' not in self.directory.contents:
            raise TagNotFoundError('Tag dir not found')
        tagdir = self.directory.traverse('tags')
        if tag not in tagdir.contents:
            raise TagNotFoundError(tag)
        return tagdir.fullpath(tag)

    @property
    def name(self):
        return self._setup_py_name() or self._base_name()

    def _base_name(self):
        """Return last path element as name"""
        return self.location.split('/')[-1]

    def _setup_py_name(self):
        """Return name according to the setup.py, if available"""
        if 'setup.py' in self.directory.head.contents:
            for line in self.directory.head.cat('setup.py'):
                match = NAME_PATTERN.search(line)
                if match:
                    name = match.group('name').strip()
                    return name


def version_key(tag_string):
    """Return version value suitable for sorting"""
    return LooseVersion(tag_string).version

