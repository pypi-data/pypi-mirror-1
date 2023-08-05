"""
Plugin for Matlab files.

A simple plugin for serving Matlab files. Should work with files from
Matlab 4 and 5.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path

from arrayterator import arrayterator 

from dap import dtypes
from dap.server import BaseHandler
from dap.exceptions import OpenFileError
from dap.helper import parse_querystring

from dap.plugins.matlab import matfile

extensions = r"""^.*\.(mat|MAT)$"""

# How many records to read each time.
BUFFER = 10000


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        """
        Handler constructor.
        """
        self.filepath = filepath
        self.environ = environ
        dir, self.filename = os.path.split(filepath)

        # Add dummy description.
        self.description = "Matlab file %s." % self.filename

    def _parseconstraints(self, constraints=None):
        """
        Dataset builder.

        This method opens the Matlab file and build the datasets,
        considering each variable as an ``ArrayType``.
        """
        try:
            # Get file.
            f = matfile.matFile(self.filepath)
        except:
            message = 'Unable to open file %s.' % self.filepath
            raise OpenFileError(message)

        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)
        dataset.attributes['filename'] = self.filename
        dataset.attributes['header'] = f.header_text

        # Get workspace.
        workspace = f.GetAllArrays()

        # Grab requested variables.
        fields, queries = parse_querystring(constraints)

        # Add variables.
        if not fields: fields = dict([(name, None) for name in workspace])
        for name in fields:
            array_ = workspace[name]
            data = arrayterator(array_, nrecs=BUFFER)
            slice_ = fields.get(name)
            if slice_: data = data[slice_]
            dataset[name] = dtypes.ArrayType(data=data, name=name, shape=data.shape, type=array_.dtype.char)

        return dataset
