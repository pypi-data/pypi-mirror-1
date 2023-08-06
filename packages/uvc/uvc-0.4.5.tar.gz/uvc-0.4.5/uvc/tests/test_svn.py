import os
from cStringIO import StringIO

import py

from uvc.path import path
from uvc import commands, svn, main, exc, util
from uvc.tests.util import test_context
from uvc.tests.mock import patch

dialect = svn.SVNDialect()

topdir = path(__file__).dirname().abspath() / ".." / ".." / "testfiles"
testfile = topdir / "foo.txt"
testfile2 = topdir / "other.txt"
testdir = topdir / "adirectory"

context = None

def setup_module(module):
    global context
    if not os.path.exists(topdir):
        os.mkdir(topdir)
    context = main.Context(topdir)
    testfile.write_bytes("hi")
    testfile2.write_bytes("hello")
    testdir.mkdir()

def teardown_module(module):
    testfile.unlink()
    testdir.rmdir()
    testfile2.unlink()
    
def test_clone_command_conversion():
    generic_clone = commands.clone(context, ["http://paver.googlecode.com/svn/trunk/", 
                                    "paver"])
    svn_clone = svn.clone(generic_clone)
    svn_clone_command = " ".join(svn_clone.get_command_line())
    assert svn_clone_command == "svn --non-interactive checkout http://paver.googlecode.com/svn/trunk/ paver"
    
def test_convert_function():
    generic_clone = commands.clone(context, ["http://paver.googlecode.com/svn/trunk/", 
                                    "paver"])
    svn_clone = dialect.convert(generic_clone)
    svn_clone_command = " ".join(svn_clone.get_command_line())
    assert svn_clone_command == "svn --non-interactive checkout http://paver.googlecode.com/svn/trunk/ paver"
    
def test_convert_unknown_command():
    class Foo(object):
        pass
    
    try:
        result = dialect.convert(Foo())
        assert False, "expected SVNError for unknown command"
    except svn.SVNError:
        pass

def test_commit_command():
    test_context.reset()
    commit_file = path(test_context.working_dir) / ".svn_commit_messages"
    if commit_file.exists():
        commit_file.unlink()
    
    generic_commit = commands.commit(test_context, 
                ["-m", "test message", "foo", "bar"])
    result = dialect.convert(generic_commit)
    assert result.get_command_line() == None
    result.generate_output(test_context)
    output = test_context.output.getvalue()
    assert output == "Commit message saved. Don't forget to push to save to the remote repository!"
    
    assert commit_file.exists(), "Expected commit file at " + commit_file
    assert commit_file.text() == "test message\n\n"
    
def test_push_command_before_commit():
    test_context.reset()
    commit_file = path(test_context.working_dir) / ".svn_commit_messages"
    if commit_file.exists():
        commit_file.unlink()
    
    generic_push = commands.push(test_context, [])
    result = dialect.convert(generic_push)
    assert result.get_command_line() == None
    
    result.generate_output(test_context)
    output = test_context.output.getvalue()
    assert output == "Nothing to push. Run commit first."
    
def test_push_after_commit():
    commit_file = path(test_context.working_dir) / ".svn_commit_messages"
    if commit_file.exists():
        commit_file.unlink()
    
    generic_commit = commands.commit(test_context, 
                ["-m", "test message1", "foo", "bar"])
    result = dialect.convert(generic_commit)
    result.generate_output(context)
    
    generic_commit = commands.commit(test_context, 
                ["-m", "test message2", "foo", "bar"])
    result = dialect.convert(generic_commit)
    result.generate_output(context)
    
    generic_push = commands.push(test_context, [])
    result = dialect.convert(generic_push)
    assert result.get_command_line() == ["svn", 
        "--non-interactive", "commit", "-m", 
        "test message1\n\ntest message2\n\n"]
    
def test_diff_command():
    generic_diff = commands.diff(context, [])
    result = dialect.convert(generic_diff)
    assert str(result) == "diff"
    
@patch("uvc.util.run_in_directory")
def test_add_all_files(rid):
    generic_add = commands.add(test_context, [])
    result = dialect.convert(generic_add)
    stdout = StringIO("""A      foo.txt
?      bar.txt
A      baz.txt
""")
    rid.return_value = [0, stdout]
    assert result.get_command_line() == ["svn", "add", "bar.txt"]
    assert rid.called
    
def test_revert_all_files():
    generic_revert = commands.revert(context, [])
    result = dialect.convert(generic_revert)
    assert result.get_command_line() == ["svn", "revert", 
        "-R", "adirectory", "foo.txt", "other.txt"]
    
@patch("uvc.util.run_in_directory")
def test_resolve_all_files(rid):
    stdout = StringIO("""A      foo.txt
C      bar.txt
A      baz.txt
""")
    rid.return_value = [0, stdout]
    generic_resolved = commands.resolved(context, [])
    result = dialect.convert(generic_resolved)
    assert result.get_command_line() == ["svn", "resolve", 
        "--accept", "working", "bar.txt"]
    assert rid.called
    
class T(object):
    def __init__(self, command, is_help=False, 
                error=False, file_error=False):
        self.command = command
        self.error = error
        self.file_error = file_error
        self.is_help = is_help
        
    @property
    def args(self):
        return ["svn"] + self.command.split(" ")
        
    def __repr__(self):
        return "%s (is_help=%s, error=%s, file_error=%s)" % (
            self.command, self.is_help, self.error, self.file_error)
        
def test_svn_native_commands():
    tests = [
        T("revert foo.txt"),
        T("revert -R foo.txt"),
        T("revert --foo", error=True),
        T("revert -h", is_help=True),
        T("revert --help", is_help=True),
        T("revert bar.txt", file_error=True),
        T("revert --depth foo foo.txt", error=True),
        T("revert --depth=infinity foo.txt"),
        T("copy foo.txt bar.txt"),
        T("copy", error=True),
        T("copy foo.txt", error=True),
        T("copy bar.txt foo.txt", file_error=True),
        T("copy foo.txt adirectory"),
        T("copy other.txt adirectory foo.txt", file_error=True),
        T("copy foo.txt other.txt adirectory"),
        T("copy http://blazingthings.com/awesome/ http://blazingthings.com/awesome/a2"),
        T("copy file://foo/bar/baz .", file_error=True),
        T("copy http://www.blazingthings.com/awesome/@658 ."),
        T("copy http://www.blazingthings.com/awesome/@658 newdir"),
        T("move foo.txt bar.txt"),
        T("move http://www.blazingthings.com/awesome/blah http://www.blazingthings.com/awesome/bar"),
        T("move foo http://www.blazingthings.com/awesome/bar", file_error=True),
        T("mkdir testdir"),
        T("merge http://foobar.baz/branch1 http://foobar.baz/branch2 ."),
        T("merge http://foobar.baz/branch1 http://foobar.baz/branch2"),
        T("merge -c 10 http://foobar.baz/branch1"),
        T("merge http://foobar.baz/branch1 .", error=True),
        T("merge -c 10 http://foobar.baz/branch1 http://foobar.baz/branch2 .",
            error=True),
        T("merge -c 10 http://foobar.baz/branch1 http://foobar.baz/branch2",
            error=True),
        T("merge branch1 http://foobar.baz/branch1", error=True),
        T("switch http://foobar.baz/branch1"),
        T("switch http://foobar.baz/branch1 ."),
        T("switch http://foobar.baz/branch1 http://foobar.baz/branch2",
            file_error=True),
        T("switch .", file_error=True),
        T("switch --relocate http://foobar.baz/branch1 http://foobar.baz/branch2 ."),
        T("delete --keep-local foo.txt"),
        T("cat http://foobar.baz/file1"),
        T("cat http://foobar.baz/file1@329"),
        T("cat foo.txt@329"),
        T("cat file:///etc/passwd", file_error=True),
        T("propset foo.txt", error=True),
        T("propset svn:externals foo.txt", error=True),
        T("propset svn:externals http://blah foo.txt"),
        T("propset svn:externals http://blah DOESNTEXIST", 
            file_error=True),
        T("propget svn:ignore"),
        T("propget svn:mime-type foo.txt"),
        T("propget svn:mime-type DOESNOTEXIST", file_error=True),
        T("propdel svn:mime-type foo.txt"),
        T("propdel svn:mime-type DOESNOTEXIST", file_error=True),
        T("proplist"),
        T("proplist foo.txt"),
        T("proplist DOESNOTEXIST", file_error=True)
    ]
    
    def test_one(t):
        try:
            command = main.convert(context, t.args, None)
            if t.error or t.file_error:
                assert False, "For %s, expected error but didn't get one" % (t.args,)
        except svn.SVNError, e:
            if t.error:
                return
            else:
                assert False, "Unexpected Exception: %s" % e
        except exc.FileError, e:
            if t.file_error:
                return
            else:
                assert False, "Unexpected file error: %s" % e
                
        command_line = command.get_command_line()
        if command_line is None:
            return
        
        final_args = t.args
        final_args.insert(1, "--non-interactive")
        assert command_line == final_args
    
    for t in tests:
        yield test_one, t
    
def test_get_native_commands():
    commands = svn.get_native_commands()
    names = [command.name() for command in commands]
    assert "commit" in names
    
