"""Implements the Subversion dialect."""
import os

from uvc.commands import UVCError, DialectCommand

class SVNError(UVCError):
    """Subversion-specific errors"""
    pass

class SVNCommand(DialectCommand):
    dialect_name = "svn"
    
class clone(SVNCommand):
    reads_remote = True
    writes_remote = False
    
    def command_parts(self):
        parts = super(clone, self).command_parts()
        parts[0] = "checkout"
        return parts

checkout = clone

class commit(SVNCommand):
    reads_remote = False
    writes_remote = False
    
class diff(SVNCommand):
    reads_remote = False
    writes_remote = False

class SVNDialect(object):
    def convert(self, command_object):
        """Converts to an SVN-specific command."""
        local_command = self.get_dialect_command_class(command_object.__class__.__name__)
        return local_command(command_object)
        
    def convert_class(self, command_class):
        """Converts a generic command class to its equivalent."""
        local_command_class = self.get_dialect_command_class(command_class.__name__)
        return local_command_class
        
    def get_dialect_command_class(self, command_name):
        """Looks up an svn-specific command class."""
        local_command = globals().get(command_name)
        if not local_command:
            raise SVNError("Command cannot be converted to svn: %s" 
                            % (command_name))
        return local_command
    
    def get_dialect_command(self, context, command_name, args):
        """Looks up an svn-specific command."""
        local_command = self.get_dialect_command_class(command_name, args)
        return local_command.from_args(context, args)
    
    def cwd_is_this_dialect(self):
        """Returns 1 if the .svn directory is here, 2 otherwise. svn
        plants directories everywhere, so if it's not in the current
        directory, it's not an svn project."""
        if os.path.isdir(".svn"):
            return 1
        return 2
    