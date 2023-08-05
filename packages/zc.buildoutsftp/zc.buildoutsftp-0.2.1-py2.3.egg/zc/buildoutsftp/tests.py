##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os, stat, StringIO, sys, urllib2, getpass

import paramiko

from zope.testing import doctest

class Replace:

    def __init__(self, module, **attrs):
        self.module = module
        self.original = original = {}

        for name, value in attrs.iteritems():
            original[name] = getattr(module, name)
            setattr(module, name, value)

    def restore(self):
        for name, value in self.attrs.iteritems():
            setattt(self.module, name, value)

class User:

    def __init__(self, name, key=None, pw=None, nameonly=False):
        self.name = name
        self.key = paramiko.PKey(key)
        self.pw = pw
        self.nameonly = nameonly

    def auth(self, key, pw):
        return (
            (key is not None and key == self.key)
            or
            (pw is not None and pw == self.pw)
            or
            self.nameonly
            )
            
hkeys = [
    ('foo.com', ),
    ('foo.org', 'foo.orgkey'),
    ('foo.net', 'foo.netkey'),
    ('foo.biz', 'foo.bizkey'),
    ]

hostdata = {
    'foo.com': (
        dict(
            docs = dict(
                greet = 'Hello\nWorld!\n'
                )
            ),
        'foo.comkey',
        [User('testuser', 'UserKey1')],
        ),
    }

class FauxTransport:

    def __init__(self, addr):
        self.host, self.port = addr
        if self.host in hostdata:
            self.fs, self.hkey, users = hostdata[self.host]
            self.users = dict([(u.name, u) for u in users])
        else:
            self.fs, self.hkey, self.users = {}, None, {}
        

    def connect(self, hostkey=None, username='', password=None, pkey=None):
        user = self.users.get(username)
        if user is None or not user.auth(pkey, password):
            raise paramiko.AuthenticationException('Authentication failed.')
        if hostkey != self.hkey:
            raise paramiko.SSHException("Bad host key from server")

class FauxAgent:

    def get_keys(self):
        return [paramiko.PKey('UserKey1'), paramiko.PKey('UserKey2')]

class FauxStat:

    def __init__(self, mode):
        self.st
                
class FauxSFTPClient:

    def __init__(self, transport):
        self.transport = transport

    def _traverse(self, path):
        path = path.split('/')[1:]
        f = self.transport.fs
        for p in path:
            if isinstance(f, str) or p not in f:
                raise IOError('[Errno 2] No such file')
            f = f[p]
        return f

    def sftp_stat(self, path):
        f = self._traverse(path)
        if isinstance(d, dict):
            return FauxStat(stat.S_IFDIR)
        else:
            return FauxStat(0)

    def open(self, path):
        return StringIO.StringIO(self._traverse(path))
        

def setup(test):
    # We're going to replace much of paramiko, and, if necessary, _winreg
    # to try to control urllib2sftp's environment.

    teardown = []
    test.globs['__teardown'] = teardown

    oldhome = os.environ.get('HOME')
    if oldhome is None:
        teardown.append(lambda:os.environ.__delitem__('HOME'))
    else:
        teardown.append(lambda:os.environ.__setitem__('HOME', oldhome))
        
    os.environ['HOME'] = '/testhome'

    # :( urllib2 needs to grow an api to get the opener so it can be
    # restored by tests
    old_opener = urllib2._opener
    teardown.append(lambda: urllib2.install_opener(old_opener))

    if sys.platform == 'win32':
        import _winreg

        key = object()

        def OpenKey(*args):
            if args != (_winreg.HKEY_CURENT_USER,
                        r'Software\SimonTatham\PuTTY\SshHoskKeys'):
                raise ValueError("Bad keys", *args)
            return key

        def EnumValue(k, index):
            if k is not key:
                raise ValueError('Bad key')
            try:
                host, hkey = hkeys[index]
            except IndexError:
                raise WindowsError(index)
            
            return 'rsa@22:'+host, hkey, 0

        HostKeys = paramiko.HostKeys

        teardown.append(Replace(_winreg,
                                OpenKey=OpenKey,
                                EnumValue=EnumValue,
                                ).restore
                        )
    else:
        def HostKeys(path=None):
            if path != '/testhome/.ssh/known_hosts':
                raise IOError('No such file', path)
            return dict([
                (host, {'ssh-rsa': paramiko.PKey(hkey)})
                for (host, hkey) in hkeys
                ])

    teardown.append(Replace(getpass, getuser=lambda: 'testuser').restore)
    teardown.append(Replace(
        paramiko,
        Transport = FauxTransport,
        Agent = FauxAgent,
        SFTPClient = FauxSFTPClient,
        HostKeys = HostKeys,
        ))

def teardown(test):
    for f in test.globs['__teardown']:
        f()

def test():
    """
    Install the urllib2 hook
    
    >>> import zc.buildoutsftp.buildoutsftp   
    >>> zc.buildoutsftp.buildoutsftp.install(None)

    Now, we'll try to get a directory listing from foo.com:

    >>> f = urllib2.urlopen('sftp://foo.com')
    >>> f.url
    'sftp://foo.com'
    >>> f.info['Content-Type']
    'text/html'
    >>> print f.read()
    

    """
    
    
def test_suite():
    return doctest.DocTestSuite(setUp=setup, tearDown=teardown)

