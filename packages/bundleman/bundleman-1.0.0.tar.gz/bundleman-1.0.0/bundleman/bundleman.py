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
"""Bundle Manager

$Id: bundleman.py 49129 2006-09-18 06:50:00Z bdelbosc $
"""
import sys
import os
import logging
from tempfile import mkdtemp
from optparse import OptionParser, TitledHelpFormatter

from version import __version__
from utils import command, initLogger, computeTagUrl, createBundle, getHashTag
from utils import SVN_EXTERNALS, parseNuxeoHistory, rst_title
from productman import ProductMan


logger = logging.getLogger('bm.bundleman')


def isValidBundlePath(bundle_path):
    """Check that the bundle_path is valid."""
    if not bundle_path:
        return False
    if not os.path.exists(os.path.join(bundle_path, '.svn')):
        return False
    ret, output = command('svn pl %s | grep "svn:externals"' % bundle_path,
                          do_raise=False)
    if ret:
        return False
    if len(output) != 1:
        return False
    return True


class BundleMan:
    """A Bundle manager class."""
    def __init__(self, bundle_path, release_tag=None, verbose=False,
                 force=False, requires_valid_bundle=True):
        self.bundle_path = bundle_path
        if requires_valid_bundle and not isValidBundlePath(bundle_path):
            msg = 'Invalid bundle path: %s.' % bundle_path
            logger.error(msg)
            raise ValueError(msg)

        self.release_tag = release_tag
        self.verbose = verbose
        self.force = force
        if bundle_path.endswith('/'):
            self.bundle_path = bundle_path[:-1]
        logger.debug('Init bundle_path: ' + self.bundle_path)
        self.analyzed = False
        self.already_prompted = False
        self.products = []
        self.bundle_url = self.getSvnUrl()


    def listProducts(self, bundle_path=None):
        """return the list of products of a bundle.

        format: [{'path':value, 'url':value, 'revision':value}, ...]
        """
        if bundle_path is None:
            bundle_path = self.bundle_path
        logger.debug('listProducts of bundle: %s' % bundle_path)
        status, output = command('svn pg svn:externals ' + bundle_path)
        products = []
        if status:
            return products
        for line in output:
            if not line or line.startswith('#'):
                continue
            ret = line.split()
            if not ret:
                continue
            path = ret[0]
            url = ret[-1]
            if not (url.startswith('http') or url.startswith('file')):
                if line[0] != '#':
                    logger.warning('Skip invalid svn return line: [%s]' % line)
                continue

            revision = None
            if len(ret) == 3:
                revision = ret[1]
                if revision.startswith('-r'):
                    revision = revision[2:]
                else:
                    logger.warning(
                        'Skipping invalid revision [%s] in line: [%s]' %
                        (revision, line))
                    revision = None
            products.append({'path':path, 'url':url, 'revision':revision})
        return products

    def getSvnUrl(self):
        """Extract the svn url from the bundle path."""
        status, output = command(
            "svn info " + self.bundle_path + " | grep '^URL'",
            do_raise=False)
        if status:
            return None
        if len(output) == 1:
            url_line = output[0].split(':', 1)
            if url_line[0] == 'URL':
                return url_line[1].strip()
        logger.warning('URL not found, invalid output: [%s]' % output)
        return None

    def analyze(self, force=False, show_action=False, verbose=False):
        """Analyze all products."""
        if self.analyzed and not force:
            return
        if not show_action:
            logger.info('Analyze all products ...')
        ret = 0
        products = self.listProducts()
        self.products = []
        for product in products:
            prod = ProductMan(os.path.join(self.bundle_path, product['path']),
                              product['url'], product['revision'])
            prod.analyze()
            if show_action:
                ret = ret | prod.showAction(verbose)
            self.products.append(prod)
        self.analyzed = True
        return ret

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
        self.prompt('Initialize bundle %s [y/N]: ' % self.bundle_url)
        self.already_prompted = True

    def init(self):
        """Create and commit default files."""
        logger.info('Initialize bundle %s.' % self.bundle_path)
        # check svn tree
        url = self.bundle_url
        path = self.bundle_path
        if not url or os.path.basename(url) != 'trunk':
            logger.error(
                'Expecting a bundle WCPATH that point to a trunk url.')
            return -1
        bundle_url = os.path.dirname(url)
        for folder in ('tags', 'branches'):
            ret, output = command('svn ls %s/%s' % (bundle_url, folder),
                                  do_raise=False)
            if ret:
                logger.error('Missing folder %s/%s.' % (bundle_url, folder))
                return -1
        # check files
        externals_path = os.path.join(path, SVN_EXTERNALS)
        if os.path.exists(externals_path):
            logger.warning('Bundle already initialized')
        else:
            self.promptInitialize()
            status, output = command('svn pg svn:externals %s' % path)
            if status or not output:
                logger.error('No svn:externals defined on %s.' % path)
                return -1
            logger.info('Creating %s file.' % SVN_EXTERNALS)
            f = open(externals_path, 'w+')
            f.write('\n'.join(output))
            f.close()
            command('svn add %s' % externals_path)
            command('svn commit -m"bundleman adding %s" %s' % (
                SVN_EXTERNALS, externals_path))

        return 0

    def showAction(self, verbose=None):
        """List things to do."""
        if verbose is None:
            verbose = self.verbose
        logger.info('List of actions to do:')
        ret = self.analyze(show_action=True, verbose=verbose)
        if not ret:
            logger.info('Ready: All products have been already released.')
        elif ret > 0:
            logger.info('Ready: Going to release some products.')
        else:
            logger.warning('Bundle not ready to be released.')
        return ret

    def doAction(self):
        """Do action for all products."""
        self.analyze()
        ret = 0
        for product in self.products:
            ret = ret | product.doAction()
        if ret or not self.release_tag:
            logger.error('Bundle is not ready to be released.')
            return ret
        ret = self.tag()
        return ret


    def tag(self):
        """Create a bundle tags/release_tag."""
        release_tag = self.release_tag
        logger.info('Create a bundle tag %s' % release_tag)

        # check bundle url
        bundle_url = self.bundle_url

        tag_url = computeTagUrl(bundle_url, release_tag)
        if tag_url is None:
            logger.error('Invalid bundle url: %s' % bundle_url)
            return -1
        ret, output = command('svn ls %s' % tag_url, do_raise=False)
        if not ret:
            logger.error('Bundle tag %s already exists.' % tag_url)
            return -1

        # analyze products
        self.analyze(force=True)
        bad_products = []
        products = []
        for product in self.products:
            if product.status != 'use_tag':
                bad_products.append(product)
            products.append({'path': product.path,
                             'revision': product.revision,
                             'url': product.tag_url})
        if bad_products:
            logger.warning('Sorry found product(s) not ready:')
            for product in bad_products:
                print str(product)
            return -1

        # create bundle
        logger.info('Creating bundle %s' % tag_url)
        createBundle(tag_url, products, release_tag)
        return 0


    def branch(self):
        """Create a branch for all products from a bundle tag."""
        release_tag = self.release_tag
        hash_tag = getHashTag(release_tag)
        bundle_tag_url = computeTagUrl(self.bundle_url, release_tag)
        if not bundle_tag_url:
            logger.error('Invalid source url: %s' % self.bundle_url)
            return -1
        bundle_branch_url = bundle_tag_url.replace('/tags/', '/branches/')
        logger.info('Branching %s -> %s hash_tag: %s.' %
                    (bundle_tag_url, bundle_branch_url, hash_tag))
        ret, output = command('svn ls %s' % bundle_tag_url, do_raise=False)
        if ret:
            logger.error('Tag not found. You need to release %s first.' %
                         release_tag)
            return -1
        ret, output = command('svn ls %s' % bundle_branch_url, do_raise=False)
        if not ret:
            logger.error('Branch %s already exists.' % bundle_branch_url)
            return -1
        products = self.listProducts(bundle_tag_url)
        branch_products = []

        # create a branch for each product
        for product in products:
            product_url = product['url']
            parent = os.path.dirname(product_url)
            ret = -1
            if os.path.basename(parent) == 'tags':
                ret, output = command('svn ls %s/CHANGES' % product_url,
                                      do_raise=False)
            if ret:
                # not a versionned product keep it asis
                branch_products.append(product)
                continue

            branch_url = os.path.dirname(parent) + '/branches/' + hash_tag
            ret, output = command('svn ls %s' % branch_url, do_raise=False)
            if not ret:
                logger.warning('Branch %s already exists.' % branch_url)
            else:
                command('svn copy -m"bundleman branch product %s release %s"'
                        '-r%s %s %s' %
                        (product['path'], hash_tag, product['revision'],
                         product_url, branch_url))
            branch_products.append({'path': product['path'],
                                    'url': branch_url})

        # create a bundle branch
        logger.info('Creating bundle %s' % bundle_branch_url)
        createBundle(bundle_branch_url, branch_products, release_tag)
        return bundle_branch_url

    def buildArchive(self, archive_dir):
        """Create a tar gz archive in archive_dir."""
        self.analyze(force=True)
        products = self.products
        products_ready = True
        for product in products:
            if product.status != 'use_tag':
                logger.error('Product %s not ready to be archived.' %
                             product.path)
                product.showAction()
                products_ready = False
        if not products_ready:
            return -1

        archive_name = '%s.tgz' % self.release_tag
        archive_path = os.path.join(archive_dir, archive_name)
        logger.info('Creating archive: %s' % archive_name)

        # extract tag
        tmpdir = mkdtemp()
        bundle_name = self.release_tag
        bundle_path = os.path.join(tmpdir, bundle_name)
        bundle_tag_url = computeTagUrl(self.bundle_url, bundle_name)
        command('svn -q export %s %s' % (bundle_tag_url, bundle_path))

        if not os.path.exists(bundle_path):
            # svn export don't complain on invalid url
            logger.error('Tag %s not found, use --release first.' %
                         bundle_tag_url)
            return -1

        # cleaning archive
        for product in self.products:
            product_path = os.path.join(bundle_path, product.path)
            try:
                os.rename(os.path.join(product_path, 'HISTORY'),
                          os.path.join(product_path, 'CHANGELOG.txt'))
                os.remove(os.path.join(product_path, 'CHANGES'))
            except OSError:
                # happens if not BM-versioned (vendor...)
                pass
            version_path = os.path.join(product_path, 'version.txt')
            if not os.path.exists(version_path):
                f = open(os.path.join(product_path, 'version.txt'), 'w+')
                f.write('%s-%s\n' % (product.version[1], product.version[2]))
                f.close()

        # add version
        f = open(os.path.join(bundle_path, 'version.txt'), 'w+')
        f.write('%s\n' % bundle_name)
        f.close()

        # add MD5SUMS
        command('cd %s; find . -type f -not -name MD5SUMS | xargs md5sum'
                '> MD5SUMS' % bundle_path)

        # tarball
        command('cd %s; tar czvf %s %s' % (tmpdir, archive_path, bundle_name))
        command('rm -rf %s' % tmpdir)
        logger.info('Archive: %s' % archive_path)
        return 0

    def changelog(self, tag1, tag2):
        """Output a changelog between to bundle tags."""
        # compute tags url
        url = self.bundle_url
        if url.endswith('/trunk'):
            tag1_url = url.replace('/trunk', '/tags/' + tag1)
            tag2_url = url.replace('/trunk', '/tags/' + tag2)
        elif url.count('/branches/') or url.count('/tags'):
            tmp = url.find('/branches/')
            if tmp == -1:
                tmp = url.find('/tags/')
            tag1_url = url[:tmp] + '/tags/' + tag1
            tag2_url = url[:tmp] + '/tags/' + tag2
        else:
            logger.error('Invalid bundle url: %s' % url)
            return -1
        return self._changelog(tag1, tag2, tag1_url, tag2_url)

    def changelog_url(self, tag1_url, tag2_url):
        """Output a changelog between to bundle urls."""
        tag1 = os.path.basename(tag1_url)
        tag2 = os.path.basename(tag2_url)
        return self._changelog(tag1, tag2, tag1_url, tag2_url)

    def _changelog(self, tag1, tag2, tag1_url, tag2_url):
        """Output a changelog between to bundle url."""

        # check that tags exists
        for tag_url in (tag1_url, tag2_url):
            ret, output = command('svn ls %s' % tag_url, do_raise=False)
            if ret:
                logger.error('Tags %s not found.' % tag_url)
                return -1

        # get list of products
        prod1_infos = self.listProducts(tag1_url)
        prod2_infos = self.listProducts(tag2_url)
        prod1_list = [prod.get('path') for prod in prod1_infos]
        prod2_list = [prod.get('path') for prod in prod2_infos]

        new_products = [prod for prod in prod2_list if prod not in prod1_list]
        removed_products = [prod for prod in prod1_list
                            if prod not in prod2_list]
        check_products = [prod for prod in prod2_list if prod in prod1_list]
        changed_products = []

        requires = []
        features = []
        bug_fixes = []
        int_features = []
        for prod in check_products:
            prod1 = [x for x in prod1_infos if x.get('path') == prod][0]
            prod2 = [x for x in prod2_infos if x.get('path') == prod][0]
            if prod1['url'] == prod2['url']:
                continue
            changed_products.append((prod, os.path.basename(prod1['url']),
                                     os.path.basename(prod2['url'])))
            # we ask for changes between HISTORY files
            hist1 = os.path.join(prod1['url'], 'HISTORY')
            hist2 = os.path.join(prod2['url'], 'HISTORY')

            ret, output = command('svn diff %s %s' % (hist1, hist2),
                                  do_raise=False)
            if ret:
                logger.warning('svn diff failed on product %s' % prod )
                continue
            diff = [line[1:] for line in output
                    if line.startswith('+') and not line.startswith('++')]
            ret = parseNuxeoHistory('\n'.join(diff))
            requires.extend(['[%s] %s'% (prod, line) for line in ret[0]])
            features.extend(['[%s] %s'% (prod, line) for line in ret[1]])
            bug_fixes.extend(['[%s] %s'% (prod, line) for line in ret[2]])
            int_features.extend(['[%s] %s'% (prod, line) for line in ret[3]])

        print rst_title("CHANGELOG between bundles %s and %s" %
                        (tag1, tag2), 0)
        print "New tag: %s" % tag2_url
        print "Old tag: %s" % tag1_url
        if new_products:
            print rst_title('New products', 2)
            print '\n'.join(new_products)
        if removed_products:
            print rst_title('Removed products', 2)
            print '\n'.join(removed_products)
        if changed_products:
            print rst_title('Changed products', 2)
            for prod in changed_products:
                print '* %s \t %s -> %s' % (prod[0], prod[1], prod[2])
        if requires:
            print rst_title('Requires', 3)
            print '* ' + '\n* '.join(requires)
        if features:
            print rst_title('Features', 3)
            print '* ' + '\n* '.join(features)
        if bug_fixes:
            print rst_title('Bug fixes', 3)
            print '* ' + '\n* '.join(bug_fixes)
        if int_features:
            print rst_title('Internal features', 3)
            print '* ' + '\n* '.join(int_features)

        return 0


class BundleManProgram:
    """Program class"""
    USAGE = """%prog [options] [WCPATH]

%prog is a bundle release manager. See BundleMan documentation for more
information.

WCPATH is a svn working copy path of a bundle, using current path if not
specified.

A bundle is an suite of products, this suites is defined using svn:externals
property of the bundle folder.

A bundle follows the classic trunk/tags/branches svn tree.

Products may be versionned using bm-product tool.

Examples
========
  %prog
                        Display status and action to be done.

  %prog --init
                        Initialize WCPATH bundle:
                          - add svn-externals file to trunk

  %prog --release APPrc1
                        Create release bundle in tags/APPrc1 that point to
                        released products.

  %prog --release APPrc1 -a
                        Create a release and a targz archive.

  %prog --archive APPrc1 -o /tmp
                        Create a targz archive in /tmp directory.
                        The tarball contains a MD5SUMS file and can be
                        verified using `md5sum -c MD5SUMS`.

  %prog --branch APPrc1
                        Create a branch bundle in branch/APPrc1 that point to
                        branched products.
                        A product branch will be created for each versioned
                        products. The branch name use a hash(APPrc1) key.

  %prog --changelog APPrc1:APPrc2
                        Output a global bundle changelog between bundle tags.
"""
    def __init__(self, argv=None):
        if argv is None:
            argv = sys.argv[1:]
        cur_path = os.path.abspath(os.path.curdir)
        self.bundle_path = cur_path
        self.release_tag = None
        options = self.parseArgs(argv)
        self.options = options
        if options.debug:
            level = logging.DEBUG
        else:
            level = logging.INFO
        initLogger('/tmp/bundleman.log', True, level)

    def parseArgs(self, argv):
        """Parse programs args."""
        parser = OptionParser(self.USAGE, formatter=TitledHelpFormatter(),
                              version="BundleMan %s" % __version__)

        def releasecb(option, opt, value, parser):
            """Parser callback."""
            setattr(parser.values, option.dest, value)
            setattr(parser.values, 'release', True)

        def branchcb(option, opt, value, parser):
            """Parser callback."""
            setattr(parser.values, option.dest, value)
            setattr(parser.values, 'branch', True)

        def archivecb(option, opt, value, parser):
            """Parser callback."""
            setattr(parser.values, option.dest, value)
            setattr(parser.values, 'archive', True)

        parser.add_option("-s", "--status", action="store_true",
                          help="Show action to be done.",
                          default=True)
        parser.add_option("-i", "--init", action="store_true",
                          help="Initialize the bundle working copy.",
                          default=False)
        parser.add_option("--release", type="string", action="callback",
                          dest="release_tag", callback=releasecb,
                          help="Release the bundle.", default=None)
        parser.add_option("-a",  action="store_true",
                          dest="archive",
                          help="Build a tar gz archive, must be used with "
                          "--release option.", default=False)
        parser.add_option("--archive",  type="string", action="callback",
                          dest="release_tag", callback=archivecb,
                          help="Build a tar gz archive from an existing"
                          "RELEASE_TAG.", default=None)
        cur_path = os.path.abspath(os.path.curdir)
        parser.add_option("-o", "--output-directory", type="string",
                          dest="output_dir",
                          help="Directory to store the archive.",
                          default=cur_path)
        parser.add_option("--branch", type="string", action="callback",
                          dest="release_tag", callback=branchcb,
                          help="Branch the bundle release.", default=None)
        parser.add_option("--changelog", type="string", default=None,
                          dest="TAG1:TAG2",
                          help="Output a changelog between 2 bundle tags.")
        parser.add_option("--changelog-url", type="string", default=None,
                          dest="TAG1_URL:TAG2_URL",
                          help="Output a changelog between 2 bundle url tags.")
        parser.add_option("-f", "--force", action="store_true",
                          help="No prompt during --init.", default=False)
        parser.add_option("-v", "--verbose", action="store_true",
                          help="Verbose output", default=False)
        parser.add_option("-d", "--debug", action="store_true",
                          help="Debug output", default=False)

        parser.set_defaults(release=False, branch=False, archive=False)
        options, args = parser.parse_args(argv)
        if len(args) == 1:
            self.bundle_path = os.path.abspath(args[0])
        if options.archive and not options.release_tag:
            parser.error("-a option must be used with --release option.")
        changelog = getattr(options, 'TAG1:TAG2')
        if changelog:
            if not changelog.count(':'):
                parser.error("Invalid value for '--changelog' option, "
                             "expects a TAG_RELEASE1:TAG_RELEASE2 input.")
        options.changelog = changelog
        changelog_url = getattr(options, 'TAG1_URL:TAG2_URL')
        if changelog_url:
            if changelog_url.count(':') != 3:
                parser.error("Invalid value for '--changelog-url' option, "
                             "expects a TAG1_URL:TAG2_URL input.")
        options.changelog_url = changelog_url

        return options


    def run(self):
        """Main."""
        options = self.options
        try:
            requires_valid_bundle = True
            if options.changelog_url:
                requires_valid_bundle = False
            bman = BundleMan(self.bundle_path, options.release_tag,
                             verbose=options.verbose,
                             force=options.force,
                             requires_valid_bundle=requires_valid_bundle)
        except ValueError:
            return -1
        if options.changelog:
            tag1, tag2 = options.changelog.split(':')
            ret = bman.changelog(tag1.strip(), tag2.strip())
        elif options.changelog_url:
            ret = options.changelog_url.split(':')
            tag1_url = ':'.join(ret[:2])
            tag2_url = ':'.join(ret[2:])
            ret = bman.changelog_url(tag1_url.strip(), tag2_url.strip())
        elif options.init:
            ret = bman.init()
        elif options.release:
            ret = bman.doAction()
            if not ret and options.archive:
                ret = bman.buildArchive(options.output_dir)
        elif options.archive:
            ret = bman.buildArchive(options.output_dir)
        elif options.release_tag:
            ret = bman.branch()
        else:
            ret = bman.showAction()

        return ret

def main():
    prog = BundleManProgram()
    ret = prog.run()
    sys.exit(ret)

if __name__ == '__main__':
    main()
