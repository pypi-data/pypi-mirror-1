# -*- coding: utf-8 -*-

"""
except.py client library
"""

import os
import os.path
import sys
import traceback
import datetime
import hashlib
import socket
import time
import httplib
import cStringIO
import struct

import simplejson


__all__ = ('send_exception', 'get_filename')


API_KEY = os.environ.get('EXCEPT_PY_API_KEY')
SERVER = os.environ.get('EXCEPT_PY_SERVER')


assert API_KEY, 'EXCEPT_PY_API_KEY not found in env'
assert SERVER, 'EXCEPT_PY_SERVER not found in env'


def get_filename(fullpath):
    """
    strips import path from filename to make traceback
    more compact and readable
    
    for example, if /usr/lib/python2.5/site-packages/django is in sys.path
    than filename /usr/lib/python2.5/site-packages/django/django/conf/__init.py
    will be stripped to django/conf/__init__.py
    """
    fullpath = os.path.realpath(os.path.abspath(fullpath))
    possible = [fullpath]
    for sys_path in sys.path:
        sys_path = os.path.realpath(os.path.abspath(sys_path))
        if fullpath.startswith(sys_path) and len(fullpath)-2 > len(sys_path):
            possible.append(fullpath[len(sys_path)+1:])
    return min(possible, key=lambda p: len(p))


def format_tb(exc_type, exc, tb):
    """
    formats traceback just like traceback.format_tb, but uses `get_filename`
    to strip long filenames
    """
    out = cStringIO.StringIO()
    out.write('Traceback (most recent call last):\n')
    for filename, line, mod, code in traceback.extract_tb(tb):
        out.write('  File "%s", line %i, in %s\n' % (
            get_filename(filename), line, mod))
        out.write('    %s\n' % code)
    out.write('%s: %s' % (exc_type.__name__, exc))
    out.seek(0)
    return out.read()


def send_exception(_mode='http', **meta):
    """
    sends exception information to except.py service
    additional meta information (url for example) are acceptable
    via kwargs - and them will be visible on exception page
    
    example usage:
        
        try:
            some_dangerous_call()
        except:
            send_exception()
    
    or with meta information:
    
        try:
            some_dangerous_call()
        except:
            send_exception(url=someurl, args=[('foo', 'bar),
                                              ('spam', 'eggs')])
    
    """
    exc_type, exc, tb = sys.exc_info()
    try:
        text = format_tb(exc_type, exc, tb)
        tb_last = tb
        while tb_last.tb_next:
            tb_last = tb_last.tb_next
        module = tb_last.tb_frame.f_globals['__name__']
        path, line, fn, code = traceback.extract_stack(tb_last.tb_frame)[-1]
        hash_string = ''.join(traceback.format_tb(tb))
        data = simplejson.dumps({
            'type': '%s.%s' % (exc_type.__module__, exc_type.__name__),
            'message': unicode(exc.message),
            'hash': hashlib.md5(hash_string).hexdigest(),
            'text': text,
            'filename': get_filename(path),
            'path': path,
            'module': module,
            'line': line,
            'fn': fn,
            'code': code,
            'timestamp': int(time.mktime(datetime.datetime.now().timetuple())),
            'meta': meta,
        })
        if _mode == 'http':
            connection = httplib.HTTPConnection(SERVER)
            connection.request('POST', '/api/issues/%s/' % API_KEY, body=data,
                               headers={'Content-Type': 'application/json'})
            response = connection.getresponse()
            resp_body = response.read()
            assert resp_body == 'Created', resp_body
        elif _mode == 'sock':
            if ':' in SERVER:
                hostname, port = SERVER.split(':')
                port = int(port)
            else:
                hostname = SERVER
                port = 8010
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((hostname, port))
            sock.send(API_KEY)
            sock.send(struct.pack('i', len(data)))
            sock.send(data)
            resp = sock.recv(2)
            assert resp == 'OK', resp
    except:
        sys.stderr.write('%s EXCEPT_PY FAILED SENDING\n%s------\n' % (
            datetime.datetime.now(),
            ''.join(traceback.format_exception(exc_type, exc, tb))
        ))
        traceback.print_exc(None, sys.stderr)
        sys.stderr.write('\n')

