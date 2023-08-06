from distutils.core import setup
from distutils.util import split_quoted
from distutils.extension import Extension
from distutils.command.build_ext import build_ext
import subprocess
import os

try:
    import _winreg
except ImportError:
    _winreg = None

# This is the only way to make old-style classes respect setter properties. :(
class MysqlExtension(Extension, object):
    def __init__(self, *a, **kw):
        self.use_mysql_flags = True
        self._extra_compile_args = []
        self._extra_link_args = []
        self._mysql_compile_args = []
        self._mysql_link_args = []
        self.get_mysql_compile_args = self.get_mysql_link_args = None
        Extension.__init__(self, *a, **kw)
    
    def _get_extra_compile_args(self):
        if not self._mysql_compile_args and self.get_mysql_compile_args:
            self._mysql_compile_args = self.get_mysql_compile_args()
        return self._extra_compile_args + self._mysql_compile_args
    
    def _set_extra_compile_args(self, args):
        self._extra_compile_args = args
    
    extra_compile_args = property(
        _get_extra_compile_args, _set_extra_compile_args)
    
    def _get_extra_link_args(self):
        if not self._mysql_link_args and self.get_mysql_link_args:
            self._mysql_link_args = self.get_mysql_link_args()
        return self._extra_link_args + self._mysql_link_args
    
    def _set_extra_link_args(self, args):
        self._extra_link_args = args
    
    extra_link_args = property(_get_extra_link_args, _set_extra_link_args)

oursql_ext = MysqlExtension("oursql", ["oursqlx/compat.c"])

try:
    from Cython.Distutils import build_ext
except ImportError:
    print "cython not found, using previously-cython'd .c file."
    oursql_ext.sources.insert(0, 'oursqlx/oursql.c')
else:
    oursql_ext.sources.insert(0, 'oursqlx/oursql.pyx')

class oursql_build_ext(build_ext):
    user_options = build_ext.user_options + [
        ('mysql-config=', None, 
            '(*nix only) path to the mysql-config executable'),
        ('use-libmysqld', None,
            '(*nix only) link against libmysqld instead of libmysqlclient'),
        ('static', None,
            '(Windows only) statically link against mysqlclient.lib'),
        ('mysql-registry-key=', None,
            '(Windows only) the registry key to query for the mysql root '
            'directory'),
        ('mysql-root=', None,
            '(Windows only) the path to the mysql installation; can be given '
            'instead of --mysql-registry-key'),
    ]
    
    boolean_options = build_ext.boolean_options + [
        'use-libmysqld', 'static'
    ]
    
    def initialize_options(self):
        build_ext.initialize_options(self)
        self.mysql_config = 'mysql_config'
        self.use_libmysqld = self.static = 0
        self.mysql_registry_key = r'SOFTWARE\MySQL AB\MySQL Server 5.0'
        self.mysql_root = None
    
    def get_mysql_config(self, option):
        args = [self.mysql_config, '--%s' % option]
        print ' '.join(args)
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        except:
            print 'failed to execute', args[0]
            raise
        stdout, _ = proc.communicate()
        return split_quoted(stdout.strip())
    
    def setup_posixish(self, ext):
        ext.get_mysql_compile_args = (
            lambda: self.get_mysql_config('cflags'))
        if self.use_libmysqld:
            ext.get_mysql_link_args = (
                lambda: self.get_mysql_config('libmysqld-libs'))
        else:
            ext.get_mysql_link_args = (
                lambda: self.get_mysql_config('libs'))
    
    def setup_windowsish(self, ext):
        if self.mysql_root:
            mysql_root = self.mysql_root
        else:
            mysql_key = _winreg.OpenKey(
                _winreg.HKEY_LOCAL_MACHINE, self.mysql_registry_key)
            mysql_root, _ = _winreg.QueryValueEx(mysql_key, 'Location')
        
        if self.static:
            client = "mysqlclient"
        else:
            client = "libmysql"

        ext.library_dirs.append(
            os.path.join(mysql_root, 'lib', 'opt'))
        ext.libraries.extend(['advapi32', 'wsock32', client])
        ext.include_dirs.append(
            os.path.join(mysql_root, 'include'))
        if self.static:
            ext.get_mysql_compile_args = lambda: ['/MT']
        else:
            ext.get_mysql_compile_args = lambda: ['/MD']

    
    def build_extension(self, ext):
        if getattr(ext, 'use_mysql_flags', False):
            try:
                subprocess.call([self.mysql_config], 
                    stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
            except OSError:
                if _winreg:
                    self.setup_windowsish(ext)
                else:
                    print ('warning: no usable mysql_config and no _winreg '
                        'module to try; hopefully you have usable '
                        'CFLAGS/LDFLAGS set.')
            else:
                self.setup_posixish(ext)
        build_ext.build_extension(self, ext)

setup(
    name='oursql',
    version='0.1rc1',
    author='Aaron Gallagher',
    author_email='habnabit@gmail.com',
    url='http://launchpad.net/oursql',
    description='MySQL bindings for python.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 2',
        'Topic :: Database :: Database Engines/Servers',
    ],
    
    ext_modules=[oursql_ext],
    cmdclass=dict(build_ext=oursql_build_ext),
)
