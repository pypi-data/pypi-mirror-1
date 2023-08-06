"""Implements the Subversion VCS dialect."""
import os
import re
import glob
from urlparse import urlsplit

import argparse

from uvc.commands import UVCError, DialectCommand, BaseCommand
from uvc.exc import RepositoryAlreadyInitialized, FileError
from uvc import util

class SVNError(UVCError):
    """A Subversion-specific error."""
    pass

class _DisplayHelp(Exception):
    pass
    
class _HelpAction(argparse.Action):
    """A replacement for the default help action that raises
    the DisplayHelp exception. This is done to ensure that the
    help output is directed to the correct place and then
    execution is stopped."""
    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super(_HelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        raise _DisplayHelp()
    
class OptionParser(argparse.ArgumentParser):
    def __init__(self, *args, **kw):
        kw['add_help'] = False
        kw['formatter_class'] = argparse.RawDescriptionHelpFormatter
        
        super(OptionParser, self).__init__(*args, **kw)
        
    def exit(self, status=0, msg=""):
        raise SVNError(msg)

class SVNCommand(DialectCommand):
    dialect_name = "svn"

def _add_auth_info(auth, parts):
    parts.insert(0, "--non-interactive")
    if auth:
        if auth['type'] == "ssh":
            parts.insert(1, "--trust-server-cert")
            parts.insert(2, "")
            parts.insert(3, "")
            parts.insert(4, "")
            #parts.insert(1, "-e")
            # setting StrictHostKeyChecking to no is less than ideal...
            #parts.insert(2, "ssh -i %s -o StrictHostKeyChecking=no" % (auth['key']))
        elif auth['type'] == "password":
            parts.insert(1, "--username")
            parts.insert(2, auth['username'])
            parts.insert(3, "--password")
            parts.insert(4, auth['password'])
            parts.insert(5, '--no-auth-cache')
    

class AuthSVNCommand(SVNCommand):
    def add_auth_info(self, parts):
        _add_auth_info(self.generic.auth, parts)
    
    def command_parts(self):
        parts = super(AuthSVNCommand, self).command_parts()
        self.add_auth_info(parts)
        return parts

class clone(AuthSVNCommand):
    reads_remote = True
    writes_remote = False

    def command_parts(self):
        parts = ["checkout", self.source_without_auth, self.dest]
        
        self.add_auth_info(parts)
            
        return parts

checkout = clone

def _commit_log_file(working_dir):
    return working_dir / ".svn_commit_messages"

class commit(SVNCommand):
    reads_remote = False
    writes_remote = False
    
    def command_parts(self):
        return []
        
    def get_command_line(self):
        return None
        
    def generate_output(self, context):
        commit_log = _commit_log_file(self.generic.working_dir)
        if not commit_log.exists():
            content = self.generic.message + "\n\n"
        else:
            content = commit_log.text() + self.generic.message + "\n\n"
        commit_log.write_text(content)
        context.output.write("Commit message saved. Don't forget to push to save to the remote repository!")
        context.output.return_code = 0

class diff(SVNCommand):
    reads_remote = False
    writes_remote = False

class remove(SVNCommand):
    reads_remote = False
    writes_remote = False
    
    def command_parts(self):
        parts = super(remove, self).command_parts()
        # uvc's remove command implies "force"
        parts.insert(1, "--force")
        return parts

delete = remove

_status_line_mask = re.compile("^(.)..... (.*)$")

def _get_file_list(working_dir, status="?"):
    retcode, stdout = util.run_in_directory(working_dir,
        ["svn", "status"])
    status_lines = stdout.read().split("\n")
    file_list = []
    for line in status_lines:
        m = _status_line_mask.match(line)
        if not m:
            continue
        if m.group(1) == status:
            filename = m.group(2)
            if not filename.startswith("."):
                file_list.append(m.group(2))
    
    return file_list

class add(SVNCommand):
    reads_remote = False
    writes_remote = False

    def command_parts(self):
        parts = super(add, self).command_parts()
        if not self.targets:
            parts.extend(_get_file_list(self.generic.working_dir))
        return parts

class push(AuthSVNCommand):
    reads_remote = True
    writes_remote = True
    
    def get_command_line(self):
        commit_log = _commit_log_file(self.generic.working_dir)
        if not commit_log.exists():
            return None
        return super(push, self).get_command_line()
        
    def generate_output(self, context):
        # only called if the commit_log doesn't exist
        output = context.output
        output.write("Nothing to push. Run commit first.")
        output.return_code = 1
    
    def command_parts(self):
        parts = []
        self.add_auth_info(parts)
        parts.append("commit")
        parts.append("-m")
        commit_log = _commit_log_file(self.generic.working_dir)
        parts.append(commit_log.text())
        return parts
        
    def command_successful(self):
        commit_log = _commit_log_file(self.generic.working_dir)
        commit_log.unlink()

class update(AuthSVNCommand):
    reads_remote = True
    writes_remote = False

    def command_parts(self):
        parts = ["update"]
        self.add_auth_info(parts)
        return parts

class resolved(SVNCommand):
   reads_remote = False
   writes_remote = False

   def command_parts(self):
       parts = super(resolved, self).command_parts()
       parts[0] = "resolve"
       parts.insert(1, "--accept")
       parts.insert(2, "working")
       if not self.targets:
           parts.extend(_get_file_list(self.generic.working_dir, status="C"))
       return parts

class status(SVNCommand):
    reads_remote = False
    writes_remote = False

class log(SVNCommand):
    reads_remote = False
    writes_remote = False

class cat(SVNCommand):
    reads_remote = False
    writes_remote = False

class revert(SVNCommand):
    reads_remote = False
    writes_remote = False

    def command_parts(self):
        parts = super(revert, self).command_parts()
        if not self.targets:
            parts.append("-R")
            pwd = os.getcwd()
            try:
                os.chdir(self.generic.working_dir)
                parts.extend(glob.glob("*"))
            finally:
                os.chdir(pwd)
        return parts
        
class SVNNativeCommand(object):
    existing_files = None
    aliases = []
    
    @classmethod
    def from_args(cls, context, initial_args):
        try:
            values = cls.parser.parse_args(initial_args)
            values.help = False
        except _DisplayHelp:
            values = argparse.Namespace(help=True)
            
        return cls(context, initial_args, values)
        
    @classmethod
    def name(cls):
        return cls.__name__[4:]
        
    def validate_args(self, context, values):
        """Validate the command line arguments passed in.
        
        Default is a no-op"""
        pass
        
    def __init__(self, context, initial_args, values):
        self.context = context
        self.auth = context.auth
        self.initial_args = initial_args
        self.values = values
        
        if values.help:
            return
            
        if self.existing_files:
            for var in self.existing_files:
                for f in getattr(self.values, var):
                    self.context.validate_exists(f)
                    
        self.validate_args(context, values)
        
        
    def command_parts(self):
        parts = [self.__class__.__name__[4:]] + self.initial_args
        _add_auth_info(self.auth, parts)
        return parts
        
    def get_command_line(self):
        if self.values.help:
            return None
        
        return ["svn"] + self.command_parts()
    
    def generate_output(self, context):
        self.parser.print_help(context.output)
        context.output.return_code = 0
    
def add_std(parser, cl=True, depth=True, files=True,
    recursive=False, quiet=True, xml=False, revision=False,
    verbose=False, force=False, parents=False, message=False, 
    accept=False):
    parser.add_argument("--help", "-h", action=_HelpAction,
                    default=argparse.SUPPRESS,
                    help="show this message and exit")
    
    if revision:
         parser.add_argument("--revision", "-r", help="""ARG (some commands also take ARG1:ARG2 range)
        A revision argument can be one of:
           NUMBER       revision number
           '{' DATE '}' revision at start of the date
           'HEAD'       latest in repository
           'BASE'       base rev of item's working copy
           'COMMITTED'  last commit at or before BASE
           'PREV'       revision just before COMMITTED""")
    
    if quiet:
        parser.add_argument("--quiet", "-q", action="store_true",
            help="print nothing, or only summary information")
    
    if verbose:
        parser.add_argument("--verbose", "-v", action="store_true",
            help="print extra information")

    if message:
        parser.add_argument("--message", "-m", 
            help="specify log message")
            
    if cl:
        parser.add_argument("--changelist", "--cl",
            help="operate only on members of changelist ARG")
            
    if depth:
        parser.add_argument("--depth", choices=["empty", "files",
                            "immediates", "infinity"],
                            help="limit operation by depth ARG ('empty', 'files', 'immediates', or 'infinity')")
                            
    if files:
        parser.add_argument("files", nargs='*',
            help="list of files to operate on")
    
    if recursive:
           parser.add_argument("--recursive", "-R", action='store_true',
               help="descend recursively, same as --depth=infinity")
    
    if xml:
        parser.add_argument("--xml", action="store_true",
            help="output in XML")
        parser.add_argument("--incremental", action="store_true",
            help="give output suitable for concatenation")
    
    if force:
        parser.add_argument("--force", action="store_true",
            help="force operation to run")
            
    if parents:
        parser.add_argument("--parents", action="store_true",
            help="make intermediate directories")
            
    if accept:
        parser.add_argument("--accept", 
            choices=('base', 'working', 'mine-full', 'theirs-full'),
            help="specify automatic conflict resolution source")
    
class SVN_revert(SVNNativeCommand):
    existing_files = ["files"]
    
    reads_remote = False
    writes_remote = False
    
    parser = OptionParser(prog="svn revert",
        description="revert: Restore pristine working copy file (undo most local edits).")
    add_std(parser, recursive=True)
        
class SVN_status(SVNNativeCommand):
    existing_files = ["files"]
    
    aliases = ["st", "stat"]
    
    reads_remote = False
    writes_remote = False
    
    parser = OptionParser(prog="svn status",
        description="""Print the status of working copy files and directories.

  With no args, print only locally modified items (no network access).
  With -q, print only summary information about locally modified items.
  With -u, add working revision and server out-of-date information.
  With -v, print full revision information on every item.

  The first six columns in the output are each one character wide:
    First column: Says if item was added, deleted, or otherwise changed
      ' ' no modifications
      'A' Added
      'C' Conflicted
      'D' Deleted
      'I' Ignored
      'M' Modified
      'R' Replaced
      'X' item is unversioned, but is used by an externals definition
      '?' item is not under version control
      '!' item is missing (removed by non-svn command) or incomplete
      '~' versioned item obstructed by some item of a different kind
    Second column: Modifications of a file's or directory's properties
      ' ' no modifications
      'C' Conflicted
      'M' Modified
    Third column: Whether the working copy directory is locked
      ' ' not locked
      'L' locked
    Fourth column: Scheduled commit will contain addition-with-history
      ' ' no history scheduled with commit
      '+' history scheduled with commit
    Fifth column: Whether the item is switched relative to its parent
      ' ' normal
      'S' switched
    Sixth column: Repository lock token
      (without -u)
      ' ' no lock token
      'K' lock token present
      (with -u)
      ' ' not locked in repository, no lock token
      'K' locked in repository, lock toKen present
      'O' locked in repository, lock token in some Other working copy
      'T' locked in repository, lock token present but sTolen
      'B' not locked in repository, lock token present but Broken

  The out-of-date information appears in the eighth column (with -u):
      '*' a newer revision exists on the server
      ' ' the working copy is up to date

  Remaining fields are variable width and delimited by spaces:
    The working revision (with -u or -v)
    The last committed revision and last committed author (with -v)
    The working copy path is always the final field, so it can
      include spaces.

  Example output:
    svn status wc
     M     wc/bar.c
    A  +   wc/qax.c

    svn status -u wc
     M           965    wc/bar.c
           *     965    wc/foo.c
    A  +         965    wc/qax.c
    Status against revision:   981

    svn status --show-updates --verbose wc
     M           965       938 kfogel       wc/bar.c
           *     965       922 sussman      wc/foo.c
    A  +         965       687 joe          wc/qax.c
                 965       687 joe          wc/zig.c
    Status against revision:   981
""")
    add_std(parser, xml=True, verbose=True)
    parser.add_argument("--show-updates", "-u", action="store_true",
        help="display update information")
    parser.add_argument("--ignore-externals", action="store_true",
        help="ignore externals definitions")

class SVN_add(SVNNativeCommand):
    existing_files = ["files"]
    
    reads_remote = False
    writes_remote = False
    
    parser = OptionParser(prog="svn add",
        description="""add: Put files and directories under version control, scheduling
them for addition to repository.  They will be added in next commit.""")
    add_std(parser)
    parser.add_argument("--force", action="store_true",
        help="force operation to run")
    parser.add_argument("--no-ignore", action="store_true",
        help="disregard default and svn:ignore property ignores")
    parser.add_argument("--auto-props", action="store_true",
        help="enable automatic properties")
    parser.add_argument("--no-auto-props", action="store_true",
        help="disable automatic properties")
    parser.add_argument("--parents", action="store_true",
        help="add intermediate parents")
        
class SVN_commit(SVNNativeCommand):
    existing_files = ["files"]
    
    aliases = ["ci"]
    
    reads_remote = True
    writes_remote = True
    
    parser = OptionParser(prog="svn commit",
        description="commit (ci): Send changes from your working copy to the repository.")
    add_std(parser, message=True)
    parser.add_argument("--no-unlock", action="store_true",
        help="don't unlock the targets")
    parser.add_argument("--with-revprop",
        help="set revision property ARG in new revision using the name[=value] format")
    parser.add_argument("--keep-changelists", action="store_true",
        help="don't delete changelists after commit")
        
class SVN_cleanup(SVNNativeCommand):
    existing_files = ["files"]
    
    reads_remote = False
    writes_remote = False
    
    parser = OptionParser(prog="svn cleanup",
        description="cleanup: Recursively clean up the working copy, removing locks, resuming unfinished operations, etc.")
    add_std(parser, cl=False, quiet=False, depth=False)
    

class SVN_update(SVNNativeCommand):
    existing_files = ["files"]
    aliases = ["up"]
    
    reads_remote = True
    writes_remote = False
    
    parser = OptionParser(prog="svn update",
        description="""update (up): Bring changes from the repository into the working copy.
        
    If no revision given, bring working copy up-to-date with HEAD rev.
    Else synchronize working copy to revision given by -r.

    For each updated item a line will start with a character reporting the
    action taken.  These characters have the following meaning:

      A  Added
      D  Deleted
      U  Updated
      C  Conflict
      G  Merged
      E  Existed

    A character in the first column signifies an update to the actual file,
    while updates to the file's properties are shown in the second column.
    A 'B' in the third column signifies that the lock for the file has
    been broken or stolen.

    If --force is used, unversioned obstructing paths in the working
    copy do not automatically cause a failure if the update attempts to
    add the same path.  If the obstructing path is the same type (file
    or directory) as the corresponding path in the repository it becomes
    versioned but its contents are left 'as-is' in the working copy.
    This means that an obstructing directory's unversioned children may
    also obstruct and become versioned.  For files, any content differences
    between the obstruction and the repository are treated like a local
    modification to the working copy.  All properties from the repository
    are applied to the obstructing path.  Obstructing paths are reported
    in the first column with code 'E'.

    Use the --set-depth option to set a new working copy depth on the
    targets of this operation.  Currently, the depth of a working copy
    directory can only be increased (telescoped more deeply); you cannot
    make a directory more shallow.
""")
    add_std(parser, revision = True, force=True)
    parser.add_argument("--set-depth", choices=["empty", "files",
                          "immediates", "infinity"],
                        help="set new working copy depth")
    parser.add_argument("--ignore-externals", action="store_true",
        help="ignore externals definitions")
    parser.add_argument("--accept", 
        choices=('postpone', 'base', 'mine-full', 'theirs-full'),
        help="specify automatic conflict resolution action")

class SVN_info(SVNNativeCommand):
    existing_files = ["files"]
    
    reads_remote = False
    writes_remote = False
    
    parser = OptionParser(prog="svn info",
        description="""info: Display information about a local or remote item.

    Print information about the paths given.
""")
    add_std(parser, xml=True, revision=True)
    
class SVN_blame(SVNNativeCommand):
    existing_files = ["files"]
    
    aliases = ["praise", "annotate", "ann"]
    
    reads_remote = True
    writes_remote = False
    
    parser = OptionParser(prog="svn blame",
        description="""blame (praise, annotate, ann): Output the content of specified files with revision and author information in-line.""")
    add_std(parser, revision=True, xml=True, verbose=True, force=True)
    parser.add_argument("--use-merge-history", "-g", action="store_true",
        help="use/display additional information from merge history")
    
class SVN_log(SVNNativeCommand):
    existing_files = ["files"]
    
    reads_remote = True
    writes_remote = False
    
    parser = OptionParser(prog="svn log",
        description="""log: Show the log messages for a set of revision(s) and/or file(s).

  1. Print the log messages for a local PATH (default: '.').
     The default revision range is BASE:1.

  2. Print the log messages for the PATHs (default: '.') under URL.
     If specified, REV determines in which revision the URL is first
     looked up, and the default revision range is REV:1; otherwise,
     the URL is looked up in HEAD, and the default revision range is
     HEAD:1.

  With -v, also print all affected paths with each log message.
  With -q, don't print the log message body itself (note that this is
  compatible with -v).

  Each log message is printed just once, even if more than one of the
  affected paths for that revision were explicitly requested.  Logs
  follow copy history by default.  Use --stop-on-copy to disable this
  behavior, which can be useful for determining branchpoints.

  Examples:
    svn log
    svn log foo.c
""")
    add_std(parser, xml=True, revision=True, verbose=True)
    parser.add_argument("--use-merge-history", "-g", action="store_true",
        help="use/display additional information from merge history")
    parser.add_argument("--change", "-c",
        help="the change made by CHANGE")
    parser.add_argument("--stop-on-copy", action="store_true",
        help="do not cross copies while traversing history")
    parser.add_argument("--limit", "-l", type=int,
        help="maximum number of log entries")
    parser.add_argument("--with-all-revprops", action="store_true",
        help="retrieve all revision properties")
    parser.add_argument("--with-revprop",
        help="retrieve revision property WITH_REVPROP")
    
class SVN_resolve(SVNNativeCommand):
    existing_files = ["files"]
    
    reads_remote = False
    writes_remote = False
    
    parser = OptionParser(prog="svn resolve",
        description="Resolve conflicts on working copy files or directories. (--accept is required)")
    
    add_std(parser, accept=True)
        
def _check_url(url_string):
    if " " in url_string:
        raise FileError("Spaces not allowed in URLs: %s" % (url_string))
    url = urlsplit(url_string)
    scheme = url[0].lower()
    if scheme not in ["http", "https", "svn+ssh"]:
        raise FileError("Unsupported URL: %s" % (url_string))
    

def _validate_urls_and_files(context, values):
    if len(values.src) == 1 and values.src[0].find("://") > -1:
        _check_url(values.src[0])
        if values.dst.find("://") > -1:
            _check_url(values.dst)
        else:
            context.validate_new_file_or_existing_dir(values.dst)
        return
        
    for f in values.src:
        context.validate_existing_file(f)
    
    if len(values.src) == 1:
        context.validate_new_file_or_existing_dir(values.dst)
    else:
        context.validate_existing_directory(values.dst)
    

class SVN_copy(SVNNativeCommand):
    reads_remote = True
    writes_remote = True
    
    aliases = ["cp"]
    
    parser = OptionParser(prog="svn copy",
        description="""copy (cp): Duplicate something in working copy or repository, remembering history.

When copying multiple sources, they will be added as children of DST,
which must be a directory.

  SRC and DST can each be either a working copy (WC) path or URL:
    WC  -> WC:   copy and schedule for addition (with history)
    WC  -> URL:  immediately commit a copy of WC to URL
    URL -> WC:   check out URL into WC, schedule for addition
    URL -> URL:  complete server-side copy;  used to branch and tag
  All the SRCs must be of the same type.

WARNING: For compatibility with previous versions of Subversion,
copies performed using two working copy paths (WC -> WC) will not
contact the repository.  As such, they may not, by default, be able
to propagate merge tracking information from the source of the copy
to the destination.
""")
    add_std(parser, files=False, revision=True, depth=False,
            cl=False, parents=True, message=True)
    parser.add_argument("--with-revprop",
        help="set revision property WITH_REVPROP in new revision using the name[=value] format")
    
    parser.add_argument("src", nargs="+", help="source file(s) or URL")
    parser.add_argument("dst", help="destination file, url or directory")
    
    def validate_args(self, context, values):
        _validate_urls_and_files(context, values)
    
class SVN_move(SVNNativeCommand):
    reads_remote = True
    writes_remote = True
    
    aliases = ["mv", "rename", "ren"]
    
    parser = OptionParser(prog="svn move",
        description="""Move and/or rename something in working copy or repository.

When moving multiple sources, they will be added as children of DST,
which must be a directory.

  Note:  this subcommand is equivalent to a 'copy' and 'delete'.
  Note:  the --revision option has no use and is deprecated.

  SRC and DST can both be working copy (WC) paths or URLs:
    WC  -> WC:   move and schedule for addition (with history)
    URL -> URL:  complete server-side rename.
  All the SRCs must be of the same type.
""")

    add_std(parser, files=False, depth=False, force=True,
            cl=False, parents=True, message=True)
    parser.add_argument("--with-revprop",
        help="set revision property WITH_REVPROP in new revision using the name[=value] format")
    parser.add_argument("src", nargs="+", help="source file(s) or URL(s)")
    parser.add_argument("dst", help="destination file, url or directory")

    def validate_args(self, context, values):
        _validate_urls_and_files(context, values)
    
class SVN_mkdir(SVNNativeCommand):
    reads_remote = True
    writes_remote = True
    
    parser = OptionParser(prog="svn mkdir",
        description="""Create a new directory under version control.

  Create version controlled directories.

  1. Each directory specified by a working copy PATH is created locally
    and scheduled for addition upon the next commit.

  2. Each directory specified by a URL is created in the repository via
    an immediate commit.

  In both cases, all the intermediate directories must already exist,
  unless the --parents option is given.
""")

    add_std(parser, files=False, parents=True, depth=False,
        message=True)
    
    parser.add_argument("path", nargs="+", help="URL or file path to create")
    
    def validate_args(self, context, values):
        for v in values.path:
            if v.find("://") > -1:
                _check_url(v)
            else:
                context.validate_new_directory(v)
    
class SVN_merge(SVNNativeCommand):
    reads_remote = True
    writes_remote = True
    
    parser = OptionParser(prog="svn merge",
        description="""Apply the differences between two sources to a working copy path.

usage: 1. merge sourceURL1[@N] sourceURL2[@M] [WCPATH]
       2. merge sourceWCPATH1@N sourceWCPATH2@M [WCPATH]
       3. merge [-c M[,N...] | -r N:M ...] SOURCE[@REV] [WCPATH]

  1. In the first form, the source URLs are specified at revisions
     N and M.  These are the two sources to be compared.  The revisions
     default to HEAD if omitted.

  2. In the second form, the URLs corresponding to the source working
     copy paths define the sources to be compared.  The revisions must
     be specified.

  3. In the third form, SOURCE can be either a URL or a working copy
     path (in which case its corresponding URL is used).  SOURCE (in
     revision REV) is compared as it existed between revisions N and M
     for each revision range provided.  If REV is not specified, HEAD
     is assumed.  '-c M' is equivalent to '-r <M-1>:M', and '-c -M'
     does the reverse: '-r M:<M-1>'.  If no revision ranges are
     specified, the default range of 0:REV is used.  Multiple '-c'
     and/or '-r' instances may be specified, and mixing of forward
     and reverse ranges is allowed.

  WCPATH is the working copy path that will receive the changes.
  If WCPATH is omitted, a default value of '.' is assumed, unless
  the sources have identical basenames that match a file within '.':
  in which case, the differences will be applied to that file.

  NOTE:  Subversion will only record metadata to track the merge
  if the two sources are on the same line of history -- if the
  first source is an ancestor of the second, or vice-versa.  This is
  guaranteed to be the case when using the third form listed above.
  The --ignore-ancestry option overrides this, forcing Subversion to
  regard the sources as unrelated and not to track the merge.

""")
    add_std(parser, files=False, revision=True, force=True, accept=True)
    
    parser.add_argument("--change", "-c", 
        help="the change made by revision ARG (like -r ARG-1:ARG) If ARG is negative this is like -r ARG:ARG-1")
    parser.add_argument("--dry-run", action="store_true",
        help="try operation but make no changes")
    parser.add_argument("--record-only", action="store_true",
        help="mark revisions as merged (use with -r)")
    parser.add_argument("--ignore-ancestry", 
        help="ignore ancestry when calculating merges")
    parser.add_argument("--reintegrate", action="store_true",
        help="lump-merge all of source URL's unmerged changes")
    
    parser.add_argument("paths", nargs="+")
    
    def validate_args(self, context, values):
        if values.change:
            if len(values.paths) > 2:
                raise SVNError("When using -c, only SOURCE[@REV] [WCPATH] arguments are permitted.")
                
            if "://" in values.paths[0]:
                _check_url(values.paths[0])
            else:
                context.validate_exists(values.paths[0])
            
            if len(values.paths) == 2:
                if "://" in values.paths[1]:
                    raise SVNError("The final argument must be a working copy path.")
                context.validate_exists(values.paths[1])
        else:
            if len(values.paths) < 2 or len(values.paths) > 3:
                raise SVNError("Two sources and an optional working copy path are required")
            if "://" in values.paths[0]:
                if "://" not in values.paths[1]:
                    raise SVNError("Both sources must be URLs")
                _check_url(values.paths[0])
                _check_url(values.paths[1])
            else:
                if "://" in values.paths[1]:
                    raise SVNError("Both sources must be working copy paths")
                context.validate_exists(values.paths[0])
                context.validate_exists(values.paths[1])
            
            if len(values.paths) == 3:
                context.validate_exists(values.paths[2])
     
class SVN_switch(SVNNativeCommand):
    reads_remote = True
    writes_remote = True
    
    aliases = ["sw"]
    
    parser = OptionParser(prog="svn switch",
        description="""Update the working copy to a different URL.

usage: 1. switch URL[@PEGREV] [PATH]
       2. switch --relocate FROM TO [PATH...]

  1. Update the working copy to mirror a new URL within the repository.
     This behaviour is similar to 'svn update', and is the way to
     move a working copy to a branch or tag within the same repository.
     If specified, PEGREV determines in which revision the target is first
     looked up.

     If --force is used, unversioned obstructing paths in the working
     copy do not automatically cause a failure if the switch attempts to
     add the same path.  If the obstructing path is the same type (file
     or directory) as the corresponding path in the repository it becomes
     versioned but its contents are left 'as-is' in the working copy.
     This means that an obstructing directory's unversioned children may
     also obstruct and become versioned.  For files, any content differences
     between the obstruction and the repository are treated like a local
     modification to the working copy.  All properties from the repository
     are applied to the obstructing path.

     Use the --set-depth option to set a new working copy depth on the
     targets of this operation.  Currently, the depth of a working copy
     directory can only be increased (telescoped more deeply); you cannot
     make a directory more shallow.

  2. Rewrite working copy URL metadata to reflect a syntactic change only.
     This is used when repository's root URL changes (such as a scheme
     or hostname change) but your working copy still reflects the same
     directory within the same repository.
""")
    add_std(parser, files=False, cl=False, revision=True, force=True, accept=True)
    
    parser.add_argument("--relocate", metavar="FROM",
        help="relocate via URL-rewriting")
    parser.add_argument("--ignore-externals", action="store_true",
        help="ignore externals definitions")
    
    parser.add_argument("url")
    parser.add_argument("path", nargs="?")
    
    def validate_args(self, context, values):
        if values.relocate:
            _check_url(values.relocate)
        
        _check_url(values.url)
        
        if values.path:
            context.validate_existing_directory(values.path)

class SVN_delete(SVNNativeCommand):
    reads_remote = True
    writes_remote = True
    
    aliases = ["del", "remove", "rm"]
    
    parser = OptionParser(prog="svn delete",
        description="""Remove files and directories from version control.

usage: 1. delete PATH...
       2. delete URL...

  1. Each item specified by a PATH is scheduled for deletion upon
    the next commit.  Files, and directories that have not been
    committed, are immediately removed from the working copy
    unless the --keep-local option is given.
    PATHs that are, or contain, unversioned or modified items will
    not be removed unless the --force option is given.

  2. Each item specified by a URL is deleted from the repository
    via an immediate commit.
""")
    add_std(parser, files=False, force=True, message=True, cl=False, 
        depth=False)
    parser.add_argument("--keep-local", action="store_true",
        help="keep path in working copy")
    parser.add_argument("files", nargs="+", metavar="PATH_OR_URL")
    
    def validate_args(self, context, values):
        for v in values.files:
            if "://" in v:
                _check_url(v)
            else:
                context.validate_exists(v)
            
class SVN_cat(SVNNativeCommand):
    reads_remote = True
    writes_remote = False
    
    parser = OptionParser(prog="svn cat",
        description="""Output the content of specified files or URLs.

usage: cat TARGET[@REV]...

  If specified, REV determines in which revision the target is first
  looked up.
""")
    add_std(parser, revision=True, files=False, depth=False, quiet=False,
                cl=False)
    parser.add_argument("targets", nargs="+")
    
    def validate_args(self, context, values):
        for v in values.targets:
            if "://" in v:
                _check_url(v)
            else:
                context.validate_path(v)

class SVN_propset(SVNNativeCommand):
    existing_files = ["path"]
    
    reads_remote = False
    writes_remote = False
    
    aliases = ["pset", "ps"]
    
    parser = OptionParser(prog="svn propset",
        description="""Set the value of a property on files, dirs, or revisions.

  Note: svn recognizes the following special versioned properties
  but will store any arbitrary properties set:
    svn:ignore     - A newline separated list of file patterns to ignore.
    svn:keywords   - Keywords to be expanded.  Valid keywords are:
      URL, HeadURL             - The URL for the head version of the object.
      Author, LastChangedBy    - The last person to modify the file.
      Date, LastChangedDate    - The date/time the object was last modified.
      Rev, Revision,           - The last revision the object changed.
      LastChangedRevision
      Id                       - A compressed summary of the previous
                                   4 keywords.
    svn:executable - If present, make the file executable.  Use
      'svn propdel svn:executable PATH...' to clear.
    svn:eol-style  - One of 'native', 'LF', 'CR', 'CRLF'.
    svn:mime-type  - The mimetype of the file.  Used to determine
      whether to merge the file, and how to serve it from Apache.
      A mimetype beginning with 'text/' (or an absent mimetype) is
      treated as text.  Anything else is treated as binary.
    svn:externals  - A newline separated list of module specifiers,
      each of which consists of a relative directory path, optional
      revision flags and an URL.  The ordering of the three elements
      implements different behavior.  Subversion 1.4 and earlier only
      support the following formats and the URLs cannot have peg
      revisions:
        foo             http://example.com/repos/zig
        foo/bar -r 1234 http://example.com/repos/zag
      Subversion 1.5 and greater support the above formats and the
      following formats where the URLs may have peg revisions:
                http://example.com/repos/zig foo
        -r 1234 http://example.com/repos/zig foo/bar
      Relative URLs are supported in Subversion 1.5 and greater for
      all above formats and are indicated by starting the URL with one
      of the following strings
        ../  to the parent directory of the extracted external
        ^/   to the repository root
        //   to the scheme
        /    to the server root
      The ambiguous format 'relative_path relative_path' is taken as
      'relative_url relative_path' with peg revision support.
    svn:needs-lock - If present, indicates that the file should be locked
      before it is modified.  Makes the working copy file read-only
      when it is not locked.  Use 'svn propdel svn:needs-lock PATH...'
      to clear.

  The svn:keywords, svn:executable, svn:eol-style, svn:mime-type and
  svn:needs-lock properties cannot be set on a directory.  A non-recursive
  attempt will fail, and a recursive attempt will set the property
  only on the file children of the directory.
""")
    parser.add_argument("propname")
    parser.add_argument("propval")
    parser.add_argument("path", nargs="+")
    add_std(parser, force=True, files=False)
    
class SVN_propget(SVNNativeCommand):
    existing_files = ["files"]
    
    reads_remote = False
    writes_remote = False
    
    aliases = ["pg", "pget"]
    
    parser = OptionParser(prog="svn propget",
        description="""Print the value of a property on files, dirs, or revisions.

  By default, this subcommand will add an extra newline to the end
  of the property values so that the output looks pretty.  Also,
  whenever there are multiple paths involved, each property value
  is prefixed with the path with which it is associated.  Use
  the --strict option to disable these beautifications (useful,
  for example, when redirecting binary property values to a file).
""")
    parser.add_argument("propname")
    add_std(parser, revision=True, quiet=False)
    parser.add_argument("--strict", action="store_true",
        help="use strict semantics")
    parser.add_argument("--xml", action="store_true",
        help="output in XML")
    
class SVN_propdel(SVNNativeCommand):
    existing_files = ["files"]
    
    reads_remote = False
    writes_remote = False
    
    aliases = ["pdel", "pd"]
    
    parser = OptionParser(prog="svn propdel",
        description="""Remove a property from files, dirs, or revisions.
""")
    
    parser.add_argument("propname")
    add_std(parser)
    
class SVN_proplist(SVNNativeCommand):
    existing_files = ["files"]
    
    reads_remote = False
    writes_remote = False
    aliases = ["plist", "pl"]
    
    parser = OptionParser(prog="svn proplist",
        description="""List all properties on files, dirs, or revisions.""")
    
    add_std(parser, verbose=True)
    parser.add_argument("--xml", action="store_true",
        help="output in XML")
    
class SVN_help(SVNNativeCommand):
    reads_remote=False
    writes_remote=False
    
    parser = OptionParser(prog="svn help",
        description="""Most subcommands take file and/or directory arguments, recursing on the directories.  If no arguments are supplied to such a command, it recurses on the current directory (inclusive) by default.""")
    
_native_commands = None
    
def get_native_commands():
    """Return a set of the command classes for all of the native
    SVN commands that are supported."""
    
    global _native_commands
    
    if _native_commands is not None:
        return _native_commands
        
    commands = []
    for key, val in globals().items():
        if key.startswith("SVN_"):
            commands.append(val)
        
    _native_commands = commands
    return commands
    
for command in get_native_commands():
    g = globals()
    for alias in command.aliases:
        g["SVN_" + alias] = command
    
class SVNDialect(object):
    
    name = "svn"
    
    def convert(self, command_object):
        """Converts to an SVN-specific command."""
        local_command = self._get_command_class(command_object.__class__.__name__)
        return local_command(command_object)
        
    def convert_class(self, command_class):
        """Converts a generic command class to its equivalent."""
        local_command_class = self._get_command_class(command_class.__name__)
        return local_command_class
        
    def _get_command_class(self, command_name):
        """Looks up an svn-specific command class."""
        local_command = globals().get(command_name)
        if not local_command:
            raise SVNError("Command cannot be converted to svn: %s" 
                            % (command_name))
        return local_command
        
    def get_dialect_command_class(self, command_name):
        """Looks up an svn-specific command class"""
        return self._get_command_class("SVN_" + command_name)
    
    def cwd_is_this_dialect(self):
        """Returns 1 if the .svn directory is here, 2 otherwise. svn
        plants directories everywhere, so if it's not in the current
        directory, it's not an svn project."""
        if os.path.isdir(".svn"):
            return 1
        return 2
    