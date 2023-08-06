import commands
import os
import pkg_resources
import shutil
import tempfile

import z3c.testsetup


def svn_setup(test):
    """Set up test svn repository in a temporary directory"""
    test.tempdir = tempfile.mkdtemp()
    repo = os.path.join(test.tempdir, 'repo')
    repo_url = 'file://' + repo
    test.globs['repo_url'] = repo_url
    commands.getoutput('svnadmin create ' + repo)
    fixture_dir = pkg_resources.resource_filename('tha.tagfinder.tests',
                                                  'fixture')
    test.globs['fixture_dir'] = fixture_dir
    export = os.path.join(test.tempdir, 'export')
    output = commands.getoutput('svn export %s %s' % (fixture_dir, export))
    if 'not a working copy' in output:
        # We're not working from a local svn checkout, but for instance from
        # an egg.  In that case, use the fixture dir as the "export"
        # location.
        export = fixture_dir
    commands.getoutput('svn import %s %s -m "import"' % (export, repo_url))


def svn_teardown(test):
    """Clean up temporary directory"""
    #print test.tempdir
    shutil.rmtree(test.tempdir)


test_suite = z3c.testsetup.register_all_tests('tha.tagfinder',
                                              setup=svn_setup,
                                              teardown=svn_teardown)
