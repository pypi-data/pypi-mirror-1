#!/usr/bin/env python
# -*- coding: utf-8 -*-
#### Copyright (c) Clovis Fabricio Costa

import functools
import time
import os
import types

from subprocess import Popen, PIPE
from pprint import pformat
from collections import deque
from select import select

from mpylayer.prop_table import property_table as _property_table

__all__=['DEBUG', 'MPlayerControl']

DEBUG=False

IGNORE=open(os.devnull, 'r+w')

def _debug(msg, msg_type='debug'):
    if DEBUG or msg_type != 'debug':
        print msg_type, pformat(msg)

class MPlayerControl(object):
    def run_command(self, cmd, *args):
        """
        Runs a mplayer command.
        """
        _debug('running %r with %r' % (cmd, args))
        self._assert_mplayer()
        if cmd == 'quit':
            return self._mp.communicate('quit\n')[0]
        if cmd != 'set_property': # set_property must give converted values
            args = self._process_args(cmd, self._cmds[cmd], *args)
        args = ' '.join(args)
        self._flush()
        self._mp.stdin.write('pausing_keep %s %s\n' % (cmd, args))
        if cmd.startswith('get_'):
            time.sleep(0.1) # wait little bit for the result, since it is a get
            return self._get_result()

    def __getitem__(self, item):
        """Retrieves a property"""
        value = self.get_property(item)
        proptype = _property_table[item]['type']
        if proptype == 'flag':
            value = value == 'yes'
        elif proptype in ('float', 'int', 'pos', 'time'):
            try:
                value = float(value)
            except ValueError:
                value = None
        return value

    def __setitem__(self, item, value):
        """Sets a property"""
        prop = _property_table[item]
        min = prop['min']
        max = prop['max']
        proptype = prop['type']        
        if proptype == 'flag':
            value = int(bool(value))
        elif proptype in ('int', 'float', 'pos', 'time'):
            value = float(value)
        else:
            value = repr(value)
        if min is not None and value < min:
            raise ValueError("%s value can't be less than %s" %
                             (item, min))
        if max is not None and value > max:
            raise ValueError("%s value can't be more than %s" %
                             (item, max))
        self.set_property(item, str(value))

    def __new__(cls, mplayer_path='mplayer', *args, **kwds):
        # create the list of commands from mplayer:
        cmdlist = Popen([mplayer_path, '-really-quiet', '-input', 'cmdlist'],
                        stdout=PIPE, stderr=IGNORE).communicate()[0].splitlines()
        cmdlist = (line.split() for line in cmdlist)
        cls._cmds = dict((line[0], line[1:]) for line in cmdlist)
        _debug(cls._cmds)

        # aux functions to create methods and property getters and setters
        def _create_runcmd(_run_method, _the_cmd, doc=''):
            @functools.wraps(_run_method)
            def _runcmd(self, *args, **kwds):
                return self.run_command(_the_cmd, *args, **kwds)
            _runcmd.__doc__ = doc
            _runcmd.__name__ = _the_cmd
            return _runcmd
       
        def _create_get(_the_prop):
            def _pget(self):
                return self[_the_prop]
            return _pget

        def _create_set(_the_prop):
            def _pset(self, value):
                self[_the_prop] = value
            return _pset

        # Defining methods
        for cmd, arglist in cls._cmds.iteritems():
            if cmd.startswith('get_') and cmd != 'get_property':
                prop = property(fget=functools.partial(cls.run_command, cmd=cmd),
                                doc='%s command\n(readonly)' % cmd)
                setattr(cls, cmd[4:], prop)
            else:
                doc = '%s(%s)' % (cmd, ', '.join(arglist))
                setattr(cls, cmd, _create_runcmd(cls.run_command, cmd, doc=doc))
        
        # Defining properties
        for prop_name, propdict in _property_table.iteritems():
            pget = _create_get(prop_name)
            if propdict['set']:
                pset = _create_set(prop_name)
            else:
                pset = None
            # create a docstring:
            doc = ["%(name)s <%(type)s>" % propdict]
            line = []
            if not propdict['set']:
                line.append('(readonly)')
            for t in ('min', 'max'):
                if propdict[t] is not None:
                    line.append('[%s: %s]' % (t, propdict[t]))
            doc.append(' '.join(line))
            if propdict['comment']:
                doc.append(propdict['comment'])
            doc = '\n'.join(doc)
            # create property
            prop = property(fget=pget, fset=pset, doc=doc)
            setattr(cls, prop_name, prop)

        return super(MPlayerControl, cls).__new__(cls, mplayer_path, *args, **kwds)

    def __init__(self, mplayer_path='mplayer'):
        """
        Starts a new mplayer process.
        mplayer_path is the path to mplayer, defaults to 'mplayer'.
        """
        self._mp_path = mplayer_path
        self._buffer = deque()
        self._run_mplayer()

    _cmdtype = {
                'Integer': (int, '%d'),
                'Float': (float, '%f'),
                'String': (str, '%r'),
                 }

    def _process_args(self, cmd, arglist, *args):
        rcvd_args = [arg for arg in reversed(args) if arg is not None]
        for arg in arglist:
            optional = arg.startswith('[')
            arg = arg.strip('[]')
            if not rcvd_args:
                if optional:
                    return
                else:
                    raise TypeError('%s takes %r arguments - %s not given in %r' %
                                    (cmd, arglist, arg, args))
            arg_func, arg_mask = self._cmdtype[arg]
            yield arg_mask % arg_func(rcvd_args.pop())        

    def _run_mplayer(self):
        self._mp = Popen([self._mp_path, '-slave', '-quiet', '-idle'],
                         stdin=PIPE, stdout=PIPE, stderr=IGNORE)

    def _assert_mplayer(self):
        if self._mp.poll() is not None:
            self._run_mplayer()

    def __del__(self):
        if self._mp.poll() is None:
            print 'Trying to quit mplayer...'
            self._mp.communicate('quit\n')

    def _get_cmdlist(self):
        cmdlist = Popen([self._mp_path, '-really-quiet', '-input', 'cmdlist'],
                        stdout=PIPE, stderr=IGNORE).communicate()[0].splitlines()
        cmdlist = (line.split() for line in cmdlist)
        self._cmds = dict((line[0], line[1:]) for line in cmdlist)
        _debug(self._cmds)

    def _read_all(self):
        while True:
            rlst, wlst, elst = select([self._mp.stdout], [], [], 0)
            if not rlst:
                break
            for r in rlst:
                self._buffer.append(r.readline())
        if self._buffer:
            _debug(self._buffer)

    def _flush(self):
        self._read_all()
        self._buffer.clear()

    def _get_result(self):
        self._read_all()
        if self._buffer:
            value = self._buffer.pop()
            if '=' in value:
                foo, foo, value = value.partition('=')
            return value.strip("'").strip()
        else:
            return ''

if __name__ == '__main__':
    mp = MPlayerControl()
    mp.loadfile('Trick_as_a_brick.mp3')
