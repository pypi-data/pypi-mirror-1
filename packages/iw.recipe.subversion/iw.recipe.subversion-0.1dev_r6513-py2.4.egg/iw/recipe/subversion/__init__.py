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

from infrae.subversion import Recipe as SubversionRecipe
import os
import sys
import py
from tarfile import TarFile


class Recipe(SubversionRecipe):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        SubversionRecipe.__init__(self, buildout, name, options)
        self.buildout, self.name, self.options = buildout, name, options
        self.install_from_cache = buildout['buildout'].get('install-from-cache', False)
        self.download_cache = buildout['buildout'].get('download-cache', False)
        if self.download_cache:
            self.cache_location = buildout['buildout']['download-cache']

    def install(self):
        """installer"""
        if not self.install_from_cache:
            files = SubversionRecipe.install(self)
            if self.download_cache:
                self.archive()
            return files
        else:
            if self.download_cache:
                self.extract()
        return self.location

    def update(self):
        """updater"""
        files = super(SubversionRecipe, self).update()
        return files

    def archive(self):
        """archive the generated location
        """
        if not os.path.isdir(self.cache_location):
            os.mkdir(self.cache_location)
        for url, name in self.urls:
            # build archive name
            wc = py.path.svnwc(self.location).join(name)
            revision = wc.status().rev
            archive = os.path.join(self.cache_location,
                    '%s-r%s.tar.gz' % (name, revision))
            if os.path.isfile(archive):
                os.remove(archive)
            tar = TarFile.open(archive, 'w:gz')

            # recurse on directory
            dirname = os.path.join(self.location, name)
            for root, dirs, filenames in os.walk(dirname):
                if '.svn' in dirs:
                    dirs.remove('.svn')
                for filename in filenames:
                    path = os.path.join(root, filename)
                    arcname = path.replace(self.location, '')
                    tar.add(path, arcname, False)
            tar.close()
        return self.download_cache

    def extract(self):
        """extract archives from path
        """
        archives = os.listdir(self.cache_location)
        for url, name in self.urls:
            for filename in archives:
                if filename.startswith('%s-r' % name):
                    tar = TarFile.open(
                            os.path.join(self.cache_location, filename),
                            'r:gz')
                    tar.extractall(os.path.join(self.location, name))
                    tar.close()

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
