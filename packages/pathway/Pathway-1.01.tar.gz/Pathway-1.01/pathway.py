#!/usr/bin/env python

"""
Pathway
=======
Pathway is a simple Python library for interacting with the filesystem. It
wraps many common file and folder operations in a clean, object-oriented
syntax.

Note that Pathway is designed to work with LOCAL, EXISTING paths.
"""

import os
import os.path
import fnmatch
import shutil

p = os.path

__all__ = ('ALL', 'FOLDERS', 'FILES', 'PathError', 'PathObject', 'Folder',
           'File', 'SomethingElse', 'new')

ALL = lambda n: True
FOLDERS = lambda n: p.isdir(n)
FILES = lambda n: p.isfile(n)

class PathError(Exception):
    defaultdesc = "The operation on %s could not be performed"
    def __init__(self, path, description=None):
        self.path = path
        self.desc = description or self.defaultdesc
    
    def __str__(self):
        return self.desc % self.path

class NonExistenceError(PathError):
    defaultdesc = "%s does not exist"

class WrongTypeError(PathError):
    def __init__(self, path, type):
        self.path = path
        self.type = type
    
    def __str__(self):
        return '%s is not a %s' % (self.path, self.type)

class WouldNotOverwriteError(PathError):
    defaultdesc = "%s already exists - would not overwrite"


def _normalize(path):
    if isinstance(path, PathObject):
        path = path.path
    return p.abspath(p.expanduser(path))


class _StatProperty(object):
    def __init__(self, statname):
        self.p = statname

    def __get__(self, instance, owner):
        if not instance:
            return
        return getattr(instance.stat, self.p)


class PathObject(object):
    def __init__(self, path):
        self.path = _normalize(path)

    def __str__(self):
        return self.path

    def __unicode__(self):
        return unicode(self.path)

    def __repr__(self):
        return "%s '%s'" % (self.__class__.__name__, self.path)

    def __hash__(self):
        return hash(self.path)

    def __nonzero__(self):
        return True

    def __eq__(self, other):
        if not isinstance(other, PathObject):
            return NotImplemented
        return self.path == other.path

    def __ne__(self, other):
        if not isinstance(other, PathObject):
            return NotImplemented
        return self.path <> other.path

    @property
    def parentpath(self):
        return p.split(self.loc)[0]

    def parent(self):
        return Folder(p.split(self.path)[0])

    def parts(self):
        return tuple(self.path.split(p.sep))

    def isancestor(self, other):
        myparts = self.parts()
        itsparts = other.parts()
        if len(myparts) > len(itsparts):
            return False
        else:
            if myparts == itsparts[:len(myparts)]:
                return True
            else:
                return False
    
    def matches(self, pattern):
        return fnmatch.fnmatch(self.path, pattern)
    
    def real(self):
        return p.realpath(self.path)
    
    def linkdest(self):
        if p.islink(self):
            return os.readlink(self)

    def __gt__(self, other):
        if not isinstance(other, PathObject):
            return NotImplemented
        return self.isancestor(other)

    def __lt__(self, other):
        if not isinstance(other, PathObject):
            return NotImplemented
        return other.isancestor(self)

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other

    base = property(lambda s: p.basename(s.path))
    basename = base
    drive = property(lambda s: p.splitdrive(s.path)[0])
    name = property(lambda s: p.splitext(s.path)[0])
    ext = property(lambda s: p.splitext(s.path)[1])
    
    isfile = False
    isdir = False


class Folder(PathObject):
    def __init__(self, path=None, mkdir=False):
        if path is None:
            path = os.getcwd()
        path = _normalize(path)
        if not p.isdir(path):
            if mkdir:
                if not p.exists(path):
                    os.makedirs(path)
                else:
                    raise WrongTypeError(path, 'folder')
            elif p.exists(path):
                raise WrongTypeError(path, 'folder')
            else:
                raise NonExistenceError(path)
        self.path = path

    def childpath(self, name):
        return p.join(self.path, name)

    def child(self, name):
        if name == '..':
            return self.parent()
        else:
            return new(p.join(self.path, name))

    def haschild(self, name):
        return p.exists(self.childpath(name))

    def mkdir(self, name):
        target = self.childpath(name)
        if p.isdir(target):
            return False
        elif p.exists(target):
            raise WrongTypeError(target, 'folder')
        else:
            os.mkdir(target)
            return True
    
    def create(self, name, contents='', overwrite=False):
        if (not overwrite) and self.haschild(name):
            raise WouldNotOverwriteError(target)
        fd = open(self.childpath(name), 'w')
        fd.write(contents)
        fd.close()
        return self.child(name)
    
    def copy(self, dest, ignore):
        if isinstance(dest, basestring):
            dest = Folder(basestring, mkdir=True)
        for item in self.ls():
            if item.isdir and not ignore(item):
                dest.mkdir(item.basename)
                item.copy(dest.child(item.basename), ignore)
            elif not ignore(item):
                item.copy(dest)
    
    def delete(self, name, recursive=False):
        c = self.child(name)
        if isinstance(c, Folder):
            if len(c.names()) > 0:
                if recursive:
                    shutil.rmtree(c.path)
                else:
                    raise PathError(c.path, "%s has contents - won't remove "
                                    "recursively")
            else:
                os.rmdir(c.path)
        del c
        return

    def cd(self):
        os.chdir(self.path)

    def ls(self, pattern=None, kind=ALL):
        if pattern:
            return fnmatch.filter([self.child(n)
                for n in os.listdir(self.path) if kind(n)], pattern)
        else:
            return [self.child(n) for n in os.listdir(self.path) if kind(n)]

    def names(self, pattern=None, kind=ALL):
        if pattern:
            return fnmatch.filter([n for n in os.listdir(self.path)
                if kind(n)], pattern)
        else:
            return [n for n in os.listdir(self.path) if kind(n)]

    def paths(self, pattern=None, kind=ALL):
        if pattern:
            return fnmatch.filter([self.childpath(n)
                for n in os.listdir(self.path) if kind(n)], pattern)
        else:
            return [self.childpath(n) for n in os.listdir(self.path)
                if kind(n)]

    def __mod__(self, pattern):
        return self.ls(pattern)

    def __iter__(self):
        return iter(self.ls())

    def __getitem__(self, name):
        if isinstance(name, tuple):
            return self.childpath(name[0])
        else:
            return self.child(name)
    
    def __getslice__(self, i, j):
        raise TypeError("Cannot slice a Folder object")

    def __contains__(self, name):
        return self.haschild(name)
    
    isdir = True


class File(PathObject):
    def __init__(self, path):
        path = _normalize(path)
        if not p.isfile(path):
            raise WrongTypeError(path, 'file')
        self.path = path
        self._stats = None

    def _restat(self):
        self._stats = os.stat(self.path)
    
    def touch(self, times=None):
        os.utime(self.path, times)
        if self._stats:
            self._restat()

    def open(self, mode='r'):
        return open(self.path, mode)
    
    if hasattr(os, 'startfile'):
        def launch(self, op='open'):
            os.startfile(self.path, op)

    def contents(self):
        fd = open(self.path, 'r')
        try:
            return fd.read()
        finally:
            fd.close()
    
    def move(self, dest, overwrite=True):
        if isinstance(dest, Folder):
            dest = dest[self.basename,]
        elif p.isdir(dest):
            dest = p.join(dest, self.basename)
        if (not overwrite) and p.exists(dest):
            raise WouldNotOverwriteError(dest)
        os.rename(self.path, dest)
        self.path = dest
        if self._stats:
            self._restat()
    
    def rename(self, newname, overwrite=True):
        """
        rename is intended to simply change a file's name within its current
        directory.
        """
        parent = self.parent()
        newpath = parent.childpath(newname)
        if (os.path.exists(newpath)) and (not overwrite):
            raise WouldNotOverwriteError(newpath)
        os.rename(self.path, newpath)
        self.path = newpath
        if self._stats:
            self._restat()
    
    def copy(self, dest, overwrite=True, meta=True):
        if isinstance(dest, Folder):
            dest = dest[self.basename,]
        elif p.isdir(dest):
            dest = p.join(dest, self.basename)
        if (not overwrite) and p.exists(dest):
            raise WouldNotOverwriteError(dest)
        if meta:
            shutil.copy2(self.path, dest)
        else:
            shutil.copy(self.path, dest)
    
    if hasattr(os, 'symlink'):
        def symlink(self, dest, overwrite=True):
            if isinstance(dest, Folder):
                dest = dest[self.basename,]
            elif p.isdir(dest):
                dest = p.join(dest, self.basename)
            if (not overwrite) and p.exists(dest):
                raise WouldNotOverwriteError(dest)
            os.symlink(self.path, dest)

    @property
    def stat(self):
        if self._stats == None:
            self._restat()
        return self._stats

    mode = _StatProperty('st_mode')
    inode = _StatProperty('st_ino')
    dev = _StatProperty('st_dev')
    links = _StatProperty('st_nlink')
    uid = _StatProperty('st_uid')
    gid = _StatProperty('st_gid')
    size = _StatProperty('st_size')
    atime = _StatProperty('st_atime')
    mtime = _StatProperty('st_mtime')
    ctime = _StatProperty('st_ctime')
    
    isfile = True


class SomethingElse(PathObject):
    def __init__(self, path):
        self.path = _normalize(path)


def new(path):
    if isinstance(path, PathObject):
        return path
    path = _normalize(path)
    if p.isdir(path):
        return Folder(path)
    elif p.isfile(path):
        return File(path)
    elif p.exists(path):
        return SomethingElse(path)
    else:
        raise NonExistenceError(path)

