# loader.py
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

# Based on djangojinja2.py by Armin Ronacher.

'''
This module provides a partially-compatible replacement for
`django.template.loader`. Included functions are `get_template`,
`select_template`, and `render_to_string`. The former two are useful for
loading template objects, whereas the latter is useful for rendering a
template given a context.

'''

from django.template.context import get_standard_processors
import jinja2

from chouwa.environment import env

class TemplateSyntaxError(jinja2.TemplateSyntaxError):
    def __init__(self, message, lineno, name, filename):
        jinja2.TemplateError.__init__(self, message)
        self.lineno = lineno
        self.name = name
        self.filename = filename

    def __unicode__(self):
        location = 'line %d' % self.lineno
        name = self.filename or self.name
        if name:
            location = 'File "%s", %s' % (name, location)
        return u'\n'.join([self.message, '  ' + location])

def get_template(template_name, globals=None):
    """Load a template."""
    return env.get_template(template_name, globals=globals)

def select_template(templates, globals=None):
    """Try to load one of the given templates."""
    for template in templates:
        return env.get_template(template, globals=globals)
    raise jinja2.TemplateNotFound(', '.join(templates))

def render_to_string(template_name, context=None, request=None):
    """Render a template into a string."""
    if context is None:
        context = {}
    if request is not None:
        context['request'] = request
        for processor in get_standard_processors():
            context.update(processor(request))
    try:
        return get_template(template_name).render(context)
    except jinja2.TemplateSyntaxError, e:
        raise TemplateSyntaxError(e.message, e.lineno, e.name, e.filename)
