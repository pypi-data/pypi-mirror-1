##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import logging, os, shutil, tempfile, urllib2, urlparse
import setuptools.archive_util
import zc.buildout

class Recipe:

    def __init__(self, buildout, name, options):
        self.logger = logging.getLogger(name)
        self.buildout, self.name, self.options = buildout, name, options
        options['location'] = options['prefix'] = os.path.join(
            buildout['buildout']['parts-directory'],
            name)

        # We look for a download directory, where we put the download tarballs
        buildout['buildout'].setdefault(
                    'download-cache',
                    os.path.join(buildout['buildout']['directory'], 'downloads'))

    def install(self):
        dest = self.options['location']
        urls = self.options['urls']
        download_dir = self.buildout['buildout']['download-cache']
        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)
            self.options.created(download_dir)

        nested_packages = self.options.get('nested-packages', None)
        if nested_packages:
            nested_packages = nested_packages.split()

        ver_suffix_packages = self.options.get('version-suffix-packages', None)
        if ver_suffix_packages:
            ver_suffix_packages = ver_suffix_packages.split()

        if os.path.exists(dest):
            shutil.rmtree(dest)
        os.mkdir(dest)

        for url in urls.split():
            nested = False
            version_suffix = False
            if nested_packages is not None and \
               len([p for p in nested_packages if url.endswith(p)]) > 0:
                nested = True
            if ver_suffix_packages is not None and \
               len([p for p in ver_suffix_packages if url.endswith(p)]) > 0:
                version_suffix = True

            _, _, urlpath, _, _, _ = urlparse.urlparse(url)
            tmp = tempfile.mkdtemp('buildout-'+self.name)
            try:
                fname = os.path.join(download_dir, urlpath.split('/')[-1])
                # Have we already downloaded the file
                if not os.path.exists(fname):
                    f = open(fname, 'wb')
                    try:
                        f.write(urllib2.urlopen(url).read())
                    except Exception, e:
                        os.remove(fname)
                        raise zc.buildout.UserError(
                            "Failed to download URL %s: %s" % (url, str(e)))
                    f.close()
                if not nested:
                    if not version_suffix:
                        setuptools.archive_util.unpack_archive(fname, dest)
                    else:
                        setuptools.archive_util.unpack_archive(fname, tmp)
                        contents = [f for f in os.listdir(tmp) if
                                          os.path.isdir(os.path.join(tmp, f))]
                        package = contents[0]
                        name = package.split('-')[0]
                        shutil.move(os.path.join(tmp, package),
                                    os.path.join(dest, name))
                else:
                    setuptools.archive_util.unpack_archive(fname, tmp)
                    top_folders = [f for f in os.listdir(tmp) if
                                      os.path.isdir(os.path.join(tmp, f))]
                    packages = []
                    for top_folder in top_folders:
                        folder = os.path.join(tmp, top_folder)
                        if os.path.exists(os.path.join(folder, '__init__.py')):
                                packages.append(folder)
                                continue

                        # Maybe the top level folder has products underneath
                        subfolders = [f for f in os.listdir(folder) if
                                    os.path.isdir(os.path.join(folder, f))]
                        for f in subfolders:
                            package = os.path.join(folder, f)
                            if os.path.exists(os.path.join(package,
                                                           '__init__.py')):
                                packages.append(package)
                    for package in packages:
                        name = os.path.split(package)[-1]
                        shutil.move(package, os.path.join(dest, name))
            finally:
                shutil.rmtree(tmp)

        return dest

    def update(self):
        pass
