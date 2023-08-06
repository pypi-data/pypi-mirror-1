"""
DDX DAP response.

This module implements the DDX DAP response, building it 
dynamically from datasets objects.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from dap.lib import INDENT, __dap__, to_list, encode_atom
from dap.dtypes import *  
from dap.dtypes import typemap

# Update typemap with more typecodes...
typemap['u'] = typemap['c'] = String
typemap['i'] = Int32
typemap['I'] = UInt32

try:
    import xml.etree.ElementTree as ET
except ImportError:
    import elementtree.ElementTree as ET


def build(self, constraints=None):
    dataset = self._parseconstraints(constraints)
    headers = [('Content-description', 'dods_ddx'),
               ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__])),
               ('Content-type', 'text/xml'),
              ]
    ddx = _dispatch(dataset)
    indent(ddx)
    output = ET.tostring(ddx, encoding='utf-8')
    return headers, output

    
def _dispatch(dapvar):
    func = {DatasetType  : _dataset,
            StructureType: _structure,
            SequenceType : _sequence,
            GridType     : _grid,
            ArrayType    : _array,
            BaseType     : _base,
           }[type(dapvar)]

    return func(dapvar)


def _dataset(dapvar):
    dataset = ET.Element('{http://xml.opendap.org/ns/DAP2}Dataset',
            name=dapvar.name)
    add_attributes(dataset, dapvar.attributes)

    for var in dapvar.walk():
        dataset.append(_dispatch(var))

    ET.SubElement(dataset, '{http://xml.opendap.org/ns/DAP2}dataBLOB', href='')

    return dataset


def _structure(dapvar):
    structure = ET.Element('{http://xml.opendap.org/ns/DAP2}Structure',
            name=dapvar.name)
    add_attributes(structure, dapvar.attributes)

    for var in dapvar.walk():
        structure.append(_dispatch(var))

    return structure


def _sequence(dapvar):
    sequence = ET.Element('{http://xml.opendap.org/ns/DAP2}Sequence',
            name=dapvar.name)
    add_attributes(sequence, dapvar.attributes)

    for var in dapvar.walk():
        sequence.append(_dispatch(var))

    return sequence


def _grid(dapvar):
    grid = ET.Element('{http://xml.opendap.org/ns/DAP2}Grid',
            name=dapvar.name)
    add_attributes(grid, dapvar.attributes)

    grid.append(_dispatch(dapvar.array))

    for map_ in dapvar.maps.values():
        child = ET.SubElement(grid, '{http://xml.opendap.org/ns/DAP2}Map',
                name=map_.name)
        child[:] = _dispatch(map_)[:]

    return grid


def _array(dapvar):
    array = ET.Element('{http://xml.opendap.org/ns/DAP2}Array',
            name=dapvar.name)
    add_attributes(array, dapvar.attributes)

    ET.SubElement(array, '{http://xml.opendap.org/ns/DAP2}%s' % dapvar.type)

    # Get the var shape and dimensions, if any.
    if dapvar.dimensions:
        dims = zip(dapvar.dimensions, dapvar.shape)
    else:
        if len(dapvar.shape) == 1:
            dims = [(dapvar.name, dapvar.shape[0])]
        else:
            dims = []
    for name, size in dims:
        ET.SubElement(array, '{http://xml.opendap.org/ns/DAP2}dimension',
                name=name, size=str(size))

    return array


def _base(dapvar, level=0):
    base = ET.Element('{http://xml.opendap.org/ns/DAP2}%s' % dapvar.type,
            name=dapvar.name)

    return base


def indent(elem, level=0):
    i = "\n" + level*INDENT
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + INDENT
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def add_attributes(element, attributes):
    for k, v in attributes.items():
        node = ET.SubElement(element, '{http://xml.opendap.org/ns/DAP2}Attribute',
                name=k)
        if isinstance(v, dict):
            node.attrib['type'] = 'Container'
            add_attributes(node, v)
        else:
            atoms = to_list(v)
            if not isinstance(atoms, list):
                atoms = [atoms]
            atoms = [encode_atom(atom) for atom in atoms]

            # Get value type and encode properly.
            if hasattr(v, 'dtype'):
                type_ = typemap[v.dtype.char]   # numpy.array
            elif hasattr(v, 'typecode'):
                type_ = typemap[v.typecode]     # array.array
            else:
                types = [typeconvert(atom) for atom in atoms]
                precedence = ['String', 'Float64', 'Int32']
                types.sort(key=lambda t: precedence.index(t))
                type_ = types[0]

            node.attrib['type'] = type_
            for value in atoms:
                child = ET.SubElement(node, '{http://xml.opendap.org/ns/DAP2}value')
                child.text = value


def typeconvert(obj):
    """Type conversion between Python and DODS, for the DAS."""
    types = [(basestring, 'String'), (float, 'Float64'),
             (long, 'Int32'), (int, 'Int32')]
    for klass, type_ in types:
        if isinstance(obj, klass):
            return type_
    

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

