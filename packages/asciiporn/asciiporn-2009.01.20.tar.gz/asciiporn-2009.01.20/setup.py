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

weave
weave/vtk_spec.py
weave/examples
weave/examples/vtk_example.py
weave/examples/md5_speed.py
weave/examples/py_none.py
weave/examples/swig2_ext.h
weave/examples/ramp.c
weave/examples/ramp2.py
weave/examples/wx_example.py
weave/examples/vq.py
weave/examples/support_code_example.py
weave/examples/dict_sort.py
weave/examples/fibonacci.py
weave/examples/binary_search.py
weave/examples/swig2_example.py
weave/examples/array3d.py
weave/examples/swig2_ext.i
weave/examples/tuple_return.py
weave/examples/print_example.py
weave/examples/cast_copy_transpose.py
weave/examples/functional.py
weave/examples/ramp.py
weave/examples/object.py
weave/examples/increment_example.py
weave/examples/wx_speed.py
weave/converters.py
weave/size_check.py
weave/inline_tools.py
weave/c_spec.py
weave/cpp_namespace_spec.py
weave/setup.py
weave/dumb_shelve.py
weave/weave_version.py
weave/platform_info.py
weave/weave_version.pyc
weave/base_spec.py
weave/swigptr.py
weave/slice_handler.py
weave/dumbdbm_patched.py
weave/__init__.py
weave/ast_tools.py
weave/scxx
weave/scxx/number.h
weave/scxx/dict.h
weave/scxx/scxx.h
weave/scxx/str.h
weave/scxx/weave_imp.cpp
weave/scxx/README.txt
weave/scxx/object.h
weave/scxx/list.h
weave/scxx/tuple.h
weave/scxx/sequence.h
weave/scxx/notes.txt
weave/accelerate_tools.py
weave/common_info.py
weave/standard_array_spec.py
weave/ext_tools.py
weave/build
weave/build/lib
weave/build/lib/weave
weave/build/lib/weave/vtk_spec.py
weave/build/lib/weave/converters.py
weave/build/lib/weave/size_check.py
weave/build/lib/weave/inline_tools.py
weave/build/lib/weave/c_spec.py
weave/build/lib/weave/cpp_namespace_spec.py
weave/build/lib/weave/dumb_shelve.py
weave/build/lib/weave/weave_version.py
weave/build/lib/weave/platform_info.py
weave/build/lib/weave/base_spec.py
weave/build/lib/weave/swigptr.py
weave/build/lib/weave/slice_handler.py
weave/build/lib/weave/dumbdbm_patched.py
weave/build/lib/weave/__init__.py
weave/build/lib/weave/ast_tools.py
weave/build/lib/weave/accelerate_tools.py
weave/build/lib/weave/common_info.py
weave/build/lib/weave/standard_array_spec.py
weave/build/lib/weave/ext_tools.py
weave/build/lib/weave/build_tools.py
weave/build/lib/weave/base_info.py
weave/build/lib/weave/bytecodecompiler.py
weave/build/lib/weave/swig2_spec.py
weave/build/lib/weave/wx_spec.py
weave/build/lib/weave/swigptr2.py
weave/build/lib/weave/info.py
weave/build/lib/weave/catalog.py
weave/doc
weave/doc/tutorial.html
weave/build_tools.py
weave/tests
weave/tests/test_build_tools.py
weave/tests/test_catalog.py
weave/tests/test_scxx_sequence.py
weave/tests/test_wx_spec.py
weave/tests/test_ext_tools.py
weave/tests/scxx_timings.py
weave/tests/test_blitz_tools.py
weave/tests/test_scxx.py
weave/tests/test_scxx_dict.py
weave/tests/test_slice_handler.py
weave/tests/weave_test_utils.py
weave/tests/test_standard_array_spec.py
weave/tests/test_c_spec.py
weave/tests/test_inline_tools.py
weave/tests/test_size_check.py
weave/tests/test_scxx_object.py
weave/tests/test_ast_tools.py
weave/base_info.py
weave/bytecodecompiler.py
weave/swig2_spec.py
weave/wx_spec.py
weave/swigptr2.py
weave/info.py
weave/catalog.py
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
    numpy
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
try: imp.find_module("numpy")
except: missing_dependency("numpy", "http://www.scipy.org/Download")



## developer stuff
class dev(core.Command):
  pass
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
    if self.doc: system("py3to2 -c 'import asciiporn; help(asciiporn)'")
    elif self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))
    elif self.quicktest: pass



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
      if not os.path.exists("weave"): system("tar -xzvf weave.tgz") ## untar src

    if command == "install":
      system("cp -a weave %s" % cmd_obj.install_lib)

    if command == "sdist":
      if os.path.exists("index_html"): src = cmd_obj.archive_files[0]; dst = "index_html/%s" % os.path.basename(src); system("cp -a %s %s" % (src, dst))



## main loop
core.setup(
  distclass = Distribution, ## custom Distribution class
  packages = ["weave"],
  py_modules = ["asciiporn"],
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
  # "Topic :: Multimedia",
  "Topic :: Multimedia :: Graphics",
  # "Topic :: Multimedia :: Graphics :: 3D Modeling",
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
