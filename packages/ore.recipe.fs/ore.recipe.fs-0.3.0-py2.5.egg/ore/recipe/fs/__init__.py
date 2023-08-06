##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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

import os
import logging
import zc.buildout


class Mkfile(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.mode = int(options.get('mode', '0644'), 8)
        options['content']
        self.originalPath = options['path']
        options['path'] = os.path.join(
                              buildout['buildout']['directory'],
                              self.originalPath,
                              )
        self.createPath = options.get('createpath', 'False').lower() in ['true', 'on', '1']

    def install(self):
        filename = self.options['path']
        dirname = os.path.dirname(self.options['path'])

        if not os.path.isdir(dirname):
            if self.createPath:
                logging.getLogger(self.name).info(
                    'Creating directory %s', dirname)
                os.makedirs(dirname)
            else:
                logging.getLogger(self.name).error(
                    'Cannot create file %s. %s is not a directory.',
                    filename, dirname)
                raise zc.buildout.UserError('Invalid path')

        f = file(filename, 'w')
        logging.getLogger(self.name).info(
            'Writing file %s', filename)
        f.write(self.options['content'])
        f.close()
        os.chmod(filename, self.mode)
        return filename


class Mkdir(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.originalPath = options['path']
        options['path'] = os.path.join(
                              buildout['buildout']['directory'],
                              self.originalPath,
                              )
        self.createPath = options.get('createpath', 'False').lower() in ['true', 'on', '1']

    def install(self):
        path = self.options['path']
        dirname = os.path.dirname(self.options['path'])

        if not os.path.isdir(dirname):
            if self.createPath:
                logging.getLogger(self.name).info(
                    'Creating parent directory %s', dirname)
                os.makedirs(dirname)
            else:
                logging.getLogger(self.name).error(
                    'Cannot create %s. %s is not a directory.',
                    path, dirname)
                raise zc.buildout.UserError('Invalid Path')

        if not os.path.isdir(path):
            logging.getLogger(self.name).info(
                'Creating directory %s', self.originalPath)
            os.mkdir(path)
        return ()

    def update(self):
        pass

