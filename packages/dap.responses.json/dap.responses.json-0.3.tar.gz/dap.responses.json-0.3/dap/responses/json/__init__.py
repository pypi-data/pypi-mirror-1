__author__ = 'Roberto De Almeida <rob@pydap.org>'

import simplejson 
from paste.request import parse_dict_querystring
from paste.deploy.converters import asbool

from dap.dtypes import *
from dap.lib import __dap__
from dap.util.ordereddict import odict


class DapEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'tolist'):
            return obj.tolist()
        else:
            return simplejson.JSONEncoder.default(self, obj)


def build(self, constraints=None):
    """
    JSON response.
    """
    dataset = self._parseconstraints(constraints)

    headers = [('Content-description', 'dods_json'),
               ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__])),
               ('Content-type', 'application/json'),
              ]

    # Output data?
    query = parse_dict_querystring(self.environ)
    output_data = asbool(query.get('output_data'))

    output = [json(dataset, output_data)]
    return headers, output


def json(dataset, output_data=False):
    out = odict()
    out[dataset.name] = recursive_build(dataset, output_data)
    out = simplejson.dumps(out, cls=DapEncoder)
    return out


def recursive_build(dapvar, output_data):
    out = odict() 

    # Add attributes, shape, dimensions.
    for attr in ['shape', 'dimensions', 'attributes']:
        value = getattr(dapvar, attr, None)
        ##if value is not None: out[attr] = value
        if value: out[attr] = value

    # BaseTypes.
    if isinstance(dapvar, BaseType):
        out['type'] = dapvar.type
        if output_data: out['data'] = dapvar.data

    # Grids.
    elif isinstance(dapvar, GridType):
        out['type'] = 'Grid'
        out['array'] = {dapvar.array.name: recursive_build(dapvar.array, output_data)}
        out['maps'] = odict()
        for map_ in dapvar.maps.values():
            out['maps'][map_.name] = recursive_build(map_, output_data)

    # Sequences.
    elif isinstance(dapvar, SequenceType):
        out['type'] = 'Sequence'
        ##if output_data: out['data'] = list(dapvar.data)
        for var in dapvar.walk():
            out[var.name] = recursive_build(var, output_data)
        
    # Structures.
    else:
        out['type'] = {StructureType: 'Structure',
                       DatasetType  : 'Dataset',
                      }[type(dapvar)]
        for var in dapvar.walk():
            out[var.name] = recursive_build(var, output_data)

    return out
