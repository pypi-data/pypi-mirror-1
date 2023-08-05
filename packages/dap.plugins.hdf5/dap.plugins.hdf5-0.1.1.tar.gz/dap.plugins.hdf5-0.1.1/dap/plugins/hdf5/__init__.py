from __future__ import division

"""
Plugin for HDF5 files.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path
import urllib

from tables import openFile

from arrayterator import arrayterator

from dap import dtypes
from dap.server import BaseHandler
from dap.exceptions import OpenFileError, ConstraintExpressionError
from dap.helper import parse_querystring
from dap.util.ordereddict import odict
from dap.lib import quote

extensions = r"""^.*\.(h5|hdf5|he5|H5|HDF5|HE5)$"""

# How many records to read each time.
BUFFER = 10000

# Conversion of types with different names from the DAP.
# Usual types (``Float64``, ``Int32``, etc.) are handled
# automatically.
type_convert = {'CharType': 'String',
                'UInt8': 'Uint16',
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

        # Fix fields, converting from shorthand notation to fully qualified names.
        # Also, when the SHN is used we should check if there aren't two variables 
        # with the same SHN.
        allvars = [(var._v_name, self._get_id(var)) for var in self._file.walkNodes('/')]
        allnames, allids = zip(*allvars)
        allnames = list(allnames)
        if fields:
            for var in self._file.walkNodes('/'):
                name = var._v_name
                if name in fields and name not in allids:
                    # Check for variables with same SHN.
                    if allnames.count(name) > 1:
                        raise ConstraintExpressionError("Ambiguous shorthand notation request: %s" % name)

                    # Replace SHN with FQN.
                    position = fields._keys.index(name)
                    id_ = self._get_id(var)
                    fields._dict[id_] = fields._dict[name]
                    del fields._dict[name]
                    fields._keys[position] = id_

        # Add arrays in root.
        for array_ in self._get_arrays('/', fields):
            dataset[array_.name] = array_
            
        # Add groups.
        for struct_ in self._get_groups('/', fields):
            dataset[struct_.name] = struct_

        # Sort keys according to the requested order.
        if fields:
            reqs = [var.split('.')[0] for var in fields]
            dataset._keys.sort(key=lambda s: reqs.index(s))

        return dataset

    def _get_id(self, var):
        names = [var._v_name]
        parent = var._v_parent
        while parent._v_name != '/':
            names.append(parent._v_name)
            parent = parent._v_parent
        names = [quote(n) for n in names]
        id_ = '.'.join(names[::-1])
        return id_

    def _get_arrays(self, group, fields):
        for array_ in self._file.listNodes(group, 'Array'):
            # Get name and id.
            name = array_._v_name
            id_ = self._get_id(array_)

            if name in fields or id_ in fields or not fields:
                # Get data and slice it.
                slice_ = fields.get(name) or fields.get(id_) or (slice(None),)
                data = arrayterator(array_, nrecs=BUFFER)[slice_]

                # Get array type.
                if str(array_.type) in dtypes._basetypes: type_ = str(array_.type)
                else: type_ = type_convert[str(array_.type)]

                # Build attributes.
                attrs = dict([(k, getattr(array_.attrs, k)) for k in array_.attrs._v_attrnames])
                if data.shape:
                    yield dtypes.ArrayType(name=name, data=data, shape=data.shape, type=type_, attributes=attrs)
                else:
                    yield dtypes.BaseType(name=name, data=data, type=type_, attributes=attrs)

    def _get_groups(self, root, fields):
        for group in self._file.listNodes(root, 'Group'):
            # Get name and id.
            name = group._v_name
            id_ = self._get_id(group)

            # If the group was requested we simply pass an empty ``fields``
            # to children so that all contained variables get included.
            if name in fields or id_ in fields: cfields = {}
            else: cfields = fields

            struct_ = dtypes.StructureType(name=name)

            # Add arrays in this group.
            for array_ in self._get_arrays(os.path.join(root, name), cfields):
                struct_[array_.name] = array_

            # Add groups.
            for group in self._get_groups(os.path.join(root, name), cfields):
                struct_[group.name] = group

            # Return only if not empty.
            if struct_.keys():
                if cfields:
                    # Sort keys according to the requested order.
                    groupid = os.path.join(root, name)
                    groupid = quote(groupid)
                    groupid = groupid.strip('/').replace('/', '.')
                    reqs = [var[len(groupid)+1:].split('.')[0] for var in fields if var.startswith(groupid)]
                    struct_._keys.sort(key=lambda s: reqs.index(s))
                yield struct_
                    
    def close(self):
        """Close the HDF5 file."""
        self._file.close()
