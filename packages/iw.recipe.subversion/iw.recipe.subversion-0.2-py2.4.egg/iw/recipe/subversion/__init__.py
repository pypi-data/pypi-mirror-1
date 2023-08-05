# -*- coding: utf-8 -*-
# Copyright (C)2007 'Ingeniweb'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""Recipe subversion"""

from tarfile import TarFile
from os.path import isdir, join
import os, sys, py
import subprocess

def command(cmd):
    """system command"""
    return subprocess.call(cmd, shell=True)

class Recipe:
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.offline = buildout['buildout'].get('offline', 'false')
        self.location = os.path.join(
                            buildout['buildout']['parts-directory'], self.name)
        urls = options['urls'].splitlines()
        self.urls = [l.split() for l in urls if l.strip()]

        if self.offline != 'true':
            self.offline = False
        self.install_from_cache = buildout['buildout'].get('install-from-cache', 'false')

        if self.install_from_cache != 'true':
            self.install_from_cache = False

        self.download_cache = buildout['buildout'].get('download-cache', False)
        if self.download_cache:
            self.cache_location = buildout['buildout']['download-cache']
            if not os.path.isdir(self.cache_location):
                os.mkdir(self.cache_location)

    def install(self):
        """installer"""
        if self.download_cache and not self.need_update:
            self.extract()
            return self.location

        if not self.install_from_cache and not self.offline:
            for url, name in self.urls:
                wc = py.path.svnwc(self.location).join(name)
                command('svn co %s %s' % (url, wc.strpath))
            if self.download_cache:
                self.archive()
        else:
            if self.download_cache:
                self.extract()
        return self.location

    def update(self):
        """updater"""
        if self.download_cache and not self.need_update:
            self.extract()
            return self.location

        if not self.install_from_cache and not self.offline:
            for url, name in self.urls:
                wc = py.path.svnwc(self.location).join(name)
                wc.update()
            if self.download_cache:
                self.archive()
        else:
            if self.download_cache:
                self.extract()
        return self.location

    def archive(self):
        """archive the generated location
        """
        if not isdir(self.cache_location):
            os.makedirs(self.cache_location)
        for url, name in self.urls:

            # remove previous archived files to avoid revisions conflicts
            for filename in os.listdir(self.cache_location):
                if filename.startswith('%s-' % name):
                    os.remove(join(self.cache_location, filename))

            # build archive name
            parts = url.split('/')
            if parts[-2] == 'tags':
                # we use the tag as archive name
                tag = parts[-1]
                archive_name = '%s-%s.tar.gz' % (name, tag)
            else:
                #use the revision
                wc = py.path.svnwc(self.location).join(name)
                revision = wc.status().rev
                archive_name = '%s-r%s.tar.gz' % (name, revision)
            archive = join(self.cache_location, archive_name)
            if os.path.isfile(archive):
                os.remove(archive)
            tar = TarFile.open(archive, 'w:gz')

            # recurse on directory
            dirname = join(self.location, name)
            for root, dirs, filenames in os.walk(dirname):
                if '.svn' in dirs:
                    dirs.remove('.svn')
                for filename in filenames:
                    path = join(root, filename)
                    arcname = path.replace(self.location, '')
                    tar.add(path, arcname, False)
            tar.close()
        return self.download_cache

    def extract(self):
        """extract archives from path
        """
        archives = sorted(os.listdir(self.cache_location))
        for url, name in self.urls:
            exist = False
            for filename in archives:
                if filename.startswith('%s-' % name):
                    exist = True
                    tar = TarFile.open(
                            join(self.cache_location, filename),
                            'r:gz')
                    tar.extractall(self.location)
                    tar.close()
            if not exist:
                print 'No archive found for %s' % name

    @property
    def need_update(self):
        """we don't need an update if:
            - urls are tagged version
            - we got an archive for each url
        """
        if not isdir(self.cache_location):
            return True

        archives = sorted(os.listdir(self.cache_location))

        def isTagged(url):
            parts = url.split('/')
            if parts[-2] == 'tags':
                return parts[-1]
            return False

        def isArchived(name, tag):
            for filename in archives:
                if filename == '%s-%s.tar.gz' % (name, tag):
                    return True
            return False
        for url, name in self.urls:
            tag = isTagged(url)
            if not tag:
                return True
            if not isArchived(name, tag):
                return True
        return False


if sys.version_info[0:2] < (2, 5):
    # this come from python 2.5

    def extractall(self, path=".", members=None):
        """Extract all members from the archive to the current working
        directory and set owner, modification time and permissions on
        directories afterwards. `path' specifies a different directory
        to extract to. `members' is optional and must be a subset of the
        list returned by getmembers().
        """
        directories = []
        if members is None:
            members = self
        for tarinfo in members:
            if tarinfo.isdir():
                # Extract directory with a safe mode, so that
                # all files below can be extracted as well.
                try:
                    os.makedirs(os.path.join(path, tarinfo.name), 0700)
                except EnvironmentError:
                    pass
                directories.append(tarinfo)
            else:
                self.extract(tarinfo, path)

        # Reverse sort directories.
        directories.sort(lambda a, b: cmp(a.name, b.name))
        directories.reverse()

        # Set correct owner, mtime and filemode on directories.
        for tarinfo in directories:
            path = os.path.join(path, tarinfo.name)
            try:
                self.chown(tarinfo, path)
                self.utime(tarinfo, path)
                self.chmod(tarinfo, path)
            except ExtractError, e:
                if self.errorlevel > 1:
                    raise
                else:
                    self._dbg(1, "tarfile: %s" % e)
    TarFile.extractall = extractall
