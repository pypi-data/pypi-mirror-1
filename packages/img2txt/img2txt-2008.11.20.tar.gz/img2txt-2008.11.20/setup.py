import distutils, imp, os, re, shutil, subprocess, sys; from distutils import command, core, dist

# dependency check
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







# init
BUILT = None
DEBUG = 1
MANIFEST = """
MANIFEST
README
setup.py

img2txt.py
img2txt_mario.py
mario.jpg
screenshot_3dplot.gif
screenshot_mario.gif
"""
def system(cmd): print cmd; return subprocess.check_call(cmd, shell = True)
def test():
  DISTRIBUTION.run_command("build")
  system("py3to2 -c 'import img2txt; img2txt.test()'")







# developer stuff
class dev(core.Command):
  description = "setup commands for developer"
  user_options = [
    ("pkginfo", None, "create pkg-info"),
    ("test", None, "run quick tests"),
    ("sdist", None, "run quick tests"),
    ]
  def initialize_options(self):
    for x in self.user_options: setattr(self, x[0], x[1])
  def finalize_options(self): pass
  def run(self):
    if self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))
    elif self.test: test()
    elif self.sdist:
      test()
      DISTRIBUTION.run_command("sdist")
      cmd_obj = DISTRIBUTION.get_command_obj("sdist")
      src = cmd_obj.archive_files[0]; dst = "index_html/%s" % os.path.basename(src); system("cp -a %s %s" % (src, dst))








# custom Distribution class
class Distribution(dist.Distribution):
  built = None
  def __init__(self, *args, **kwds):
    dist.Distribution.__init__(self, *args, **kwds); global DISTRIBUTION; DISTRIBUTION = self
    self.cmdclass["dev"] = dev
    self.metadata.long_description = README
  def run_command(self, command):
    cmd_obj = self.get_command_obj(command)
    def null(*args, **kwds): pass
    cmd_obj.byte_compile = null # disable byte compiling
    dist.Distribution.run_command(self, command)

    # DEBUG sdist attr
            # _dry_run        None
            # archive_files   ['dist/img2txt-2008.11.20.tar.gz']
            # byte_compile    <function null at 0x2a98f19cf8>
            # dist_dir        dist
            # distribution    <__main__.Distribution instance at 0x2a98df1e60>
            # filelist        <distutils.filelist.FileList instance at 0x2a98f1ff38>
            # finalized       1
            # force   None
            # force_manifest  0
            # formats         ['gztar']
            # help    0
            # keep_temp       0
            # manifest        MANIFEST
            # manifest_only   0
            # prune   1
            # template        MANIFEST.in
            # use_defaults    1
            # verbose         1
    if 0 and DEBUG:
      print "DEBUG command = %s, cmd_obj = %s, sub_cmd = %s" % (command, cmd_obj, cmd_obj.get_sub_commands())
      if 1 and command in "sdist".split(" "):
        print "DEBUG %s attr" % command
        for k, x in sorted(cmd_obj.__dict__.items()): print "\t", k, "\t", x

    if command == "build":
      force = cmd_obj.force
      open("MANIFEST", "w").write(MANIFEST)
      open("README", "w").write(README)







# readme
README = """
################################################################################
this is a fairly sophisticated python3.0 script fully utilizing
extensions, & demonstrated to run under python2.6 via py3to2.
for performance, portions of it have been inlined w/ direct C code using
scipy.weave.  the algorithm also heavily uses bitwise operations.
it takes a jpg, gif... image file & outputs it in colorized ascii art.
also serves dual purpose as a 3-d colorized scientific plotter in text terminals
(screenshots of image conversion & 3d plot in putty terminal included)

AUTHOR:
  kai zhu
  kaizhu@ugcs.caltech.edu

REQUIREMENTS:
  - posix/unix os (Windows currently unsupported)
  - py3to2
  - Python Imaging Library
  - scipy

API:
  img2txt module:
    - img2plaintxt - converts image file to portable plain txt
                     u can copy & paste in documents
    - img2txt - converts image to high-quality colorized txt
                for display on terminals supporting 256 color (putty, xterm...)

    - tplot3d - 3d color scientific plotter

USAGE:

  if something fails, try updating ur install of py3to2 to the latest version
  @: http://pypi.python.org/pypi/py3to2

  how to enable 256 color on putty: http://www.emacswiki.org/emacs/PuTTY#toc2
  how to enable 256 color on xterm: http://www.frexx.de/xterm-256-notes/

  img2txt is hard-coded to use lucida-console font, but courier looks ok.
  the screenshot shows putty w/ lucida-console 5pt.

  start up the py3to2 interpreter by typing "py3to2" in ur terminal &
  import img2txt:
    $ py3to2

    Python 2.6.py3to2 (r26:66714, Nov 18 2008, 00:56:43)
    [GCC 3.4.6 20060404 (Red Hat 3.4.6-10)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    >>> import img2txt
    created...
    py3k server starting...
    >>> ...py3k server started w/...
    >>>

  in this example, u'll b loading the image file included w/ this distribution,
  "mario.jpg".  its a fairly large image, so u probably want to scale it down
  to 0.5 (or less):
    >>> colortxt = img2txt.img2txt('mario.jpg', scale = 0.5)
    >>> print( colortxt )

    ... beautiful image appears ^_^

    >>> plaintxt = img2txt.img2plaintxt('mario.jpg', scale = 0.5)
    >>> print( plaintxt )

    ... rather plain b/w img, but u can copy & paste it in documents

  actually, the plaintxt prolly won't look well when pasted,
  b/c most document readers invert the color:
    >>> plaintxt = img2txt.img2plaintxt('mario.jpg', scale = 0.5, invert = True)
    >>> print( plaintxt )

    ... b/w img w/ colors inverted.  may look funny now,
        it'll b normal when u paste it into ur document

  the 3d plotting feature is a bit more complicated.  for the time being,
  simply run the test.  (if u want to kno how to use it,
  u'll need to look @ the img2txt.tplot3d.test() method in img2txt.py)
    >>> img2txt.tplot3d.test()

################################################################################
RECENT CHANGELOG:
current
  fixed bug where 64bit  gets truncated to 32 on 32bit machine
  256 color support
20081119
  fixed bugs in setup.py
"""







# main loop
core.setup(
  name = "img2txt",
  version = "2008.11.20",
  author = "kai zhu",
  author_email = "kaizhu@ugcs.caltech.edu",
  url = "http://www-rcf.usc.edu/~kaizhu/work/img2txt",
  description = """
takes a jpeg, gif, etc... image file & outputs it as colorized ascii art.
also does 3d-plots (screenshots of image conversion & 3d plots in putty terminal
included)
""",
  py_modules=["img2txt", "img2txt_mario"],
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
  "Programming Language :: C",
  "Programming Language :: Python",
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
  distclass = Distribution, # custom Distribution class
)
