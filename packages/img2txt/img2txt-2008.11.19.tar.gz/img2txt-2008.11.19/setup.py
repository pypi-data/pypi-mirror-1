import distutils, imp, os, re, subprocess, sys; from distutils import command, core, dist

print """
  img2txt requires:
    py3to2
    Python Imaging Library
    scipy
  make sure these packages are installed before running setup
"""

def missing_dependency(name, url):
  raise Exception("""

  img2txt requires %s
  please download & install %s from:

  %s

  or another source first
""" % (name, name, url))

try: imp.find_module("py3to2")
except: missing_dependency("py3to2", "http://pypi.python.org/pypi/py3to2")
try: imp.find_module("PIL")
except: missing_dependency("Python Imaging Library", "http://www.pythonware.com/products/pil/")
try: imp.find_module("scipy")
except: missing_dependency("scipy", "http://www.scipy.org/Download")

BUILT = None
DEBUG = 1

def system(cmd): print cmd; return subprocess.check_call(cmd, shell = True)

class dev(core.Command):
  description = "setup commands for developer"
  user_options = [
    ("pkginfo", None, "create pkg-info"),
    ]
  def initialize_options(self):
    for x in self.user_options: setattr(self, x[0], x[1])
  def finalize_options(self): pass
  def run(self):
    if self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))

class Distribution(dist.Distribution):
  built = None
  def __init__(self, *args, **kwds):
    dist.Distribution.__init__(self, *args, **kwds); global DISTRIBUTION; DISTRIBUTION = self
    self.cmdclass["dev"] = dev
    self.metadata.long_description = open("README").read()
  def run_command(self, command):
    cmd_obj = self.get_command_obj(command)

    def null(*args, **kwds): pass
    cmd_obj.byte_compile = null # disable byte compiling

    dist.Distribution.run_command(self, command)

    if 0 and DEBUG:
      print "DEBUG command = %s, cmd_obj = %s, sub_cmd = %s" % (command, cmd_obj, cmd_obj.get_sub_commands())
      if 0 or command in "build debug install".split(" "):
        print "DEBUG %s attr" % command
        for k, x in sorted(cmd_obj.__dict__.items()): print "\t", k, "\t", x

core.setup(
  name = "img2txt",
  version = "2008.11.19",
  author = "kai zhu",
  author_email = "kaizhu@ugcs.caltech.edu",
  description = """
takes a jpeg, gif, etc... image file & outputs it as colorized ascii art.
also does 3d-plots (screenshots of image conversion & 3d plots in putty terminal
included)
""",
  py_modules=["img2txt"],
  requires = ["py3to2", "PIL", "scipy"],

  classifiers = [
  "Development Status :: 3 - Alpha",
  # "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  # "Intended Audience :: Education",
  # "Intended Audience :: End Users/Desktop",
  "Intended Audience :: Science/Research",
  "Natural Language :: English",
  "Operating System :: POSIX",
  "Operating System :: POSIX :: Linux",
  "Operating System :: Unix",
  # "Programming Language :: C",
  "Programming Language :: Python",
  # "Programming Language :: Python :: 2.5",
  "Programming Language :: Python :: 2.6",
  "Programming Language :: Python :: 2.7",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.0",
  "Programming Language :: Python :: 3.1",
  # "Topic :: Education",
  # "Topic :: Education :: Testing",
  "Topic :: Scientific/Engineering",
  # "Topic :: Software Development",
  # "Topic :: Software Development :: Assemblers",
  # "Topic :: Software Development :: Build Tools",
  # "Topic :: Software Development :: Code Generators",
  # "Topic :: Software Development :: Compilers",
  # "Topic :: Software Development :: Disassemblers",
  # "Topic :: Software Development :: Interpreters",
  # "Topic :: Software Development :: Libraries",
  # "Topic :: Software Development :: Libraries :: Python Modules",
  # "Topic :: Software Development :: Pre-processors",
  # "Topic :: Software Development :: Testing",
  # "Topic :: System :: Emulators",
  # "Topic :: System :: Shells",
  # "Topic :: System :: System Shells",
  # "Topic :: Utilities",
  "Topic :: Multimedia :: Graphics",
  "Topic :: Multimedia :: Graphics :: Graphics Conversion",
  "Topic :: Multimedia :: Graphics :: Viewers",
  ],
  distclass = Distribution, # custom dist class
)
