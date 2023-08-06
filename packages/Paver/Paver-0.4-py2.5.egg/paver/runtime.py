"""Helper functions and data structures used by pavements."""

import os
import subprocess
import copy

class Bunch(dict):
    """Simple but handy collector of a bunch of named stuff."""

    def __repr__(self):
        keys = self.keys()
        keys.sort()
        args = ', '.join(['%s=%r' % (key, self[key]) for key in keys])
        return '%s(%s)' % (self.__class__.__name__, args)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

TARGETS = dict()
OPTIONS = Bunch(dry_run=False)

# contains both long and short names
_ALL_TARGETS = dict()

def target(func):
    """Specifies that this function is a target.
    
    Note that this decorator does not actually replace the function object.
    It just keeps track of the target and sets an is_target flag on the
    function object."""
    target = Target(func)
    name = target.name
    
    # the last target with a specific name has its short name added
    if name in TARGETS:
        t = TARGETS[name]
        if t != target:
            TARGETS[t.longname] = t
    TARGETS[name] = target
    _ALL_TARGETS[name] = target
    _ALL_TARGETS[target.longname] = target
    func.is_target = True
    return func

def needs(req):
    """Specifies targets upon which this target depends.
    
    req can be a string or a list of strings with the names
    of the targets. You can call this decorator multiple times
    and the various requirements are added on.
    
    The requirements are called in the order presented in the
    list."""
    def entangle(func):
        if hasattr(func, "needs"):
            needs_list = func.needs
        else:
            needs_list = []
            func.needs = needs_list
        if isinstance(req, basestring):
            needs_list.append(req)
        elif isinstance(req, (list, tuple)):
            needs_list.extend(req)
        else:
            raise PavementError("'needs' decorator requires a list or string "
                                "but got %s" % req)
        return func
    return entangle

def call_target(target_name):
    """Calls the desired target, including any targets upon which that target
    depends.
    
    You can always call a target directly by calling the function directly.
    But, if you do so the dependencies aren't called. call_target ensures
    that these are called.
    
    Note that call_target will only call the target `once` during a given
    build as long as the options remain the same. If the options are
    changed, the target will be called again."""
    try:
        target = _ALL_TARGETS[target_name]
    except KeyError:
        raise PavementError("Unknown target: %s" % target_name)
    for need in target.needs:
        call_target(need)
    info("---> " + target_name)
    target()

def require_keys(keys):
    """A set of dotted-notation keys that must be present in the
    options for this target to be relevant.
    
    """
    def operate(func):
        k = keys
        if isinstance(k, basestring):
            k = [k]
        try:
            keylist = func.required_keys
        except AttributeError:
            keylist = set()
            func.required_keys = keylist
        keylist.update(k)
        return func
    return operate

class Target(object):
    def __init__(self, func):
        self.func = func
        self.called_options = list()
    
    @property
    def name(self):
        return self.func.__name__
    
    @property
    def doc(self):
        try:
            return self.func.__doc__
        except AttributeError:
            return ""
    
    @property
    def help(self):
        doc = self.doc
        if doc:
            period = doc.find(".")
            if period > -1:
                doc = doc[0:period]
        else:
            doc = ""
        return doc
    
    def __call__(self, *args, **kw):
        options = copy.deepcopy(OPTIONS)
        if options in self.called_options:
            return
        self.called_options.append(options)
        return self.func(*args, **kw)
    
    def __hash__(self):
        return hash(self.func)
    
    def __eq__(self, other):
        return self.func == other.func
    
    @property
    def longname(self):
        if hasattr(self, "_longname"):
            return self._longname
        return "%s.%s" % (self.func.__module__, self.name)
    
    @property
    def needs(self):
        return getattr(self.func, "needs", [])
    
    def valid(self, options):
        """Determine if this target is allowable given the 
        current build environment."""
        if hasattr(self.func, "required_keys"):
            for key in self.func.required_keys:
                parts = key.split(".")
                current = options
                valid = True
                for part in parts:
                    if part not in current:
                        valid = False
                        break
                    current = current[part]
                if not valid:
                    return False
        return True

def info(message):
    if not OPTIONS.quiet:
        print message

def debug(message):
    print message

def sh(command, capture=False):
    def runpipe():
        return subprocess.Popen(command, shell=True, 
                stdout=subprocess.PIPE).stdout.read()
    if capture:
        return dry(command, runpipe)
    else:
        dry(command, os.system, command)

_updating_options = False
def options(**kw):
    global _updating_options
    if _updating_options:
        return kw
    OPTIONS.update(kw)

def dry(message, func, *args, **kw):
    info(message)
    if OPTIONS['dry_run']:
        return
    return func(*args, **kw)

class PavementError(Exception):
    pass

class BuildFailure(Exception):
    pass

from paver.path import path

