#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#
# Copyright 2008 Nilton Volpato <nilton dot volpato | gmail com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""\
simpleopt - a simple parser for options in command line
=======================================================

Usage Example
-------------

You just define a function, and optionally annotate the type of the
parameters, the same arguments will be parsed on the command line::

  @annotation(command=str, interval=float, differences=bool,
              args=str, kwargs=str)
  def watch(command, interval=2.0, differences=False, *args, **kwargs):
      print (command, interval, differences, args, kwargs)

  if __name__ == '__main__':
      SimpleOpt(watch).run()

Then you can call it like this, supposing you saved it on a file named
watch.py and made it executable::

  $ watch.py "df -h"
  ('df -h', 2.0, False, (), {})

  $ watch.py --interval 1.0 "df -h"
  ('df -h', 1.0, False, (), {})

  $ watch.py --noverbose --differences "df -h"
  ('df -h', 1.0, True, (), {})

  $ python simpleopt.py --foo bar --bar baz "df -h" quux quuux
  ('df -h', 2.0, False, ('quux', 'quuux'), {'foo': 'bar', 'bar': 'baz'})

Another example::

  @annotation(foo={str:int})
  def example(foo):
      return foo

  $ example.py --foo a:1,b:2,c:3
  {'a': 1, 'c': 3, 'b': 2}

  $ example.py a:1,b:2,c:3
  {'a': 1, 'c': 3, 'b': 2}


Working details
---------------

The command-line arguments are classified in one of two types: (i) option
arguments and (ii) positional arguments.

  (i) option arguments have the form --OPTION or --OPTION=VALUE where
      OPTION is the argument name and VALUE is an optional value given to
      that argument.

  (ii) positional arguments are those that are not option arguments.

The way that command-line arguments are assigned to the function's formal
parameters differ from the way that python assigns input arguments in python
code.

When a python script is run on the command line, the command-line arguments are
assigned to the function's formal parameters as follows:

  - For each formal parameter, there is a slot which will be used to contain
    the value of the argument assigned to that parameter.

  - Each slot is either 'empty' or 'filled'. Slots which had values assigned
    to them are 'filled', otherwise they are 'empty'.

  - Initially, all slots are marked 'empty'.

  - Option arguments are assigned first, followed by positional arguments.

  - For each option argument:

     o If there is a parameter with the same name as the option argument, then
       the argument value is assigned to that parameter slot. However, if the
       parameter is already filled, then that is an error.

     o Otherwise, if there is a 'keyword dictionary' argument, the argument is
       added to the dictionary using the keyword name as the dictionary key,
       unless there is already an entry with that key, in which case it is an
       error.

     o Otherwise, if there is no keyword dictionary, and no matching named
       parameter, then it is an error.

  - For each positional argument:

     o Attempt to bind the argument to the first unfilled parameter slot that
       has *no default value*. If the slot is not a vararg slot, then mark the
       slot as 'filled'.

     o Otherwise, if the next unfilled slot is a vararg slot then all remaining
       positional arguments are placed into the vararg slot.

  - Finally:

     o If the vararg slot is not yet filled, assign an empty tuple as its
       value.

     o If the keyword dictionary argument is not yet filled, assign an empty
       dicionary as its value.

     o For each remaining empty slot: if there is a default value for that
       slot, then fill the slot with the default value. If there is no default
       value, then it is an error.

When an error happens, a message is printed about the error.
"""

__author__ = "Nilton Volpato"
__author_email__ = "nilton dot volpato | gmail com"
__date__ = "2008-03-26"
__version__ = "0.1.2a"

# TODO:
#   - add support for short options to the parser

# Changelog:
#
# 2008-03-26: v0.1a first public version
# 2008-05-23: v0.1.1a removed external dependency of odict
# 2008-05-27: v0.1.2a implemented a simple odict

import inspect
import os
import sys
import textwrap

class odict(object):
    "handicapped version of an ordered dict, but useful for our purposes"
    def __init__(self):
        self._dict = {}
        self._keys = []
    def __getitem__(self, key):
        return self._dict[key]
    def __setitem__(self, key, val):
        if key not in self._dict:
            self._keys.append(key)
        self._dict[key] = val
    def __contains__(self, key):
        return key in self._dict
    def iterkeys(self):
        return iter(self._keys)
    def keys(self):
        return self._keys
    def itervalues(self):
        for key in self.iterkeys():
            yield self._dict[key]
    def values(self):
        return list(self.itervalues())
    def iteritems(self):
        for key in self.iterkeys():
            yield key, self._dict[key]
    def items(self):
        return list(self.iteritems())
    def __iter__(self):
        return self.iterkeys()

def annotation(**ann):
    def decorate(f):
        f.__annotations__ = ann
        return f
    return decorate


class SimpleOptError(Exception):
    def __init__(self, *args, **kw):
        Exception.__init__(self, *args)
        self.print_usage = kw.get('print_usage', False)


class Slot(object):
    __slots__ = ('value', 'default', 'type')

    empty = property(lambda self: not hasattr(self, 'value'))
    has_default = property(lambda self: hasattr(self, 'default'))

    def __str__(self):
        attrs = {}
        for attr in Slot.__slots__:
            try:
                attrs[attr] = getattr(self, attr)
            except AttributeError:
                pass
        return '%s(%s)' % (self.__class__.__name__, attrs)

    __repr__ = __str__


class ArgumentType(object):
    default_argtype = str

    def __init__(self, func):
        self.func = func
        self.ann = getattr(func, '__annotations__', {})

    @classmethod
    def validate(cls, argtype):
        if isinstance(argtype, type):
            return True
        elif isinstance(argtype, list):
            return len(argtype) == 1 and isinstance(argtype[0], type)
        elif isinstance(argtype, dict):
            items = argtype.items()
            if len(items) == 1:
                key_argtype, value_argtype = items[0]
                return isinstance(key_argtype, type) and \
                       isinstance(value_argtype, type)
            return False
        else:
            return False

    def format(self, name):
        argtype = self.ann.get(name, self.default_argtype)
        if isinstance(argtype, type):
            return argtype.__name__
        elif isinstance(argtype, list):
            return '[%s]' % argtype[0].__name__
        elif isinstance(argtype, dict):
            key_argtype, value_argtype = argtype.items()[0]
            return '{%s:%s}' % (key_argtype.__name__, value_argtype.__name__)
        else:
            raise NotImplementedError("formatting for %r not implemented"
                                      % argtype)

    def cast_value(self, value, argtype):
        if argtype is None:
            argtype = self.ann.get(name, self.default_argtype)
        if isinstance(argtype, type):
            if argtype is bool:
                if value.lower() in ('true', 't', '1'):
                    return True
                elif value.lower() in ('false', 'f', '0'):
                    return False
                else:
                    raise SimpleOptError(
                        "got an invalid value for a boolean argument '%s'"
                        % value)
            return argtype(value)
        elif isinstance(argtype, list):
            elem_argtype = argtype[0]
            return [ self.cast_value(elem, elem_argtype)
                     for elem in value.split(',') ]
        elif isinstance(argtype, dict):
            key_argtype, value_argtype = argtype.items()[0]
            retdict = {}
            for keyval in value.split(','):
                try:
                    key, val = keyval.split(':', 1)
                except ValueError:
                    raise SimpleOptError("expected 'key:val' got '%s'" % value)
                retdict[self.cast_value(key, key_argtype)] = \
                    self.cast_value(val, value_argtype)
            return retdict
        else:
            raise NotImplementedError("type coercion for %r not implemented"
                                      % argtype)


class SimpleOptParser(object):
    # TODO(nilton): finish this

    def __init__(self, slots):
        self.slots = slots

    def do_long(self, argname, args, optargs):
        slots = self.slots

        try:
            argname, value = argname.split('=', 1)
        except ValueError:
            value = None

        if value is None:
            if argname == 'help': # help is an exception and always shows usage
                raise SimpleOptError("--help found", print_usage=True)
            if argname in slots and slots[argname].type is bool:
                value = 'true'
            elif (argname.startswith('no') and argname[2:] in slots and
                  slots[argname[2:]].type is bool):
                argname = argname[2:]
                value = 'false'
            else:
                try:
                    value = args.pop(0)
                except IndexError:
                    raise SimpleOptError(
                        "expected a value for option '%s'" % argname)

        if argname not in optargs:
            optargs[argname] = value
        else:
            raise SimpleOptError(
                "got a duplicate option argument '%s'" % argname)

    def do_short(self, argname, args, optargs):
        raise NotImplementedError("short options not implemented yet")

    def parse(self, args):
        args = args[:]
        optargs = odict()
        posargs = []

        while args:
            arg = args.pop(0)

            if arg == '--':
                posargs += args[1:]
                break

            if arg[:2] == '--':
                self.do_long(arg[2:], args, optargs)
            elif arg[:1] == '-':
                self.do_short(arg[1:], args, optargs)
            else:
                posargs.append( arg )

        return optargs, posargs


class SimpleOpt(object):

    def __init__(self, func, args=None, prog=None, gen_short_opts=True):
        self.func = func
        if prog is None:
            prog = os.path.basename(sys.argv[0])
        self.prog = prog
        if args is None:
            args = sys.argv[1:]
        self.args = args
        self.gen_short_opts = gen_short_opts

    def run(self):
        try:
            ret = self._apply_func()
            if ret is not None:
                print repr(ret)
        except SimpleOptError, e:
            if e.print_usage:
                self.print_usage()
            else:
                self.print_error(e.args[0])
                sys.exit(2)

    def print_error(self, msg):
        print >> sys.stderr, "%s: %s" % (self.prog, msg)
        print >> sys.stderr, "Try `%s --help' for more information." % self.prog

    def print_usage(self):
        doc = inspect.getdoc(self.func)
        ann = getattr(self.func, '__annotations__', {})

        if doc is not None:
            print doc
        else:
            # TODO: generate automatic documentation from the function
            # arguments
            argtype = ArgumentType(self.func)
            def formatarg(name):
                return name + ':' + argtype.format(name)
            def formatvarargs(name):
                return '*' + name + ':' + argtype.format(name)
            def formatvarkw(name):
                return '**' + name + ':' + argtype.format(name)
            func_spec = self.func.__name__ + \
                        inspect.formatargspec(formatarg=formatarg,
                                              formatvarargs=formatvarargs,
                                              formatvarkw=formatvarkw,
                                              *inspect.getargspec(self.func))
            func_name_len = len(self.func.__name__)
            lines = textwrap.wrap(func_spec,
                                  subsequent_indent=' ' + ' ' * func_name_len,
                                  width=78)
            for line in lines:
                print line

    def _apply_func(self):
        self.slots = self._create_slots()
        if self.gen_short_opts:
            self.shopts = self._autogen_short_opts()
        #self.optargs, self.posargs = self._parse_input_arguments(self.args)
        self.optargs, self.posargs = \
                      SimpleOptParser(self.slots).parse(self.args)
        self._fill_slots()
        args = [ slot.value for slot in self.slots.itervalues() ]
        if self.slots.varargs:
            args += self.slots.varargs.value
        if self.slots.varkwargs is not None:
            kwargs = self.slots.varkwargs.value
        else:
            kwargs = {}
        return self.func(*args, **kwargs)

    def _autogen_short_opts(self):
        shopts = {}
        for argname in self.slots:
            for char in argname:
                if char not in shopts:
                    shopts[char] = argname
                    break
        return shopts

    def _create_slots(self):
        args, varargs, varkw, func_defaults = inspect.getargspec(self.func)
        if hasattr(self.func, '__annotations__'):
            ann = self.func.__annotations__
        else:
            ann = {}
        slots = odict()

        if func_defaults:
            firstdefault = len(args) - len(func_defaults)
        for i in xrange(len(args)):
            argname = args[i]
            slot = Slot()
            slot.type = ann.get(argname, ArgumentType.default_argtype)
            if func_defaults and i >= firstdefault:
                slot.default = func_defaults[i - firstdefault]
            slots[argname] = slot
        
        if varargs is not None:
            slots.varargs_name = varargs
            slots.varargs = slot = Slot()
            slot.type = ann.get(varargs, ArgumentType.default_argtype)
            slot.default = []
        else:
            slots.varargs = None

        if varkw is not None:
            slots.varkwargs_name = varkw
            slots.varkwargs = slot = Slot()
            slot.type = ann.get(varkw, ArgumentType.default_argtype)
            slot.default = {}
        else:
            slots.varkwargs = None

        return slots

    def _parse_input_arguments(self, args):
        optargs = odict()
        posargs = []
        for arg in args:
            if arg.startswith('--'):
                if '=' in arg:
                    argname, value = arg[2:].split('=', 1)
                    if argname not in optargs:
                        optargs[argname] = value
                    else:
                        raise SimpleOptError(
                            "got a duplicate option argument '%s'" % argname)
                else:
                    argname = arg[2:]
                    if argname == 'help':
                        raise SimpleOptError("--help found", print_usage=True)
                    if argname in self.slots:
                        value = 'true'
                    elif argname.startswith('no') and argname[2:] in self.slots:
                        argname = argname[2:]
                        value = 'false'
                    else:
                        raise SimpleOptError(
                            "got an unexpected boolean argument '%s'" % argname)
                    if argname not in optargs:
                        optargs[argname] = value
                    else:
                        raise SimpleOptError(
                            "got a duplicate boolean argument '%s'" % argname)
            else:
                posargs.append(arg)
        return optargs, posargs

    def _fill_slots(self):
        slots = self.slots
        argument = ArgumentType(self.func)

        for argname, value in self.optargs.iteritems():
            if argname in slots:
                slot = slots[argname]
                if slot.empty:
                    slot.value = argument.cast_value(value, slot.type)
                else:
                    raise SimpleOptError(
                        "got a duplicate option argument '%s'" % argname)
            elif slots.varkwargs is not None:
                slot = slots.varkwargs
                if slot.empty:
                    slot.value = {}
                if argname not in slot.value:
                    slot.value[argname] = argument.cast_value(value, slot.type)
                else:
                    raise SimpleOptError(
                        "got a duplicate option argument '%s'" % argname)
            else:
                raise SimpleOptError(
                    "unknown option argument provided '%s' and no keyword "
                    "dictionary slot defined" % argname)

        empty_slots = [ name for name in slots if slots[name].empty
                        and not slots[name].has_default ]
        for i in xrange(len(self.posargs)):
            if empty_slots:
                argname = empty_slots.pop(0)
                value = self.posargs[i]
                slot = slots[argname]
                slot.value = argument.cast_value(value, slot.type)
            elif slots.varargs is not None:
                slot = slots.varargs
                slot.value = [ argument.cast_value(value, slot.type)
                               for value in self.posargs[i:] ]
                break
            else:
                raise SimpleOptError("too many positional arguments "
                                     "and no varargs slot defined")

        if slots.varargs is not None and slots.varargs.empty:
            slots.varargs.value = slots.varargs.default
        if slots.varkwargs is not None and slots.varkwargs.empty:
            slots.varkwargs.value = slots.varkwargs.default
        for name in slots:
            slot = slots[name]
            if slot.empty:
                if slot.has_default:
                    slot.value = slot.default
                else:
                    raise SimpleOptError("missing required parameter '%s'" %
                                         name)


if __name__ == '__main__':
    @annotation(inputfile=str, outputfile=str, verbose=bool)
    def test1(inputfile, outputfile, verbose, *args, **kwargs):
        return (inputfile, outputfile, verbose, args, kwargs)

    @annotation(command=str, interval=float, differences=bool,
                args=str, kwargs=str)
    def watch(command, interval=2.0, differences=False, *args, **kwargs):
        return (command, interval, differences, args, kwargs)

    @annotation(foo=str, bar=int, baz=int)
    def test2(foo, bar, baz=10):
        return (foo, bar, baz)

    @annotation(numbers=[int])
    def test3(numbers):
        return numbers

    @annotation(foo={str:int})
    def test4(foo):
        return foo

    SimpleOpt(watch).run()
