import imp, os, subprocess, sys; from distutils import command, core, dist; BUILT = DEBUG = 0
NAME = "asciiporn"
MANIFEST = """
MANIFEST
README
setup.py

asciiporn.py
mario.jpg
screenshot_3dplot.gif
screenshot_mario.gif
"""
def quicktest(): DISTRIBUTION.run_command("build"); system("py3to2 -c 'import %s; %s.quicktest()'" % (NAME, NAME))
def system(cmd): print( cmd ); return subprocess.check_call(cmd, shell = True)
class Info(object):
  def __init__(self, mname): s = open(mname + ".py").read(); s = s[:s.find("## end setup info")]; exec(s, self.__dict__); global README; README = self.__doc__



## dependency check
print( """
  %s requires:
    py3to2
    Python Imaging Library
    scipy
  make sure these packages are installed before running setup
""" % NAME )
def missing_dependency(name, url):
  raise Exception("""

  %s requires %s
  please download & install %s from:

  %s

  or another source first.
  then quit this shell & rerun setup in a new shell
""" % (NAME, name, name, url))
try: imp.find_module("py3to2")
except: missing_dependency("py3to2", "http://pypi.python.org/pypi/py3to2")
try: imp.find_module("PIL")
except: missing_dependency("Python Imaging Library", "http://www.pythonware.com/products/pil/")
try: imp.find_module("scipy")
except: missing_dependency("scipy", "http://www.scipy.org/Download")



## developer stuff
class dev(core.Command):
  pass
  description = "setup commands for developer"
  user_options = [
    ("pkginfo", None, "create pkg-info"),
    ("quicktest", None, "run quick tests"),
    ("sdist", None, "custom sdist"),
    ]
  def initialize_options(self):
    for x in self.user_options: setattr(self, x[0], x[1])
  def finalize_options(self): pass
  def run(self):
    if self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))
    elif self.quicktest: quicktest()
    elif self.sdist:
      quicktest()
      DISTRIBUTION.run_command("sdist")
      cmd_obj = DISTRIBUTION.get_command_obj("sdist")
      src = cmd_obj.archive_files[0]; dst = "index_html/%s" % os.path.basename(src); system("cp -a %s %s" % (src, dst))



## custom Distribution class
class Distribution(dist.Distribution):
  built = None
  def __init__(self, *args, **kwds):
    dist.Distribution.__init__(self, *args, **kwds); global DISTRIBUTION; DISTRIBUTION = self; self.cmdclass["dev"] = dev
    info = Info(NAME)
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
      'name':	NAME,
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

    if 0 and DEBUG:
      print "DEBUG command = %s, cmd_obj = %s, sub_cmd = %s" % (command, cmd_obj, cmd_obj.get_sub_commands())
      if 1 and command in "sdist".split(" "):
        print "DEBUG %s attr" % command
        for k, x in sorted(cmd_obj.__dict__.items()): print "\t", k, "\t", x

    if command == "build":
      force = cmd_obj.force
      open("MANIFEST", "w").write(MANIFEST)
      open("README", "w").write(README)



## main loop
core.setup(
  distclass = Distribution, ## custom Distribution class
  py_modules=["asciiporn"],
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
  ])
