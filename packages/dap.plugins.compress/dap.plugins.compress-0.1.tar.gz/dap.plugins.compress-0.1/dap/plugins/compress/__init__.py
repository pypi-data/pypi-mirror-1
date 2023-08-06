"""Metaplugin for compressed files."""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os
import re

from dap.server import BaseHandler
from dap.exceptions import OpenFileError
from dap.plugins.lib import loadhandler


extensions = re.compile(r"^.*\.(zip|gz|z|bz2)$", re.IGNORECASE)

COMMANDS = {'.gz' : 'gunzip -c %s > %s',
            '.bz2': 'bunzip2 -c %s > %s',
            '.z'  : 'uncompress -c %s > %s',
            '.zip': 'unzip -c %s > %s',
           }


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        self.environ = environ
        
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
