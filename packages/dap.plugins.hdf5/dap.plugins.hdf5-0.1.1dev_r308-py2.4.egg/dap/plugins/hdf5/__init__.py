from __future__ import division

"""
Plugin for HDF5 files.
"""


__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path

from tables import openFile

from arrayterator import arrayterator

from dap import dtypes
from dap.server import BaseHandler
from dap.exceptions import OpenFileError
from dap.helper import parse_querystring

extensions = r"""^.*\.(h5|hdf5|H5|HDF5)$"""

# How many records to read each time.
BUFFER = 10000

type_convert = {'CharType': 'String',
               }


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        """Handler constructor.
        """
        self.filepath = filepath
        self.environ = environ
        
        dir, self.filename = os.path.split(filepath)
        try:
            self._file = openFile(filepath)
        except:
            message = 'Unable to open file %s.' % filepath
            raise OpenFileError(message)

        # Add description.
        self.description = getattr(self._file, 'title', self.filename)

    def _parseconstraints(self, constraints=None):
        """Dataset builder.

        This method build the dataset according to the constraint
        expression.
        """
        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)

        # Grab requested variables.
        fields, queries = parse_querystring(constraints)

        # Add arrays in root.
        for array_ in self._get_arrays('/', fields):
            dataset[array_.name] = array_
            
        # Add groups.
        for struct_ in self._get_groups('/', fields):
            dataset[struct_.name] = struct_

        return dataset

    def _get_arrays(self, group, fields):
        for array_ in self._file.listNodes(group, 'Array'):
            name = array_._v_name

            # Get id.
            names = [name]
            parent = array_._v_parent
            while parent._v_name != '/':
                names.append(parent._v_name)
                parent = parent._v_parent
            id_ = '.'.join(names[::-1])

            if name in fields or id_ in fields or not fields:
                slice_ = fields.get(name) or fields.get(id_) or (slice(None),)
                data = arrayterator(array_, nrecs=BUFFER)[slice_]
                type_ = type_convert[str(array_.type)]
                attrs = dict([(k, getattr(array_.attrs, k)) for k in array_.attrs._v_attrnames])
                yield dtypes.ArrayType(name=name, data=data, shape=data.shape, type=type_, attributes=attrs)

    def _get_groups(self, root, fields):
        for group in self._file.listNodes(root, 'Group'):
            name = group._v_name
            struct_ = dtypes.StructureType(name=name)

            # Add arrays in this group.
            for array_ in self._get_arrays(os.path.join(root, name), fields):
                struct_[array_.name] = array_

            # Add groups.
            for group in self._get_groups(os.path.join(root, name), fields):
                struct_[group.name] = group

            # Return only if not empty.
            if struct_.keys(): yield struct_
                    
    def close(self):
        """Close the HDF5 file."""
        self._file.close()
