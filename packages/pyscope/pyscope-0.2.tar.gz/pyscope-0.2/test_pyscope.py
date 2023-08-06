import sys
from pyscope import scope, scoped
from StringIO import StringIO

def test_scoped_var():
    var = scoped(1)
    assert var == 1

    with scope(var, 3):
        assert str(var) == "3"

        with scope(var, 4):
            assert var ==4


def test_stdout_scope(monkeypatch):
    monkeypatch.setattr(sys, 'stdout', scoped(sys.stdout))
    io = StringIO()
    with scope(sys.stdout, io):
        assert io == sys.stdout
        print "Hello"
    assert sys.stdout != io
    assert io.getvalue() == "Hello\n"

