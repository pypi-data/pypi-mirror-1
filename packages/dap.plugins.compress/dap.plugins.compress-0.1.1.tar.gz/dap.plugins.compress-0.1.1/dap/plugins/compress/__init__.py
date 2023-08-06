"""Metaplugin for compressed files."""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os
import re

from dap.server import BaseHandler
from dap.exceptions import OpenFileError
from dap.plugins.lib import loadhandler


extensions = re.compile(r"^.*\.(zip|gz|z|bz2)$", re.IGNORECASE)


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        self.environ = environ

        COMMANDS = {
            '.gz' : '%s -c %%s > %%s' % environ.get('dap.plugins.compress.gunzip', 'gunzip'),
            '.bz2': '%s -c %%s > %%s' % environ.get('dap.plugins.compress.bunzip2', 'bunzip2'),
            '.z'  : '%s -c %%s > %%s' % environ.get('dap.plugins.compress.uncompress', 'uncompress'),
            '.zip': '%s -c %%s > %%s' % environ.get('dap.plugins.compress.unzip', 'unzip'),
        }

        tmpdir = environ.get('dap.plugins.compress.tmpdir', '/tmp')
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)

        id_, extension = os.path.splitext(filepath)
        id_ = id_.replace(os.path.sep, '_')
        self.filepath = newpath = os.path.join(tmpdir, id_)

        if not os.path.exists(newpath):
            try:
                command = COMMANDS[extension.lower()] % (filepath, newpath)
                os.popen(command)
            except:
                raise OpenFileError('Unable to open file %s.' % filepath)
                
    def _parseconstraints(self, constraints=None):
         H = loadhandler(self.filepath, self.environ)
         return H._parseconstraints(constraints)
