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

if not hasattr(__builtin__, 'set'):
    from sets import Set as set

from simpleweb.extlib.resolver import resolve


class Assassin(object):
    """WSGI middleware for per request code reloading.
    
    This class reloads only targeted packages.

    Per request reloading is very nice while developing but probably 
    a very bad idea in production, so Mori has on and off methods.
    """

    def __init__(self, resolvable, targets, exceptions=None, turn_on=True):
        """Just set things up and optionally turn reloading on.

        First arg is a resolver statement for the WSGI app to wrap.
        (See resolver documentation for details.)
        The second is a list of packages to reload.
        The optional third arg is a list of names to not reload.
        
        Default is to turn reloading on.
        """
        self.resolvable = resolvable
        self.targets = targets
        if exceptions is None:
            self.exceptions = []
        else:
            self.exceptions = exceptions
        self.mode = 'off'
        if turn_on: 
            self.turn_on()

    def turn_on(self):
        """Turn on reloading."""
        self.mode = "on"

    def __call__(self, environ, start_response):
        """Call reload if on then import and call the app."""
        if self.mode == 'on':
            self._reload()
        return resolve(self.resolvable)(environ, start_response)

    def potential_target(self, name):
        """Is this name in or of one of the target packages?"""
        for target in self.targets:
            if name == target:
                return True
            if name.startswith(target+'.'):
                return True
        else:
            return False

    def _reload(self):
        """Forget all target package imports if not in exceptions."""
        for name in sys.modules.keys():
            if name not in self.exceptions and self.potential_target(name):
                sys.modules.pop(name)

    def turn_off(self):
        """Turn off reloading."""
        self.mode = 'off'


class Mori(object):
    """WSGI middleware for per request code reloading.
    
    This class reloads everything imported since the last request.
    This does not seem to play nice with some packages.
    
    Per request reloading is very nice while developing but probably 
    a very bad idea in production, so Mori has on and off methods.
    """

    def __init__(self, resolvable, turn_on=True):
        """Just set things up and optionally turn reloading on.

        First arg is a resolver statement for the WSGI app to wrap.
        See resolve method for details.
        
        Default is to turn reloading on.
        """
        self.resolvable = resolvable
        self.real_import = __builtin__.__import__
        self.previous_modules = set()
        self.new_modules = set()
        if turn_on:
            self.turn_on()

    def turn_on(self):
        """Turn on reloading.
        
        Everything imported after this will be forgotten when
        self._reload() is called (as it is for each request).
        """
        self.new_modules.clear()
        self.previous_modules.clear()
        self.previous_modules.update(sys.modules.keys())
        __builtin__.__import__ = self._import

    def _import(self, name, my_globals, my_locals, fromlist):
        """Proxy to replace builtin import to keep track of new imports."""
        if fromlist is None:
            fromlist = []
        result = self.real_import(name, my_globals, my_locals, fromlist)
        self.new_modules.add(name)
        return result

    def __call__(self, environ, start_response):
        """Call reload then import and call the app."""
        self._reload()
        return resolve(self.resolvable)(environ, start_response)

    def _reload(self):
        """Forget all imports since reloading was turned on."""
        for name in self.new_modules - self.previous_modules:
            if name in sys.modules:
                sys.modules.pop(name)
                #del sys.modules[name]
        for name in sys.modules.keys():
            if sys.modules[name] is None:
                sys.modules.pop(name)
        self.new_modules.clear()

    def turn_off(self):
        """Turn off reloading."""
        __builtin__.__import__ = self.real_import
        self.new_modules.clear()


