VERSION = "2009.11.16.py3k.cpp"
MANIFEST = """setup.py
README.pseudomethod
pseudomethod/_pseudomethod.cpp
pseudomethod/__init__.py
pseudomethod/lucida06x10.bmp
pseudomethod/main.py
pseudomethod/mario.png"""
README = open("README.pseudomethod").read()
DESCRIPTION = README.split("\n")[0]
README = """REQUIRES PYTHON3.1
test usage: python3.1 setup.py build dev --quicktest
""" + README
README += """
RECENT CHANGEs:
20091116 - package integrated
20081219
- tobias rodaebel points out ".." is used in relative imports as well.
  fixed pseudomethod 2 b compatible w/ this
- removed limitation where parser disallows use of keyword "__pseudomethod__"
  in scripts
"""

import os, shutil, sys, traceback; from distutils import command, core, dist, log
def closure(*args, **kwds): return lambda fnc: fnc(*args, **kwds)
def quicktest(): system("python3.1 -c 'import pseudomethod; pseudomethod.quicktest()'")
def system(cmd): print( cmd ); import subprocess; return subprocess.check_call(cmd, shell = True)

class dev(core.Command):
  description = "developer stuff"
  user_options = [
    ("alias=", None, "alias package"),
    ("doc", None, "print doc"),
    ("pkginfo", None, "create pkg-info"),
    ("quicktest", None, "run quick tests"),
    ("sdist-test=", None, "test sdist package"),
    ("uninstall=", None, "uninstall"),
    ]
  def initialize_options(self):
    for aa in self.user_options: setattr(self, aa[0].replace("=", "").replace("-", "_"), aa[1])
  def finalize_options(self): pass
  def run(self):
    if self.alias:
      for aa in MANIFEST.split("\n"):
        if aa == "setup.py": bb = aa; aa = "_setup.py"
        else: bb = aa.replace("pseudomethod", self.alias)
        if "README" not in aa: print( "aliasing %s -> %s" % (aa, bb) ); ss = open(aa, "rb").read().replace(b"pseudomethod", self.alias.encode("latin")); open(bb, "wb").write(ss)
      system("python3.1 setup.py %s" % " ".join(sys.argv[3:]))
      exit()
    if self.doc: system("python3.1 -c 'import pseudomethod; help(pseudomethod)'")
    if self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))
    if self.quicktest: quicktest()
    if self.sdist_test:
      system("python3.1 setup.py sdist; rm -r test; mkdir test"); os.chdir("test"); print()
      fpath = "pseudomethod-%s" % VERSION; print(fpath); system("tar -xzf ../index_html/sdist/%s.tar.gz; lndir %s;" % (fpath, fpath)); print()
      try: system("python3.1 setup.py dev --uninstall=%s", self.sdist_test); print()
      except: pass
      system("python3.1 setup.py install --prefix=%s" % self.sdist_test); print()
      system("python3.1 -c 'import pseudomethod; pseudomethod.quicktest()'"); print()

    if self.uninstall:
      cmd_obj = DISTRIBUTION.get_command_obj("install"); cmd_obj.prefix = self.uninstall; cmd_obj.ensure_finalized()
      system("rm -r %s/pseudomethod" % cmd_obj.install_lib)

## custom Distribution class
class Distribution(dist.Distribution):
  def __init__(self, *args, **kwds): dist.Distribution.__init__(self, *args, **kwds); self.cmdclass["dev"] = dev; global DISTRIBUTION; DISTRIBUTION = self;

  def run_command(self, command):
    if self.have_run.get(command): return # Already been here, done that? then return silently.
    log.info("\nrunning %s", command); cmd_obj = self.get_command_obj(command); cmd_obj.ensure_finalized() ## get cmd
    if 0: print( "DEBUG %s\tcmd_obj=%s\tsub_cmd=%s" % (command, cmd_obj, cmd_obj.get_sub_commands()) ) ## DEBUG

    ## pre hack
    if 1: cmd_obj.byte_compile = lambda *args, **kwds: None ## disable byte compile
    if command == "build":
      print( """pseudomethod requires:
      Python 3.1
      make sure these packages are installed before building""" )
      if sys.version_info[:2] != (3, 1): raise Exception("pseudomethod requires Python 3.1")
    if command == "build_ext":
      def closure(self = cmd_obj, build_extension = cmd_obj.build_extension):
        def fnc(*args):
          self.compiler.compiler_so += "-O0".split(" ") ## add compiler flag
          for aa in "-Wstrict-prototypes -O3".split(" "): ## remove compiler flag
            if aa in self.compiler.compiler_so: self.compiler.compiler_so.remove(aa)
          return build_extension(*args)
        self.build_extension = fnc
      closure()
    if command == "sdist": open("MANIFEST", "w").write(MANIFEST)

    cmd_obj.run(); self.have_run[command] = 1 ## run cmd

    ## post hack
    if command == "build_ext": system("cp %s/pseudomethod/_pseudomethod.so pseudomethod" % cmd_obj.build_lib) ## copy built library
    if command == "sdist":
      if os.path.exists("index_html"): system("cp %s index_html/sdist/%s" % (cmd_obj.archive_files[0], os.path.basename(cmd_obj.archive_files[0]))) ## archive sdist

core.setup(
  distclass = Distribution,
  name = "pseudomethod",
  version = VERSION,
  author = "kai zhu",
  author_email = "kaizhu256@gmail.com",
  url = "http://pypi.python.org/pypi/pseudomethod",
  description = DESCRIPTION,
  long_description = README,
  packages = ["pseudomethod"],
  ext_modules = [core.Extension("pseudomethod._pseudomethod", sources = ["pseudomethod/_pseudomethod.cpp"], libraries = ["png"])],
  data_files = [("lib/python3.1/site-packages/pseudomethod", ["pseudomethod/mario.png"])],

  classifiers = [
  "Development Status :: 3 - Alpha",
  # "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Intended Audience :: End Users/Desktop",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: GNU General Public License (GPL)",
  "Natural Language :: English",
  # "Operating System :: POSIX",
  "Operating System :: POSIX :: Linux",
  # "Operating System :: Unix",
  "Programming Language :: C",
  "Programming Language :: Python",
  "Programming Language :: Python :: 3.1",
  "Topic :: Multimedia",
  "Topic :: Multimedia :: Graphics",
  # "Topic :: Multimedia :: Graphics :: 3D Modeling",
  # "Topic :: Multimedia :: Graphics :: 3D Rendering",
  # "Topic :: Multimedia :: Graphics :: Capture",
  # "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
  # "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
  # "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
  # "Topic :: Multimedia :: Graphics :: Editors",
  # "Topic :: Multimedia :: Graphics :: Editors :: Raster-Based",
  # "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
  "Topic :: Multimedia :: Graphics :: Graphics Conversion",
  # "Topic :: Multimedia :: Graphics :: Presentation",
  # "Topic :: Multimedia :: Graphics :: Viewers",
  # "Topic :: Scientific/Engineering",
  # "Topic :: Scientific/Engineering :: Artificial Intelligence",
  # "Topic :: Scientific/Engineering :: Astronomy",
  # "Topic :: Scientific/Engineering :: Atmospheric Science",
  # "Topic :: Scientific/Engineering :: Bio-Informatics",
  # "Topic :: Scientific/Engineering :: Chemistry",
  # "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
  # "Topic :: Scientific/Engineering :: GIS",
  # "Topic :: Scientific/Engineering :: Human Machine Interfaces",
  "Topic :: Scientific/Engineering :: Image Recognition",
  # "Topic :: Scientific/Engineering :: Information Analysis",
  # "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
  "Topic :: Scientific/Engineering :: Mathematics",
  # "Topic :: Scientific/Engineering :: Medical Science Apps.",
  # "Topic :: Scientific/Engineering :: Physics",
  "Topic :: Scientific/Engineering :: Visualization",
  # "Topic :: Software Development",
  "Topic :: Software Development :: Libraries",
  "Topic :: Software Development :: Libraries :: Python Modules",
  # "Topic :: System :: Emulators",
  # "Topic :: System :: Shells",
  # "Topic :: System :: System Shells",
  # "Topic :: Utilities",
  ])
