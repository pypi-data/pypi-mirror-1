__copyright__ = """"2006 by Tiago Cogumbreiro <cogumbreiro@users.sf.net>"""
__license__ = "LGPL <http://www.gnu.org/copyleft/lesser.txt>"

import subprocess

class NotSuccessfullError(StandardError):
    pass

# This functions were taken and adapted from pygtk distribution.
# 
def call_getoutput(*args, **kwargs):
    """Return output (stdout or stderr) of executing cmd in a shell."""
    kwargs["stdout"] = subprocess.PIPE
    proc = subprocess.Popen(*args, **kwargs)
    data = proc.communicate()[0]
    if proc.returncode != 0:
        raise NotSuccessfullError
    
    return data

class Pkg(object):
    def __init__(self, name, version=None, pkg_config="pkg-config", blacklist=()):
        self.name = name
        self.version = version
        self.pkg_config = pkg_config
        self.blacklist = blacklist

        self._init_parsers()
    
    def _init_parsers(self):
        self.libraries = []
        self.include_dirs = []
        self.library_dirs = []
        self.extra_link_args = []

        def parser(prefix, container, part):
            if part.startswith(prefix):
                container.append(part[len(prefix):])
                return True
            return False
        
        def create_parser(prefix, container):
            return lambda part: parser(prefix, container, part)
        
        self.parsers = (
            create_parser("-l", self.libraries),
            create_parser("-Wl", self.extra_link_args),
            create_parser("-I", self.include_dirs),
            create_parser("-L", self.library_dirs),
        )
    
    def _run(self, *args):
        cmd = [self.pkg_config]
        cmd.extend(args)
        return subprocess.call(cmd, stdout=subprocess.PIPE)
    
    def _run_output(self, *args):
        cmd = [self.pkg_config]
        cmd.extend(args)
        return [part[2:] for part in call_getoutput(cmd).strip().split()]
    
    def check_version(self):
        if self.version is None:
            args = (self.name, "--exists")
        else:
            args = (self.name, "--atleast-version=%s" % self.version)
            
        if self._run(*args) != 0:
            return False
        
        
        cmd = [self.pkg_config, self.name, "--cflags", "--libs"]
        for part in call_getoutput(cmd).strip().split():
            if part in self.blacklist:
                continue
            
            for parser in self.parsers:
                if parser(part):
                    continue
            
            
        return True

    def __str__(self):
        if self.version is not None:
            version = " >= %s" % self.version
        else:
            version = ""
        return "%s%s" % (self.name, version)

    def __repr__(self):
        return "<Pkg: %r>" % self.__str__()

    def update_extension(self, ext):
        ext.include_dirs.extend(self.include_dirs)
        ext.library_dirs.extend(self.library_dirs)
        ext.libraries.extend(self.libraries)
        ext.extra_link_args.extend(self.extra_link_args)

    @classmethod
    def create_pkgs(cls, *args):
        for arg in args:
            if isinstance(arg, tuple) or isinstance(arg, list):
                yield cls(*arg)
            else:
                yield cls(arg)