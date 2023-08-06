# shortcuts.py
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
It is often more convienient to defer the actual rendering of templates
to helper functions rather than manipulate template objects oneself.
This module offers shortcut functions for common use cases involving
template rendering. For finer-grained control, see `chouwa.loader`.

'''

from django.http import HttpResponse

from chouwa.loader import render_to_string

def direct_to_template(request, template, extra_context=None,
                       mimetype=None):
    '''
    Render a template and return the result in a
    `django.http.HTTPResponse`. The context of the template rendering
    is populated by applying the standard context processors, and then
    updating the context with the values supplied in `extra_context`.
    Similar to `django.views.generic.simple.direct_to_template`.

    :Parameters:
      request : `django.http.HTTPRequest`
        The request object from django.
      template : str
        The path of the template relative to one of the template
        directories.
      extra_context : dict
        A dictionary containing all extra items to add to the template
        context.
      mimetype : str
        The Content-type to send to the client.

    '''

    return HttpResponse(render_to_string(template, extra_context,
                                         request=request),
                        mimetype=mimetype)
