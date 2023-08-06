"""Recipe for setting up mongoDB."""

import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib
import zc.recipe.egg

logger = logging.getLogger(__name__)


class Recipe(zc.recipe.egg.Eggs):
    """Buildout recipe for installing mongoDB."""

    def __init__(self, buildout, name, opts):
        """Standard constructor for zc.buildout recipes."""

        self.options = opts
        self.buildout = buildout
        self.name = name

    def install_mongodb(self):
        """Downloads and installs mongoDB."""

        arch_url_opt = '%s-%s-url' % (sys.platform, platform.architecture()[0])
        arch_filename = self.options[arch_url_opt].split(os.sep)[-1]
        dst = os.path.join(self.buildout['buildout']['parts-directory'],
                           self.name)
        downloads_dir = os.path.join(os.getcwd(), 'downloads')
        if not os.path.isdir(downloads_dir):
            os.mkdir(downloads_dir)
        src = os.path.join(downloads_dir, arch_filename)
        if not os.path.isfile(src):
            logger.info("downloading mongoDB distribution...")
            urllib.urlretrieve(self.options[arch_url_opt], src)
        else:
            logger.info("mongoDB distribution already downloaded.")

        extract_dir = tempfile.mkdtemp("buildout-" + self.name)
        remove_after_install = [extract_dir]
        is_ext = arch_filename.endswith
        is_archive = True
        if is_ext('.tar.gz') or is_ext('.tgz'):
            call = ['tar', 'xzf', src, '-C', extract_dir]
        elif is_ext('.tar.bz2') or is_ext('.tbz2'):
            call = ['tar', 'xjf', src, '-C', extract_dir]
        elif is_ext('.zip'):
            call = ['unzip', src, '-d', extract_dir]
        else:
            is_archive = False

        if is_archive:
            retcode = subprocess.call(call)
            if retcode != 0:
                raise Exception("extraction of file %r failed (tempdir: %r)" %
                                (arch_filename, extract_dir))
        else:
            shutil.copy(arch_filename, extract_dir)

        if is_archive:
            top_level_contents = os.listdir(extract_dir)
            if len(top_level_contents) != 1:
                raise ValueError("can't strip top level directory because "
                                 "there is more than one element in the "
                                 "archive.")
            base = os.path.join(extract_dir, top_level_contents[0])
        else:
            base = extract_dir

        if not os.path.isdir(dst):
            os.mkdir(dst)

            for filename in os.listdir(base):
                shutil.move(os.path.join(base, filename),
                            os.path.join(dst, filename))
        else:
            logger.info("mongoDB already installed.")

        bindir = self.buildout['buildout']['bin-directory']
        mongod = os.path.join(bindir, 'mongod')
        if not os.path.isfile(mongod):
            shutil.copy(os.path.join(dst, 'bin', 'mongod'), mongod)

        for path in remove_after_install:
            shutil.rmtree(path)

        return (dst,)

    def install(self):
        """Creates the part."""

        options = self.options
        self.install_mongodb()
        return ()

    def update(self):
        """Updates the part."""

        options = self.options
        return ()
