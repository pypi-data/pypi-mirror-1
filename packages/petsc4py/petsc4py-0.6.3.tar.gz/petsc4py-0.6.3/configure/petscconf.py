# $Id$

# --------------------------------------------------------------------

__all__ = ['setup',
           'Extension',
           'config',
           'build',
           'build_src',
           'build_py',
           'build_ext',
           'build_clib',
           'sdist',
           ]

# --------------------------------------------------------------------

import sys, os
from cStringIO import StringIO

from numpy.distutils.core import setup
from numpy.distutils.core import Extension as _Extension
from numpy.distutils.command.config     import config     as _config
from numpy.distutils.command.build      import build      as _build
from numpy.distutils.command.build_src  import build_src  as _build_src
from numpy.distutils.command.build_py   import build_py   as _build_py
from numpy.distutils.command.build_ext  import build_ext  as _build_ext
from numpy.distutils.command.build_clib import build_clib as _build_clib
from numpy.distutils.command.sdist      import sdist      as _sdist
from numpy.distutils import log

import cfgutils

# --------------------------------------------------------------------

if not hasattr(sys, 'version_info') or \
       sys.version_info < (2, 4, 0,'final'):
    raise SystemExit("Python 2.4 or later is required "
                     "to build PETSc package.")

# --------------------------------------------------------------------


class PetscConfig:

    def __init__(self, petsc_dir, petsc_arch):
        self.build(petsc_dir, petsc_arch)
    
    def __call__(self, extension):
        self.configure(extension)

    def __getitem__(self, item):
        return self.petscconf[item]

    def build(self, petsc_dir, petsc_arch):
        self.PETSC_DIR  = petsc_dir 
        self.PETSC_ARCH = petsc_arch
        self.petscconf = self._get_petsc_conf(self.PETSC_DIR,
                                              self.PETSC_ARCH)
        self.mpiconf  = self._get_mpi_conf(self.petscconf)
        self.language = self._get_lang(self['PETSC_LANGUAGE'])

    def _get_petsc_conf(self, petsc_dir, petsc_arch):
        bmake = os.path.join(petsc_dir,  'bmake')
        petscvars = os.path.join(bmake,'common',    'variables')
        petscconf = os.path.join(bmake, petsc_arch, 'petscconf')
        confstr  = 'PETSC_DIR = %s\n'  % petsc_dir
        confstr += 'PETSC_ARCH = %s\n' % petsc_arch
        confstr += open(petscvars).read()
        confstr += open(petscconf).read()
        confstr += 'PACKAGES_LIBS = ${MPI_LIB} ${X11_LIB} ${BLASLAPACK_LIB}\n'
        confdct = cfgutils.makefile(StringIO(confstr))
        return confdct

    def _get_mpi_conf(self, petsc_conf):
        # try to find MPI configuration from PETSc
        mpicompiler = petsc_conf.get('PCC')
        if mpicompiler:
            for opts in ('-showme:compile -showme:link',    # LAM/OMPI
                         '-shlib -compile_info -link_info', # MPICH
                         '-compile_info -link_info',        # MPICH2
                         ):
                cmdline = '%s %s' % (mpicompiler, opts)
                flags = cfgutils.command(cmdline)
                if flags: # found !
                    return cfgutils.flaglist(flags)
        return { }

    def _get_lang(self, lang):
        langs = {'CONLY':'c', 'CXXONLY':'c++'}
        return langs[lang]

    def configure(self, extension, compiler=None):
        self._configure_extension(extension)
        if compiler is not None:
            self._configure_compiler(compiler)

    def _configure_extension(self, extension):
        # MPI configuration
        self._configure_ext(extension, self.mpiconf)
        # define macros
        macros = [('PETSC_DIR',  self.PETSC_DIR),
                  ('PETSC_ARCH', self.PETSC_ARCH),
                  ('__SDIR__',   '\'\"petsc4py/\"\'')]
        extension.define_macros.extend(macros)
        # includes and libraries
        petsc_inc = cfgutils.flaglist(self['PETSC_INCLUDE'])
        petsc_lib = cfgutils.flaglist(self['PETSC_LIB'])
        self._configure_ext(extension, petsc_inc)
        self._configure_ext(extension, petsc_lib)
        # extra configuration
        cflags = self['PCC_FLAGS'].split()
        try:
            cflags.remove('-Wwrite-strings')
        except ValueError:
            pass
        extension.extra_compile_args.extend(cflags)
        lflags = []
        extension.extra_link_args.extend(lflags)
        
    def _configure_ext(self, ext, dct):
        extdict = ext.__dict__
        for key, values in dct.items():
            if key in extdict:
                for value in values:
                    if value not in extdict[key]:
                        extdict[key].append(value)

    def _configure_compiler(self, compiler):
        pass
        
    def log_info(self):
        if not self.PETSC_DIR: return
        log.info('PETSC_DIR:   %s' % self.PETSC_DIR)
        log.info('PETSC_ARCH:  %s' % self.PETSC_ARCH)
        language    = self['PETSC_LANGUAGE']
        scalar_type = self['PETSC_SCALAR']
        precision   = self['PETSC_PRECISION']
        log.info('language:    %s' % language)
        log.info('scalar-type: %s' % scalar_type)
        log.info('precision:   %s' % precision)


# --------------------------------------------------------------------

class Extension(_Extension):
    pass


# --------------------------------------------------------------------

class config(_config):

    user_options = _config.user_options + [
        ('petsc-dir=', None,
         "define PETSC_DIR, overriding environmental variables"),
        ('petsc-arch=', None,
         "define PETSC_ARCH, overriding environmental variables"),
        ]
    
    def initialize_options(self):
        _config.initialize_options(self)
        self.petsc_dir  = None
        self.petsc_arch = None

    def finalize_options(self):
        _config.finalize_options(self)
        self.petsc_dir  = self._get_petsc_dir(self.petsc_dir)
        self.petsc_arch = self._get_petsc_arch(self.petsc_dir,
                                               self.petsc_arch)
        self.petsc_arch = self.petsc_arch or []

    def _get_petsc_dir(self, petsc_dir):
        petsc_dir = os.path.expandvars(petsc_dir)
        if not petsc_dir or '$PETSC_DIR' in petsc_dir:
            log.warn("PETSC_DIR not specified")
            return None
        petsc_dir = os.path.expanduser(petsc_dir)
        petsc_dir = os.path.abspath(petsc_dir)
        return self._chk_petsc_dir(petsc_dir)

    def _chk_petsc_dir(self, petsc_dir):
        if not os.path.isdir(petsc_dir):
            log.warn('invalid PETSC_DIR:  %s' % petsc_dir)
            return None
        return petsc_dir

    def _get_petsc_arch(self, petsc_dir, petsc_arch):
        if not petsc_dir:
            return None
        petsc_arch = os.path.expandvars(petsc_arch)
        if not petsc_arch or '$PETSC_ARCH' in petsc_arch:
            log.warn("PETSC_ARCH not specified, trying default")
            petscconf = os.path.join(petsc_dir, 'bmake', 'petscconf')
            if not os.path.exists(petscconf):
                log.warn("file '%s' not found" % petscconf)
                return None
            petscconf = StringIO(file(petscconf).read())
            petscconf = cfgutils.makefile(petscconf)
            petsc_arch = petscconf.get('PETSC_ARCH')
            if not petsc_arch:
                log.warn("default PETSC_ARCH not found")
                return None
        petsc_arch = petsc_arch.split(',')
        return self._chk_petsc_arch(petsc_dir, petsc_arch)
        
    def _chk_petsc_arch(self, petsc_dir, petsc_arch):
        valid_archs = []
        for arch in petsc_arch:
            arch_path = os.path.join(petsc_dir, 'bmake', arch)
            if not os.path.isdir(arch_path):
                log.warn("invalid PETSC_ARCH: '%s' (ignored)" % arch)
                continue
            valid_archs.append(arch)
        if not valid_archs:
            log.warn("could not find a valid PETSC_ARCH")
            return None
        return valid_archs

    def _log_info(self):
        log.info('-' * 70)
        log.info('PETSC_DIR:   %s' % self.petsc_dir)
        for arch in self.petsc_arch:
            config = PetscConfig(self.petsc_dir, arch)
            language = config['PETSC_LANGUAGE']
            compiler = config['PCC']
            scalar_type = config['PETSC_SCALAR']
            precision = config['PETSC_PRECISION']
            log.info('-'*70)
            log.info('PETSC_ARCH:  %s' % config.PETSC_ARCH)
            log.info('language:    %s' % language)
            log.info('compiler:    %s' % compiler)
            log.info('scalar-type: %s' % scalar_type)
            log.info('precision:   %s' % precision)
        log.info('-' * 70)

    def run(self):
        _config.run(self)
        if self.petsc_dir and self.petsc_arch:
            self._log_info()


class build(_build):

    def initialize_options(self):
        _build.initialize_options(self)
        self.petsc_dir  = None
        self.petsc_arch = None

    def finalize_options(self):
        _build.finalize_options(self)
        self.set_undefined_options('config',
                                   ('petsc_dir',  'petsc_dir'),
                                   ('petsc_arch', 'petsc_arch'))


class build_py(_build_py):

    def build_package_data (self):
        _build_py.build_package_data(self)
        for package, src_dir, build_dir, filenames in self.data_files:
            for filename in filenames:
                if filename == 'petsc.cfg':
                    target = os.path.join(build_dir, filename)
                    if os.path.exists(target):
                        self._config(target)
                        break 

    def _config(self, py_file):
        PETSC_DIR  = '$PETSC_DIR'
        PETSC_ARCH = '$PETSC_ARCH'
        config_py = open(py_file, 'r')
        config_data = config_py.read()
        config_py.close()
        if '%(PETSC_DIR)s' not in config_data:
            return # already configured
        config = self.get_finalized_command('config')
        petsc_dir  = config.petsc_dir
        petsc_arch = config.petsc_arch
        if petsc_dir:
            PETSC_DIR  = petsc_dir 
        if petsc_arch:
            PETSC_ARCH = petsc_arch[0]
        log.info('writing %s' % py_file)
        config_py = open(py_file, 'w')
        config_py.write(config_data % vars())
        config_py.close()
        

class build_src(_build_src):

    def initialize_options(self):
        _build_src.initialize_options(self)
        self.petsc_dir  = None
        self.petsc_arch = None

    def finalize_options(self):
        _build_src.finalize_options(self)
        self.set_undefined_options('build',
                                   ('petsc_dir',  'petsc_dir'),
                                   ('petsc_arch', 'petsc_arch'))
        self.inplace = True
        if not self.petsc_dir: return
        if not self.petsc_arch: return
        macros = ['-DPETSC_DIR=%s'  % self.petsc_dir,
                  '-DPETSC_ARCH=%s' % self.petsc_arch[0]]
        self.swigflags.extend(macros)
        self.swigflags.append('-O')
        self.swigflags.append('-fcompact')
        #self.swigflags.append('-noproxy')

    def swig_sources(self, sources, extension):
        all_src = _build_src.swig_sources(self, sources, extension)
        sources, py_files = self.filter_py_files(all_src)
        for py_file in py_files:
            if os.path.exists(py_file):
                os.remove(py_file)
        return sources

    def run(self):
        if self.petsc_dir and self.petsc_arch:
            log.info('PETSC_DIR:  %s' % self.petsc_dir)
            log.info('PETSC_ARCH: %s' % self.petsc_arch[0])
            _build_src.run(self)
        

class build_ext(_build_ext):

    def initialize_options(self):
        _build_ext.initialize_options(self)
        self.petsc_dir  = None
        self.petsc_arch = None
        self._outputs = []

    def finalize_options(self):
        _build_ext.finalize_options(self)
        self.set_undefined_options('build',
                                   ('petsc_dir',  'petsc_dir'),
                                   ('petsc_arch', 'petsc_arch'))

    def _copy_ext(self, ext, petsc_arch):
        extclass = ext.__class__
        fullname = self.get_ext_fullname(ext.name)
        _frags = fullname.split('.')
        _frags.insert(-1, petsc_arch)
        name = '.'.join(_frags)
        srcs = list(ext.sources)
        incs = list(ext.include_dirs)
        macs = list(ext.define_macros)
        deps = list(ext.depends)
        lang = ext.language
        return extclass(name, sources=srcs, depends=deps,
                        include_dirs=incs, define_macros=macs, language=lang)

    def _build_ext_arch(self, ext, arch):
        build_temp_orig = self.build_temp
        self.build_temp = os.path.join(build_temp_orig, arch)
        _build_ext.build_extension(self, ext)
        self.build_temp = build_temp_orig

    def build_extension(self, ext):
        if not isinstance(ext, Extension):
            _build_ext.build_extension(self, ext)
            return
        petsc_arch = [arch for arch in self.petsc_arch if arch]
        for arch in petsc_arch:
            config = PetscConfig(self.petsc_dir, arch)
            if ext.language == config.language:
                config.log_info()
                newext = self._copy_ext(ext, arch)
                config.configure(newext)
                self._build_ext_arch(newext, arch)

    def get_outputs(self):
        self.check_extensions_list(self.extensions)
        outputs = []
        for ext in self.extensions:
            fullname = self.get_ext_fullname(ext.name)
            filename = self.get_ext_filename(fullname)
            if isinstance(ext, Extension):
                head, tail = os.path.split(filename)
                for arch in self.petsc_arch:
                    outfile = os.path.join(self.build_lib,
                                           head,arch,tail)
                    outputs.append(outfile)
            else:
                outfile = os.path.join(self.build_lib,filename)
                outputs.append(outfile)
        outputs = list(set(outputs))
        return outputs


class build_clib(_build_clib):
    pass


class sdist(_sdist):

    def run(self):
        self.run_command('build_src')
        _sdist.run(self)


# --------------------------------------------------------------------
