# decorators.py
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
Applications can add their own global objects and filters to the jinja2
environment. This is accomplished by creating a module ``jinjaglobals`` 
inside an installed application, and marking the desired globals in that
module with one of the decorators below. Note that the globals and
filters are not actually namespaced by application: all applications can
see globals added by any application. For an example, see below:

.. python::

    from time import time as time_

    from chouwa.decorators import jinjaglobal, jinjafilter

    @jinjafilter
    def add_five(value):
        return value + 5

    @jinjaglobal
    def time():
        return time_()

This example adds a filter `add_five` which retuns the value passed to
it with 5 added, and adds a global `time` which returns the current unix
timestamp.

'''

def jinjaglobal(function):
    '''
    Mark a callable as a jinja global.

    '''

    function.is_jinja_global = True
    return function

def jinjafilter(function):
    '''
    Mark a callable as a `jinja filter`_.

    _`jinja filter`: http://jinja.pocoo.org/2/documentation/api#custom-filters

    '''

    function.is_jinja_filter = True
    return function

def jinjatest(function):
    '''
    Mark a callable as a `jinja test`_.

    _`jinja test`: http://jinja.pocoo.org/2/documentation/api#writing-tests

    '''

    function.is_jinja_test = True
    return function
