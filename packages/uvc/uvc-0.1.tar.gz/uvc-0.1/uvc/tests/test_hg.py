import os

from uvc.path import path
from uvc import commands, hg, main
from uvc.tests.util import test_context

dialect = hg.HgDialect()

topdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", 
                        "testfiles"))

context = None

def setup_module(module):
    global context
    if not os.path.exists(topdir):
        os.mkdir(topdir)
    context = main.Context(topdir)

def test_clone_command_conversion():
    generic_clone = commands.clone(context, ["http://hg.mozilla.org/labs/bespin", 
                                    "bespin"])
    hg_clone = hg.clone(generic_clone)
    assert str(hg_clone) == "clone http://hg.mozilla.org/labs/bespin bespin"
    
def test_convert_function():
    generic_clone = commands.clone(context, ["http://hg.mozilla.org/labs/bespin", 
                                    "bespin"])
    result = dialect.convert(generic_clone)
    assert str(result) == "clone http://hg.mozilla.org/labs/bespin bespin"
    
def test_convert_unknown_command():
    class Foo(object):
        pass
    
    try:
        result = dialect.convert(Foo())
        assert False, "expected HgError for unknown command"
    except hg.HgError:
        pass

def test_commit_command():
    generic_commit = commands.commit(test_context, ["-m", "test message", "foo", "bar"])
    result = dialect.convert(generic_commit)
    assert not result.reads_remote
    assert not result.writes_remote
    assert str(result) == "commit -m test message foo bar"
    
def test_diff_command():
    generic_diff = commands.diff(context, [])
    result = dialect.convert(generic_diff)
    assert not result.reads_remote
    assert not result.writes_remote
    assert str(result) == "diff"
    
def test_clone_command_simple_ssh_auth():
    context = main.Context(topdir, auth=dict(type="ssh", key="/tmp/id.rsa"))
    generic_clone = commands.clone(context, ["ssh://hg.mozilla.org/bar"])
    result = dialect.convert(generic_clone)
    assert result.reads_remote
    assert not result.writes_remote
    assert str(result) == "clone -e ssh -i /tmp/id.rsa -o StrictHostKeyChecking=no ssh://hg.mozilla.org/bar bar"
    
def test_clone_command_ssh_username_auth():
    context = main.Context(topdir, auth=dict(type="ssh", key="/tmp/id.rsa", 
                                username="someone_else"))
    generic_clone = commands.clone(context, ["ssh://hg.mozilla.org/bar"])
    result = dialect.convert(generic_clone)
    assert str(result) == "clone -e ssh -i /tmp/id.rsa -o StrictHostKeyChecking=no ssh://someone_else@hg.mozilla.org/bar bar"
    
def test_clone_command_http_password_auth():
    context = main.Context(topdir, auth=dict(type="password", 
                        username="supercooluser", password="hithere"))
    generic_clone = commands.clone(context, ["http://hg.mozilla.org/bar"])
    result = dialect.convert(generic_clone)
    assert str(result) == "clone http://supercooluser:hithere@hg.mozilla.org/bar bar"
    
def test_push_command_ssh_username_auth():
    context = main.Context(topdir, auth=dict(type="ssh", key="/tmp/id.rsa", 
                                username="someone_else"))
    generic_push = commands.push(context, ["ssh://hg.mozilla.org/bar"])
    result = dialect.convert(generic_push)
    assert result.writes_remote
    assert result.reads_remote
    assert str(result) == "push -e ssh -i /tmp/id.rsa -o StrictHostKeyChecking=no ssh://someone_else@hg.mozilla.org/bar"

def test_update_command():
    generic_update = commands.update(context, [])
    update = hg.update(generic_update)
    assert update.reads_remote
    assert not update.writes_remote
    assert update.get_command_line() == ["hg", "fetch"]
    
def test_resolved_command():
    myfile = path(topdir) / "myfile"
    myfile.write_bytes("test data")
    try:
        generic_resolved = commands.resolved(context, ["myfile"])
        resolved = hg.resolved(generic_resolved)
    finally:
        myfile.unlink()
        
    assert not resolved.reads_remote
    assert not resolved.writes_remote
    assert resolved.get_command_line() == ["hg", "resolve", "-m", "myfile"]
    
def test_resolved_command_no_targets():
    myfile = path(topdir) / "myfile"
    myfile.write_bytes("test data")
    try:
        generic_resolved = commands.resolved(context, [])
        resolved = hg.resolved(generic_resolved)
    finally:
        myfile.unlink()
        
    assert not resolved.reads_remote
    assert not resolved.writes_remote
    assert resolved.get_command_line() == ["hg", "resolve", "-m", "-a"]
    