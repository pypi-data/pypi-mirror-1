# Copyright (C) 2008, Charles Wang <charlesw1234@163.com>
# Author: Charles Wang <charlesw1234@163.com>

import os
import os.path
import popen2
import shutil
import string

from ConfigParser import ConfigParser
from pkg_resources import parse_requirements
from setuptools.package_index import PackageIndex
from setuptools.archive_util import unpack_archive

from pypi2pkgsys.utils import *

patchdir = os.path.join(os.path.dirname(__file__), 'patches')
config = ConfigParser()
config.read(os.path.join(patchdir, 'index.ini'))

popen_fmt = '(cd %s; python setup.py dump | tail -n 1 -)'

class PYPI2Package(object):
    def __init__(self, PackageSystem, argv):
        self.options = { '--url' : 'http://pypi.python.org/simple',
                         '--download-dir' : '/var/tmp/pypi/downloads',
                         '--unpack-dir' : '/var/tmp/pypi/unpack' }

        self.pkgsys = PackageSystem()
        self.options = self.pkgsys.InitializeOptions(self.options)

        optname = None
        self.packages = []

        for arg in argv[1:]:
            if optname is not None:
                self.options[optname] = arg
                optname = None
            elif arg in self.options:
                optname = arg
            else:
                self.packages.append(arg)

        # Ensure the exists of the working directories.
        map(lambda diropt: ensure_dir(self.options[diropt]),
            ['--download-dir', '--unpack-dir'])

        self.options = self.pkgsys.FinalizeOptions(self.options)

    def run(self):
        # Prepare for iterations.
        pkgidx = PackageIndex(index_url = self.options['--url'])
        packages = self.packages
        unpackdir = self.options['--unpack-dir']

        # Main loop.
        ok_packages = []
        while len(packages) > 0:
            new_packages = []
            print 'Downloading %s ...' % string.join(packages)
            # Download the sources of all requested packages and return their
            # informations by Distribution object list.
            dists = map(lambda reqobj:
                            pkgidx.fetch_distribution(reqobj,
                                                      self.options['--download-dir'],
                                                      source = True),
                        parse_requirements(packages))
            assert len(packages) == len(dists)
            for idx in xrange(len(packages)):
                pkg = packages[idx]
                dist = dists[idx]
                if dist is None:
                    print '%s is None!'
                    continue
                print 'Processing ...', pkg

                pkgdir = '%s-%s' % (dist.project_name, dist.version)
                cfgsec = pkgdir
                pkgpath = os.path.join(unpackdir, pkgdir)
                # Get setup arguments of the dist.
                if config.has_option(cfgsec, 'mkdir'):
                    unpack_archive(dist.location, pkgpath)
                else:
                    unpack_archive(dist.location, unpackdir)
                if config.has_option(cfgsec, 'patches'):
                    for p in config.get(cfgsec, 'patches').split():
                        print 'Applying %s' % p
                        os.system('(cd %s; patch -p0 < %s)' % \
                                      (pkgpath, os.path.join(patchdir, p)))
                print 'Get distribution args from %s' % pkgpath
                p = popen2.popen2(popen_fmt % pkgpath)
                p[1].close()
                c = p[0].read()
                p[0].close()
                args = eval(c)
                shutil.rmtree(pkgpath)
                # All setup arguments are saved in args.

                args['package_path'] = dist.location
                args['package_file'] = os.path.basename(dist.location)
                args['package_dir'] = pkgdir

                if config.has_section(cfgsec):
                    for name, value in config.items(cfgsec):
                        args['config_' + name] = value
                if config.has_option(cfgsec, 'patches'):
                    args['package_patches'] = \
                        config.get(cfgsec, 'patches').split()
                else:
                    args['package_patches'] = []

                if 'install_requires' not in args or \
                        args['install_requires'] is None:
                    args['install_requires'] = []
                if 'extras_require' not in args or \
                        args['extras_require'] is None:
                    args['extras_require'] = {}

                # Generate package from args and options.
                updated, deps = self.pkgsys.GenPackage(args, self.options)
                ok_packages.append(pkg)
                new_packages = uniq_extend(new_packages, deps)

            # Process all required but not processed packages.
            packages = []
            for pkg in new_packages:
                if pkg not in ok_packages: packages.append(pkg)
