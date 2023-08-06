import os, subprocess, sys; from distutils import command, core, dist; BUILT = DEBUG = 0
NAME = "py3to2"
MANIFEST = """
## setup files
MANIFEST
README
setup.py
py3to2.diff
py3to2.py
py3to2_init.py
py3to2_test.py

## patched files
patch/code.h
patch/funcobject.h
patch/patchlevel.h

patch/codeobject.c
patch/funcobject.c
patch/typeobject.c

patch/ceval.c
patch/pythonrun.c

patch/_py3to2module.c
patch/Setup.local
"""
PATCH = (
  "py3to2.py	Lib/py3to2.py",
  "py3to2_init.py	Lib/py3to2_init.py",

  "patch/code.h	Include/code.h",
  "patch/funcobject.h	Include/funcobject.h",
  "patch/patchlevel.h	Include/patchlevel.h",

  "patch/codeobject.c	Objects/codeobject.c",
  "patch/funcobject.c	Objects/funcobject.c",
  "patch/typeobject.c	Objects/typeobject.c",

  "patch/ceval.c	Python/ceval.c",
  "patch/pythonrun.c	Python/pythonrun.c",

  "patch/_py3to2module.c	Modules/_py3to2module.c",
  "patch/Setup.local	Modules/Setup.local",
  )
def diff():
  DISTRIBUTION.patch("patched", PATCH[2:])
  try: system("diff -Naur src patched > py3to2.diff")
  except: pass
def quicktest(): DISTRIBUTION.run_command("build"); system("./py3to2 -c 'import py3to2; py3to2.quicktest()'")
def system(cmd): print( cmd ); return subprocess.check_call(cmd, shell = True)
class Info(object):
  def __init__(self, mname): s = open(mname + ".py").read(); s = s[:s.find("## end setup info")]; exec(s, self.__dict__); global README; README = self.__doc__



## dependency check
print( """
  %s requires:
    Python-2.6 & Python-3.0
  make sure they are installed before running setup
""" % NAME )
def missing_dependency(name, url):
  raise Exception("""

  %s requires %s
  please download & install %s from:

  %s

  or another source first.
  then quit this shell & rerun setup in a new shell
""" % (NAME, name, name, url))
if os.name == "nt": raise OSError("py3to2 currently doesn't support Windows/NT/XP/Vista")
try: system("python2.6 -V")
except: missing_dependency("Python-2.6", "http://www.python.org/download/releases/2.6/")
try: system("python3.0 -V")
except: missing_dependency("Python-3.0", "http://www.python.org/download/releases/3.0/")
if sys.version_info[0] is not 2 or sys.version_info[1] < 6: raise Exception("setup needs to b run w/ Python-2.6")



## developer stuff
class dev(core.Command):
  description = "setup commands for developer"
  user_options = [
    ("diff", None, "create 'py3to2.diff' patch against Python-2.6 src"),
    ("doc", None, "print doc"),
    ("maketest", None, "make test - run regression tests"),
    ("pkginfo", None, "create pkg-info"),
    ("py2to3test", None, "test importing python2.6 standard library generated from 2to3"),
    ("quicktest", None, "run quick tests"),
    ("sdist", None, "custom sdist"),
    ]
  def initialize_options(self):
    for x in self.user_options: setattr(self, x[0], x[1])
  def finalize_options(self): pass
  def run(self):
    quicktest()
    if self.diff: diff()
    elif self.doc: system("py3to2 -c 'import py3to2; help(py3to2)'")
    elif self.maketest:
      CWD = os.getcwd(); os.chdir("Python-2.6")
      try: system("make test"); print( "completed %s regression tests" % sys.version )
      finally: os.chdir(CWD)
    elif self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))
    elif self.py2to3test:
      if not os.path.exists("py3k_Lib"): system("cp -a Python-2.6/Lib py3k_Lib")
      system("./py3to2 -c 'import py3to2; py3to2.py2to3.test_stdlib(\"py3k_Lib\")'")
    elif self.quicktest: pass
    elif self.sdist:
      diff()
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
  def patch(self, basedir, patch = PATCH):
    for x in patch: a, b = x.split("\t"); system("cp -a %s %s" % (a, os.path.join(basedir, b)))
  def run_command(self, command):
    cmd_obj = self.get_command_obj(command)
    def null(*args, **kwds): pass
    cmd_obj.byte_compile = null ## disable byte compiling
    dist.Distribution.run_command(self, command)

    if 1 and DEBUG:
      print( "DEBUG command = %s, cmd_obj = %s, sub_cmd = %s" % (command, cmd_obj, cmd_obj.get_sub_commands()) )
      if 0 or command in "build debug install".split(" "):
        print( "DEBUG %s attr" % command )
        for k, x in sorted(cmd_obj.__dict__.items()): print( "\t", k, "\t", x )

    if command == "build":
      force = cmd_obj.force
      open("MANIFEST", "w").write(MANIFEST)
      open("README", "w").write(README)

      if not os.path.lexists("py3to2"): system("ln -s Python-2.6/py3to2 .") ## create link to built binary
      if not os.path.exists("Python-2.6"):
        try: system("tar -xzvf Python-2.6.tgz") ## untar src
        except: raise Exception("""\n
py3to2 requires Python-2.6 src files in order to b built.
please first download src Python-2.6.tgz from:

  http://www.python.org/ftp/python/2.6/Python-2.6.tgz

into CURRENT directory.  then run setup again
""")
      self.patch("Python-2.6") ## patch src

      CWD = os.getcwd(); os.chdir("Python-2.6")
      try:
        if not os.path.exists("Makefile") or force: system("./configure --disable-shared") ## ./configure
        if force: system("make clean") ## make clean
        system("make; cp python py3to2") ## make
      finally: global BUILT; BUILT = True; os.chdir(CWD) ## leave build dir

    if command == "install":
      system("cp py3to2 %s" % cmd_obj.install_scripts)



## main loop
core.setup(
  distclass = Distribution, ## custom dist class
  py_modules = ["py3to2", "py3to2_init"],
  classifiers = [
  # "Development Status :: 1 - Planning",
  # "Development Status :: 2 - Pre-Alpha",
  "Development Status :: 3 - Alpha",
  # "Development Status :: 4 - Beta",
  # "Development Status :: 5 - Production/Stable",
  # "Development Status :: 6 - Mature",
  # "Development Status :: 7 - Inactive",
  "Environment :: Console",
  # "Environment :: Console :: Curses",
  # "Environment :: Console :: Framebuffer",
  # "Environment :: Console :: Newt",
  # "Environment :: Console :: svgalib",
  # "Environment :: Handhelds/PDA's",
  # "Environment :: MacOS X",
  # "Environment :: MacOS X :: Aqua",
  # "Environment :: MacOS X :: Carbon",
  # "Environment :: MacOS X :: Cocoa",
  # "Environment :: No Input/Output (Daemon)",
  # "Environment :: Other Environment",
  # "Environment :: Plugins",
  # "Environment :: Web Environment",
  # "Environment :: Web Environment :: Buffet",
  # "Environment :: Web Environment :: Mozilla",
  # "Environment :: Web Environment :: ToscaWidgets",
  # "Environment :: Win32 (MS Windows)",
  # "Environment :: X11 Applications",
  # "Environment :: X11 Applications :: Gnome",
  # "Environment :: X11 Applications :: GTK",
  # "Environment :: X11 Applications :: KDE",
  # "Environment :: X11 Applications :: Qt",
  # "Framework :: Buildout",
  # "Framework :: Chandler",
  # "Framework :: Django",
  # "Framework :: IDLE",
  # "Framework :: Paste",
  # "Framework :: Plone",
  # "Framework :: Pylons",
  # "Framework :: Setuptools Plugin",
  # "Framework :: Trac",
  # "Framework :: TurboGears",
  # "Framework :: TurboGears :: Applications",
  # "Framework :: TurboGears :: Widgets",
  # "Framework :: Twisted",
  # "Framework :: ZODB",
  # "Framework :: Zope2",
  # "Framework :: Zope3",
  # "Intended Audience :: Customer Service",
  "Intended Audience :: Developers",
  "Intended Audience :: Education",
  "Intended Audience :: End Users/Desktop",
  # "Intended Audience :: Financial and Insurance Industry",
  # "Intended Audience :: Healthcare Industry",
  # "Intended Audience :: Information Technology",
  # "Intended Audience :: Legal Industry",
  # "Intended Audience :: Manufacturing",
  # "Intended Audience :: Other Audience",
  # "Intended Audience :: Religion",
  "Intended Audience :: Science/Research",
  # "Intended Audience :: System Administrators",
  # "Intended Audience :: Telecommunications Industry",
  # "License :: Aladdin Free Public License (AFPL)",
  # "License :: DFSG approved",
  # "License :: Eiffel Forum License (EFL)",
  # "License :: Free For Educational Use",
  # "License :: Free For Home Use",
  # "License :: Free for non-commercial use",
  # "License :: Freely Distributable",
  # "License :: Free To Use But Restricted",
  # "License :: Freeware",
  # "License :: Netscape Public License (NPL)",
  # "License :: Nokia Open Source License (NOKOS)",
  # "License :: OSI Approved",
  # "License :: OSI Approved :: Academic Free License (AFL)",
  # "License :: OSI Approved :: Apache Software License",
  # "License :: OSI Approved :: Apple Public Source License",
  # "License :: OSI Approved :: Artistic License",
  # "License :: OSI Approved :: Attribution Assurance License",
  "License :: OSI Approved :: BSD License",
  # "License :: OSI Approved :: Common Public License",
  # "License :: OSI Approved :: Eiffel Forum License",
  # "License :: OSI Approved :: GNU Affero General Public License v3",
  # "License :: OSI Approved :: GNU Free Documentation License (FDL)",
  # "License :: OSI Approved :: GNU General Public License (GPL)",
  # "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
  # "License :: OSI Approved :: IBM Public License",
  # "License :: OSI Approved :: Intel Open Source License",
  # "License :: OSI Approved :: Jabber Open Source License",
  # "License :: OSI Approved :: MIT License",
  # "License :: OSI Approved :: MITRE Collaborative Virtual Workspace License (CVW)",
  # "License :: OSI Approved :: Motosoto License",
  # "License :: OSI Approved :: Mozilla Public License 1.0 (MPL)",
  # "License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)",
  # "License :: OSI Approved :: Nethack General Public License",
  # "License :: OSI Approved :: Nokia Open Source License",
  # "License :: OSI Approved :: Open Group Test Suite License",
  # "License :: OSI Approved :: Python License (CNRI Python License)",
  # "License :: OSI Approved :: Python Software Foundation License",
  # "License :: OSI Approved :: Qt Public License (QPL)",
  # "License :: OSI Approved :: Ricoh Source Code Public License",
  # "License :: OSI Approved :: Sleepycat License",
  # "License :: OSI Approved :: Sun Industry Standards Source License (SISSL)",
  # "License :: OSI Approved :: Sun Public License",
  # "License :: OSI Approved :: University of Illinois/NCSA Open Source License",
  # "License :: OSI Approved :: Vovida Software License 1.0",
  # "License :: OSI Approved :: W3C License",
  # "License :: OSI Approved :: X.Net License",
  # "License :: OSI Approved :: zlib/libpng License",
  # "License :: OSI Approved :: Zope Public License",
  # "License :: Other/Proprietary License",
  # "License :: Public Domain",
  # "Natural Language :: Afrikaans",
  # "Natural Language :: Arabic",
  # "Natural Language :: Bengali",
  # "Natural Language :: Bosnian",
  # "Natural Language :: Bulgarian",
  # "Natural Language :: Catalan",
  # "Natural Language :: Chinese (Simplified)",
  # "Natural Language :: Chinese (Traditional)",
  # "Natural Language :: Croatian",
  # "Natural Language :: Czech",
  # "Natural Language :: Danish",
  # "Natural Language :: Dutch",
  "Natural Language :: English",
  # "Natural Language :: Esperanto",
  # "Natural Language :: Finnish",
  # "Natural Language :: French",
  # "Natural Language :: German",
  # "Natural Language :: Greek",
  # "Natural Language :: Hebrew",
  # "Natural Language :: Hindi",
  # "Natural Language :: Hungarian",
  # "Natural Language :: Icelandic",
  # "Natural Language :: Indonesian",
  # "Natural Language :: Italian",
  # "Natural Language :: Japanese",
  # "Natural Language :: Javanese",
  # "Natural Language :: Korean",
  # "Natural Language :: Latin",
  # "Natural Language :: Latvian",
  # "Natural Language :: Macedonian",
  # "Natural Language :: Malay",
  # "Natural Language :: Marathi",
  # "Natural Language :: Norwegian",
  # "Natural Language :: Panjabi",
  # "Natural Language :: Persian",
  # "Natural Language :: Polish",
  # "Natural Language :: Portuguese",
  # "Natural Language :: Portuguese (Brazilian)",
  # "Natural Language :: Romanian",
  # "Natural Language :: Russian",
  # "Natural Language :: Serbian",
  # "Natural Language :: Slovak",
  # "Natural Language :: Slovenian",
  # "Natural Language :: Spanish",
  # "Natural Language :: Swedish",
  # "Natural Language :: Tamil",
  # "Natural Language :: Telugu",
  # "Natural Language :: Thai",
  # "Natural Language :: Turkish",
  # "Natural Language :: Ukranian",
  # "Natural Language :: Urdu",
  # "Natural Language :: Vietnamese",
  # "Operating System :: BeOS",
  # "Operating System :: MacOS",
  # "Operating System :: MacOS :: MacOS 9",
  # "Operating System :: MacOS :: MacOS X",
  # "Operating System :: Microsoft",
  # "Operating System :: Microsoft :: MS-DOS",
  # "Operating System :: Microsoft :: Windows",
  # "Operating System :: Microsoft :: Windows :: Windows 3.1 or Earlier",
  # "Operating System :: Microsoft :: Windows :: Windows 95/98/2000",
  # "Operating System :: Microsoft :: Windows :: Windows CE",
  # "Operating System :: Microsoft :: Windows :: Windows NT/2000",
  # "Operating System :: OS/2",
  # "Operating System :: OS Independent",
  # "Operating System :: Other OS",
  # "Operating System :: PalmOS",
  # "Operating System :: PDA Systems",
  "Operating System :: POSIX",
  # "Operating System :: POSIX :: AIX",
  # "Operating System :: POSIX :: BSD",
  # "Operating System :: POSIX :: BSD :: BSD/OS",
  # "Operating System :: POSIX :: BSD :: FreeBSD",
  # "Operating System :: POSIX :: BSD :: NetBSD",
  # "Operating System :: POSIX :: BSD :: OpenBSD",
  # "Operating System :: POSIX :: GNU Hurd",
  # "Operating System :: POSIX :: HP-UX",
  # "Operating System :: POSIX :: IRIX",
  # "Operating System :: POSIX :: Linux",
  # "Operating System :: POSIX :: Other",
  # "Operating System :: POSIX :: SCO",
  # "Operating System :: POSIX :: SunOS/Solaris",
  "Operating System :: Unix",
  # "Programming Language :: Ada",
  # "Programming Language :: APL",
  # "Programming Language :: ASP",
  # "Programming Language :: Assembly",
  # "Programming Language :: Awk",
  # "Programming Language :: Basic",
  "Programming Language :: C",
  # "Programming Language :: C#",
  # "Programming Language :: C++",
  # "Programming Language :: Cold Fusion",
  # "Programming Language :: Delphi/Kylix",
  # "Programming Language :: Dylan",
  # "Programming Language :: Eiffel",
  # "Programming Language :: Emacs-Lisp",
  # "Programming Language :: Erlang",
  # "Programming Language :: Euler",
  # "Programming Language :: Euphoria",
  # "Programming Language :: Forth",
  # "Programming Language :: Fortran",
  # "Programming Language :: Haskell",
  # "Programming Language :: Java",
  # "Programming Language :: JavaScript",
  # "Programming Language :: Lisp",
  # "Programming Language :: Logo",
  # "Programming Language :: ML",
  # "Programming Language :: Modula",
  # "Programming Language :: Objective C",
  # "Programming Language :: Object Pascal",
  # "Programming Language :: OCaml",
  # "Programming Language :: Other",
  # "Programming Language :: Other Scripting Engines",
  # "Programming Language :: Pascal",
  # "Programming Language :: Perl",
  # "Programming Language :: PHP",
  # "Programming Language :: Pike",
  # "Programming Language :: Pliant",
  # "Programming Language :: PL/SQL",
  # "Programming Language :: PROGRESS",
  # "Programming Language :: Prolog",
  "Programming Language :: Python",
  # "Programming Language :: Python :: 2",
  # "Programming Language :: Python :: 2.3",
  # "Programming Language :: Python :: 2.4",
  # "Programming Language :: Python :: 2.5",
  "Programming Language :: Python :: 2.6",
  "Programming Language :: Python :: 2.7",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.0",
  "Programming Language :: Python :: 3.1",
  # "Programming Language :: REBOL",
  # "Programming Language :: Rexx",
  # "Programming Language :: Ruby",
  # "Programming Language :: Scheme",
  # "Programming Language :: Simula",
  # "Programming Language :: Smalltalk",
  # "Programming Language :: SQL",
  # "Programming Language :: Tcl",
  # "Programming Language :: Unix Shell",
  # "Programming Language :: Visual Basic",
  # "Programming Language :: XBasic",
  # "Programming Language :: YACC",
  # "Programming Language :: Zope",
  # "Topic :: Adaptive Technologies",
  # "Topic :: Artistic Software",
  # "Topic :: Communications",
  # "Topic :: Communications :: BBS",
  # "Topic :: Communications :: Chat",
  # "Topic :: Communications :: Chat :: AOL Instant Messenger",
  # "Topic :: Communications :: Chat :: ICQ",
  # "Topic :: Communications :: Chat :: Internet Relay Chat",
  # "Topic :: Communications :: Chat :: Unix Talk",
  # "Topic :: Communications :: Conferencing",
  # "Topic :: Communications :: Email",
  # "Topic :: Communications :: Email :: Address Book",
  # "Topic :: Communications :: Email :: Email Clients (MUA)",
  # "Topic :: Communications :: Email :: Filters",
  # "Topic :: Communications :: Email :: Mailing List Servers",
  # "Topic :: Communications :: Email :: Mail Transport Agents",
  # "Topic :: Communications :: Email :: Post-Office",
  # "Topic :: Communications :: Email :: Post-Office :: IMAP",
  # "Topic :: Communications :: Email :: Post-Office :: POP3",
  # "Topic :: Communications :: Fax",
  # "Topic :: Communications :: FIDO",
  # "Topic :: Communications :: File Sharing",
  # "Topic :: Communications :: File Sharing :: Gnutella",
  # "Topic :: Communications :: File Sharing :: Napster",
  # "Topic :: Communications :: Ham Radio",
  # "Topic :: Communications :: Internet Phone",
  # "Topic :: Communications :: Telephony",
  # "Topic :: Communications :: Usenet News",
  # "Topic :: Database",
  # "Topic :: Database :: Database Engines/Servers",
  # "Topic :: Database :: Front-Ends",
  # "Topic :: Desktop Environment",
  # "Topic :: Desktop Environment :: File Managers",
  # "Topic :: Desktop Environment :: Gnome",
  # "Topic :: Desktop Environment :: GNUstep",
  # "Topic :: Desktop Environment :: K Desktop Environment (KDE)",
  # "Topic :: Desktop Environment :: K Desktop Environment (KDE) :: Themes",
  # "Topic :: Desktop Environment :: PicoGUI",
  # "Topic :: Desktop Environment :: PicoGUI :: Applications",
  # "Topic :: Desktop Environment :: PicoGUI :: Themes",
  # "Topic :: Desktop Environment :: Screen Savers",
  # "Topic :: Desktop Environment :: Window Managers",
  # "Topic :: Desktop Environment :: Window Managers :: Afterstep",
  # "Topic :: Desktop Environment :: Window Managers :: Afterstep :: Themes",
  # "Topic :: Desktop Environment :: Window Managers :: Applets",
  # "Topic :: Desktop Environment :: Window Managers :: Blackbox",
  # "Topic :: Desktop Environment :: Window Managers :: Blackbox :: Themes",
  # "Topic :: Desktop Environment :: Window Managers :: CTWM",
  # "Topic :: Desktop Environment :: Window Managers :: CTWM :: Themes",
  # "Topic :: Desktop Environment :: Window Managers :: Enlightenment",
  # "Topic :: Desktop Environment :: Window Managers :: Enlightenment :: Epplets",
  # "Topic :: Desktop Environment :: Window Managers :: Enlightenment :: Themes DR15",
  # "Topic :: Desktop Environment :: Window Managers :: Enlightenment :: Themes DR16",
  # "Topic :: Desktop Environment :: Window Managers :: Enlightenment :: Themes DR17",
  # "Topic :: Desktop Environment :: Window Managers :: Fluxbox",
  # "Topic :: Desktop Environment :: Window Managers :: Fluxbox :: Themes",
  # "Topic :: Desktop Environment :: Window Managers :: FVWM",
  # "Topic :: Desktop Environment :: Window Managers :: FVWM :: Themes",
  # "Topic :: Desktop Environment :: Window Managers :: IceWM",
  # "Topic :: Desktop Environment :: Window Managers :: IceWM :: Themes",
  # "Topic :: Desktop Environment :: Window Managers :: MetaCity",
  # "Topic :: Desktop Environment :: Window Managers :: MetaCity :: Themes",
  # "Topic :: Desktop Environment :: Window Managers :: Oroborus",
  # "Topic :: Desktop Environment :: Window Managers :: Oroborus :: Themes",
  # "Topic :: Desktop Environment :: Window Managers :: Sawfish",
  # "Topic :: Desktop Environment :: Window Managers :: Sawfish :: Themes 0.30",
  # "Topic :: Desktop Environment :: Window Managers :: Sawfish :: Themes pre-0.30",
  # "Topic :: Desktop Environment :: Window Managers :: Waimea",
  # "Topic :: Desktop Environment :: Window Managers :: Waimea :: Themes",
  # "Topic :: Desktop Environment :: Window Managers :: Window Maker",
  # "Topic :: Desktop Environment :: Window Managers :: Window Maker :: Applets",
  # "Topic :: Desktop Environment :: Window Managers :: Window Maker :: Themes",
  # "Topic :: Desktop Environment :: Window Managers :: XFCE",
  # "Topic :: Desktop Environment :: Window Managers :: XFCE :: Themes",
  # "Topic :: Documentation",
  "Topic :: Education",
  # "Topic :: Education :: Computer Aided Instruction (CAI)",
  # "Topic :: Education :: Testing",
  # "Topic :: Games/Entertainment",
  # "Topic :: Games/Entertainment :: Arcade",
  # "Topic :: Games/Entertainment :: Board Games",
  # "Topic :: Games/Entertainment :: First Person Shooters",
  # "Topic :: Games/Entertainment :: Fortune Cookies",
  # "Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)",
  # "Topic :: Games/Entertainment :: Puzzle Games",
  # "Topic :: Games/Entertainment :: Real Time Strategy",
  # "Topic :: Games/Entertainment :: Role-Playing",
  # "Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games",
  # "Topic :: Games/Entertainment :: Simulation",
  # "Topic :: Games/Entertainment :: Turn Based Strategy",
  # "Topic :: Home Automation",
  # "Topic :: Internet",
  # "Topic :: Internet :: File Transfer Protocol (FTP)",
  # "Topic :: Internet :: Finger",
  # "Topic :: Internet :: Log Analysis",
  # "Topic :: Internet :: Name Service (DNS)",
  # "Topic :: Internet :: Proxy Servers",
  # "Topic :: Internet :: WAP",
  # "Topic :: Internet :: WWW/HTTP",
  # "Topic :: Internet :: WWW/HTTP :: Browsers",
  # "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
  # "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
  # "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards",
  # "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
  # "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Page Counters",
  # "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
  # "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
  # "Topic :: Internet :: WWW/HTTP :: Site Management",
  # "Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
  # "Topic :: Internet :: WWW/HTTP :: WSGI",
  # "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
  # "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
  # "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
  # "Topic :: Internet :: Z39.50",
  # "Topic :: Multimedia",
  # "Topic :: Multimedia :: Graphics",
  # "Topic :: Multimedia :: Graphics :: 3D Modeling",
  # "Topic :: Multimedia :: Graphics :: 3D Rendering",
  # "Topic :: Multimedia :: Graphics :: Capture",
  # "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
  # "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
  # "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
  # "Topic :: Multimedia :: Graphics :: Editors",
  # "Topic :: Multimedia :: Graphics :: Editors :: Raster-Based",
  # "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
  # "Topic :: Multimedia :: Graphics :: Graphics Conversion",
  # "Topic :: Multimedia :: Graphics :: Presentation",
  # "Topic :: Multimedia :: Graphics :: Viewers",
  # "Topic :: Multimedia :: Sound/Audio",
  # "Topic :: Multimedia :: Sound/Audio :: Analysis",
  # "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
  # "Topic :: Multimedia :: Sound/Audio :: CD Audio",
  # "Topic :: Multimedia :: Sound/Audio :: CD Audio :: CD Playing",
  # "Topic :: Multimedia :: Sound/Audio :: CD Audio :: CD Ripping",
  # "Topic :: Multimedia :: Sound/Audio :: CD Audio :: CD Writing",
  # "Topic :: Multimedia :: Sound/Audio :: Conversion",
  # "Topic :: Multimedia :: Sound/Audio :: Editors",
  # "Topic :: Multimedia :: Sound/Audio :: MIDI",
  # "Topic :: Multimedia :: Sound/Audio :: Mixers",
  # "Topic :: Multimedia :: Sound/Audio :: Players",
  # "Topic :: Multimedia :: Sound/Audio :: Players :: MP3",
  # "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
  # "Topic :: Multimedia :: Sound/Audio :: Speech",
  # "Topic :: Multimedia :: Video",
  # "Topic :: Multimedia :: Video :: Capture",
  # "Topic :: Multimedia :: Video :: Conversion",
  # "Topic :: Multimedia :: Video :: Display",
  # "Topic :: Multimedia :: Video :: Non-Linear Editor",
  # "Topic :: Office/Business",
  # "Topic :: Office/Business :: Financial",
  # "Topic :: Office/Business :: Financial :: Accounting",
  # "Topic :: Office/Business :: Financial :: Investment",
  # "Topic :: Office/Business :: Financial :: Point-Of-Sale",
  # "Topic :: Office/Business :: Financial :: Spreadsheet",
  # "Topic :: Office/Business :: Groupware",
  # "Topic :: Office/Business :: News/Diary",
  # "Topic :: Office/Business :: Office Suites",
  # "Topic :: Office/Business :: Scheduling",
  # "Topic :: Other/Nonlisted Topic",
  # "Topic :: Printing",
  # "Topic :: Religion",
  "Topic :: Scientific/Engineering",
  # "Topic :: Scientific/Engineering :: Artificial Intelligence",
  # "Topic :: Scientific/Engineering :: Astronomy",
  # "Topic :: Scientific/Engineering :: Atmospheric Science",
  # "Topic :: Scientific/Engineering :: Bio-Informatics",
  # "Topic :: Scientific/Engineering :: Chemistry",
  # "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
  # "Topic :: Scientific/Engineering :: GIS",
  # "Topic :: Scientific/Engineering :: Human Machine Interfaces",
  # "Topic :: Scientific/Engineering :: Image Recognition",
  # "Topic :: Scientific/Engineering :: Information Analysis",
  # "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
  # "Topic :: Scientific/Engineering :: Mathematics",
  # "Topic :: Scientific/Engineering :: Medical Science Apps.",
  # "Topic :: Scientific/Engineering :: Physics",
  # "Topic :: Scientific/Engineering :: Visualization",
  # "Topic :: Security",
  # "Topic :: Security :: Cryptography",
  # "Topic :: Sociology",
  # "Topic :: Sociology :: Genealogy",
  # "Topic :: Sociology :: History",
  "Topic :: Software Development",
  "Topic :: Software Development :: Assemblers",
  "Topic :: Software Development :: Bug Tracking",
  "Topic :: Software Development :: Build Tools",
  "Topic :: Software Development :: Code Generators",
  "Topic :: Software Development :: Compilers",
  "Topic :: Software Development :: Debuggers",
  "Topic :: Software Development :: Disassemblers",
  # "Topic :: Software Development :: Documentation",
  # "Topic :: Software Development :: Embedded Systems",
  # "Topic :: Software Development :: Internationalization",
  "Topic :: Software Development :: Interpreters",
  "Topic :: Software Development :: Libraries",
  "Topic :: Software Development :: Libraries :: Application Frameworks",
  # "Topic :: Software Development :: Libraries :: Java Libraries",
  # "Topic :: Software Development :: Libraries :: Perl Modules",
  # "Topic :: Software Development :: Libraries :: PHP Classes",
  # "Topic :: Software Development :: Libraries :: Pike Modules",
  "Topic :: Software Development :: Libraries :: Python Modules",
  # "Topic :: Software Development :: Libraries :: Ruby Modules",
  # "Topic :: Software Development :: Libraries :: Tcl Extensions",
  # "Topic :: Software Development :: Localization",
  # "Topic :: Software Development :: Object Brokering",
  # "Topic :: Software Development :: Object Brokering :: CORBA",
  "Topic :: Software Development :: Pre-processors",
  # "Topic :: Software Development :: Quality Assurance",
  "Topic :: Software Development :: Testing",
  # "Topic :: Software Development :: Testing :: Traffic Generation",
  # "Topic :: Software Development :: User Interfaces",
  # "Topic :: Software Development :: Version Control",
  # "Topic :: Software Development :: Version Control :: CVS",
  # "Topic :: Software Development :: Version Control :: RCS",
  # "Topic :: Software Development :: Version Control :: SCCS",
  # "Topic :: Software Development :: Widget Sets",
  # "Topic :: System",
  # "Topic :: System :: Archiving",
  # "Topic :: System :: Archiving :: Backup",
  # "Topic :: System :: Archiving :: Compression",
  # "Topic :: System :: Archiving :: Mirroring",
  # "Topic :: System :: Archiving :: Packaging",
  # "Topic :: System :: Benchmark",
  # "Topic :: System :: Boot",
  # "Topic :: System :: Boot :: Init",
  # "Topic :: System :: Clustering",
  # "Topic :: System :: Console Fonts",
  # "Topic :: System :: Distributed Computing",
  "Topic :: System :: Emulators",
  # "Topic :: System :: Filesystems",
  # "Topic :: System :: Hardware",
  # "Topic :: System :: Hardware :: Hardware Drivers",
  # "Topic :: System :: Hardware :: Mainframes",
  # "Topic :: System :: Hardware :: Symmetric Multi-processing",
  # "Topic :: System :: Installation/Setup",
  # "Topic :: System :: Logging",
  # "Topic :: System :: Monitoring",
  # "Topic :: System :: Networking",
  # "Topic :: System :: Networking :: Firewalls",
  # "Topic :: System :: Networking :: Monitoring",
  # "Topic :: System :: Networking :: Monitoring :: Hardware Watchdog",
  # "Topic :: System :: Networking :: Time Synchronization",
  # "Topic :: System :: Operating System",
  # "Topic :: System :: Operating System Kernels",
  # "Topic :: System :: Operating System Kernels :: BSD",
  # "Topic :: System :: Operating System Kernels :: GNU Hurd",
  # "Topic :: System :: Operating System Kernels :: Linux",
  # "Topic :: System :: Power (UPS)",
  # "Topic :: System :: Recovery Tools",
  "Topic :: System :: Shells",
  # "Topic :: System :: Software Distribution",
  # "Topic :: System :: Systems Administration",
  # "Topic :: System :: Systems Administration :: Authentication/Directory",
  # "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
  # "Topic :: System :: Systems Administration :: Authentication/Directory :: NIS",
  # "Topic :: System :: System Shells",
  # "Topic :: Terminals",
  # "Topic :: Terminals :: Serial",
  # "Topic :: Terminals :: Telnet",
  # "Topic :: Terminals :: Terminal Emulators/X Terminals",
  # "Topic :: Text Editors",
  # "Topic :: Text Editors :: Documentation",
  # "Topic :: Text Editors :: Emacs",
  # "Topic :: Text Editors :: Integrated Development Environments (IDE)",
  # "Topic :: Text Editors :: Text Processing",
  # "Topic :: Text Editors :: Word Processors",
  "Topic :: Text Processing",
  "Topic :: Text Processing :: Filters",
  # "Topic :: Text Processing :: Fonts",
  # "Topic :: Text Processing :: General",
  # "Topic :: Text Processing :: Indexing",
  # "Topic :: Text Processing :: Linguistic",
  # "Topic :: Text Processing :: Markup",
  # "Topic :: Text Processing :: Markup :: HTML",
  # "Topic :: Text Processing :: Markup :: LaTeX",
  # "Topic :: Text Processing :: Markup :: SGML",
  # "Topic :: Text Processing :: Markup :: VRML",
  # "Topic :: Text Processing :: Markup :: XML",
  "Topic :: Utilities",
  ])
