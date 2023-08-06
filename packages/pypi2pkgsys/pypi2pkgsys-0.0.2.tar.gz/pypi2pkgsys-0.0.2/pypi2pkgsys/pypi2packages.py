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
        dldir = self.options['--download-dir']
        unpackdir = self.options['--unpack-dir']

        # Main loop.
        ok_packages = []
        while len(packages) > 0:
            new_packages = []
            for idx in xrange(len(packages)):
                pkg = packages[idx]

                print 'Downloading %s ...' % pkg
                dist = map(lambda reqobj:
                               pkgidx.fetch_distribution(reqobj, dldir,
                                                         source = True),
                           parse_requirements([pkg]))[0]
                if dist is None:
                    print '%s is None!'
                    continue

                print 'Processing ...', pkg
                # Prepare parameters.
                pkgdir = '%s-%s' % (dist.project_name, dist.version)
                cfgmap = {}
                if config.has_section(pkgdir):
                    for name, value in config.items(pkgdir):
                        cfgmap[name] = value
                if config.has_section(dist.project_name):
                    for name, value in config.items(dist.project_name):
                        if name not in cfgmap: cfgmap[name] = value
                if not 'patches' in cfgmap: cfgmap['patches'] = []
                else: cfgmap['patches'] = cfgmap['patches'].split()
                if 'pkgdir' in cfgmap: pkgdir = cfgmap['pkgdir']
                else: cfgmap['pkgdir'] = pkgdir
                cfgmap['pkgpath'] = dist.location
                cfgmap['pkgfile'] = os.path.basename(dist.location)
                unpackpath = os.path.join(unpackdir, pkgdir)
                cfgmap['unpackpath'] = unpackpath

                # Get setup arguments of the dist.
                if 'mkdir' in cfgmap: unpack_archive(dist.location, unpackpath)
                else: unpack_archive(dist.location, unpackdir)
                self._setup_convert(os.path.join(unpackpath, 'setup.py'))
                for p in cfgmap['patches']:
                    print 'Applying %s' % p
                    os.system('(cd %s; patch -p0 < %s)' % \
                                  (unpackpath, os.path.join(patchdir, p)))
                print 'Get distribution args from %s' % unpackpath
                p = popen2.popen2(popen_fmt % unpackpath)
                p[1].close()
                c = p[0].read()
                p[0].close()
                args = eval(c)
                shutil.rmtree(unpackpath)
                if 'install_requires' not in args or \
                        args['install_requires'] is None:
                    args['install_requires'] = []
                if 'extras_require' not in args or \
                        args['extras_require'] is None:
                    args['extras_require'] = {}

                # Generate package from args and options.
                updated, deps = \
                    self.pkgsys.GenPackage(args, self.options, cfgmap)
                ok_packages.append(pkg)
                new_packages = uniq_extend(new_packages, deps)

            # Process all required but not processed packages.
            packages = []
            for pkg in new_packages:
                if pkg not in ok_packages: packages.append(pkg)

    def _setup_convert(self, setup_path):
        modified = False
        setup_fp = file(setup_path)
        output = ''
        ln = setup_fp.readline()
        while ln:
            lnlist = ln.split()
            if len(lnlist) >= 4 and \
                    lnlist[0] == 'from' and \
                    lnlist[1] == 'distutils.core' and \
                    lnlist[2] == 'import' and \
                    'setup' in lnlist:
                idx = ln.find('distutils.core')
                ln = ln[:idx] + 'setuptools' + ln[idx + len('distutils.core'):]
                modified = True
            output = output + ln
            ln = setup_fp.readline()
        setup_fp.close()
        if modified:
            setup_fp = file(setup_path, 'w')
            setup_fp.write(output)
            setup_fp.close()
