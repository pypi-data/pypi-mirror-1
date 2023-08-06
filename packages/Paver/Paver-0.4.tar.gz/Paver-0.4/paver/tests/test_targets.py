from paver import command, runtime, defaults, setuputils

from paver.tests.mock import Mock

def reset_runtime():
    runtime.TARGETS.clear()
    runtime.OPTIONS.clear()
    reload(setuputils)
    reload(defaults)
    return runtime.Bunch(dry_run=True, quiet=True)

def test_targets_are_pruned_when_options_are_missing():
    cmdopts = reset_runtime()
    assert runtime.TARGETS, "Targets should have repopulated"
    assert 'setup' not in runtime.OPTIONS
    command.load_build("", cmdopts)
    assert 'setup' not in runtime.OPTIONS
    # develop should go away because there are no 'setup'
    # options
    assert 'develop' not in runtime.TARGETS, "develop command should be missing"

def test_target_overrides_work_properly():
    cmdopts = reset_runtime()
    @runtime.target
    def bdist_egg():
        pass
    
    command.load_build("""options(setup=dict())""", cmdopts)
    
    assert runtime.TARGETS['bdist_egg'].func == bdist_egg, \
        runtime.TARGETS['bdist_egg'].longname
    assert runtime.TARGETS['paver.setuputils.bdist_egg'].func == setuputils.bdist_egg
    
def test_basic_dependencies():
    cmdopts = reset_runtime()
    cmdopts.quiet = False
    runtime.OPTIONS.update(cmdopts)
    
    @runtime.target
    def t1():
        t1.called = True
    
    t1.called = False
    t1.t2_was_called = False
    
    @runtime.target
    @runtime.needs('t1')
    def t2():
        assert t1.called
        t1.t2_was_called = True
    
    runtime.call_target('t2')
    assert t1.t2_was_called

def test_longname_resolution_in_dependencies():
    cmdopts = reset_runtime()
    cmdopts.quiet = False
    runtime.OPTIONS.update(cmdopts)
    
    @runtime.target
    def t1():
        t1.called = True
    
    t1.called = False
    t1.t2_was_called = False
    
    @runtime.target
    @runtime.needs('paver.tests.test_targets.t1')
    def t2():
        assert t1.called
        t1.t2_was_called = True
    
    print list(runtime._ALL_TARGETS.keys())
    runtime.call_target('t2')
    assert t1.t2_was_called
    
def test_chained_dependencies():
    cmdopts = reset_runtime()
    cmdopts.quiet = False
    runtime.OPTIONS.update(cmdopts)
    
    called = [False, False, False, False]
    
    @runtime.target
    def t1():
        assert called == [False, False, False, False]
        called[0] = True
    
    @runtime.target
    @runtime.needs('t1')
    def t2():
        assert called == [True, False, False, False]
        called[1] = True
    
    @runtime.target
    def t3():
        assert called == [True, True, False, False]
        called[2] = True
    
    @runtime.target
    @runtime.needs(['t2', 't3'])
    def t4():
        assert called == [True, True, True, False]
        called[3] = True
    
    runtime.call_target('t4')
    assert called == [True, True, True, True]

def test_targets_dont_repeat():
    cmdopts = reset_runtime()
    cmdopts.quiet = False
    runtime.OPTIONS.update(cmdopts)
    
    called = [0, 0, 0, 0]
    
    @runtime.target
    def t1():
        assert called == [0, 0, 0, 0]
        called[0] += 1
    
    @runtime.target
    @runtime.needs('t1')
    def t2():
        assert called == [1, 0, 0, 0]
        called[1] += 1
    
    @runtime.target
    @runtime.needs('t1')
    def t3():
        assert called == [1, 1, 0, 0]
        called[2] += 1
    
    @runtime.target
    @runtime.needs(['t2', 't3'])
    def t4():
        assert called == [1, 1, 1, 0]
        called[3] += 1
    
    runtime.call_target('t4')
    assert called == [1, 1, 1, 1]
