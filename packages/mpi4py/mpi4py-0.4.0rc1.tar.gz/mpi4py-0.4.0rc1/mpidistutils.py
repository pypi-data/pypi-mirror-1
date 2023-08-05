# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Revision:  $Revision: 1.18 $
# Date:      $Date: 2006/10/02 21:55:04 $
# Copyright: This module has been placed in the public domain.

# --------------------------------------------------------

# Environmental variables to look for configuration
MPICC_ENV  = ['MPI4PY_CC',  'MPICC']
MPICXX_ENV = ['MPI4PY_CXX', 'MPICXX']
MPICFG_ENV = ['MPI4PY_CFG', 'MPI_CONFIG', 'MPI_CFG']

# Default values to use for configuration
MPICC  = ['mpicc']
MPICXX = ['mpicxx', 'mpiCC', 'mpic++']
MPICFG = ('mpi', 'mpi.cfg')

# --------------------------------------------------------

import os
from distutils import sysconfig
from distutils.spawn import find_executable
from distutils import log


def customize_compiler(compiler, environ=None):
    """Do any platform-specific customization of a CCompiler instance.

    Mainly needed on Unix, so we can plug in the information that
    varies across Unices and is stored in Python's Makefile.
    """
    if environ is None:
        environ = os.environ
    if compiler.compiler_type == 'unix':
        (cc, cxx, opt, basecflags, ccshared, ldshared, so_ext) = \
            sysconfig.get_config_vars('CC', 'CXX', 'OPT', 'BASECFLAGS', 'CCSHARED', 'LDSHARED', 'SO')

        if environ.has_key('CC'):
            cc = environ['CC']
        if environ.has_key('CXX'):
            cxx = environ['CXX']
        if environ.has_key('LDSHARED'):
            ldshared = environ['LDSHARED']
        if environ.has_key('CPP'):
            cpp = environ['CPP']
        else:
            cpp = cc + " -E"           # not always
        if environ.has_key('LDFLAGS'):
            ldshared = ldshared + ' ' + environ['LDFLAGS']
        if basecflags:
            opt = basecflags + ' ' + opt
        if environ.has_key('CFLAGS'):
            opt = opt + ' ' + environ['CFLAGS']
            ldshared = ldshared + ' ' + environ['CFLAGS']
        if environ.has_key('CPPFLAGS'):
            cpp = cpp + ' ' + environ['CPPFLAGS']
            opt = opt + ' ' + environ['CPPFLAGS']
            ldshared = ldshared + ' ' + environ['CPPFLAGS']

        cc_cmd = cc + ' ' + opt
        compiler.set_executables(
            preprocessor=cpp,
            compiler=cc_cmd,
            compiler_so=cc_cmd + ' ' + ccshared,
            compiler_cxx=cxx,
            linker_so=ldshared,
            linker_exe=cc)

        compiler.shared_lib_extension = so_ext

def customize_mpi_environ(mpicc, mpicxx=None, environ=None):
    if environ is None:
        environ = dict(os.environ)
    if mpicc: # C compiler
        environ['CC'] = mpicc
    if mpicxx: # C++ compiler
        environ['CXX'] = mpicxx
    mpild = mpicc or mpicxx
    if mpild: # linker for shared
        ldshared = sysconfig.get_config_var('LDSHARED')
        if not ldshared:
            environ['LDSHARED'] = mpild
        else:
            ldshared = ldshared.split(' ', 1)
            if len(ldshared) == 2:
                environ['LDSHARED'] = mpild + ' ' + ldshared[1]
    return environ

def _find_mpi_compiler(envvars, executables, path=None):
    # search in environment
    if envvars:
        if isinstance(envvars, str):
            envvars = (envvars,)
        for var in envvars:
            cmd = os.environ.get(var)
            if cmd is not None: return cmd
    # search in path
    if executables:
        if isinstance(executables, str):
            executables = (executables,)
        for exe in executables:
            cmd = find_executable(exe, path)
            if cmd is not None: return cmd
    # nothing found
    return None


# --------------------------------------------------------

from ConfigParser import ConfigParser
from ConfigParser import Error as ConfigParserError

def _config_parser(section, filenames, raw=False, vars=None):
    """
    Returns a dictionary of options obtained by parsing configuration
    files.
    """
    parser = ConfigParser()
    try:
        parser.read(filenames.split(','))
    except ConfigParserError:
        log.error("error: parsing configuration file/s '%s'", filenames)
        return None
    if not parser.has_section(section):
        log.error("error: section '%s' not found "
                  "in configuration file/s '%s'", section, filenames)
        return None
    config_info = {}
    for k, v in parser.items(section, raw, vars):
        config_info[k] = v.replace('\\',' ').split()
    if 'define_macros' in config_info:
        macros = []
        for m in config_info['define_macros'] :
            try: # "-DFOO=blah"
                idx = m.index("=")
                macro = (m[:idx], m[idx+1:] or None)
            except ValueError: # bare "-DFOO"
                macro = (m, None)
            macros.append(macro)
        config_info['define_macros'] = macros
    return config_info


def _find_mpi_config(section, filenames,
                     envvars=None, defaults=None):
    if not section and not filenames and envvars:
        # look in environment
        if isinstance(envvars, str):
            envvars = (envvars,)
        for var in envvars:
            if var in os.environ:
                section, filenames = os.environ[var], None
                break
    if section and ',' in section:
        section, filenames = section.split(',', 1)
    if defaults:
        if not section:
            section = defaults[0]
        if not filenames:
            fname = defaults[1]
            if os.path.exists(fname):
                filenames = fname
    # parse configuraration
    if section and filenames:
        config_info = _config_parser(section, filenames)
        return section, filenames, config_info
    else:
        return section, filenames, None


def _configure(extension, confdict):
    if confdict is None: return
    for key, value in confdict.iteritems():
        if hasattr(extension, key):
            item = getattr(extension, key)
            if type(item) is list:
                if type(value) is list:
                    for v in value:
                        if v not in item:
                            item.append(v)
                else:
                    if value not in item:
                        item.append(value)
            else:
                setattr(extension, key, value)

# --------------------------------------------------------

from distutils.command import config as cmd_config
from distutils.command import build as cmd_build
from distutils.command import build_ext as cmd_build_ext
from distutils.command import sdist as cmd_sdist
from distutils.errors import DistutilsPlatformError


ConfigTests = [
    # ----------------------------------------------------------------
    ('MPI_VERSION',
     'int version; version = MPI_VERSION;'),
    ('MPI_GET_VERSION',
     'MPI_Get_version((int*)0,(int*)0);'),
    # ----------------------------------------------------------------
    ('MPI_INIT_THREAD',
     "MPI_Init_thread((int*)0,(char***)0,MPI_THREAD_SINGLE,(int*)0);"),
    ('MPI_QUERY_THREAD',
     "MPI_Query_thread((int*)0);"),
    ('MPI_IS_THREAD_MAIN',
     "MPI_Is_thread_main((int*)0);"),
    # ----------------------------------------------------------------
    ('MPI_WCHAR',
     'MPI_Datatype datatype; datatype = MPI_WCHAR;'),
    ('MPI_SIGNED_CHAR',
     'MPI_Datatype datatype; datatype = MPI_SIGNED_CHAR;'),
    ('MPI_LONG_LONG',
     'MPI_Datatype datatype; datatype = MPI_LONG_LONG;'),
    ('MPI_LONG_LONG_INT',
     'MPI_Datatype datatype; datatype = MPI_LONG_LONG_INT;'),
    ('MPI_UNSIGNED_LONG_LONG',
     'MPI_Datatype datatype; datatype = MPI_UNSIGNED_LONG_LONG;'),
    ('MPI_TYPE_GET_EXTENT',
     'MPI_Type_get_extent(MPI_DATATYPE_NULL,(MPI_Aint*)0,(MPI_Aint*)0);'),
    ('MPI_TYPE_DUP',
     'MPI_Type_dup(MPI_DATATYPE_NULL,(MPI_Datatype*)0);'),
    ('MPI_TYPE_CREATE_INDEXED_BLOCK',
     'MPI_Type_create_indexed_block(0,0,(int*)0,MPI_DATATYPE_NULL,(MPI_Datatype*)0);'),
    ('MPI_TYPE_CREATE_HVECTOR',
     'MPI_Type_create_hvector(0,0,(MPI_Aint)0,MPI_DATATYPE_NULL,(MPI_Datatype*)0);'),
    ('MPI_TYPE_CREATE_HINDEXED',
     'MPI_Type_create_hindexed(0,(int*)0,(MPI_Aint*)0,MPI_DATATYPE_NULL,(MPI_Datatype*)0);'),
    ('MPI_TYPE_CREATE_STRUCT',
     'MPI_Type_create_struct(0,(int*)0,(MPI_Aint*)0,(MPI_Datatype*)0,(MPI_Datatype*)0);'),
    ('MPI_TYPE_CREATE_SUBARRAY',
     'MPI_Type_create_subarray(0,(int*)0,(int*)0,(int*)0,0,MPI_DATATYPE_NULL,(MPI_Datatype*)0);'),
    ('MPI_TYPE_CREATE_DARRAY',
     'MPI_Type_create_darray(0,0,0,(int*)0,(int*)0,(int*)0,(int*)0,0,MPI_DATATYPE_NULL,(MPI_Datatype*)0);'),
    ('MPI_TYPE_CREATE_RESIZED',
     'MPI_Type_create_resized(MPI_DATATYPE_NULL,0,0,(MPI_Datatype*)0);'),
    ('MPI_TYPE_GET_TRUE_EXTENT',
     'MPI_Type_get_true_extent(MPI_DATATYPE_NULL,(MPI_Aint*)0,(MPI_Aint*)0);'),
    ('MPI_GET_ADDRESS',
     'MPI_Get_address((void*)0,(MPI_Aint*)0);'),
    ('MPI_PACK_EXTERNAL',
     'MPI_Pack_external((char*)0,(void*)0,0,MPI_DATATYPE_NULL,(void*)0,0,(MPI_Aint*)0);'),
    ('MPI_UNPACK_EXTERNAL',
     'MPI_Unpack_external((char*)0,(void*)0,0,(MPI_Aint*)0,(void*)0,0,MPI_DATATYPE_NULL);'),
    ('MPI_PACK_EXTERNAL_SIZE',
     'MPI_Pack_external_size((char*)0,0,MPI_DATATYPE_NULL,(MPI_Aint*)0);'),
    # ----------------------------------------------------------------
    ('MPI_STATUS_IGNORE' ,
     'MPI_Status *status; status = MPI_STATUS_IGNORE;'),
    ('MPI_STATUSES_IGNORE' ,
     'MPI_Status *status; status = MPI_STATUSES_IGNORE;'),
    ('MPI_REQUEST_GET_STATUS' ,
     'MPI_Request_get_status(MPI_REQUEST_NULL,(int*)0,(MPI_Status*)0);'),
    # ----------------------------------------------------------------
    ('MPI_IN_PLACE',
     'MPI_Scan(MPI_IN_PLACE,(void*)0,0,MPI_DATATYPE_NULL,MPI_OP_NULL,MPI_COMM_NULL);'),
    ('MPI_ROOT',
     'MPI_Bcast((void*)0,0,MPI_DATATYPE_NULL,MPI_ROOT,MPI_COMM_NULL);'),
    ('MPI_EXSCAN',
     'MPI_Exscan((void*)0,(void*)0,0,MPI_DATATYPE_NULL,MPI_OP_NULL,MPI_COMM_NULL);'),
    # ----------------------------------------------------------------
    ('MPI_COMM_GET_ERRHANDLER' ,
     'MPI_Comm_get_errhandler(MPI_COMM_NULL,(MPI_Errhandler*)0);'),
    ('MPI_COMM_SET_ERRHANDLER' ,
     'MPI_Comm_set_errhandler(MPI_COMM_NULL,MPI_ERRHANDLER_NULL);'),
    ('MPI_COMM_CALL_ERRHANDLER',
     'MPI_Comm_call_errhandler(MPI_COMM_NULL,0);'),
    # ----------------------------------------------------------------
    ('MPI_INFO_NULL',
     'MPI_Info info; info = MPI_INFO_NULL;'),
    ('MPI_INFO_CREATE',
     'MPI_Info_create((MPI_Info*)0);'),
    ('MPI_INFO_FREE',
     'MPI_Info_free((MPI_Info*)0);'),
    ('MPI_ERR_INFO',       'int ierr; ierr = MPI_ERR_INFO;'),
    ('MPI_ERR_INFO_KEY',   'int ierr; ierr = MPI_ERR_INFO_KEY;'),
    ('MPI_ERR_INFO_VALUE', 'int ierr; ierr = MPI_ERR_INFO_VALUE;'),
    ('MPI_ERR_INFO_NOKEY', 'int ierr; ierr = MPI_ERR_INFO_NOKEY;'),
    # ----------------------------------------------------------------
    ('MPI_WIN_NULL',
     'MPI_Win win; win = MPI_WIN_NULL;'),
    ('MPI_WIN_CREATE',
     'MPI_Win_create((void*)0,(MPI_Aint)0,0,MPI_INFO_NULL,MPI_COMM_NULL,(MPI_Win*)0);'),
    ('MPI_WIN_FREE',
     'MPI_Win_free((MPI_Win*)0);'),
    ('MPI_WIN_TEST',
     'MPI_Win_test(MPI_WIN_NULL,(int*)0);'),
    ('MPI_WIN_LOCK',
     'MPI_Win_lock(0,0,0,MPI_WIN_NULL);'),
    ('MPI_WIN_UNLOCK',
     'MPI_Win_unlock(0,MPI_WIN_NULL);'),
    ('MPI_LOCK_EXCLUSIVE', 'int lock; lock = MPI_LOCK_EXCLUSIVE;'  ),
    ('MPI_LOCK_SHARED'   , 'int lock; lock = MPI_LOCK_SHARED;'     ),
    ('MPI_ERR_WIN'         , 'int ierr; ierr = MPI_ERR_WIN;'         ),
    ('MPI_ERR_BASE'        , 'int ierr; ierr = MPI_ERR_BASE;'        ),
    ('MPI_ERR_SIZE'        , 'int ierr; ierr = MPI_ERR_SIZE;'        ),
    ('MPI_ERR_DISP'        , 'int ierr; ierr = MPI_ERR_DISP;'        ),
    ('MPI_ERR_LOCKTYPE'    , 'int ierr; ierr = MPI_ERR_LOCKTYPE;'    ),
    ('MPI_ERR_ASSERT'      , 'int ierr; ierr = MPI_ERR_ASSERT;'      ),
    ('MPI_ERR_RMA_CONFLICT', 'int ierr; ierr = MPI_ERR_RMA_CONFLICT;'),
    ('MPI_ERR_RMA_SYNC'    , 'int ierr; ierr = MPI_ERR_RMA_SYNC;'    ),
    ('MPI_REPLACE',
     'MPI_Op op; op = MPI_REPLACE;'),
    # ----------------------------------------------------------------
    ('MPI_FILE_NULL',
     'MPI_File file; file = MPI_FILE_NULL;'),
    ('MPI_FILE_OPEN',
     'MPI_File_open(MPI_COMM_NULL,(char*)0,0,MPI_INFO_NULL,(MPI_File*)0);'),
    ('MPI_FILE_CLOSE',
     'MPI_File_close((MPI_File*)0);'),
    ('MPI_DISPLACEMENT_CURRENT',
     'MPI_Offset disp; disp = MPI_DISPLACEMENT_CURRENT;'),
    ('MPI_MAX_DATAREP_STRING', 'int len; len = MPI_MAX_DATAREP_STRING;'),
    # ----------------------------------------------------------------
    ('MPI_ALLOC_MEM',
     'MPI_Alloc_mem((MPI_Aint)0,MPI_INFO_NULL,(void*)0);'             ),
    ('MPI_FREE_MEM',
     'MPI_Free_mem((void*)0);'                                       ),
    ('MPI_ERR_NO_MEM', 'int ierr; ierr = MPI_ERR_NO_MEM;'            ),
    # ----------------------------------------------------------------
    ('MPI_OPEN_PORT',
     'MPI_Open_port(MPI_INFO_NULL,(char*)0);'),
    ('MPI_CLOSE_PORT',
     'MPI_Close_port((char*)0);'),
    ('MPI_PUBLISH_NAME',
     'MPI_Publish_name((char*)0, MPI_INFO_NULL,(char*)0);'),
    ('MPI_UNPUBLISH_NAME',
     'MPI_Unpublish_name((char*)0, MPI_INFO_NULL,(char*)0);'),
    ('MPI_LOOKUP_NAME',
     'MPI_Lookup_name((char*)0, MPI_INFO_NULL,(char*)0);'),
    ('MPI_COMM_ACCEPT',
     'MPI_Comm_accept((char*)0,MPI_INFO_NULL,0,MPI_COMM_NULL,(MPI_Comm*)0);'),
    ('MPI_COMM_CONNECT',
     'MPI_Comm_connect((char*)0,MPI_INFO_NULL,0,MPI_COMM_NULL,(MPI_Comm*)0);'),
    ('MPI_COMM_DISCONNECT',
     'MPI_Comm comm = MPI_COMM_NULL; MPI_Comm_disconnect(&comm);'),
    ('MPI_COMM_SPAWN',
     'MPI_Comm_spawn((char*)0,(char**)0,0,' \
     'MPI_INFO_NULL,0,MPI_COMM_NULL,(MPI_Comm*)0,(int*)0);'),
    ('MPI_COMM_GET_PARENT',
     'MPI_Comm_get_parent((MPI_Comm*)0);'),
    ('MPI_COMM_JOIN',
     'MPI_Comm_join(0,(MPI_Comm*)0);'),
    ('MPI_ERR_NAME',    'int ierr; ierr = MPI_ERR_NAME;'),
    ('MPI_ERR_PORT',    'int ierr; ierr = MPI_ERR_PORT;'),
    ('MPI_ERR_SERVICE', 'int ierr; ierr = MPI_ERR_SERVICE;'),
    ('MPI_ERR_SPAWN',   'int ierr; ierr = MPI_ERR_SPAWN;'),
    # ----------------------------------------------------------------
    ('MPI_TYPE_GET_NAME',
     'MPI_Type_get_name(MPI_DATATYPE_NULL,(char*)0,(int*)0);'),
    ('MPI_TYPE_SET_NAME',
     'MPI_Type_set_name(MPI_DATATYPE_NULL,(char*)0);'),
    ('MPI_COMM_GET_NAME',
     'MPI_Comm_get_name(MPI_COMM_NULL,(char*)0,(int*)0);'),
    ('MPI_COMM_SET_NAME',
     'MPI_Comm_set_name(MPI_COMM_NULL,(char*)0);'),
    ('MPI_WIN_GET_NAME',
     'MPI_Win_get_name(MPI_WIN_NULL,(char*)0,(int*)0);'),
    ('MPI_WIN_SET_NAME',
     'MPI_Win_set_name(MPI_WIN_NULL,(char*)0);'),
    ('MPI_MAX_OBJECT_NAME', 'int len; len = MPI_MAX_OBJECT_NAME;'),
    # ----------------------------------------------------------------
    ('MPI_ERR_KEYVAL', 'int ierr; ierr = MPI_ERR_KEYVAL;'),
    # ----------------------------------------------------------------
    ]

_ConfigTest = """\
int main(int argc, char **argv) {
  MPI_Init(&argc,&argv);
  MPI_Finalize();
  return 0;
}
"""


mpi_cmd_opts = [

    ('mpicc=',   None,
     "MPI C compiler command, "
     "overrides environmental variables 'MPICC' "
     "(defaults to 'mpicc' if available)"),

    ('mpicxx=',  None,
     "MPI C++ compiler command, "
     "overrides environmental variables 'MPICXX' "
     "(defaults to 'mpicxx', 'mpiCC', or 'mpic++' if any is available)"),

    ('mpi-cfg=', None,
     "specify a configuration file to look for MPI includes/libraries "
     "(defaults to 'mpi.cfg')"),

    ('mpi=',     None,
     "specify a configuration section, "
     "and an optional comma-separated list of configuration files "
     "(e.g. --mpi=section,file1,file2,file3),"
     "to look for MPI includes/libraries, "
     "overrides environmental variables 'MPICFG' "
     "(defaults to section 'mpi' in configuration file 'mpi.cfg')"),
    
    ('try-mpi-2', None,
     "test for availability of MPI 2 features"),
    ]



class config(cmd_config.config):

    user_options = cmd_config.config.user_options + mpi_cmd_opts

    def initialize_options(self):
        cmd_config.config.initialize_options(self)
        self.noisy = 0
        self.mpicc = None
        self.mpicxx = None
        self.mpi = None
        self.mpi_cfg = None
        self.try_mpi_2 = None
        
    def finalize_options(self):
        cmd_config.config.finalize_options(self)
        if not self.noisy:
            self.dump_source = 0
        
    def find_mpi_compiler(self, envvars, executables, path=None):
        return _find_mpi_compiler(envvars, executables, path)

    def run(self):
        # test MPI C compiler
        mpicc = self.mpicc
        if mpicc is None:
            mpicc = self.find_mpi_compiler(MPICC_ENV, MPICC)
        if mpicc:
            log.info("MPI C compiler:    %s", mpicc  or 'not found')
            self.compiler = None
            self._check_compiler()
            environ = customize_mpi_environ(mpicc, None)
            customize_compiler(self.compiler, environ)
            self.try_link(_ConfigTest, headers=['mpi.h'], lang='c')
        # test MPI C++ compiler
        mpicxx = self.mpicxx
        if mpicxx is None:
            mpicxx = self.find_mpi_compiler(MPICXX_ENV, MPICXX)
        if mpicxx:
            log.info("MPI C++ compiler:  %s", mpicxx or 'not found')
            self.compiler = None
            self._check_compiler()
            environ = customize_mpi_environ(None, mpicxx)
            customize_compiler(self.compiler, environ)
            if self.compiler.compiler_type in ('unix', 'cygwin', 'mingw32'):
                self.compiler.compiler_so[0] = mpicxx
                self.compiler.linker_exe[0] = mpicxx
            self.try_link(_ConfigTest, headers=['mpi.h'], lang='c++')
        # test configuration in specified section and file
        if self.mpi or self.mpi_cfg:
            sct, fn, cfg = _find_mpi_config(self.mpi, self.mpi_cfg,
                                            MPICFG_ENV, MPICFG)
            log.info("MPI configuration: "
                     "section '%s' from file/s '%s'", sct, fn)
            _configure(self, cfg)
            self.compiler = None
            self._check_compiler()
            self.try_link(_ConfigTest, headers=['mpi.h'], lang='c')

    def get_config_macros(self, test_list, compiler, config_info):
        self.compiler = compiler
        _configure(self, config_info)
        # run configure tests
        macros = []
        for name, code in test_list:
            result = self.try_config_test(code)
            macros.append(('HAVE_%s' % name, int(result)))
        return macros
        
    def try_config_test(self, lines):
        if type(lines) is not str:
            lines = '\n  '.join(lines)
        body = "int main(void) {\n  %s\n  return 0;\n}\n" % lines
        return self.try_link(body, headers=['mpi.h'],
                             include_dirs=self.include_dirs,
                             libraries=self.libraries,
                             library_dirs=self.library_dirs)
        

class build(cmd_build.build):

    user_options = cmd_build.build.user_options + mpi_cmd_opts
    
    def initialize_options(self):
        cmd_build.build.initialize_options(self)
        self.mpicc = None
        self.mpicxx = None
        self.mpi = None
        self.mpi_cfg = None
        self.try_mpi_2 = None
        
    def finalize_options(self):
        cmd_build.build.finalize_options(self)
        config_cmd = self.get_finalized_command('config')
        if isinstance(config_cmd,  config):
            self.set_undefined_options('config',
                                       ('mpicc',    'mpicc'),
                                       ('mpicxx',   'mpicxx'),
                                       ('mpi',      'mpi'),
                                       ('mpi_cfg',  'mpi_cfg'),
                                       ('try_mpi_2','try_mpi_2'))
        

class build_ext(cmd_build_ext.build_ext):

    user_options = cmd_build_ext.build_ext.user_options + mpi_cmd_opts

    def initialize_options(self):
        cmd_build_ext.build_ext.initialize_options(self)
        self.mpicc = None
        self.mpicxx = None
        self.mpi = None
        self.mpi_cfg = None
        self.try_mpi_2 = None

    def finalize_options(self):
        cmd_build_ext.build_ext.finalize_options(self)
        build_cmd = self.get_finalized_command('build')
        if isinstance(build_cmd,  build):
            self.set_undefined_options('build',
                                       ('mpicc',    'mpicc'),
                                       ('mpicxx',   'mpicxx'),
                                       ('mpi',      'mpi'),
                                       ('mpi_cfg',  'mpi_cfg'),
                                       ('try_mpi_2','try_mpi_2'))

    def build_extensions(self):
        # First, sanity-check the 'extensions' list
        self.check_extensions_list(self.extensions)
        # parse configuration file and  configure compiler
        config_info = self.configure_extensions()
        mpicc = mpicxx = None
        if config_info:
            mpicc = config_info.get('mpicc',[None])[0]
            mpicxx = config_info.get('mpicxx',[None])[0]
        compiler = self.configure_compiler(mpicc=mpicc, mpicxx=mpicxx)
        # extra configuration, MPI 2 features
        if self.try_mpi_2:
            log.info('testing for MPI 2 features')
            config = self.get_finalized_command('config')
            get_macros = config.get_config_macros
            macros = get_macros(ConfigTests, compiler, config_info)
            for (name, value) in macros:
                self.compiler.define_macro(name, value)
                log.info('%s %d' % (name, value))
        # build extensions
        for ext in self.extensions:
            self.build_extension(ext)

    def configure_compiler(self, compiler=None, mpicc=None, mpicxx=None):
        mpicc, mpicxx = self.mpicc or mpicc, self.mpicxx or mpicxx
        if mpicc is None:
            mpicc = self.find_mpi_compiler(MPICC_ENV, MPICC)
        if mpicxx is None:
            mpicxx = self.find_mpi_compiler(MPICXX_ENV, MPICXX)
        if compiler is None:
            compiler = self.compiler
        log.info("MPI C compiler:    %s", mpicc  or 'not found')
        log.info("MPI C++ compiler:  %s", mpicxx or 'not found')
        environ = customize_mpi_environ(mpicc, mpicxx)
        customize_compiler(compiler, environ)
        return compiler

    def find_mpi_compiler(self, envvars, executables, path=None):
        return _find_mpi_compiler(envvars, executables, path)

    def configure_extensions(self):
        config_info = self.find_mpi_config(self.mpi, self.mpi_cfg,
                                           MPICFG_ENV, MPICFG)
        if config_info:
            for ext in self.extensions:
                self.configure_extension(ext, config_info)
        return config_info

    def find_mpi_config(self, section, filenames,
                        envvars=None, defaults=None):
        # parse configuration file
        sect, fnames, cfg_info = _find_mpi_config(section, filenames,
                                                  envvars, defaults)
        if cfg_info:
            log.info("MPI configuration: "
                     "from section '%s' in file/s '%s'", sect, fnames)
        return cfg_info
        
    def configure_extension(self, extension, config_info):
        _configure(extension, config_info)
