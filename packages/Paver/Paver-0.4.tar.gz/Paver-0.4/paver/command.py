import os
import sys
import optparse

from paver import defaults
from paver import runtime

def load_build(source):
    module = compile(source, "pavement.py", "exec")
    exec module in defaults.__dict__

def set_options(cmdopts):
    options = runtime.OPTIONS
    options.dry_run = cmdopts.dry_run
    options.quiet = cmdopts.quiet
    defaults.options = options
    prune_targets(options)

def prune_targets(options):
    for name, target in runtime.TARGETS.items():
        if not target.valid(options):
            del runtime.TARGETS[name]

def _check_file():
    if not os.path.exists("pavement.py"):
        print "WARNING: No pavement.py file here!"
        return False
    return True
    
def _read_pavement():
    return open("pavement.py").read().strip()

def main():
    has_pavement = _check_file()
    parser = optparse.OptionParser()
    parser.add_option("-n", "--dry-run", dest="dry_run",
        help="don't actually perform operations", action="store_true",
        default=False)
    parser.add_option("-q", "--quiet", dest="quiet",
        help="Show only error messages", action="store_true",
        default=False)
    
    (cmdopts, args) = parser.parse_args()
    
    if has_pavement:
        load_build(_read_pavement())
    set_options(cmdopts)
    
    if len(args) == 0:
        args.append("help")
    for target_name in args:
        runtime.call_target(target_name)

def setup():
    """Calls setuptools or distutils setup. Note that what this should
    do is handle command line arguments appropriately and ultimately call
    Paver targets rather than distutils/setuptools commands."""
    _check_file()
    
    cmdopts = runtime.Bunch(dry_run=False, quiet=False)
    if '-n' in sys.argv:
        cmdopts.dry_run = True
    if '-q' in sys.argv:
        cmdopts.quiet = True
    
    load_build(_read_pavement())
    set_options(cmdopts)    
    
    from paver import setuputils
    setuputils.setup()
