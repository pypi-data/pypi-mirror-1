from setuptools import setup, Feature, Extension, Command
from setuptools import Distribution as _Distribution
from setuptools.command.test import test, ScanningLoader
from distutils.errors import DistutilsOptionError
from distutils.command.build_ext import build_ext

import re
import os
import sys

class ITAPSCommand(Command):
    @staticmethod
    def _get_defs(itaps_defs, iface):
        from distutils.sysconfig import parse_makefile

        makefile = parse_makefile(itaps_defs)
        prefix = iface.upper()

        include_dirs = []
        library_dirs = []
        libraries = []

        inc_match = re.compile(r'(?:(?<=\s)|^)-(I)\s*(\S*)')
        for m in inc_match.finditer( makefile[prefix+'_INCLUDES'] ):
            if m.group(2) not in include_dirs:
                include_dirs.append( m.group(2) )

        lib_match = re.compile(r'(?:(?<=\s)|^)-([lL])\s*(\S*)')
        for m in lib_match.finditer( makefile[prefix+'_LIBS'] ):
            if m.group(1) == 'L' and m.group(2) not in library_dirs:
                library_dirs.append( m.group(2) )
            elif m.group(1) == 'l' and m.group(2) not in libraries:
                libraries.append( m.group(2) )

        return (include_dirs, library_dirs, libraries)

    @staticmethod
    def _find_defs(iface, path=None):
        if path:
            name = os.path.join(path, iface+'-Defs.inc')
            if os.path.isfile(name):
                return os.path.normpath(name)
            name = os.path.join(path, 'lib', iface+'-Defs.inc')
            if os.path.isfile(name):
                return os.path.normpath(name)
            raise Exception # TODO
        else:
            # try a bunch of places where iXxx-Defs.inc might be located
            search = [os.path.join(i, '..', 'lib') for i in
                      (os.getenv('PATH') or "").split(':') +
                      (os.getenv('CPATH') or "").split(':') +
                      (os.getenv('LD_LIBRARY_PATH') or "").split(':')] + \
                     ['/usr/local/lib', '/usr/lib']
            for i in search:
                name = os.path.join(i, iface+'-Defs.inc')
                if os.path.isfile(name):
                    return os.path.normpath(name)

    def initialize_options(self):
        self.defs = {}

    def finalize_options(self):
        for iface in ('iMesh', 'iGeom', 'iRel'):
            if not getattr(self.distribution, "with_"+iface):
                continue

            if hasattr(self.distribution, iface+"_dir"):
                path = getattr(self.distribution, iface+"_dir")
                self.defs[iface] = self._get_defs(self._find_defs(iface, path),
                                                  iface)
            else:
                defs_file = self._find_defs(iface)
                if defs_file:
                    self.defs[iface] = self._get_defs(defs_file, iface)


class BuildExtCommand(build_ext, ITAPSCommand):
    def _check_for_ifaces(self):
        from distutils.ccompiler import new_compiler, CompileError
        from shutil import rmtree
        import tempfile

        tmpdir = tempfile.mkdtemp()
        old = os.getcwd()

        os.chdir(tmpdir)
        for iface in ('iMesh', 'iGeom', 'iRel'):
            if not getattr(self.distribution, "with_"+iface):
                continue

            # Try to include the relevant iXxx header, and disable the module
            # if it can't be found
            f = open('%s.c' % iface, 'w')
            f.write("#include <%s.h>\n" % iface)
            f.close()
            try:
                new_compiler().compile([f.name], include_dirs=self.include_dirs)
            except CompileError:
                print >>sys.stderr, ("Warning: unable to find %s.h. " +
                    "itaps.%s module disabled") % (iface, iface)
                self.distribution.features[iface].exclude_from(
                    self.distribution)
        os.chdir(old)
        rmtree(tmpdir)

    def initialize_options(self):
        build_ext.initialize_options(self)
        ITAPSCommand.initialize_options(self)

    def finalize_options(self):
        build_ext.finalize_options(self)
        ITAPSCommand.finalize_options(self)

        # automatically include NumPy header dir if possible
        try:
            import numpy.core as nc
            self.include_dirs.append(os.path.join(nc.__path__[0], 'include'))
        except:
            pass

        # add in libs/dirs from iXxx-Defs.inc
        for m in self.extensions:
            name = m.name.split(".")[1]
            if name == "iBase": # TODO: hack
                for defs in self.defs.itervalues():
                    m.include_dirs.extend(defs[0])
            else:
                defs = self.defs.get(m.name.split(".")[1])
                if defs:
                    m.include_dirs.extend(defs[0])
                    m.library_dirs.extend(defs[1])
                    m.libraries.extend(defs[2])

        # self._check_for_ifaces()


class TestCommand(test):
    user_options = test.user_options + [
        ('log=', 'l', 'log file'),
        ]

    @staticmethod
    def _get_module(module):
        if type(module) == type(''):
            m = __import__(module)
            for part in module.split('.')[1:]:
                m = getattr(m, part)
        return m

    def initialize_options(self):
        test.initialize_options(self)
        self.log = None

    def finalize_options(self):
        test.finalize_options(self)

    def run_tests(self):
        from unittest import TextTestRunner
        verbosity = 2 if self.verbose else 1

        if self.log:
            stream = open(self.log, 'w')
            runner = TextTestRunner(stream=stream, verbosity=verbosity)
        else:
            runner = TextTestRunner(verbosity=verbosity)
        
        module = self._get_module(self.test_suite)
        res = runner.run( ScanningLoader().loadTestsFromModule(module) )

        if self.log:
            stream.close()

        if res.errors or res.failures:
            exit(1)


class DocCommand(Command):
    description = 'build documentation'
    user_options = [
        ('builder=', 'b', 'documentation builder'),
        ('target=',  't', 'target directory'),
        ]

    def initialize_options(self):
        self.builder = 'html'
        self.target = None

    def finalize_options(self):
        if self.target:
            self.target = os.path.abspath(self.target)
        else:
            self.target = '_build/' + self.builder

    def run(self):
        root = 'doc'
        old = os.getcwd()

        os.chdir(root)
        os.system('sphinx-build -b "%s" -d _build/doctrees . "%s"' %
                  (self.builder, self.target))
        os.chdir(old)        

class PerfCommand(Command):
    description = 'build/execute performance tests'
    user_options = [
        ('file=',  'F', 'file or directory containing test file(s)'),
        ('count=', 'c', 'number of times to test'),
        ]

    def initialize_options(self):
        self.file = None
        self.count = 20

    def finalize_options(self):
        if not self.file:
            raise DistutilsOptionError('"file" must be specified')

        try:
            self.count = int(self.count)
        except ValueError:
            raise DistutilsOptionError('"count" option must be an integer')

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

    sub_commands = [
        ('perf_build', None),
        ('perf_run',   None),
        ]

class PerfBuildCommand(ITAPSCommand):
    description = 'build performance tests'

    sep_by = " (separated by '%s')" % os.pathsep
    user_options = [
        ('include-dirs=', 'I',
         'list of directories to search for header files' + sep_by),
        ('libraries=', 'l',
         'external C libraries to link with'),
        ('library-dirs=', 'L',
         'directories to search for external C libraries' + sep_by),
        ]

    def initialize_options(self):
        ITAPSCommand.initialize_options(self)

    def finalize_options(self):
        ITAPSCommand.finalize_options(self)

    def run(self):
        root = 'perf'
        old = os.getcwd()
        os.chdir(root)

        from distutils.ccompiler import new_compiler
        self.compiler = new_compiler()

        objs = self.compiler.compile(
            ['perf.c'], include_dirs=self.defs['iMesh'][0])
        self.compiler.link_executable(
            objs, 'perf', library_dirs=self.defs['iMesh'][1],
            libraries=self.defs['iMesh'][2])

        os.chdir(old)


class PerfRunCommand(Command):
    description = 'execute performance tests'
    user_options = [
        ('file=',  'F', 'file or directory containing test file(s)'),
        ('count=', 'c', 'number of times to test'),
        ]

    def initialize_options(self):
        self.file = None
        self.count = 20

    def finalize_options(self):
        self.set_undefined_options('perf',
                                   ('file', 'file'),
                                   ('count', 'count') )

        if not self.file:
            raise DistutilsOptionError('"file" must be specified')

        try:
            self.count = int(self.count)
        except ValueError:
            raise DistutilsOptionError('"count" option must be an integer')

    def run(self):
        root = 'perf'
        old = os.getcwd()
        os.chdir(root)
        os.system('python perf.py -c%d "%s"' % (self.count, self.file))
        os.chdir(old)



iBase = Extension('itaps.iBase',
                  depends = ['common.h', 'iBase_Python.h'],
                  sources = ['iBase.c']
                  )

iMesh = Feature('iMesh interface',
                standard = True,
                ext_modules = [Extension(
                            'itaps.iMesh',
                            depends = ['common.h', 'errors.h', 'helpers.h', 
                                       'iMesh_Python.h', 'iBase_Python.h',
                                       'iMesh_entSet.inl', 'iMesh_iter.inl',
                                       'iMesh_tag.inl', 'numpy_extensions.h'],
                            sources = ['iMesh.c']
                            )]
                )

iGeom = Feature('iGeom interface',
                standard = True,
                ext_modules = [Extension(
                            'itaps.iGeom',
                            depends = ['common.h', 'errors.h', 'helpers.h',
                                       'iGeom_Python.h', 'iBase_Python.h',
                                       'iGeom_entSet.inl', 'iGeom_iter.inl',
                                       'iGeom_tag.inl', 'numpy_extensions.h'],
                            sources = ['iGeom.c']
                          )]
                )

iRel  = Feature('iRel interface',
                standard = True,
                ext_modules = [Extension(
                            'itaps.iRel',
                            depends = ['common.h', 'errors.h', 'helpers.h',
                                       'iRel_Python.h', 'iBase_Python.h',
                                       'iRel_relation.inl',
                                       'iBase_handleTempl.def',
                                       'numpy_extensions.h'],
                            sources = ['iRel.c']
                          )]
                )

class Distribution(_Distribution):
    global_options = _Distribution.global_options + [
        ('iMesh-dir=', None, 'root directory for iMesh interface'),
        ('iGeom-dir=', None, 'root directory for iGeom interface'),
        ('iRel-dir=',  None, 'root directory for iRel interface'),
        ]

setup(name = 'PyTAPS',
      version = '0.9.0',
      description = 'Python bindings for ITAPS interfaces',
      author = 'Jim Porter',
      author_email = 'jvporter@wisc.edu',

      classifiers = [ 'Development Status :: 4 - Beta',
                      'Environment :: Console',
                      'Intended Audience :: Developers',
                      'Intended Audience :: Science/Research',
                      'License :: OSI Approved :: GNU Library or Lesser ' +
                          'General Public License (LGPL)',
                      'Topic :: Scientific/Engineering',
                      ],

      requires = ['numpy'],
      provides = ['itaps'],

      package_dir = {'itaps': 'pkg'},
      packages = ['itaps'],

      ext_modules = [iBase],
      py_modules = ['itaps.helpers'],
      features = { 'iMesh' : iMesh,
                   'iGeom' : iGeom,
                   'iRel'  : iRel,
                   },
      test_suite = 'test',

      distclass = Distribution,
      cmdclass = { 'build_ext'  : BuildExtCommand,
                   'test'       : TestCommand,
                   'doc'        : DocCommand,
                   'perf'       : PerfCommand,
                   'perf_build' : PerfBuildCommand,
                   'perf_run'   : PerfRunCommand,
                   },
      )
