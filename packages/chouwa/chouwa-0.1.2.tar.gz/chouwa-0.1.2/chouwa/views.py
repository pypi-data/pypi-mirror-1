# views.py
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
The following views are provided to facilitate the use of jinja
templates for django error pages. They serve as replacements for
`django.views.defaults.page_not_found` and
`django.views.defaults.server_error`.

To use these views in your project, add the following line to your root
URLconf after ``from django.conf.urls.defaults import *``. The module
`django.conf.urls.defaults` includes default 404 and 500 handlers, thus
it is necessary to import the chouwa handlers after an ``import *`` from
the django module.

.. python::

    from chouwa.views import handler404, handler500

'''

from django.http import HttpResponseNotFound, HttpResponseServerError

from chouwa.loader import get_template

handler404 = 'chouwa.views.page_not_found'
handler500 = 'chouwa.views.server_error'

def page_not_found(request, template_name='404.html'):
    t = get_template(template_name)
    return HttpResponseNotFound(t.render({'request_path': request.path}))

def server_error(request, template_name='500.html'):
    t = get_template(template_name)
    return HttpResponseServerError(t.render())
