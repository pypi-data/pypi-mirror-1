"""
run "python setup.py develop" before running the contained test
"""
import py

pytest_plugins = "pytester", "figleaf"

def test_functional(testdir):
    testdir.makepyfile("""
        def f():    
            x = 42
        def test_whatever():
            pass
        """)
    result = testdir.runpytest('--figleaf')
    assert result.ret == 0
    assert result.stdout.fnmatch_lines([
        '*figleaf html*'
        ])
    #print result.stdout.str()

def test_functional_other_path(testdir):
    testdir.makepyfile("""
        def f():    
            x = 42
        def test_whatever():
            pass
        """)
    result = testdir.runpytest('--figleaf', '--fig-data=xyz', '--fig-html=x3')
    assert result.ret == 0
    assert result.stdout.fnmatch_lines([
        '*figleaf html*'
        ])
    data = testdir.tmpdir.join("xyz")
    assert data.check()
    html = testdir.tmpdir.join("x3")
    assert html.check()

def test_no_figleaf_import(testdir):
    testdir.makepyfile("""
        import sys
        def test_whatever():
            assert 'figleaf' not in sys.modules, "figleaf was imported"
        """)
    result = testdir.runpytest()
    assert result.ret == 0
    assert result.stdout.fnmatch_lines([
        '*1 passed*',
        ])
    #print result.stdout.str()
