NAME = "asciiporn"
MANIFEST = """
mario.jpg
screenshot_mario.gif
screenshot_plot.gif

MANIFEST
README
setup.py

asciiporn/__init__.py
asciiporn/_asciiporn.py

asciiporn/weave/__init__.py
asciiporn/weave/accelerate_tools.py
asciiporn/weave/ast_tools.py
asciiporn/weave/base_info.py
asciiporn/weave/base_spec.py
asciiporn/weave/build_tools.py
asciiporn/weave/bytecodecompiler.py
asciiporn/weave/c_spec.py
asciiporn/weave/catalog.py
asciiporn/weave/common_info.py
asciiporn/weave/converters.py
asciiporn/weave/cpp_namespace_spec.py
asciiporn/weave/doc
asciiporn/weave/doc/tutorial.html
asciiporn/weave/dumb_shelve.py
asciiporn/weave/dumbdbm_patched.py
asciiporn/weave/examples
asciiporn/weave/examples/array3d.py
asciiporn/weave/examples/binary_search.py
asciiporn/weave/examples/cast_copy_transpose.py
asciiporn/weave/examples/dict_sort.py
asciiporn/weave/examples/fibonacci.py
asciiporn/weave/examples/functional.py
asciiporn/weave/examples/increment_example.py
asciiporn/weave/examples/md5_speed.py
asciiporn/weave/examples/object.py
asciiporn/weave/examples/print_example.py
asciiporn/weave/examples/py_none.py
asciiporn/weave/examples/ramp.c
asciiporn/weave/examples/ramp.py
asciiporn/weave/examples/ramp2.py
asciiporn/weave/examples/support_code_example.py
asciiporn/weave/examples/swig2_example.py
asciiporn/weave/examples/swig2_ext.h
asciiporn/weave/examples/swig2_ext.i
asciiporn/weave/examples/tuple_return.py
asciiporn/weave/examples/vq.py
asciiporn/weave/examples/vtk_example.py
asciiporn/weave/examples/wx_example.py
asciiporn/weave/examples/wx_speed.py
asciiporn/weave/ext_tools.py
asciiporn/weave/info.py
asciiporn/weave/inline_tools.py
asciiporn/weave/platform_info.py
asciiporn/weave/scxx
asciiporn/weave/scxx/README.txt
asciiporn/weave/scxx/dict.h
asciiporn/weave/scxx/list.h
asciiporn/weave/scxx/notes.txt
asciiporn/weave/scxx/number.h
asciiporn/weave/scxx/object.h
asciiporn/weave/scxx/scxx.h
asciiporn/weave/scxx/sequence.h
asciiporn/weave/scxx/str.h
asciiporn/weave/scxx/tuple.h
asciiporn/weave/scxx/weave_imp.cpp
asciiporn/weave/setup.py
asciiporn/weave/size_check.py
asciiporn/weave/slice_handler.py
asciiporn/weave/standard_array_spec.py
asciiporn/weave/swig2_spec.py
asciiporn/weave/swigptr.py
asciiporn/weave/swigptr2.py
asciiporn/weave/tests
asciiporn/weave/tests/scxx_timings.py
asciiporn/weave/tests/test_ast_tools.py
asciiporn/weave/tests/test_build_tools.py
asciiporn/weave/tests/test_c_spec.py
asciiporn/weave/tests/test_catalog.py
asciiporn/weave/tests/test_ext_tools.py
asciiporn/weave/tests/test_inline_tools.py
asciiporn/weave/tests/test_scxx.py
asciiporn/weave/tests/test_scxx_dict.py
asciiporn/weave/tests/test_scxx_object.py
asciiporn/weave/tests/test_scxx_sequence.py
asciiporn/weave/tests/test_size_check.py
asciiporn/weave/tests/test_slice_handler.py
asciiporn/weave/tests/test_standard_array_spec.py
asciiporn/weave/tests/test_wx_spec.py
asciiporn/weave/tests/weave_test_utils.py
asciiporn/weave/vtk_spec.py
asciiporn/weave/weave_version.py
asciiporn/weave/wx_spec.py
"""



import imp, os, subprocess, sys; from distutils import command, core, dist; BUILT = DEBUG = 0
# if sys.version_info[1] < 6: raise Exception("asciiporn requires Python 2.6 or higher")
def quicktest(): DISTRIBUTION.run_command("build"); system("python -c 'import %s; %s.quicktest()'" % (NAME, NAME))
def system(cmd): print( cmd ); return subprocess.check_call(cmd, shell = True)
class Info(object):
  def __init__(self, fname): s = open(fname).read(); s = s[:s.find("## end setup info")]; exec(s, self.__dict__); global README; README = self.__doc__




## dependency check
print( """
  %s requires:
    Python 2.6
    Python Imaging Library
    numpy
  make sure these packages are installed before running setup
""" % NAME )
def missing_dependency(name, url):
  raise Exception("""

  %s requires %s
  please download & install %s from:

  %s

  or ur source distro first.
  then quit this shell & rerun setup in a new shell
""" % (NAME, name, name, url))
try: imp.find_module("PIL")
except: missing_dependency("Python Imaging Library", "http://www.pythonware.com/products/pil/")
try: imp.find_module("numpy")
except: missing_dependency("numpy", "http://www.scipy.org/Download")



## developer stuff
class dev(core.Command):
  description = "setup commands for developer"
  user_options = [
    ("doc", None, "print doc"),
    ("pkginfo", None, "create pkg-info"),
    ("quicktest", None, "run quick tests"),
    ]
  def initialize_options(self):
    for x in self.user_options: setattr(self, x[0], x[1])
  def finalize_options(self): pass
  def run(self):
    quicktest()
    if self.doc: system("python -c 'import asciiporn; help(asciiporn)'")
    elif self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))
    elif self.quicktest: pass



## custom Distribution class
class Distribution(dist.Distribution):
  built = None
  def __init__(self, *args, **kwds):
    dist.Distribution.__init__(self, *args, **kwds); global DISTRIBUTION; DISTRIBUTION = self; self.cmdclass["dev"] = dev
    info = Info(os.path.join("asciiporn", "__init__.py"))
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
    if command == "sdist": quicktest() ## pre sdist
    dist.Distribution.run_command(self, command)

    if 0 or DEBUG:
      print( "DEBUG command = %s, cmd_obj = %s, sub_cmd = %s" % (command, cmd_obj, cmd_obj.get_sub_commands()) )
      if 1 and command in "install sdist".split(" "):
        print( "DEBUG %s attr" % command )
        for k, x in sorted(cmd_obj.__dict__.items()): print( "\t", k, "\t", x )

    if command == "build":
      force = cmd_obj.force
      open("MANIFEST", "w").write(MANIFEST)
      open("README", "w").write(README)

    if command == "install":
      system("cp -a weave %s" % cmd_obj.install_lib)

    if command == "sdist":
      if os.path.exists("index_html"): src = cmd_obj.archive_files[0]; dst = "index_html/%s" % os.path.basename(src); system("cp -a %s %s" % (src, dst))




## main loop
core.setup(
  distclass = Distribution, ## custom Distribution class
  packages = ["asciiporn"],
  py_modules = [],
  classifiers = [
  "Development Status :: 3 - Alpha",
  # "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Intended Audience :: End Users/Desktop",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: GNU General Public License (GPL)",
  "Natural Language :: English",
  "Operating System :: POSIX",
  "Operating System :: POSIX :: Linux",
  "Operating System :: Unix",
  "Programming Language :: C",
  "Programming Language :: Python",
  "Programming Language :: Python :: 2.6",
  # "Programming Language :: Python :: 2.7",
  "Topic :: Multimedia",
  "Topic :: Multimedia :: Graphics",
  "Topic :: Multimedia :: Graphics :: 3D Modeling",
  "Topic :: Multimedia :: Graphics :: 3D Rendering",
  # "Topic :: Multimedia :: Graphics :: Capture",
  # "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
  # "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
  # "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
  # "Topic :: Multimedia :: Graphics :: Editors",
  # "Topic :: Multimedia :: Graphics :: Editors :: Raster-Based",
  # "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
  "Topic :: Multimedia :: Graphics :: Graphics Conversion",
  # "Topic :: Multimedia :: Graphics :: Presentation",
  "Topic :: Multimedia :: Graphics :: Viewers",
  "Topic :: Scientific/Engineering",
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
