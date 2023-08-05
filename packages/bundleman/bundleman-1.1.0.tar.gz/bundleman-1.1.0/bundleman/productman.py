# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author: bdelbosc@nuxeo.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#
"""Product Manager.

$Id: productman.py 49642 2006-10-17 15:57:01Z bdelbosc $
"""
import sys
import os
import logging
from datetime import datetime
from optparse import OptionParser, TitledHelpFormatter
from tempfile import mkdtemp

from version import __version__
from utils import command, initLogger, computeTagUrl, parseZopeVersionFile
from utils import parseVersionString, parseNuxeoVersionFile, parseNuxeoChanges
from utils import prepareProductArchive

logger = logging.getLogger('bm.productman')

class ProductMan:
    """Manage a product."""

    tpl_changes = """Requires
~~~~~~~~
-
New features
~~~~~~~~~~~~
-
Bug fixes
~~~~~~~~~
-
New internal features
~~~~~~~~~~~~~~~~~~~~~
- %s
"""
    tpl_version = """# BUNDLEMAN PRODUCT CONFIGURATION FILE
# do not edit this file
PKG_NAME=%s
PKG_VERSION=%s
PKG_RELEASE=%s
"""

    def __init__(self, fpath, url=None, revision=None, verbose=False,
                 force=False, increment_major=False, release_again=False):
        """
        fpath is the full path of the check out
        url is the svn url repo
        revision is a svn revision if any.
        """
        if fpath.endswith('/'):
            self.fpath = fpath[:-1]
        else:
            self.fpath = fpath
        self.verbose = verbose
        self.force = force
        self.increment_major = increment_major
        self.release_again = release_again
        self.path = os.path.basename(self.fpath)
        if url is not None:
            self.url = url
        else:
            self.url = self.getSvnUrl()
        self.revision = revision
        self.version = None
        self.changes = None
        self.status = None
        self.version_new = None
        self.tag_url = None
        self.analyzed = False
        self.already_prompted = False
        self.bm_versioned = self.isManaged()
        logger.debug('Init product: ' + self.path)

    def analyze(self, force=False):
        """Extract all needed information."""
        if self.analyzed and not force:
            return
        logger.debug('Analyze product: %s' % self.path)
        if self.url is None:
            self.url = self.getSvnUrl()
        if self.revision is None or force:
            self.revision = self.getSvnRevision()
        self.version = self.getVersion()
        self.changes = self.getChanges()
        self.status = self.getStatus()
        self.version_new = self.computeVersion()
        self.tag_url = self.computeTagUrl()
        self.analyzed = True

    def isManaged(self):
        """Check if product is managed with bundleman."""
        ret, output = command('svn pl %s | grep "bundleman"' % self.fpath,
                              do_raise=False)
        if ret:
            return False
        return True

    def showAction(self, verbose=None):
        """Render action to do."""
        if verbose is None:
            verbose = self.verbose
        self.analyze()
        status = self.status
        exit_code = -1
        logger.debug(str(self))
        name = self.path
        if self.version[1]:
            str_version = '%s-%s' % (self.version[1], self.version[2])
        else:
            str_version = 'not-versioned'
        if status == 'new_version':
            print "%-25s %-20s New version: %s-%s" % (name,
                                                      str_version,
                                                      self.version_new[1],
                                                      self.version_new[2])
            exit_code = 1
        elif status == 'use_tag':
            if self.bm_versioned:
                state = 'Already released'
            else:
                state = 'Not versioned with bundleman'
            if verbose:
                print "%-25s %-20s %s." % (name, str_version, state)
            exit_code = 0
        elif status == 'missing_changes':
            print "%-25s %-20s CHANGES file must be filled !." % (name,
                                                                  str_version)
        elif status == 'svn_not_uptodate':
            print "%-25s %-20s Requires a svn update/commit." % (
                name, str_version)
        elif status == "invalid":
            print "%-25s %-20s Invalid svn repository" % (name, str_version)
        elif status == 'tag_not_found':
            print "%-25s %-20s First version %s-%s" % (name, str_version,
                                                       self.version_new[1],
                                                       self.version_new[2])
        else:
            print "UNKNOWN: %s" % str(self)
        return exit_code

    def doAction(self):
        """Tag the product if needed"""
        self.analyze()
        status = self.status
        if status in ('new_version', 'tag_not_found'):
            return self.tagVersion()
        else:
            self.showAction(True)
            if status not in ('use_tag'):
                return -1
        return 0

    def __str__(self):
        """Render a product."""
        txt = """Product: %s
        Status:           %s
        Svn url:          %s
        Svn revision:     %s
        Version:          %s
""" % (self.path, self.status, self.url, self.revision,
       self.version)
        if not self.bm_versioned:
            txt += "        This product is not versioned with bm!\n"

        if (self.status in ('new_version', 'tag_not_found') and
            self.version_new and filter(None, self.version_new)):
            ident = "\n" + 14*' '
            txt += """\
        New version:      %s
        Svn target tag:   %s
        Changes:
            Requires:
              %s
            Features:
              %s
            Bug fixes:
              %s
            Internal Features:
              %s
"""  % (self.version_new, self.tag_url,
        ident.join(self.changes[0]), ident.join(self.changes[1]),
        ident.join(self.changes[2]), ident.join(self.changes[3]))
        else:
            txt += "        Svn tag:          %s" % self.tag_url
        return txt

    # --------------------------------------------------
    # extract information from a co
    def getSvnUrl(self):
        """Extract the svn url from the product path."""
        status, output = command(
            "svn info " + self.fpath + " | grep '^URL'",
            do_raise=False)
        if not status and len(output) == 1:
            url_line = output[0].split(':', 1)
            if url_line[0] == 'URL':
                return url_line[1].strip()
        msg = 'Invalid product path %s, or svn url.' % self.fpath
        logger.error(msg)
        raise ValueError(msg)

    def getSvnRevision(self):
        """Extract the svn revision of the product path.

        Check that all the product is sync with the same revision.
        """
        status, output = command(
            "svn info -R " + self.fpath + " | grep '^Revision' | sort -u",
            do_raise=False)
        if status:
            return None
        if len(output) == 1:
            rev_line = output[0].split(':')
            if rev_line[0] == 'Revision':
                return rev_line[1].strip()
        if len(output) > 1:
            logger.debug('Product [%s] is out of date' % self.path)
        else:
            logger.warning('Invalid output: [%s]' % output)
        return None

    def getSvnLastChangedRevision(self, url=None):
        """Extract from the svn repository the latest changed revision."""
        if url is None:
            url = self.url
        status, output = command("svn info %s | grep '^Last Changed Rev: '" %
                                 url, do_raise=False)
        if status:
            return None
        if len(output) == 1:
            rev_line = output[0].split(':')
            return rev_line[1].strip()
        logger.warning('Invalid output: [%s]' % output)
        return None

    def getVersion(self):
        """Extract name, version, release from VERSION or version.txt file."""
        ret = [None, None, None]
        content = None
        for file_name in ('version.txt', 'VERSION.txt', 'VERSION'):
            version_path = os.path.join(self.fpath, file_name)
            try:
                content = open(version_path).read()
                break
            except IOError:
                continue
        if not content:
            logger.debug("No version file found for %s, "
                         "not bundleman managed product." % self.path)
            self.bm_versioned = False
            return ret
        try:
            if file_name == 'VERSION':
                ret = parseNuxeoVersionFile(content)
            else:
                ret = parseZopeVersionFile(content)
        except ValueError:
            logger.warning('Product [%s] has invalid version %s file.' % (
                self.path, file_name))
        if not ret[0]:
            ret[0] = self.path
        return ret

    def getChanges(self):
        """Return the change type."""
        changes_path = os.path.join(self.fpath, 'CHANGES')
        content = ''
        try:
            content = open(changes_path).read()
        except IOError:
            self.bm_versioned = False
            logger.debug('no CHANGES file in product %s' % self.path)
        return parseNuxeoChanges(content)

    def getStatus(self):
        """Return a status:

        new_version:      ready to be packaged
        use_tag:          already tagged
        svn_not_uptodate: require a svn up
        missing_changes:  changes is empty but src differ from last package
        tag_not_found:    the version tag does not exist
        invalid:          svn repo not accessible
        """
        if not self.revision:
            return 'svn_not_uptodate'

        if not self.force:
            # do not accept locally modified by default, do not check externals
            status, output = command("svn status --ignore-externals %s "
                                     " | grep -v '^[?X]'" %
                                     self.fpath, do_raise=False)
            if output:
                logger.debug('Found some locally modified: %s' % output)
                return 'svn_not_uptodate'
        if not self.bm_versioned:
            # do not touch a product not versioned with bundleman
            return 'use_tag'

        co_url = self.url
        package_url = self.computeTagUrl()

        if co_url != package_url:
            try:
                last_changed_rev = int(self.getSvnLastChangedRevision())
                revision = int(self.revision)
            except (TypeError, ValueError):
                return 'invalid'

            if last_changed_rev > revision:
                # not in sync with the trunk or branch
                # prevent to release with a wc not up to date
                logger.debug("Svn repository contains changes at r%d "
                             "the wc is at r%d and requires a svn up." % (
                    last_changed_rev, revision))
                return 'svn_not_uptodate'

        if co_url != package_url and filter(None, self.changes):
            return 'new_version'

        if co_url == package_url:
            return 'use_tag'

        # check if the tag exists
        status, output = command("svn ls %s" % package_url, do_raise=False)
        if status:
            return 'tag_not_found'

        # check if the latest package is identical to our co
        status, output = command("svn diff %s@%s %s" %
                                 (co_url, self.revision,
                                  package_url), do_raise=False)
        if status:
            return 'invalid'
        if output:
            if self.release_again:
                return 'new_version'
            return 'missing_changes'

        return 'use_tag'

    def computeTagUrl(self):
        """Using version file guess the tag url of the product."""
        co_url = self.url
        if self.version_new and self.version_new[1]:
            tag = self.version_new[1]
        else:
            tag = self.version[1]
        if not tag:
            return co_url
        if not self.bm_versioned:
            return co_url
        package_url = computeTagUrl(co_url, tag)
        if not package_url:
            return co_url
        return package_url


    def computeVersion(self):
        """Computes the new version of the product."""
        changes = self.changes
        name = self.version[0]
        version = parseVersionString(self.version[1])
        release = self.version[2] and int(self.version[2])
        if not filter(None, changes) or not version:
            if self.status == 'tag_not_found':
                if self.version[1]:
                    # need to create the tag
                    return self.version
                else:
                    # not a versioned product
                    return [None, None, None]
            if not self.release_again and self.status != 'new_version':
                # no change
                return [None, None, None]

        if changes[0] or changes[1] or changes[3]:
            # any requires/features/int. features
            release = 1
            if self.increment_major:
                # major++
                version[0] += 1
                version[1] = 0
                version[2] = 0
            else:
                # minor++
                version[1] = version[1] + 1
                version[2] = 0
        elif changes[2]:
            # bug fixes
            release = 1
            version[2] = version[2] + 1
        else:
            # release again
            release += 1
        str_version = '.'.join(map(str, version)[:-1])
        if '/branches/' in self.url:
            # setup branch flag
            str_version += '-' + os.path.basename(self.url)
        return [name, str_version, str(release)]


    # --------------------------------------------------
    # actions
    #
    def prompt(self, query):
        """Prompt user for a positive reply."""
        if self.force:
            return
        sys.stdout.write(query)
        res = sys.stdin.readline().strip().lower()
        if res[0] not in 'yo':
            logger.warning('User abort.')
            sys.exit(-2)

    def promptInitialize(self):
        """Prompt user if ready to initialize a product."""
        if self.already_prompted:
            return
        self.prompt('Initialize product %s [y/N]: ' % self.url)
        self.already_prompted = True

    def init(self):
        """Create and commit default files."""
        self.analyze()
        logger.info('Initialize product %s.' % self.path)
        fpath = self.fpath
        # check svn tree
        url = self.url
        if not url or os.path.basename(self.url) != 'trunk':
            logger.error(
                'Expecting a working copy path that point to a trunk url.')
            return -1
        prod_url = os.path.dirname(url)
        for folder in ('tags', 'branches'):
            ret, output = command('svn ls %s/%s' % (prod_url, folder),
                                  do_raise=False)
            if ret:
                logger.error('Missing folder %s/%s.' % (prod_url, folder))
                return -1
        # check files
        changes_path = os.path.join(fpath, 'CHANGES')
        files_to_add = []
        if os.path.exists(changes_path):
            logger.debug('CHANGES file already exist.')
        else:
            self.promptInitialize()
            logger.info('Creating CHANGES file.')
            f = open(changes_path, 'w+')
            msg_first_package = 'First package'
            f.write(self.tpl_changes % msg_first_package)
            f.close()
            files_to_add.append(changes_path)

        version_path = os.path.join(fpath, 'VERSION')
        if os.path.exists(version_path):
            logger.debug('VERSION file already exists.')
        else:
            self.promptInitialize()
            logger.info('Creating VERSION file.')
            f = open(version_path, 'w+')
            name = self.version[0]
            version = self.version[1]
            release = self.version[2]
            if not name:
                name = self.path
                self.version[0] = name
            if not version:
                version = '0.0.0'
                self.version[1] = version
            if not release:
                release = '1'
                self.version[2] = release
            f.write(self.tpl_version % tuple(self.version))
            f.close()
            files_to_add.append(version_path)

        history_path = os.path.join(fpath, 'HISTORY')
        if os.path.exists(history_path):
            logger.debug('HISTORY file already exists.')
        else:
            self.promptInitialize()
            logger.info('Creating HISTORY file.')
            f = open(history_path, 'w+')
            f.write('')
            f.close()
            files_to_add.append(history_path)

        if files_to_add:
            command('svn add ' + ' '.join(files_to_add))

        if not self.bm_versioned:
            logger.info('Add a bundleman svn property.')
            command("svn ps bundleman 'manages this product.' %s" % fpath)
            files_to_add.append(fpath)

        if files_to_add:
            command('svn commit -N -m"bundleman init." %s' %
                    ' '.join(files_to_add))
            command('svn up %s' % fpath)
            self.analyzed = False
            self.revision = None
        else:
            logger.info('Product was already initialized.')
        self.bm_versioned = True
        return 0

    def tagVersion(self):
        """Create a product tag and flush CHANGES, update VERSION."""
        if self.status not in ('new_version', 'tag_not_found'):
            return 0
        logger.info('Tag product %s version %s-%s' %
                    tuple(self.version_new))
        url = self.url
        revision = self.revision
        tag_url = self.tag_url
        prod_name = self.version_new[0]
        prod_version = self.version_new[1]
        fpath = self.fpath

        # check if the tag exists
        status, output = command("svn ls %s" % tag_url, do_raise=False)
        if not status:
            if self.release_again or self.force:
                logger.info('Removing exising tag %s' % tag_url)
                command("svn remove -m'bundleman replace tag' %s" % tag_url)
            else:
                logger.error('The new tag %s already exists.' % tag_url)
                return -1

        # copy src to tag
        command("svn copy -m'bundleman tag creation' -r%s %s %s" %
                (revision, url, tag_url))

        # switch to tag
        command("svn switch %s %s" % (tag_url, fpath))

        # update VERSION, CHANGES, HISTORY
        changes = open(os.path.join(fpath, 'CHANGES')).read()
        history = open(os.path.join(fpath, 'HISTORY')).read()
        f = open(os.path.join(fpath, 'HISTORY'), 'w+')
        header = """===========================================================
Package: %s %s
===========================================================
First release built by: %s at: %s
SVN Tag: %s
Build from: %s@%s

""" % (prod_name, prod_version, os.getenv('USER'),
       datetime.now().isoformat()[:19], tag_url, self.url, revision)
        f.write(header)
        f.write(changes)
        f.write('\n')
        f.write(history)
        f.close()
        f = open(os.path.join(fpath, 'CHANGES'), 'w+')
        f.write(self.tpl_changes % '')
        f.close()
        # set up VERSION
        f = open(os.path.join(fpath, 'VERSION'), 'w+')
        f.write(self.tpl_version % tuple(self.version_new))
        f.close()

        # commit files
        command("svn commit -m'bundleman edit product %s %s in tag' "
                "%s/CHANGES %s/HISTORY %s/VERSION" % (
            prod_name, prod_version, fpath, fpath, fpath))

        # switch back to src
        command("svn switch %s %s" % (url, fpath))

        # merge stuff
        command("svn merge %s@%s %s %s" % (url, revision, tag_url, fpath))

        # commit
        command("svn commit -m'merging changes from %s' "
                "%s/CHANGES %s/HISTORY %s/VERSION" % (
            tag_url, fpath, fpath, fpath))

        command("svn up %s" % fpath)

        logger.info('Tag %s done.' % tag_url)
        # update status
        self.status = 'use_tag'
        self.version = self.version_new
        self.version_new = None
        self.analyzed = False
        self.revision = None
        return 0

    def buildArchiveFromUrl(self, archive_dir, url):
        """Create a tar gz from a svn url."""
        if url.count('/branches/') or url.count('/tags/'):
            name = os.path.basename(os.path.dirname(os.path.dirname(url)))
            version = os.path.basename(url)
        else:
            revision = self.getSvnLastChangedRevision(url)
            if url.endswith('/trunk'):
                name = os.path.basename(os.path.dirname(url))
            else:
                name = os.path.basename(url)
            version = 'r' + revision
        return self._buildArchive(archive_dir, url, name, version)

    def buildArchive(self, archive_dir):
        """Create a tar gz archive in archive_dir."""
        self.analyze()
        if self.status not in ('use_tag'):
            logger.error('Product not ready to be archived.')
            self.showAction()
            return -1
        if self.version[1]:
            version = self.version[1] + '-' + self.version[2]
        else:
            # not a bundleman product
            version = 'r' + self.revision
        self._buildArchive(archive_dir, self.tag_url, self.path, version)

    def prepareProductArchive(self, product_path, version):
        """Prepare a product checkout before creating an archive."""
        prepareProductArchive(product_path, self.bm_versioned, version)

    def _buildArchive(self, archive_dir, url, name, version):
        """Create a tar gz."""
        archive_name = '%s-%s.tgz' % (name, version)
        archive_path = os.path.join(archive_dir, archive_name)
        logger.info('Creating archive: %s' % archive_name)

        # extract tag
        tmpdir = mkdtemp()
        product_path = os.path.join(tmpdir, name)
        command('svn -q export %s %s' % (url, product_path))

        # cleaning archive
        self.prepareProductArchive(product_path, version)

        # add MD5SUMS
        command('cd %s; find . -type f -not -name MD5SUMS -print0 '
                '| xargs -0 md5sum > MD5SUMS' % product_path)

        # tarball
        command('cd %s; tar czf %s %s' % (tmpdir, archive_path, name))
        command('rm -rf %s' % tmpdir)
        logger.info('Archive: %s' % archive_path)
        return 0



class ProductManProgram:
    """Program class"""
    DEFAULT_LOG_PATH = '~/bundleman.log'
    USAGE = """%prog [options] [WCPATH]

%prog is a product release manager. See BundleMan documentation for more
information.

WCPATH is a svn working copy path of a product, using current path if not
specified.

Product follows the classic svn trunk/tags/branches repository layout.

Product is versioned using 3 files:

* CHANGES (not present in an archive) this file contains 4 sections:
  - Requires: things that must be done to install this new release.
  - New features: list of new features customer oriented.
  - Bug fixes: list of bug fix.
  - New internal features: list of new features devel oriented.
  This file *MUST* be filled during devel of the product.
  This file is reseted during product release.

* VERSION: (or version.txt in an archive) this file contains the product name,
  product version and release number. The version format is
  MAJOR.MINOR.BUGFIX[-branch_name].

  A new version is automaticly computed using the content of the CHANGES file
  with the following rules:
  - If there is *ONLY* bug fixes increment the BUGFIX number else increment the
    MINOR number.
  - If the svn url is a branch append the branch name to the version.

* HISTORY (or CHANGELOG.txt in an archive)
  This file contains the concatenation of all CHANGES.

Exemples
========

  %prog
                Display status and action to be done for WCPATH.

  %prog --init
                Initialize the WCPATH product:
                * Check that the WCPATH point to a trunk svn url.
                * Check that tags and branches svn url exists.
                * If missing prompt the user to add VERSION, CHANGES
                  and HISTORY files to the product working copy and
                  commit them.

  %prog --release
               Release the WCPATH product:
               * Analyse the working copy:
                  - Checks that WCPATH is up to date with the svn.
                  - Parses the CHANGES file and computes the new version
                  - If CHANGES is empty checks the that there is no diff
                    between the WCPATH and the tagged version.
               * Create a tag using WCPATH svn revision: tags/VERSION
               * Fush CHANGES into HISTORY, update VERSION files and commit,
                 in the tag and the WCPATH url.

  %prog --archive -o /tmp
               Create a tarball archive in the /tmp directory. The product must
               be released. The tarball contains a MD5SUMS file and can be
               verified using `md5sum -c MD5SUMS`.

"""
    def __init__(self, argv=None):
        if argv is None:
            argv = sys.argv[1:]
        cur_path = os.path.abspath(os.path.curdir)
        self.product_path = cur_path
        options = self.parseArgs(argv)
        self.options = options
        if options.debug:
            level = logging.DEBUG
        else:
            level = logging.INFO
        initLogger(options.log_file, True, level)
        logger.debug('### RUN ProductMan from %s args: %s ' %
                     (cur_path, ' '.join(argv)))

    def parseArgs(self, argv):
        """Parse programs args."""
        parser = OptionParser(self.USAGE, formatter=TitledHelpFormatter(),
                              version="BundleMan %s" % __version__)
        parser.add_option("-s", "--status", action="store_true",
                          help="Show status and action to be done for WCPATH.",
                          default=True)
        parser.add_option("--init", action="store_true",
                          help="Initialize the WCPATH product.",
                          default=False)
        parser.add_option("--release", action="store_true",
                          help="Release the product WCPATH.",
                          default=False)
        parser.add_option("--major", action="store_true",
                          help="Increment the MAJOR number instead of the "
                          "MINOR number of the version.",
                          default=False)
        parser.add_option("--again", action="store_true",
                          help="Rebuild the same version, increment the "
                          "release number.",
                          default=False)
        cur_path = os.path.abspath(os.path.curdir)
        parser.add_option("-a", "--archive", action="store_true",
                          help="Build a targz archive.", default=False)
        parser.add_option("--archive-url", type="string",
                          dest="svn_release_url",
                          help="Build a targz archive from a svn url.")
        parser.add_option("-o", "--output-directory", type="string",
                          dest="output_dir",
                          help="Directory to store the archive.",
                          default=cur_path)
        parser.add_option("-f", "--force", action="store_true",
                          help="No prompt during --init. "
                          "Replaces an existing tag during --release. "
                          "Release even with locally modified files.",
                          default=False)
        parser.add_option("-l", "--log-file", type="string",
                          dest="log_file",
                          help="The log file path. Default is %s." %
                          self.DEFAULT_LOG_PATH,
                          default=os.path.expanduser(self.DEFAULT_LOG_PATH))
        parser.add_option("-v", "--verbose", action="store_true",
                          help="Verbose output", default=True)
        parser.add_option("-d", "--debug", action="store_true",
                          help="Debug output", default=False)
        options, args = parser.parse_args(argv)
        if len(args) == 1:
            self.product_path = os.path.abspath(args[0])
        return options

    def run(self):
        """Main."""
        options = self.options
        try:
            pman = ProductMan(self.product_path, verbose=options.verbose,
                              increment_major=options.major,
                              url=options.svn_release_url,
                              release_again=options.again, force=options.force)
        except ValueError:
            return -1
        if options.init:
            ret = pman.init()
        elif options.release:
            ret = pman.doAction()
            if not ret and options.archive:
                ret = pman.buildArchive(options.output_dir)
        elif options.archive:
            ret = pman.buildArchive(options.output_dir)
        elif options.svn_release_url:
            ret = pman.buildArchiveFromUrl(options.output_dir,
                                           options.svn_release_url)
        else:
            ret = pman.showAction()
        return ret

def main():
    prog = ProductManProgram()
    ret = prog.run()
    sys.exit(ret)

if __name__ == '__main__':
    main()

