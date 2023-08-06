import logging


logger = logging.getLogger('tagfinder')


class Finder(object):
    """Recursively detect trunk/tag projects in a structure"""

    def __init__(self, lister, info_extracter,
                 stop_indicators=[]):
        self.lister = lister
        self.stop_indicators = stop_indicators
        projects = sorted(self._find_projects())
        self.projects = [info_extracter(project) for project in projects]

    def _find_projects(self, lister=None):
        """Iterate through the structure and return projects"""
        projects = []
        if lister == None:
            lister = self.lister
        if lister.is_project:
            logger.info("Found project: %s", lister.location)
            projects.append(lister)
        elif [item for item in lister.contents
              if item in self.stop_indicators]:
            logger.debug("Found stop indicator, not doing anything with %s",
                         lister.location)
            return projects
        else:
            subdirs = [subdir for subdir in lister.contents
                       if lister.is_dir(subdir)]
            for subdir in subdirs:
                projects += self._find_projects(
                    lister=lister.traverse(subdir))
        return projects
