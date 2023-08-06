# __init__.py
#
# Copyright (c) 2009 Trevor Caira
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
Chouwa is a library which aims to ease the integration of jinja2 into
django projects. It does this by providing equivalents of some of
django's helper methods which depend on its template subsystem, as well
as providing builtin globals and filters and providing a mechanism for
user applications to introduce their own globals and filters.

To install chouwa, clone the repository to your python path. The name of
the directory containing the python modules should be ``chouwa``.

Basic usage of chouwa is simple. Consider the use case of rendering a
template within a django application from a view and returning the
result as a `django.http.HTTPResponse`. This use case corresponds to the
`django.views.generic.simple.direct_to_template` helper function. Using
chouwa, the corresponding idiom is as follows:

.. python::

    from chouwa.shortcuts import direct_to_template
    from django.shortcuts import get_object_or_404

    from myapp.models import Entry

    def entry_detail(request, entry_id):
        entry = get_object_or_404(Entry, id=entry_id)
        return direct_to_template(request, 'myapp/entry_detail.html',
                                  {'entry': entry})

`jinja`_ supports similar functionality to django filters and tags by
inserting python functions into the context and either calling them or
applying the filter syntax to them. `Custom filters and global
functions`_ are supported by creating a python modules named
``jinjaglobals`` inside your django application packages. For further
documentation on the creation of custom filters and globals, see the
`chouwa.decorators` documentation.

.. _`jinja`: http://jinja.pocoo.org/2/documentation/
.. _`Custom filters and global functions`:
   http://jinja.pocoo.org/2/documentation/api#custom-filters

'''

__version__ = (0, 2, 0)
