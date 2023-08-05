__copyright__ = """"2006 by Tiago Cogumbreiro <cogumbreiro@users.sf.net>"""
__license__ = "LGPL <http://www.gnu.org/copyleft/lesser.txt>"

from distutils.core import setup, Extension, Command, DistutilsError
from distutils.command.build import build

import sys
import os.path
from codegen.pkgconfig import Pkg, call_getoutput
from codegen import names

class cross_compile(Command):
    description = ("cross compile the Python extension module to win32 "
                   "and generate the installer for it.")
    user_options = [
        ("scintilla-dir=", None, "Scintilla source directory."),
        ("build-scintilla", None, ("cross compiles the Scintilla library, "
                                   "and quits.")),
        ("build-only", None, "doesn't create the installer."),
        ("clean-only", "c", "cleans the generated files and quits."),
    ]
    
    boolean_options = ["build-scintilla", "build-only", "clean-only"]

    def initialize_options(self):
        self.scintilla_dir = None
        self.build_scintilla = False
        self.build_only = False
        self.clean_only = False
        
        get_dir = lambda foo: os.path.join(".", "scripts", foo)
        self._compile_scintilla = get_dir("cross-compile-scintilla")
        self._compile_pscyntilla = get_dir("cross-compile-pscyntilla")
        
    def finalize_options(self):
        if self.scintilla_dir is None:
            self.scintilla_dir = os.path.abspath(os.path.join(".", "scintilla"))

    def _make(self, make, *args):
        cmd = ["sh", make, self.scintilla_dir]
        cmd.extend(args)
        self.spawn(cmd)

    def scintilla_make(self, *args):
        self._make(self._compile_scintilla, *args)
        # Correct the 'scintilla.a' file
        get_file = lambda foo: os.path.join(self.scintilla_dir, "bin", foo)
        if os.path.exists(get_file("scintilla.a")):
            self.copy_file(get_file("scintilla.a"), get_file("libscintilla.a"))
        
    def pscyntilla_make(self, *args):
        self._make(self._compile_pscyntilla, *args)

    def create_installer(self):
        bdist_dir = self.get_finalized_command('bdist').bdist_base
        bdist_dir = os.path.join(bdist_dir, "cross-compile")
        lib_dir = os.path.join(bdist_dir, "PURELIB")
        self.mkpath(lib_dir)
        self.copy_file("src/scintilla.pyd", os.path.join(lib_dir, "scintilla.pyd"))
        args = self.distribution.get_option_dict("bdist_wininst")
        args["bdist_dir"] = ("command line", bdist_dir)
        args["skip_build"] = ("command line", True)
        self.run_command("bdist_wininst")

    def run(self):
        if self.clean_only:
            self.scintilla_make("clean")
            self.pscyntilla_make("clean")
            return

        self.scintilla_make()
        if self.build_scintilla:
            return
            
        self.pscyntilla_make()
        
        if self.build_only:
            return
        
        self.create_installer()


class Scintilla(Command):
    
    user_options = [
        ("scintilla-dir=", None, "Scintilla source directory."),
    ]
    
    def initialize_options(self):
        self.scintilla_dir = None
        
    def finalize_options(self):
        if self.scintilla_dir is None:
            self.scintilla_dir = os.path.abspath(os.path.join(".", "scintilla"))

    def get_scintilla_path(self, *args):
        return os.path.join(self.scintilla_dir, *args)
        

##############################################################################
class ScintillaMake(Scintilla):
    def make(self, *args):
        cmd = ["make"]
        cmd.extend(args)
        self.spawn(cmd)

    def run(self):
        cwd = os.getcwd()
        os.chdir(self.get_scintilla_path("gtk"))
        self._run()
        os.chdir(cwd)
        

class build_scintilla(ScintillaMake):

    description = "compile Scintilla library"

    def _run(self):
        self.make()
        # Correct the 'scintilla.a' file
        get_file = lambda foo: os.path.join(self.scintilla_dir, "bin", foo)
        if os.path.exists(get_file("scintilla.a")):
            self.copy_file(get_file("scintilla.a"), get_file("libscintilla.a"))


        

##############################################################################
class build_scintilla_ext(Scintilla):
    description = "compile Scintilla extesion module"
    
    def run(self):
        pkgs = tuple(Pkg.create_pkgs("gtk+-2.0", "glib-2.0", "pygtk-2.0",
                               "gthread-2.0"))
        
        for pkg in pkgs:
            if not pkg.check_version():
                raise DistutilsError("Package '%s' not found" % pkg)
        SOURCES = [
            'gtkscintilla2/gtkscintilla.c',
            'gtkscintilla2/gtkscintilladoc.cxx',
            'gtkscintilla2/sci_exts.c',
            'gtkscintilla2/scintillamodule.c',
            'gtkscintilla2/scintilla.c',
        ]
        inc_dirs = [
            self.get_scintilla_path('include'),
            self.get_scintilla_path('src'),
            "gtkscintilla2",
        ]

        ext = Extension('pyscintilla._scintilla',
                  define_macros = [("GTK",1), ("SCI_LEXER",1)],
                  libraries = ['stdc++', 'scintilla', 'stdc++'],
                  library_dirs = [self.get_scintilla_path("bin")],
                  include_dirs = inc_dirs,
                  sources = SOURCES)
        
        for pkg in pkgs:
            pkg.update_extension(ext)
        
        self.distribution.ext_modules = [ext]
        self.run_command("build_ext")


##############################################################################
class clean_scintilla(ScintillaMake):
    
    description = "cleans compiled Scintilla objects."
    
    def _run(self):
        self.make("clean")


##############################################################################
class GtkScintillaDep:
    
    sources = [
        "gtkscintilla2/gtkscintilla.c.in",
        "gtkscintilla2/gtkscintilla.h.in",
    ]
    
    targets = [
        "gtkscintilla2/gtkscintilla.c",
        "gtkscintilla2/gtkscintilla.h",
        # TODO: make sure this dies
        "gtkscintilla2/gtkscintilla.def",
    ]
    
    def __init__(self, parent):
        self.parent = parent
    
    def generate(self):
        # TODO: make this a function call
        cwd = os.getcwd()
        os.chdir("gtkscintilla2")
        self.parent.spawn([
            sys.executable, "scigen.py",
             "--scintilla-dir=%s" % self.parent.scintilla_dir])
        os.chdir(cwd)

class SciConstantsDep:
    # TODO: move this onto the build directory
    targets = ["pyscintilla/constants.py"]
    
    def __init__(self, cmd):
        self.sources = [os.path.join(cmd.scintilla_dir, "include",
                        "Scintilla.iface")]

    def generate(self):
        fd_in = open(self.sources[0])
        
        fd_out = open(self.targets[0], "w")
        names.generate_constants(fd_in, fd_out)
        fd_out.close()


class ScintillaDefsDep:
    sources = [
        "gtkscintilla2/gtkscintilla.h",
        "gtkscintilla2/gtkscintilladoc.h",
        "gtkscintilla2/sci_exts.h",
    ]
    
    targets = [
        "gtkscintilla2/scintilla.defs",
    ]
    
    def __init__(self, cmd):
        self.cmd = cmd

    def generate(self):
        # TODO: make this right
        h2def = "/usr/share/pygtk/2.0/codegen/h2def.py"
        cmd = [sys.executable, h2def]
        cmd.extend(self.sources)
        data = call_getoutput(cmd)
        
        fd = open(self.targets[0], "w")
        fd.write(data)
        fd.close()


class ScintillaModuleDep:
    sources = [
        "gtkscintilla2/scintilla.override",
        "gtkscintilla2/scintilla.defs",
    ]
    
    targets = [
        "gtkscintilla2/scintilla.c",
    ]
    
    def __init__(self, cmd):
        self.cmd = cmd

    def generate(self):
        # TODO: make this support universal paths
        pygtk_data = '/usr/share/pygtk/2.0'
        gdk_types_defs = os.path.join(pygtk_data, 'defs', 'gdk-types.defs')
        codegen = os.path.join(pygtk_data, 'codegen', 'codegen.py')
        cmd = [sys.executable, codegen, "--register", gdk_types_defs,
            "--override", "gtkscintilla2/scintilla.override",
            "--prefix", "pyscintilla", "gtkscintilla2/scintilla.defs"]
        
        txt = call_getoutput(cmd)
        fd = open(self.targets[0], 'w')
        fd.write(txt)
        fd.close()
        



class build_wrappers(Scintilla):
    
    description = "generates some files for Pscyntilla"
    
    def run(self):
        src_dependencies = (
            GtkScintillaDep,
            SciConstantsDep,
            ScintillaDefsDep,
            ScintillaModuleDep,
        )
        
        for dep_factory in src_dependencies:
            dep = dep_factory(self)
        
            most_recent_time = 0
            for filename in dep.sources:
                tm = os.path.getmtime(filename)
                if tm > most_recent_time:
                    most_recent_time = tm
                
            for filename in dep.targets:
                if not os.path.isfile(filename) or (os.path.getmtime(filename) < most_recent_time):
                    dep.generate()
                    break


    
def unlink(filename):
    try:
        os.unlink(filename)
    except os.error:
        pass

class clean_wrappers(Command):

    description = "cleans generated source files used in Pscyntilla"

    sources = (
        "pyscintilla/constants.py",
        "gtkscintilla2/gtkscintilla.c",
        "gtkscintilla2/gtkscintilla.h",
        "gtkscintilla2/gtkscintilla.def",
        "gtkscintilla2/scintilla.defs",
        "gtkscintilla2/scintilla.c",
    )
    
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        for file in self.sources:
            unlink(file)
            
        
build.sub_commands.insert(0, ('build_scintilla', lambda foo: True))
build.sub_commands.insert(1, ('build_wrappers', lambda foo: True))

if len(sys.argv) > 1 and sys.argv[1] == 'cross_compile':
    pass
else:
    build.sub_commands.insert(2, ('build_scintilla_ext', lambda foo: True))


setup (name = 'pscyntilla',
       version = '1.0',
       description = 'Python wrapper for Scintilla under GTK2',
       author = 'Tiago Cogumbreiro',
       author_email = 'cogumbreiro@users.sf.net',
       url = 'http://pida.berlios.de/',
       cmdclass = {
           'cross_compile': cross_compile,
           'build_scintilla': build_scintilla,
           'clean_scintilla': clean_scintilla,
           'build_wrappers': build_wrappers,
           'clean_wrappers': clean_wrappers,
           'build_scintilla_ext': build_scintilla_ext,
       },
       py_modules = ['pyscintilla.constants', 'pyscintilla.utils',
       # TODO: generate lexer info
       #'def_lexer_info',
       ],
       long_description = '''
Pscyntilla is a wrapper for the widget Scintilla (GTK+ version), a textual 
editing component.
''',
)

