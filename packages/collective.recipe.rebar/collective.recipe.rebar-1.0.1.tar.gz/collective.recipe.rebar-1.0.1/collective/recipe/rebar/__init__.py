# -*- coding: utf-8 -*-
"""Recipe for rebar"""

import os
import shutil
import tempfile
import logging
import setuptools.archive_util
import zc.buildout
import zc.buildout.download


def system(c):
    if os.system(c):
        raise SystemError("Failed", c)


class Recipe(object):

    def __init__(self, buildout, name, options):
        location = options.get('location', buildout['buildout']['parts-directory'])
        options['location'] = os.path.join(location, name)

        self.buildout = buildout
        self.name = name
        self.options = options
        self.url = self.options['url']

        erlang_path = self.options.get('erlang-path')
        if erlang_path is not None:
            path = os.environ['PATH'].split(os.pathsep)
            if erlang_path not in path:
                path = [erlang_path] + path
                os.environ['PATH'] = os.pathsep.join(path)

    def install(self):
        logger = logging.getLogger(self.name)
        download = zc.buildout.download.Download(
            self.buildout['buildout'], namespace='rebar', hash_name=True,
            logger=logger)

        dest = self.options['location']
        here = os.getcwd()
        if not os.path.exists(dest):
            os.mkdir(dest)

        fname, is_temp = download(self.url, md5sum=self.options.get('md5sum'))

        # now unpack and work as normal
        tmp = tempfile.mkdtemp('buildout-' + self.name)
        logger.info('Unpacking')
        try:
            setuptools.archive_util.unpack_archive(fname, tmp)
        finally:
            if is_temp:
                os.remove(fname)

        try:
            os.chdir(tmp)
            try:
                while not os.path.exists('rebar'):
                    entries = os.listdir(tmp)
                    if len(entries) == 1:
                        os.chdir(entries[0])
                    else:
                        raise ValueError("Couldn't find rebar")
                self.compile_and_install(logger, dest)
            finally:
                os.chdir(here)
        except:
            shutil.rmtree(dest)
            raise

        return dest

    def update(self):
        pass

    def compile_and_install(self, logger, target):
        logger.info('Compiling')
        system("./rebar compile")
        logger.info('Installing')
        system("./rebar install --force target='%s'" % target)
