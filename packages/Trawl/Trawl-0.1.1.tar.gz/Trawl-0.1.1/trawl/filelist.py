
import copy
import functools
import glob
import os
import re

from trawl.path import path

# These aren't all strictly necessary but I'm feeling too
# lazy to separate the wheat from the chaffe right now.
SPECIAL_METHODS = """
repr str lt le eq ne gt ge cmp hash nonzero unicode call
len getitem setitem delitem iter reversed contains getslice
setslice delslice add sub mul floordiv mod divmod pow lshift
rshift and xor or radd rsub rmul rdiv rtruediv rfloordiv rmod
rdivmod rpow rlshift rrshift rand rxor ror iadd isub imul
idiv itruediv ifloordiv imod ipow ilshift irshift iand ixor
ior neg pos abs invert complex int long float oct hex index
coerce enter exit
""".split()

def _exclude_cores(fn):
    return re.search(r"(^|[\/\\])core$", fn) and not os.path.isdir(fn)

def skip_resolve(fn):
    fn.__skip_resolve__ = True
    return fn

class FileListMeta(type):
    def __new__(mcs, name, bases, dict):
        ret = type.__new__(mcs, name, bases, dict)
        for method in SPECIAL_METHODS:
            base = getattr(list, "__%s__" % method, None)
            if base is None:
                continue
            def mkfunc(func):
                def _resolved(self, *args, **kwargs):
                    self.resolve()
                    return func(self, *args, **kwargs)
                return _resolved
            setattr(ret, "__%s__" % method, mkfunc(base))
        return ret

class FileListIterator(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def next(self):
        ret = self.wrapped.next()
        if isinstance(ret, path):
            return ret
        return path(ret)

class FileList(list):
    """\
    A FileList is essentially an special class for dealing with lists of
    file names.
    
    FileLists are lazy. When given a list of glob patterns for possible
    files to be included in the file list, instead of search the file
    structures to find the files, a FileList holds the pattern for latter use.
    
    This allows us to define a number of patterns to match any number of
    files, but only search out the actual files when the FileList itself
    is actually used.
    """
    
    __metaclass__ = FileListMeta
    
    DEFAULT_EXCLUDE_PATTERNS = [
        re.compile(r"(^|[\/\\])CVS([\/\\]|$)"),
        re.compile(r"(^|[\/\\])\.svn([\/\\]|$)"),
        re.compile(r"(^|[\/\\])\.git([\/\\]|$)"),
        re.compile(r"(^|[\/\\])\.hg([\/\\]|$)"),
        re.compile(r"\.bak$"),
        re.compile(r"~$")
    ]
    
    DEFAULT_EXCLUDE_FUNCS = [
        _exclude_cores
    ]
    
    def __init__(self, *patterns):
        """\
        Create a FileList from the provided globbable patterns. If you
        wish to perform multiple includes or excludes when creating
        new instances, use the method chaining pattern.
        
        Example:
          file_list = FileList("lib/**/*.py", "test/test*.py")
          
          pkg_files = FileList("lib/**/*").exclude_re(r"\bCVS\b")
                        .exclude_re(r"\b.git\b").exclude_re("\b.svn\b")
        """
        if len(patterns) == 1 and isinstance(patterns[0], FileList):
            other = patterns[0]
            self._pending_add = copy.copy(other._pending_add)
            self._pending = other._pending
            self._exclude_patterns = copy.copy(other._exclude_patterns)
            self._exclude_funcs = copy.copy(other._exclude_funcs)
            self._exclude_regexps = copy.copy(other._exclude_regexps)
        else:
            self._pending_add = []
            self._pending = False
            self._exclude_patterns = FileList.DEFAULT_EXCLUDE_PATTERNS[:]
            self._exclude_funcs = FileList.DEFAULT_EXCLUDE_FUNCS[:]
            self._exclude_regexps = []
            map(self.include, patterns)

    def __getattribute__(self, name):
        """\
        Make sure that any functions called on instances
        return instances of FileList and not a plain list.
        """
        attr = super(FileList, self).__getattribute__(name)
        if name == "__class__":
            return attr
        if callable(attr):
            if not getattr(attr, "__skip_resolve__", False):
                self.resolve()
            @functools.wraps(attr)
            def _wrap(*args, **kwargs):
                ret = attr(*args, **kwargs)
                if isinstance(ret, FileList):
                    return ret
                elif not isinstance(ret, list):
                    return ret
                return FileList(ret)
            return _wrap
        return attr

    @skip_resolve
    def copy(self):
        "Return a cloned instance of this FileList"
        return self.__class__(self)

    @skip_resolve
    def include(self, *patterns):
        """\
        Add new glob patterns to this FileList instance. If an aray is given,
        add each element of the array.
        
        Example:
          file_list.include("*.rb", "*.cfg")
          file_list.include("math.c lib.h *.o".split())
        """
        for p in patterns:
            if isinstance(p, basestring):
                self._pending_add.append(p)
            else:
                map(self.include, p)
        self._pending = True
        return self

    @skip_resolve
    def exclude(self, *patterns):
        """\
        Register a list of glob patterns that should be excluded from the
        list. Remember that a full pathname is a valid glob if you want
        to exclude specific files.
        
        Note that glob patterns are expanded against the file system. If a
        file is explicitly aded to af ile list, but does not exist on the
        file system, then a glob pattern in the exclude list will not
        exclude the file.
        
        Examples:
          FileList('a.c', 'b.c').exclude('a.c') -> ['b.c']
         
        If "a.c" is a file:
          FileList('a.c', 'b.c').exclude('a.*') -> ['b.c']
         
        If "a.c" is not a file:
          FileList('a.c', 'b.c').exclude('a.*') -> ['a.c', 'b.c']
        
        """
        for p in patterns:
            if isinstance(p, basestring):
                self._exclude_patterns.append(p)
            elif callable(p):
                self._exclude_funcs.append(p)
            else:
                map(self.exclude, p)
        if not self._pending:
            self._resolve_excludes()
        return self
    
    @skip_resolve
    def exclude_re(self, *patterns):
        """\
        Register a list of regular expression patterns or objects that
        should be excluded from the list of file names.
        
        The `search` method is used to compare regular expressions
        to file names which means that you need to explicitly anchor
        patterns with '^' if you want to start at the beginning of
        the string.
        
        Examples:
          FileList('ab.c', 'b.c').exclude_re(r"a.*") -> ['b.c']
          FileList('ab.c', 'b.c').exclude_re(r"^b") -> ['ab.c']
        
        """
        for p in patterns:
            if isinstance(p, basestring):
                self._exclude_patterns.append(re.compile(p))
            elif hasattr(p, "pattern") and hasattr(p, "search"):
                # Can't find a better test for a compiled regular expression
                self._exclude_patterns.append(p)
            else:
                map(self.exclude_re, p)
        if not self._pending:
            self._resolve_excludes()
        return self
    
    @skip_resolve
    def clear_excludes(self):
        "Clear all the exclude patterns."
        self._exclude_patterns = []
        self._exclude_funcs = []
        if not self._pending:
            self._calculate_exclude_regexp()
        return self

    @skip_resolve
    def resolve(self):
        "Resolve all the pending glob patterns."
        if self._pending:
            self._pending = False
            for fn in self._pending_add:
                self._resolve_add(fn)
            self._pending_add = []
            self._resolve_excludes()
        return self

    def sub(self, pattern, repl):
        """\
        Calls re.sub(pattern, repl, fn) on each filename.

        Triggers file name resolution.
        """
        p = re.compile(pattern)
        for idx in range(len(self)):
            self[idx] = p.sub(repl, self[idx])
        return self

    def existing(self):
        """\
        Remove any file names that don't exist on the file system.
        
        Triggers file name resolution.
        """
        idx = 0
        while idx < len(self):
            if not self[idx].exists():
                self.pop(idx)
            else:
                idx += 1
        return self

    @skip_resolve
    def _resolve_add(self, fn):
        if re.search(r"[*?\[\{]", fn):
            self._add_matching(fn)
        else:
            self.append(fn)

    @skip_resolve
    def _add_matching(self, pattern):
        "Add files matching the glob pattern."
        fnames = filter(lambda fn: not self._exclude(fn), glob.glob(pattern))
        self.extend(path(fn) for fn in fnames)

    @skip_resolve
    def _exclude(self, fn):
        "Should the given filename be excluded?"
        if not self._exclude_regexps:
            self._calculate_exclude_regexp()
        if any(r.search(fn) for r in self._exclude_regexps):
            return True
        return any(func(fn) for func in self._exclude_funcs)
    
    @skip_resolve
    def _resolve_excludes(self):
        self._calculate_exclude_regexp()
        idx = 0
        while idx < len(self):
            if self._exclude(self[idx]):
                self.pop(idx)
            else:
                idx += 1

    @skip_resolve
    def _calculate_exclude_regexp(self):
        self._exclude_regexps = []
        for e in self._exclude_patterns:
            if hasattr(e, "pattern") and hasattr(e, "search"):
                self._exclude_regexps.append(e)
            elif re.search(r"[*?]", e):
                for fn in glob.glob(e):
                    self._exclude_regexps.append(re.compile(fn))
            else:
                self._exclude_regexps.append(re.compile(e))
