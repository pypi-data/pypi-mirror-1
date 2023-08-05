"""HTML DAP response.

This module implements the HTML DAP response, building it
dynamically from datasets objects.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import types

from dap import dtypes
from dap.lib import encode_atom


def build(dapvar):
    func = {dtypes.DatasetType  : _dataset,
            dtypes.StructureType: _structure,
            dtypes.SequenceType : _sequence,
            dtypes.BaseType     : _base,
            dtypes.ArrayType    : _array,
            dtypes.GridType     : _grid,
           }[type(dapvar)]

    return func(dapvar)


def _nested_attrs(attrs):
    yield '<dl class="attributes">\n'
    for attr, values in attrs.items():
        # Nested attributes.
        if isinstance(values, dict):
            yield '<dt>%s</dt>\n' % attr
            yield '<dd>\n'
            for line in _nested_attrs(values): yield line
            yield '</dd>\n'
        else:
            # Convert values to list.
            if not isinstance(values, list): values = [values]

            # Get value type and encode properly.
            values = [encode_atom(v) for v in values]
            values = ', '.join(values)

            yield '<dt>%s</dt>\n' % attr
            yield '<dd>%s</dd>\n' % values
    yield '</dl>\n\n'
    

def _dataset(dapvar):
    """Returns a HTML form for the dataset."""
    if dapvar.attributes:
        for line in _nested_attrs(dapvar.attributes): yield line

    yield '<hr />\n'

    # Add the form for the POST request.
    yield '<form id="dods_form" method="post" action="#post">\n\n'

    # Add the HTML for each variable.
    for var in dapvar.values():
        for html_ in build(var):
            yield html_

    # Submit button for the form.
    yield '<p><input type="submit" id="submit" value="Download data" /> <input type="reset" value="Reset" /></p>\n'
    yield '</form>\n\n'


def _structure(dapvar):
    """Returns a HTML form for the structure."""
    yield '<!-- Starting %s -->\n' % dapvar.id
    yield '<fieldset>\n<legend>%s</legend>\n' % dapvar.name

    # Attributes.
    yield '<dl class="attributes">\n'
    for attr,values in dapvar.attributes.items():
        # Convert values to list.
        if not isinstance(values, list): values = [values]

        # Get value type and encode properly.
        values = [encode_atom(v) for v in values]
        values = ', '.join(values)

        yield '<dt>%s</dt>\n' % attr
        yield '<dd>%s</dd>\n' % values
    yield '</dl>\n'

    for var in dapvar.values():
        for html_ in build(var):
            yield html_
    yield '</fieldset>\n'
    yield '<!-- Finishing %s -->\n\n' % dapvar.id


def _sequence(dapvar):
    """Returns a HTML form for the sequence."""
    yield '<!-- Starting %s -->\n' % dapvar.id
    yield '<fieldset>\n<legend>%s</legend>\n\n' % dapvar.name

    # Selection.
    yield '<!-- Selection -->\n'
    yield '<p><select name="var1_%s_0" id="var1_%s_0">\n' % (dapvar.id, dapvar.id)
    yield '<option value="--" selected="selected">--</option>\n'
    for var in dapvar.values():
        yield '<option value="%s">%s</option>\n' % (var.id, var.id)
    yield '</select>\n'
    yield '<select name="op_%s_0" id="op_%s_0">\n' % (dapvar.id, dapvar.id)
    yield '<option value="=" selected="selected">=</option>\n'
    yield '<option value="!=">!=</option>\n'
    yield '<option value="&lt;">&lt;</option>\n'
    yield '<option value="&lt;=">&lt;=</option>\n'
    yield '<option value="&gt;">&gt;</option>\n'
    yield '<option value="&gt;=">&gt;=</option>\n'
    yield '<option value="=~">=~</option>\n'
    yield '</select>\n'
    yield '<input type="text" name="var2_%s_0" id="var2_%s_0" value="" /></p>\n\n' % (dapvar.id, dapvar.id)

    # Attributes.
    if dapvar.attributes:
        yield '<dl class="attributes">\n'
        for attr,values in dapvar.attributes.items():
            if not isinstance(values, list): values = [values]
            values = [encode_atom(v) for v in values]
            values = ', '.join(values)
            yield '<dt>%s</dt>\n' % attr
            yield '<dd>%s</dd>\n' % values
        yield '</dl>\n\n'

    for var in dapvar.values():
        for html_ in build(var):
            yield html_
    yield '</fieldset>\n'
    yield '<!-- Finishing %s -->\n\n' % dapvar.id


def _base(dapvar):
    yield '<!-- Starting %s -->\n' % dapvar.id
    yield '<fieldset>\n<legend>%s</legend>\n' % dapvar.name
    yield '<p><input type="checkbox" name="%s" id="%s" /> <label for="%s">Retrieve this variable.</label></p>\n' % (dapvar.id, dapvar.id, dapvar.id)  

    # Attributes.
    yield '<dl class="attributes">\n'
    for attr,values in dapvar.attributes.items():
        if not isinstance(values, list): values = [values]
        values = [encode_atom(v) for v in values]
        values = ', '.join(values)
        yield '<dt>%s</dt>\n' % attr
        yield '<dd>%s</dd>\n' % values
    yield '</dl>\n'
    yield '</fieldset>\n'
    yield '<!-- Finishing %s -->\n\n' % dapvar.id


def _array(dapvar):
    yield '<!-- Starting %s -->\n' % dapvar.id
    yield '<fieldset>\n<legend>%s</legend>\n' % dapvar.name
    yield '<p><input type="checkbox" name="%s" id="%s" /> <label for="%s">Retrieve this variable.</label></p>\n' % (dapvar.id, dapvar.id, dapvar.id)  

    # Dimensions.
    dimensions = dapvar.dimensions or ['dim_%d' % i for i,j in enumerate(dapvar.shape)]
    for dim,shape in zip(dimensions, dapvar.shape):
        yield '<label for="%s_%s">%s</label>:<br />\n' % (dapvar.id, dim, dim)
        yield '<input type="text" name="%s_%s" id="%s_%s" value="0:1:%d" /><br />\n' % (dapvar.id, dim, dapvar.id, dim, shape-1)

    # Attributes.
    yield '\n<dl class="attributes">\n'
    for attr,values in dapvar.attributes.items():
        if not isinstance(values, list): values = [values]
        values = [encode_atom(v) for v in values]
        values = ', '.join(values)
        yield '<dt>%s</dt>\n' % attr
        yield '<dd>%s</dd>\n' % values
    yield '</dl>\n'
    yield '</fieldset>\n'
    yield '<!-- Finishing %s -->\n\n' % dapvar.id


def _grid(dapvar):
    yield '<!-- Starting %s -->\n' % dapvar.id
    yield '<fieldset>\n<legend>%s</legend>\n' % dapvar.name
    yield '<p><input type="checkbox" name="%s" id="%s" /> <label for="%s">Retrieve this variable.</label></p>\n' % (dapvar.id, dapvar.id, dapvar.id)  

    # Dimensions.
    dimensions = dapvar.dimensions or ['dim_%d' % i for i,j in enumerate(dapvar.shape)]
    for dim,shape in zip(dimensions, dapvar.shape):
        yield '<label for="%s_%s">%s</label>:<br />\n' % (dapvar.id, dim, dim)

        min_ = dapvar.maps[dim][0]
        # Check for single-valued dimensions.
        if dapvar.maps[dim].shape[0] == 1:
            inc = 0
        else:
            inc = dapvar.maps[dim][1] - min_
        
        units = dapvar.maps[dim].attributes.get('units', '')
        yield '<input type="text" name="%s_%s" id="%s_%s" value="0:1:%d" dap_min="%.6g" dap_length="%d" dap_inc="%.6g" dap_units="%s" /><br />\n' % (dapvar.id, dim, dapvar.id, dim, shape-1, min_, shape-1, inc, units)

    # Attributes.
    yield '\n<dl class="attributes">\n'
    for attr,values in dapvar.attributes.items():
        if not isinstance(values, list): values = [values]
        values = [encode_atom(v) for v in values]
        values = ', '.join(values)
        yield '<dt>%s</dt>\n' % attr
        yield '<dd>%s</dd>\n' % values
    yield '</dl>\n'
    yield '</fieldset>\n'
    yield '<!-- Finishing %s -->\n\n' % dapvar.id


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

