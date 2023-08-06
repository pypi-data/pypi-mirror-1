from distutils import command, core, dist
import os, re, subprocess, sys

if os.name == "nt": raise OSError("py3to2 currently doesn't support Windows/NT/XP/Vista")
if sys.version_info[0] is not 2 or sys.version_info[1] < 6: raise Exception("py3to2 requires Python-2.6 or higher")

BUILT = None
DEBUG = 0
PATCH = (
  "py3to2.py	Lib/py3to2.py",
  "py3to2_init.py	Lib/py3to2_init.py",
  "patch/ceval.c	Python/ceval.c",
  "patch/funcobject.c	Objects/funcobject.c",
  "patch/patchlevel.h	Include/patchlevel.h",
  "patch/_py3to2module.c	Modules/_py3to2module.c",
  "patch/pythonrun.c	Python/pythonrun.c",
  "patch/Setup.local	Modules/Setup.local",
  "patch/typeobject.c	Objects/typeobject.c",
  )

def system(cmd): print cmd; return subprocess.check_call(cmd, shell = True)

try: system("python3.0 -V")
except: raise Exception("py3to2 requires python3.0")

class dev(core.Command):
  description = "setup commands for developer"

  user_options = [
    ("diff", None, "create 'py3to2.diff' patch against Python-2.6 src"),
    ("maketest", None, "make test"),
    ("pkginfo", None, "create pkg-info"),
    ]

  def initialize_options(self):
    for x in self.user_options: setattr(self, x[0], x[1])

  def finalize_options(self): pass

  def run(self):
    CWD = os.getcwd(); os.chdir("Python-2.6")
    try:
      if self.maketest: system("make test")
    finally: os.chdir(CWD)

    if self.diff:
      DISTRIBUTION.patch("patched")
      try: system("diff -Naur src patched > py3to2.diff")
      except: pass

    elif self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))

class Distribution(dist.Distribution):
  built = None

  def __init__(self, *args, **kwds):
    dist.Distribution.__init__(self, *args, **kwds); global DISTRIBUTION; DISTRIBUTION = self
    self.cmdclass["dev"] = dev
    self.metadata.long_description = open("README").read()

  def patch(self, basedir):
    for x in PATCH: a, b = x.split("\t"); system("cp -a %s %s" % (a, os.path.join(basedir, b)))

  def run_command(self, command):
    cmd_obj = self.get_command_obj(command)
    dist.Distribution.run_command(self, command)

    # DEBUG build attr
      # _dry_run        None
      # build_base      build
      # build_lib       build/lib
      # build_platlib   build/lib.linux-x86_64-2.6
      # build_purelib   build/lib
      # build_scripts   build/scripts-2.6
      # build_temp      build/temp.linux-x86_64-2.6
      # compiler        None
      # debug   None
      # distribution    <__main__.Distribution instance at 0x2a988f1bd8>
      # executable      /home/rcf-40/kaizhu/x86_64/bin/python
      # finalized       1
      # force   None
      # help    0
      # plat_name       linux-x86_64
      # verbose         1
    # DEBUG install attr
      # _dry_run        None
      # build_base      build
      # build_lib       build/lib
      # compile         None
      # config_vars     {'usersite': '/home/rcf-40/kaizhu/.local/lib/python2.6/site-packages', 'py_version_nodot': '26', 'platbase': '/home/rcf-40/kaizhu/x86_64', 'py_version_short': '2.6', 'dist_fullname': 'py3to2-2008.11.19', 'prefix': '/home/rcf-40/kaizhu/x86_64', 'base': '/home/rcf-40/kaizhu/x86_64', 'sys_prefix': '/home/rcf-40/kaizhu/x86_64', 'py_version': '2.6', 'userbase': '/home/rcf-40/kaizhu/.local', 'dist_name': 'py3to2', 'exec_prefix': '/home/rcf-40/kaizhu/x86_64', 'dist_version': '2008.11.19', 'sys_exec_prefix': '/home/rcf-40/kaizhu/x86_64'}
      # distribution    <__main__.Distribution instance at 0x2a988c1e18>
      # exec_prefix     /home/rcf-40/kaizhu/x86_64
      # extra_dirs
      # extra_path      None
      # finalized       1
      # force   None
      # help    0
      # home    None
      # install_base    /home/rcf-40/kaizhu/x86_64
      # install_data    /home/rcf-40/kaizhu/x86_64
      # install_headers         /home/rcf-40/kaizhu/x86_64/include/python2.6/py3to2
      # install_lib     /home/rcf-40/kaizhu/x86_64/lib/python2.6/site-packages/
      # install_libbase         /home/rcf-40/kaizhu/x86_64/lib/python2.6/site-packages
      # install_path_file       1
      # install_platbase        /home/rcf-40/kaizhu/x86_64
      # install_platlib         /home/rcf-40/kaizhu/x86_64/lib/python2.6/site-packages
      # install_purelib         /home/rcf-40/kaizhu/x86_64/lib/python2.6/site-packages
      # install_scripts         /home/rcf-40/kaizhu/x86_64/bin
      # install_userbase        /home/rcf-40/kaizhu/.local
      # install_usersite        /home/rcf-40/kaizhu/.local/lib/python2.6/site-packages
      # optimize        None
      # path_file       None
      # prefix  /home/rcf-40/kaizhu/x86_64
      # record  None
      # root    None
      # skip_build      0
      # user    0
      # verbose         1
      # warn_dir        1

    if 1 and DEBUG:
      print "DEBUG command = %s, cmd_obj = %s, sub_cmd = %s" % (command, cmd_obj, cmd_obj.get_sub_commands())
      if 0 or command in "build debug install".split(" "):
        print "DEBUG %s attr" % command
        for k, x in sorted(cmd_obj.__dict__.items()): print "\t", k, "\t", x

    if command == "build":
      force = cmd_obj.force

      if not os.path.lexists("py3to2"): system("ln -s Python-2.6/py3to2 .") # create link to built binary
      if not os.path.exists("Python-2.6") or force:
        system("wget -c http://www.python.org/ftp/python/2.6/Python-2.6.tgz") # download src
        system("tar -xzvf Python-2.6.tgz") # untar src

      self.patch("Python-2.6") # patch src

      CWD = os.getcwd(); os.chdir("Python-2.6")
      try:
        if not os.path.exists("Makefile") or force: system("./configure --disable-shared") # ./configure
        if force: system("make clean") # make clean
        system("make; cp python py3to2") # make
      finally: global BUILT; BUILT = True; os.chdir(CWD) # leave build dir

    if command == "install":
      system("cp py3to2 %s" % cmd_obj.install_scripts)

core.setup(
  name = "py3to2",
  version = "2008.11.20",
  author = "kai zhu",
  author_email = "kaizhu@ugcs.caltech.edu",
  url = "http://www-rcf.usc.edu/~kaizhu/work/py3to2",
  description = "backport 3.0 opcodes to Python-2.6 so it can natively run 3.0 scripts w/ 2.6 extension modules",
  py_modules=["py3to2", "py3to2_init"],

  classifiers = [
  "Development Status :: 3 - Alpha",
  # "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Intended Audience :: Education",
  "Intended Audience :: End Users/Desktop",
  "Intended Audience :: Science/Research",
  "Natural Language :: English",
  "Operating System :: POSIX",
  "Operating System :: POSIX :: Linux",
  "Operating System :: Unix",
  "Programming Language :: C",
  "Programming Language :: Python",
  # "Programming Language :: Python :: 2.5",
  "Programming Language :: Python :: 2.6",
  "Programming Language :: Python :: 2.7",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.0",
  "Programming Language :: Python :: 3.1",
  "Topic :: Education",
  "Topic :: Education :: Testing",
  "Topic :: Scientific/Engineering",
  "Topic :: Software Development",
  "Topic :: Software Development :: Assemblers",
  "Topic :: Software Development :: Build Tools",
  "Topic :: Software Development :: Code Generators",
  "Topic :: Software Development :: Compilers",
  "Topic :: Software Development :: Disassemblers",
  "Topic :: Software Development :: Interpreters",
  "Topic :: Software Development :: Libraries",
  "Topic :: Software Development :: Libraries :: Python Modules",
  "Topic :: Software Development :: Pre-processors",
  "Topic :: Software Development :: Testing",
  "Topic :: System :: Emulators",
  "Topic :: System :: Shells",
  "Topic :: System :: System Shells",
  "Topic :: Utilities",
  ],
  distclass = Distribution, # custom dist class
)
