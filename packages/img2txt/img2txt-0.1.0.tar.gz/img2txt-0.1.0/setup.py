from distutils.core import setup

setup (name = "img2txt",
       version = "0.1.0",
       author = "kai zhu",
       author_email = "kaizhu256@gmail.com",
       url = "http://www-rcf.usc.edu/~kaizhu/work/py3to2/apps/",
       description = """
takes a jpeg, gif... image file & outputs it in colorized ascii art.
the actual purpose is for colorized 3-d scientific plottin in text
terminal (screenshots of image conversion & 3d plots in putty terminal
included)
""",
       scripts = ["img2txt.py"],
       requires = ["py3to2"],
       classifiers = [
  "Development Status :: 3 - Alpha",
  "Intended Audience :: Developers",
  "Intended Audience :: Science/Research",
  "Natural Language :: English",
  "Operating System :: POSIX :: Linux",
  "Programming Language :: Python",
  "Topic :: Multimedia :: Graphics",
  "Topic :: Multimedia :: Graphics :: Graphics Conversion",
  "Topic :: Multimedia :: Graphics :: Viewers",
  ],
)
