import os, subprocess, sys; from distutils import command, core, dist; BUILT = DEBUG = 0
def quicktest(): DISTRIBUTION.run_command("build"); system("python3.0 -c 'import pseudomethod; pseudomethod.quicktest()'")
def system(cmd): print( cmd ); return subprocess.check_call(cmd, shell = True)
class Info(object):
  def __init__(self, fpath): s = open(fpath).read(); s = s[:s.find("\n## end setup info")]; exec(s, self.__dict__); global README; README = self.__doc__



## dependency check
print( """
  pseudomethod requires:
    python3.0
  make sure its are installed before running setup
""")

def missing_dependency(name, url):
  raise Exception("""

  pseudomethod requires %s
  please download & install %s from:

  %s

  or another source first
""" % (name, name, url))

if sys.version_info[0] is not 3:
  if not ("register" in sys.argv or "upload" in sys.argv): ## bypass version check for "register" & "upload"
    ## missing_dependency("Python-3.0", "http://www.python.org/download/releases/3.0/")
    raise Exception("setup must b run w/ python3.0")
  else: x = list(sys.version_info); x[0] = 3; sys.version_info = x
import pseudomethod



## init
MANIFEST = """
MANIFEST
README
setup.py
pseudomethod.py
pseudomethod_test.py
"""



## developer stuff
class dev(core.Command):
  description = "setup commands for developer"
  user_options = [
    ("doc", None, "print doc"),
    ("pkginfo", None, "create pkg-info"),
    ("sdist", None, "custom sdist"),
    ("quicktest", None, "run quick tests"),
    ]
  def initialize_options(self):
    for x in self.user_options: setattr(self, x[0], x[1])
  def finalize_options(self): pass
  def run(self):
    quicktest()
    if self.doc: system("python3.0 -c 'import pseudomethod; help(pseudomethod)'")
    elif self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))
    elif self.sdist:
      DISTRIBUTION.run_command("sdist")
      cmd_obj = DISTRIBUTION.get_command_obj("sdist")
      src = cmd_obj.archive_files[0]; dst = "index_html/%s" % os.path.basename(src); system("cp -a %s %s" % (src, dst))
    elif self.quicktest: pass



## custom Distribution class
class Distribution(dist.Distribution):
  built = None
  ## def __init__(self, *args, **kwds):
    ## dist.Distribution.__init__(self, *args, **kwds); global DISTRIBUTION; DISTRIBUTION = self
    ## self.cmdclass["dev"] = dev
    ## self.metadata.long_description = pseudomethod.__doc__
  def __init__(self, *args, **kwds):
    dist.Distribution.__init__(self, *args, **kwds); global DISTRIBUTION; DISTRIBUTION = self; self.cmdclass["dev"] = dev
    info = Info("pseudomethod.py")
    self.metadata.__dict__.update({
      'author':	info.__author__,
      'author_email':	info.__author_email__,
      'description':	info.__description__,
      'download_url':	info.__download_url__,
      'keywords':	info.__keywords__,
      'license':	info.__license__,
      'long_description':	info.__doc__,
      'maintainer':	info.__maintainer__,
      'maintainer_email':	info.__maintainer_email__,
      'name':	info.__name__,
      'obsoletes':	info.__obsoletes__,
      'platforms':	info.__platforms__,
      'provides':	info.__provides__,
      'requires':	info.__requires__,
      'url':	info.__url__,
      'version':	info.__version__,
      })
  def run_command(self, command):
    cmd_obj = self.get_command_obj(command)
    def null(*args, **kwds): pass
    cmd_obj.byte_compile = null ## disable byte compiling
    dist.Distribution.run_command(self, command)
    if 0 and DEBUG: ## print debug info
      print( "DEBUG command = %s, cmd_obj = %s, sub_cmd = %s" % (command, cmd_obj, cmd_obj.get_sub_commands()) )
      if 1 and command in "sdist".split(" "):
        print( "DEBUG %s attr" % command )
        for k, x in sorted(cmd_obj.__dict__.items()): print( "\t", k, "\t", x )
    if command == "build":
      force = cmd_obj.force
      open("MANIFEST", "w").write(MANIFEST)
      open("README", "w").write(self.metadata.long_description)



  ## def get_command_class (self, command):
    ## if command == "register": return distutils_custom.register
    ## elif command == "upload": return distutils_custom.upload
    ## return dist.Distribution.get_command_class(self, command)



## main loop
core.setup(
  ## name = "pseudomethod",
  ## version = "2008.11.22",
  ## author = "kai zhu",
  ## author_email = "kaizhu@ugcs.caltech.edu",
  ## url = "http://www-rcf.usc.edu/~kaizhu/work/pseudomethod",
  ## description = """
## call almost any function on-the-fly as a "method" for any class or object
## """,
  ## py_modules = ["pseudomethod", "pseudomethod_test"],
  ## requires = [],
  ## distclass = Distribution, ## custom Distribution class
  ## registerclass = Distribution, ## custom Distribution class
  distclass = Distribution, ## custom dist class
  py_modules = ["pseudomethod", "pseudomethod_test"],
  classifiers = [
  "Development Status :: 3 - Alpha",
  ## "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Intended Audience :: Education",
  "Intended Audience :: End Users/Desktop",
  ## "Intended Audience :: Science/Research",
  "Natural Language :: English",
  "Operating System :: POSIX",
  "Operating System :: POSIX :: Linux",
  "Operating System :: Unix",
  "Programming Language :: C",
  "Programming Language :: Python",
  ## "Programming Language :: Python :: 2.6",
  ## "Programming Language :: Python :: 2.7",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.0",
  "Programming Language :: Python :: 3.1",
  "Topic :: Education",
  "Topic :: Education :: Testing",
  ## "Topic :: Scientific/Engineering",
  "Topic :: Software Development",
  "Topic :: Software Development :: Assemblers",
  "Topic :: Software Development :: Build Tools",
  "Topic :: Software Development :: Code Generators",
  "Topic :: Software Development :: Compilers",
  "Topic :: Software Development :: Disassemblers",
  "Topic :: Software Development :: Interpreters",
  ## "Topic :: Software Development :: Libraries",
  ## "Topic :: Software Development :: Libraries :: Python Modules",
  "Topic :: Software Development :: Pre-processors",
  "Topic :: Software Development :: Testing",
  "Topic :: System :: Emulators",
  ## "Topic :: System :: Shells",
  ## "Topic :: System :: System Shells",
  "Topic :: Utilities",
  ## "Topic :: Multimedia :: Graphics",
  ## "Topic :: Multimedia :: Graphics :: Graphics Conversion",
  ## "Topic :: Multimedia :: Graphics :: Viewers",
  ],
)
