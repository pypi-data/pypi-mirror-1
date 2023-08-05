"""memento - WSGI middleware for per request code reloading.

Copyright (C) 2006 Luke Arno - http://lukearno.com/

This program is free software; you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by the 
Free Software Foundation; either version 2 of the License, or (at your 
option) any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.

Luke Arno can be found at http://lukearno.com/

"""

import __builtin__
import sys

try: set = set
except: from sets import Set as set


class Mori(object):
    """WSGI middleware for per request code reloading.
    
    Per request reloading is very nice while developing but probably 
    a very bad idea in production, so Mori has on and off methods.
    """

    def __init__(self, resolvable, on=True):
        """Just set things up and optionally turn reloading on.

        First arg is a resolver statement for the WSGI app to wrap.
        See resolve method for details.
        
        Default is to turn reloading on.
        """
        self.resolvable = resolvable
        self.real_import = __builtin__.__import__
        self.previous_modules = set()
        self.new_modules = set()
        if on: self.on()

    def on(self):
        """Turn on reloading.
        
        Everything imported after this will be forgotten when
        self._reload() is called (as it is for each request).
        """
        self.new_modules.clear()
        self.previous_modules.clear()
        self.previous_modules.update(sys.modules.keys())
        __builtin__.__import__ = self._import

    def _import(self, name, globals=None, locals=None, fromlist=[]):
        """Proxy to replace builtin import to keep track of new imports."""
        result = apply(self.real_import, (name, globals, locals, fromlist))
        self.new_modules.add(name)
        return result

    def __call__(self, environ, start_response):
        """Call reload then import and call the app."""
        self._reload()
        return resolve(self.resolvable)(environ, start_response)

    def _reload(self):
        """Forget all imports since reloading was turned on."""
        for name in self.new_modules - self.previous_modules:
            del sys.modules[name]
        self.new_modules.clear()

    def off(self):
        """Turn off reloading."""
        __builtin__.__import__ = self.real_import
        self.new_modules.clear()


def resolve(statement):
    """Resolve a specially formated statement to a Python object.
    
    dot.path.to.import:TheRest().is_evaled.('in', 'that', 'context')
    
    == The following two lines would be equivilent: ==
    
    {{{
    
    x = resolve('foo.bar:baz')
    from foo.bar import baz as x

    }}}

    == Everything to the right of the colon is evaled so: ==

    {{{
    
    x = resolve("module:FooApp('blarg').prop")

    ...is like...

    from module import FooApp
    x = FooApp('blarg').prop
    
    }}}
    
    You can even do this:
    
    {{{
    
    resolve("pak.mod:foo('resolve(\'pak.mod:bar\')')")
    
    }}}
    
    == If you just want to eval an expression: ==

    {{{

    plus_two = resolve(":lambda x: x + 2")

    }}

    This is taken from http://lukearno.com/projects/selector/
    
    At some point I will probably have both this and selector
    import this from some common place. Time will tell if 
    that is the right thing to do.
    """
    import_path, evalable = statement.strip().split(':', 1)
    if not import_path:
        return eval(evalable)
    descend = import_path.split('.')[1:]
    res = __import__(import_path)
    for d in descend:
        res = getattr(res, d)
    return eval("res.%s" % evalable)


