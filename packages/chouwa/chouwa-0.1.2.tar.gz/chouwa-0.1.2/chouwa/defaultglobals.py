# defaultglobals.py
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
This module provides a few filters and globals similar to those shipped
with django but not present in jinja2 by default.

'''

from datetime import datetime

from django.core.urlresolvers import reverse
from django.utils.dateformat import format

from chouwa.decorators import jinjaglobal, jinjafilter

@jinjaglobal
def url(viewname, *args, **kwargs):
    '''
    Lookup a url via `django.core.urlresolvers.reverse`.

    :Parameters:
      viewname : str
        The label associated with a url or the dotted path module name
        of a view.
    '''

    return reverse(viewname, *args, **kwargs)

@jinjaglobal
def now(format_string):
    '''
    Displays the date, formatted according to the given string.

    Format specifiers are identical to those understood by PHP's
    ``date()`` function. See <http://php.net/date>.

    Sample usage::

        It is {{ now("F jS, Y H:i") }}.

    Based on `django.template.defaulttags.now`.

    :Parameters:
      format_string : str
        The PHP ``date()``-style format specifier.

    '''

    return format(datetime.now(), format_string)

@jinjafilter
def date(dt, format_string):
    '''
    Format a date using the PHP ``date()`` format specifiers. Similar to
    the `now` function, except that it formats an arbitrary date.

    :Parameters:
      dt : `datetime.datetime`
        The datetime object to format.
      format_string : str
        The PHP ``date()``-style format specifier.

    '''

    return format(dt, format_string)
