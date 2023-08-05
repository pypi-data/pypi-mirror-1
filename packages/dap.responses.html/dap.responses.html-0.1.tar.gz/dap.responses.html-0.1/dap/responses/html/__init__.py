"""
HTML DAP response.

This is a simple HTML response, building a form to download data
in ASCII format. The response builds the HTML page and redirects
the user to the ASCII response when a POST is done.

Even though pydap uses Cheetah for templating, I decided to use a
templating engine called ``templess`` for this response. Templess
is lightweight (~25k) and fun to work with, justifying the choice.

A nice thing about the response is that the redirection to the ASCII
response and the error message when no variable is selected are
both done by raising exceptions. These exceptions are *not* captured
by the server, that allows them to be captured by the Paste#httpexceptions
middleware.

If you use this response, don't forget to edit the template file
and add a link pointing to the HTML response when clicking a filename.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from paste.request import construct_url, parse_formvars
from paste.httpexceptions import HTTPSeeOther, HTTPBadRequest

from dap.dtypes import *
from dap.lib import __dap__, __version__
from dap.responses import dds

from dap.responses.html import templess


def build(self, constraints=None):
    dataset = self._parseconstraints(constraints)

    # If we came from a post, parse response and redirect to ascii.
    if self.environ['REQUEST_METHOD'] == 'POST':
        return _post(dataset, self.environ)
        
    headers = [('Content-description', 'dods_form'),
               ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__])),
               ('Content-type', 'text/html'),
              ]

    output = _dispatch(dataset, self.description, self.environ)

    return headers, output


def _post(dataset, environ):
    """
    Parse POST and redirect to ASCII response.
    """
    form = parse_formvars(environ)
    projection = []
    selection = []
    for k in form:
        # Selection.
        if k.startswith('var1') and form[k] != '--':
            name = k[5:]
            sel = '%s%s%s' % (form[k], form['op_%s' % name], form['var2_%s' % name])
            selection.append(sel)
        # Projection.
        if form[k] == 'on':
            var = [k]
            for dim in form:
                if dim.startswith('%s_' % k):
                    var.append('[%s]' % form[dim])
            var = ''.join(var)
            if var not in projection:
                projection.append(var)

    projection = ','.join(projection)
    selection = '&'.join(selection)
    if selection: query = '%s&%s' % (projection, selection)
    else: query = projection
    
    # Get location.
    location = construct_url(environ, with_query_string=False)

    # Empty queries SHOULD NOT return everything, because this
    # means the user didn't select any variables.
    if not query: raise HTTPBadRequest('You did not select any variables.')

    # Replace html extension for ascii and redirect.
    redirect = '%s.ascii?%s' % (location[:-5], query)
    raise HTTPSeeOther(redirect)


def _dispatch(dapvar, description, environ):
    func = {DatasetType  : _dataset,
            StructureType: _structure,
            SequenceType : _sequence,
            GridType     : _grid,
            ArrayType    : _array,
            BaseType     : _base,
           }[type(dapvar)]

    return func(dapvar, description, environ)


def _nested_attrs(attrs):
    # Return object if is not a dict.
    if not isinstance(attrs, dict): return attrs

    html = """<?xml version="1.0" encoding="UTF-8"?>
<dl xmlns:t="http://johnnydebris.net/xmlns/templess" class="attributes">
    <div t:replace="attrs"><dt t:content="k" /><dd t:content="v" /></div>
</dl>"""

    context = {'attrs': [{'k': k, 'v': _nested_attrs(v)} for (k, v) in attrs.items()]}
    t = templess.template(html)
    return t.render(context)


def _dataset(dapvar, description, environ):
    html = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns:t="http://johnnydebris.net/xmlns/templess" xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <title t:content="title" />
</head>
<body>
    <h1>DODS directory for <span t:content="location" /></h1>

    <div t:content="attrs" />
    <hr />

    <form id="dods_form" method="post" t:attr="action action">
    <div t:content="children" />
    <p><input type="submit" id="submit" value="Download data" /> <input type="reset" value="Reset" /></p>
    </form>
    <hr />

    <pre><code t:content="dds" /></pre>
    <hr />
    
    <p><em><a href="http://pydap.org">pydap/<span t:content="version" /></a></em> &copy; Roberto De Almeida</p>
</body>
</html>"""

    context = {'title'   : 'DODS server: %s' % description,
               'location': construct_url(environ, with_query_string=False).lstrip('/')[:-5],
               'attrs'   : _nested_attrs(dapvar.attributes),
               'action'  : construct_url(environ, with_query_string=False).lstrip('/'),
               'children': [_dispatch(var, description, environ) for var in dapvar.walk()],
               'dds'     : ''.join(dds._dispatch(dapvar)),
               'version' : '.'.join([str(i) for i in __version__]),
              }
    t = templess.template(html)
    output = [t.unicode(context).encode('utf-8')]
    return output


def _structure(dapvar, description, environ):
    html = """<fieldset xmlns:t="http://johnnydebris.net/xmlns/templess">
    <legend t:content="name" />
    <div t:content="attrs" />
    <div t:content="children" />
</fieldset>"""

    context = {'name'    : dapvar.name,
               'attrs'   : _nested_attrs(dapvar.attributes),
               'children': [_dispatch(var, description, environ) for var in dapvar.walk()],
              }
    t = templess.template(html)
    return t.render(context)


def _sequence(dapvar, description, environ):
    html = """<fieldset xmlns:t="http://johnnydebris.net/xmlns/templess">
    <legend t:content="name" />

    <p><select t:attr="name var1_id; id var1_id">
    <option value="--" selected="selected">--</option>
    <span t:replace="vars">
        <option t:attr="value id" t:content="id" />
    </span>
    </select>
    <select t:attr="name op_id; id op_id">
    <option value="%3D" selected="selected">=</option>
    <option value="%21%3D">!=</option>
    <option value="%3C">&lt;</option>
    <option value="%3C%3D">&lt;=</option>
    <option value="%3E">&gt;</option>
    <option value="%3E%3D">&gt;=</option>
    <option value="%3D%7E">=~</option>
    </select>
    <input type="text" t:attr="name var2_id; id var2_id" value="" /></p>

    <div t:content="attrs" />
    <div t:content="children" />
</fieldset>"""

    context = {'name'    : dapvar.name,
               'var1_id' : 'var1_%s' % dapvar.id,
               'vars'    : [{'id': var.id} for var in dapvar.walk()],
               'op_id'   : 'op_%s' % dapvar.id,
               'var2_id' : 'var2_%s' % dapvar.id,
               'attrs'   : _nested_attrs(dapvar.attributes),
               'children': [_dispatch(var, description, environ) for var in dapvar.walk()],
              }
    t = templess.template(html)
    return t.render(context)


def _base(dapvar, description, environ):
    html = """<fieldset xmlns:t="http://johnnydebris.net/xmlns/templess">
    <legend t:content="name" />
    <p><input type="checkbox" t:attr="name id; id id" /><label t:attr="for id">Retrieve this variable.</label></p>
    <div t:content="attrs" />
</fieldset>"""

    context = {'name' : dapvar.name,
               'id'   : dapvar.id,
               'attrs': _nested_attrs(dapvar.attributes),
              }
    t = templess.template(html)
    return t.render(context)


def _grid(dapvar, description, environ):
    html = """<fieldset xmlns:t="http://johnnydebris.net/xmlns/templess">
    <legend t:content="name" />
    <p><input type="checkbox" t:attr="name id; id id" /><label t:attr="for id">Retrieve this variable.</label></p>
    <div t:content="dims">
        <label t:attr="for id" t:content="dim" />:<br />
        <input type="text" t:attr="name id; id id; value value" /><br />
    </div>
    <div t:content="attrs" />
</fieldset>"""

    dims = []
    dimensions = dapvar.dimensions or ['dim_%d' % i for i,j in enumerate(dapvar.shape)]
    for dim, shape in zip(dimensions, dapvar.shape):
        dims.append({'id': '%s_%s' % (dapvar.id, dim), 'dim': dim, 'value': '0:1:%d' % (shape-1)})

    context = {'name' : dapvar.name,
               'id'   : dapvar.id,
               'dims' : dims,
               'attrs': _nested_attrs(dapvar.attributes),
              }
    t = templess.template(html)
    return t.render(context)

_array = _grid
