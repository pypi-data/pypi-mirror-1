#!/usr/bin/env python
"""Create a "virtual" Python installation
"""

import sys
import os
import optparse
import shutil
import logging
import distutils.sysconfig
try:
    import subprocess
except ImportError, e:
    if sys.version_info <= (2, 3):
        print 'ERROR: %s' % e
        print 'ERROR: this script requires Python 2.4 or greater; or at least the subprocess module.'
        print 'If you copy subprocess.py from a newer version of Python this script will probably work'
        sys.exit(101)
    else:
        raise
try:
    set
except NameError:
    from sets import Set as set
    
join = os.path.join
py_version = 'python%s.%s' % (sys.version_info[0], sys.version_info[1])
is_jython = sys.platform.startswith('java')
expected_exe = is_jython and 'jython' or 'python'

REQUIRED_MODULES = ['os', 'posix', 'posixpath', 'ntpath', 'genericpath',
                    'fnmatch', 'locale', 'encodings', 'codecs',
                    'stat', 'UserDict', 'readline', 'copy_reg', 'types',
                    're', 'sre', 'sre_parse', 'sre_constants', 'sre_compile',
                    'lib-dynload', 'config', 'zlib']

if sys.version_info[:2] == (2, 6):
    REQUIRED_MODULES.extend(['warnings', 'linecache', '_abcoll', 'abc'])
if sys.version_info[:2] <= (2, 3):
    REQUIRED_MODULES.extend(['sets', '__future__'])

class Logger(object):

    """
    Logging object for use in command-line script.  Allows ranges of
    levels, to avoid some redundancy of displayed information.
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    NOTIFY = (logging.INFO+logging.WARN)/2
    WARN = WARNING = logging.WARN
    ERROR = logging.ERROR
    FATAL = logging.FATAL

    LEVELS = [DEBUG, INFO, NOTIFY, WARN, ERROR, FATAL]

    def __init__(self, consumers):
        self.consumers = consumers
        self.indent = 0
        self.in_progress = None
        self.in_progress_hanging = False

    def debug(self, msg, *args, **kw):
        self.log(self.DEBUG, msg, *args, **kw)
    def info(self, msg, *args, **kw):
        self.log(self.INFO, msg, *args, **kw)
    def notify(self, msg, *args, **kw):
        self.log(self.NOTIFY, msg, *args, **kw)
    def warn(self, msg, *args, **kw):
        self.log(self.WARN, msg, *args, **kw)
    def error(self, msg, *args, **kw):
        self.log(self.WARN, msg, *args, **kw)
    def fatal(self, msg, *args, **kw):
        self.log(self.FATAL, msg, *args, **kw)
    def log(self, level, msg, *args, **kw):
        if args:
            if kw:
                raise TypeError(
                    "You may give positional or keyword arguments, not both")
        args = args or kw
        rendered = None
        for consumer_level, consumer in self.consumers:
            if self.level_matches(level, consumer_level):
                if (self.in_progress_hanging
                    and consumer in (sys.stdout, sys.stderr)):
                    self.in_progress_hanging = False
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                if rendered is None:
                    if args:
                        rendered = msg % args
                    else:
                        rendered = msg
                    rendered = ' '*self.indent + rendered
                if hasattr(consumer, 'write'):
                    consumer.write(rendered+'\n')
                else:
                    consumer(rendered)

    def start_progress(self, msg):
        assert not self.in_progress, (
            "Tried to start_progress(%r) while in_progress %r"
            % (msg, self.in_progress))
        if self.level_matches(self.NOTIFY, self._stdout_level()):
            sys.stdout.write(msg)
            sys.stdout.flush()
            self.in_progress_hanging = True
        else:
            self.in_progress_hanging = False
        self.in_progress = msg

    def end_progress(self, msg='done.'):
        assert self.in_progress, (
            "Tried to end_progress without start_progress")
        if self.stdout_level_matches(self.NOTIFY):
            if not self.in_progress_hanging:
                # Some message has been printed out since start_progress
                sys.stdout.write('...' + self.in_progress + msg + '\n')
                sys.stdout.flush()
            else:
                sys.stdout.write(msg + '\n')
                sys.stdout.flush()
        self.in_progress = None
        self.in_progress_hanging = False

    def show_progress(self):
        """If we are in a progress scope, and no log messages have been
        shown, write out another '.'"""
        if self.in_progress_hanging:
            sys.stdout.write('.')
            sys.stdout.flush()

    def stdout_level_matches(self, level):
        """Returns true if a message at this level will go to stdout"""
        return self.level_matches(level, self._stdout_level())

    def _stdout_level(self):
        """Returns the level that stdout runs at"""
        for level, consumer in self.consumers:
            if consumer is sys.stdout:
                return level
        return self.FATAL

    def level_matches(self, level, consumer_level):
        """
        >>> l = Logger()
        >>> l.level_matches(3, 4)
        False
        >>> l.level_matches(3, 2)
        True
        >>> l.level_matches(slice(None, 3), 3)
        False
        >>> l.level_matches(slice(None, 3), 2)
        True
        >>> l.level_matches(slice(1, 3), 1)
        True
        >>> l.level_matches(slice(2, 3), 1)
        False
        """
        if isinstance(level, slice):
            start, stop = level.start, level.stop
            if start is not None and start > consumer_level:
                return False
            if stop is not None or stop <= consumer_level:
                return False
            return True
        else:
            return level >= consumer_level

    #@classmethod
    def level_for_integer(cls, level):
        levels = cls.LEVELS
        if level < 0:
            return levels[0]
        if level >= len(levels):
            return levels[-1]
        return levels[level]

    level_for_integer = classmethod(level_for_integer)

def mkdir(path):
    if not os.path.exists(path):
        logger.info('Creating %s', path)
        os.makedirs(path)
    else:
        logger.info('Directory %s already exists', path)

def copyfile(src, dest, symlink=True):
    if not os.path.exists(src):
        # Some bad symlink in the src
        logger.warn('Cannot find file %s (bad symlink)', src)
        return
    if os.path.exists(dest):
        logger.debug('File %s already exists', dest)
        return
    if not os.path.exists(os.path.dirname(dest)):
        logger.info('Creating parent directories for %s' % os.path.dirname(dest))
        os.makedirs(os.path.dirname(dest))
    if symlink and hasattr(os, 'symlink'):
        logger.info('Symlinking %s', dest)
        os.symlink(os.path.abspath(src), dest)
    else:
        logger.info('Copying to %s', dest)
        if os.path.isdir(src):
            shutil.copytree(src, dest, True)
        else:
            shutil.copy2(src, dest)

def writefile(dest, content, overwrite=True):
    if not os.path.exists(dest):
        logger.info('Writing %s', dest)
        f = open(dest, 'wb')
        f.write(content)
        f.close()
        return
    else:
        f = open(dest, 'rb')
        c = f.read()
        f.close()
        if c != content:
            if not overwrite:
                logger.notify('File %s exists with different content; not overwriting', dest)
                return
            logger.notify('Overwriting %s with new content', dest)
            f = open(dest, 'wb')
            f.write(content)
            f.close()
        else:
            logger.info('Content %s already in place', dest)

def rmtree(dir):
    if os.path.exists(dir):
        logger.notify('Deleting tree %s', dir)
        shutil.rmtree(dir)
    else:
        logger.info('Do not need to delete %s; already gone', dir)

def make_exe(fn):
    if hasattr(os, 'chmod'):
        oldmode = os.stat(fn).st_mode & 07777
        newmode = (oldmode | 0555) & 07777
        os.chmod(fn, newmode)
        logger.info('Changed mode of %s to %s', fn, oct(newmode))

def install_distribute(py_executable, unzip=False):
    setup_fn = 'distribute-0.6-py%s.egg' % sys.version[:3]
    search_dirs = ['.', os.path.dirname(__file__), join(os.path.dirname(__file__), 'support-files')]
    if os.path.splitext(os.path.dirname(__file__))[0] != 'virtualenv':
        # Probably some boot script; just in case virtualenv is installed...
        try:
            import virtualenv
        except ImportError:
            pass
        else:
            search_dirs.append(os.path.join(os.path.dirname(virtualenv.__file__), 'support-files'))
    for dir in search_dirs:
        if os.path.exists(join(dir, setup_fn)):
            setup_fn = join(dir, setup_fn)
            break
    if is_jython and os._name == 'nt':
        # Jython's .bat sys.executable can't handle a command line
        # argument with newlines
        import tempfile
        fd, distribute_setup = tempfile.mkstemp('.py')
        os.write(fd, DISTRIBUTE_SETUP_PY)
        os.close(fd)
        cmd = [py_executable, distribute_setup]
    else:
        cmd = [py_executable, '-c', DISTRIBUTE_SETUP_PY]
    if unzip:
        cmd.append('--always-unzip')
    env = {}
    if logger.stdout_level_matches(logger.DEBUG):
        cmd.append('-v')
    if os.path.exists(setup_fn):
        logger.info('Using existing distribute egg: %s', setup_fn)
        cmd.append(setup_fn)
        if os.environ.get('PYTHONPATH'):
            env['PYTHONPATH'] = setup_fn + os.path.pathsep + os.environ['PYTHONPATH']
        else:
            env['PYTHONPATH'] = setup_fn
    else:
        logger.info('No distribute egg found; downloading')
        cmd.extend(['--always-copy', '-U', 'distribute'])
    logger.start_progress('Installing distribute...')
    logger.indent += 2
    cwd = None
    if not os.access(os.getcwd(), os.W_OK):
        cwd = '/tmp'
    try:
        call_subprocess(cmd, show_stdout=False,
                        filter_stdout=filter_distribute_setup,
                        extra_env=env,
                        cwd=cwd)
    finally:
        logger.indent -= 2
        logger.end_progress()
        if is_jython and os._name == 'nt':
            os.remove(distribute_setup)

def filter_distribute_setup(line):
    if not line.strip():
        return Logger.DEBUG
    for prefix in ['Reading ', 'Best match', 'Processing distribute',
                   'Copying distribute', 'Adding distribute',
                   'Installing ', 'Installed ']:
        if line.startswith(prefix):
            return Logger.DEBUG
    return Logger.INFO

def main():
    parser = optparse.OptionParser(
        version="1.3.4dev",
        usage="%prog [OPTIONS] DEST_DIR")

    parser.add_option(
        '-v', '--verbose',
        action='count',
        dest='verbose',
        default=0,
        help="Increase verbosity")

    parser.add_option(
        '-q', '--quiet',
        action='count',
        dest='quiet',
        default=0,
        help='Decrease verbosity')

    parser.add_option(
        '-p', '--python',
        dest='python',
        metavar='PYTHON_EXE',
        help='The Python interpreter to use, e.g., --python=python2.5 will use the python2.5 '
        'interpreter to create the new environment.  The default is the interpreter that '
        'virtualenv was installed with (%s)' % sys.executable)

    parser.add_option(
        '--clear',
        dest='clear',
        action='store_true',
        help="Clear out the non-root install and start from scratch")

    parser.add_option(
        '--no-site-packages',
        dest='no_site_packages',
        action='store_true',
        help="Don't give access to the global site-packages dir to the "
             "virtual environment")

    parser.add_option(
        '--unzip-distribute',
        dest='unzip_distribute',
        action='store_true',
        help="Unzip distribute when installing it")

    parser.add_option(
        '--relocatable',
        dest='relocatable',
        action='store_true',
        help='Make an EXISTING virtualenv environment relocatable.  '
        'This fixes up scripts and makes all .pth files relative')

    if 'extend_parser' in globals():
        extend_parser(parser)

    options, args = parser.parse_args()

    global logger

    if 'adjust_options' in globals():
        adjust_options(options, args)

    verbosity = options.verbose - options.quiet
    logger = Logger([(Logger.level_for_integer(2-verbosity), sys.stdout)])

    if options.python and not os.environ.get('VIRTUALENV_INTERPRETER_RUNNING'):
        env = os.environ.copy()
        interpreter = resolve_interpreter(options.python)
        if interpreter == sys.executable:
            logger.warn('Already using interpreter %s' % interpreter)
        else:
            logger.notify('Running virtualenv with interpreter %s' % interpreter)
            env['VIRTUALENV_INTERPRETER_RUNNING'] = 'true'
            file = __file__
            if file.endswith('.pyc'):
                file = file[:-1]
            os.execvpe(interpreter, [interpreter, file] + sys.argv[1:], env)

    if not args:
        print 'You must provide a DEST_DIR'
        parser.print_help()
        sys.exit(2)
    if len(args) > 1:
        print 'There must be only one argument: DEST_DIR (you gave %s)' % (
            ' '.join(args))
        parser.print_help()
        sys.exit(2)

    home_dir = args[0]

    if os.environ.get('WORKING_ENV'):
        logger.fatal('ERROR: you cannot run virtualenv while in a workingenv')
        logger.fatal('Please deactivate your workingenv, then re-run this script')
        sys.exit(3)

    if os.environ.get('PYTHONHOME'):
        if sys.platform == 'win32':
            name = '%PYTHONHOME%'
        else:
            name = '$PYTHONHOME'
        logger.warn('%s is set; this can cause problems creating environments' % name)

    if options.relocatable:
        make_environment_relocatable(home_dir)
        return

    create_environment(home_dir, site_packages=not options.no_site_packages, clear=options.clear,
                       unzip_distribute=options.unzip_distribute)
    if 'after_install' in globals():
        after_install(options, home_dir)

def call_subprocess(cmd, show_stdout=True,
                    filter_stdout=None, cwd=None,
                    raise_on_returncode=True, extra_env=None):
    cmd_parts = []
    for part in cmd:
        if len(part) > 40:
            part = part[:30]+"..."+part[-5:]
        if ' ' in part or '\n' in part or '"' in part or "'" in part:
            part = '"%s"' % part.replace('"', '\\"')
        cmd_parts.append(part)
    cmd_desc = ' '.join(cmd_parts)
    if show_stdout:
        stdout = None
    else:
        stdout = subprocess.PIPE
    logger.debug("Running command %s" % cmd_desc)
    if extra_env:
        env = os.environ.copy()
        env.update(extra_env)
    else:
        env = None
    try:
        proc = subprocess.Popen(
            cmd, stderr=subprocess.STDOUT, stdin=None, stdout=stdout,
            cwd=cwd, env=env)
    except Exception, e:
        logger.fatal(
            "Error %s while executing command %s" % (e, cmd_desc))
        raise
    all_output = []
    if stdout is not None:
        stdout = proc.stdout
        while 1:
            line = stdout.readline()
            if not line:
                break
            line = line.rstrip()
            all_output.append(line)
            if filter_stdout:
                level = filter_stdout(line)
                if isinstance(level, tuple):
                    level, line = level
                logger.log(level, line)
                if not logger.stdout_level_matches(level):
                    logger.show_progress()
            else:
                logger.info(line)
    else:
        proc.communicate()
    proc.wait()
    if proc.returncode:
        if raise_on_returncode:
            if all_output:
                logger.notify('Complete output from command %s:' % cmd_desc)
                logger.notify('\n'.join(all_output) + '\n----------------------------------------')
            raise OSError(
                "Command %s failed with error code %s"
                % (cmd_desc, proc.returncode))
        else:
            logger.warn(
                "Command %s had error code %s"
                % (cmd_desc, proc.returncode))


def create_environment(home_dir, site_packages=True, clear=False,
                       unzip_distribute=False):
    """
    Creates a new environment in ``home_dir``.

    If ``site_packages`` is true (the default) then the global
    ``site-packages/`` directory will be on the path.

    If ``clear`` is true (default False) then the environment will
    first be cleared.
    """
    home_dir, lib_dir, inc_dir, bin_dir = path_locations(home_dir)

    py_executable = install_python(
        home_dir, lib_dir, inc_dir, bin_dir, 
        site_packages=site_packages, clear=clear)

    install_distutils(lib_dir, home_dir)

    install_distribute(py_executable, unzip=unzip_distribute)

    install_activate(home_dir, bin_dir)

def path_locations(home_dir):
    """Return the path locations for the environment (where libraries are,
    where scripts go, etc)"""
    # XXX: We'd use distutils.sysconfig.get_python_inc/lib but its
    # prefix arg is broken: http://bugs.python.org/issue3386
    if sys.platform == 'win32':
        # Windows has lots of problems with executables with spaces in
        # the name; this function will remove them (using the ~1
        # format):
        mkdir(home_dir)
        if ' ' in home_dir:
            try:
                import win32api
            except ImportError:
                print 'Error: the path "%s" has a space in it' % home_dir
                print 'To handle these kinds of paths, the win32api module must be installed:'
                print '  http://sourceforge.net/projects/pywin32/'
                sys.exit(3)
            home_dir = win32api.GetShortPathName(home_dir)
        lib_dir = join(home_dir, 'Lib')
        inc_dir = join(home_dir, 'Include')
        bin_dir = join(home_dir, 'Scripts')
    elif is_jython:
        lib_dir = join(home_dir, 'Lib')
        inc_dir = join(home_dir, 'Include')
        bin_dir = join(home_dir, 'bin')
    else:
        lib_dir = join(home_dir, 'lib', py_version)
        inc_dir = join(home_dir, 'include', py_version)
        bin_dir = join(home_dir, 'bin')
    return home_dir, lib_dir, inc_dir, bin_dir

def install_python(home_dir, lib_dir, inc_dir, bin_dir, site_packages, clear):
    """Install just the base environment, no distutils patches etc"""
    if sys.executable.startswith(bin_dir):
        print 'Please use the *system* python to run this script'
        return
        
    if clear:
        rmtree(lib_dir)
        ## FIXME: why not delete it?
        ## Maybe it should delete everything with #!/path/to/venv/python in it
        logger.notify('Not deleting %s', bin_dir)

    if hasattr(sys, 'real_prefix'):
        logger.notify('Using real prefix %r' % sys.real_prefix)
        prefix = sys.real_prefix
    else:
        prefix = sys.prefix
    mkdir(lib_dir)
    fix_lib64(lib_dir)
    stdlib_dirs = [os.path.dirname(os.__file__)]
    if sys.platform == 'win32':
        stdlib_dirs.append(join(os.path.dirname(stdlib_dirs[0]), 'DLLs'))
    elif sys.platform == 'darwin':
        stdlib_dirs.append(join(stdlib_dirs[0], 'site-packages'))
    for stdlib_dir in stdlib_dirs:
        if not os.path.isdir(stdlib_dir):
            continue
        if hasattr(os, 'symlink'):
            logger.info('Symlinking Python bootstrap modules')
        else:
            logger.info('Copying Python bootstrap modules')
        logger.indent += 2
        try:
            for fn in os.listdir(stdlib_dir):
                if fn != 'site-packages' and os.path.splitext(fn)[0] in REQUIRED_MODULES:
                    copyfile(join(stdlib_dir, fn), join(lib_dir, fn))
        finally:
            logger.indent -= 2
    mkdir(join(lib_dir, 'site-packages'))
    writefile(join(lib_dir, 'site.py'), SITE_PY)
    writefile(join(lib_dir, 'orig-prefix.txt'), prefix)
    site_packages_filename = join(lib_dir, 'no-global-site-packages.txt')
    if not site_packages:
        writefile(site_packages_filename, '')
    else:
        if os.path.exists(site_packages_filename):
            logger.info('Deleting %s' % site_packages_filename)
            os.unlink(site_packages_filename)

    stdinc_dir = join(prefix, 'include', py_version)
    if os.path.exists(stdinc_dir):
        copyfile(stdinc_dir, inc_dir)
    else:
        logger.debug('No include dir %s' % stdinc_dir)

    if sys.exec_prefix != prefix:
        if sys.platform == 'win32':
            exec_dir = join(sys.exec_prefix, 'lib')
        elif is_jython:
            exec_dir = join(sys.exec_prefix, 'Lib')
        else:
            exec_dir = join(sys.exec_prefix, 'lib', py_version)
        for fn in os.listdir(exec_dir):
            copyfile(join(exec_dir, fn), join(lib_dir, fn))
    
    if is_jython:
        # Jython has either jython-dev.jar and javalib/ dir, or just
        # jython.jar
        for name in 'jython-dev.jar', 'javalib', 'jython.jar':
            src = join(prefix, name)
            if os.path.exists(src):
                copyfile(src, join(home_dir, name))
        # XXX: registry should always exist after Jython 2.5rc1
        src = join(prefix, 'registry')
        if os.path.exists(src):
            copyfile(src, join(home_dir, 'registry'), symlink=False)
        copyfile(join(prefix, 'cachedir'), join(home_dir, 'cachedir'),
                 symlink=False)

    mkdir(bin_dir)
    py_executable = join(bin_dir, os.path.basename(sys.executable))
    if 'Python.framework' in prefix:
        if py_executable.endswith('/Python'):
            # The name of the python executable is not quite what
            # we want, rename it.
            py_executable = os.path.join(
                    os.path.dirname(py_executable), 'python')

    logger.notify('New %s executable in %s', expected_exe, py_executable)
    if sys.executable != py_executable:
        ## FIXME: could I just hard link?
        executable = sys.executable
        if sys.platform == 'cygwin' and os.path.exists(executable + '.exe'):
            # Cygwin misreports sys.executable sometimes
            executable += '.exe'
            py_executable += '.exe'
            logger.info('Executable actually exists in %s' % executable)
        shutil.copyfile(executable, py_executable)
        make_exe(py_executable)
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
            if os.path.exists(pythonw):
                logger.info('Also created pythonw.exe')
                shutil.copyfile(pythonw, os.path.join(os.path.dirname(py_executable), 'pythonw.exe'))
                
    if os.path.splitext(os.path.basename(py_executable))[0] != expected_exe:
        secondary_exe = os.path.join(os.path.dirname(py_executable),
                                     expected_exe)
        py_executable_ext = os.path.splitext(py_executable)[1]
        if py_executable_ext == '.exe':
            # python2.4 gives an extension of '.4' :P
            secondary_exe += py_executable_ext
        if os.path.exists(secondary_exe):
            logger.warn('Not overwriting existing %s script %s (you must use %s)'
                        % (expected_exe, secondary_exe, py_executable))
        else:
            logger.notify('Also creating executable in %s' % secondary_exe)
            shutil.copyfile(sys.executable, secondary_exe)
            make_exe(secondary_exe)
    
    if 'Python.framework' in prefix:
        logger.debug('MacOSX Python framework detected')
        
        # Make sure we use the the embedded interpreter inside
        # the framework, even if sys.executable points to
        # the stub executable in ${sys.prefix}/bin
        # See http://groups.google.com/group/python-virtualenv/
        #                              browse_thread/thread/17cab2f85da75951
        shutil.copy(
                os.path.join(
                    prefix, 'Resources/Python.app/Contents/MacOS/Python'),
                py_executable)

        # Copy the framework's dylib into the virtual 
        # environment
        virtual_lib = os.path.join(home_dir, '.Python')

        if os.path.exists(virtual_lib):
            os.unlink(virtual_lib)
        copyfile(
            os.path.join(prefix, 'Python'),
            virtual_lib)

        # And then change the install_name of the copied python executable
        try:
            call_subprocess(
                ["install_name_tool", "-change",
                 os.path.join(prefix, 'Python'),
                 '@executable_path/../.Python',
                 py_executable])
        except:
            logger.fatal(
                "Could not call install_name_tool -- you must have Apple's development tools installed")
            raise

        # Some tools depend on pythonX.Y being present
        pth = py_executable + '%s.%s' % (
                sys.version_info[0], sys.version_info[1])
        if os.path.exists(pth):
            os.unlink(pth)
        os.symlink('python', pth)

    if sys.platform == 'win32' and ' ' in py_executable:
        # There's a bug with subprocess on Windows when using a first
        # argument that has a space in it.  Instead we have to quote
        # the value:
        py_executable = '"%s"' % py_executable
    cmd = [py_executable, '-c', 'import sys; print sys.prefix']
    logger.info('Testing executable with %s %s "%s"' % tuple(cmd))
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE)
    proc_stdout, proc_stderr = proc.communicate()
    proc_stdout = os.path.normcase(os.path.abspath(proc_stdout.strip()))
    if proc_stdout != os.path.normcase(os.path.abspath(home_dir)):
        logger.fatal(
            'ERROR: The executable %s is not functioning' % py_executable)
        logger.fatal(
            'ERROR: It thinks sys.prefix is %r (should be %r)'
            % (proc_stdout, os.path.normcase(os.path.abspath(home_dir))))
        logger.fatal(
            'ERROR: virtualenv is not compatible with this system or executable')
        sys.exit(100)
    else:
        logger.info('Got sys.prefix result: %r' % proc_stdout)

    pydistutils = os.path.expanduser('~/.pydistutils.cfg')
    if os.path.exists(pydistutils):
        logger.notify('Please make sure you remove any previous custom paths from '
                      'your %s file.' % pydistutils)
    ## FIXME: really this should be calculated earlier
    return py_executable

def install_activate(home_dir, bin_dir):
    if sys.platform == 'win32' or is_jython and os._name == 'nt':
        files = {'activate.bat': ACTIVATE_BAT,
                 'deactivate.bat': DEACTIVATE_BAT}
        if os.environ.get('OS') == 'Windows_NT' and os.environ.get('OSTYPE') == 'cygwin':
            files['activate'] = ACTIVATE_SH
    else:
        files = {'activate': ACTIVATE_SH}
    files['activate_this.py'] = ACTIVATE_THIS
    for name, content in files.items():
        content = content.replace('__VIRTUAL_ENV__', os.path.abspath(home_dir))
        content = content.replace('__VIRTUAL_NAME__', os.path.basename(os.path.abspath(home_dir)))
        content = content.replace('__BIN_NAME__', os.path.basename(bin_dir))
        writefile(os.path.join(bin_dir, name), content)

def install_distutils(lib_dir, home_dir):
    distutils_path = os.path.join(lib_dir, 'distutils')
    mkdir(distutils_path)
    ## FIXME: maybe this prefix setting should only be put in place if
    ## there's a local distutils.cfg with a prefix setting?
    home_dir = os.path.abspath(home_dir)
    ## FIXME: this is breaking things, removing for now:
    #distutils_cfg = DISTUTILS_CFG + "\n[install]\nprefix=%s\n" % home_dir
    writefile(os.path.join(distutils_path, '__init__.py'), DISTUTILS_INIT)
    writefile(os.path.join(distutils_path, 'distutils.cfg'), DISTUTILS_CFG, overwrite=False)

def fix_lib64(lib_dir):
    """
    Some platforms (particularly Gentoo on x64) put things in lib64/pythonX.Y
    instead of lib/pythonX.Y.  If this is such a platform we'll just create a
    symlink so lib64 points to lib
    """
    if [p for p in distutils.sysconfig.get_config_vars().values() 
        if isinstance(p, basestring) and 'lib64' in p]:
        logger.debug('This system uses lib64; symlinking lib64 to lib')
        assert os.path.basename(lib_dir) == 'python%s' % sys.version[:3], (
            "Unexpected python lib dir: %r" % lib_dir)
        lib_parent = os.path.dirname(lib_dir)
        assert os.path.basename(lib_parent) == 'lib', (
            "Unexpected parent dir: %r" % lib_parent)
        copyfile(lib_parent, os.path.join(os.path.dirname(lib_parent), 'lib64'))

def resolve_interpreter(exe):
    """
    If the executable given isn't an absolute path, search $PATH for the interpreter
    """
    if os.path.abspath(exe) != exe:
        paths = os.environ.get('PATH', '').split(os.pathsep)
        for path in paths:
            if os.path.exists(os.path.join(path, exe)):
                exe = os.path.join(path, exe)
                break
    if not os.path.exists(exe):
        logger.fatal('The executable %s (from --python=%s) does not exist' % (exe, exe))
        sys.exit(3)
    return exe

############################################################
## Relocating the environment:

def make_environment_relocatable(home_dir):
    """
    Makes the already-existing environment use relative paths, and takes out 
    the #!-based environment selection in scripts.
    """
    activate_this = os.path.join(home_dir, 'bin', 'activate_this.py')
    if not os.path.exists(activate_this):
        logger.fatal(
            'The environment doesn\'t have a file %s -- please re-run virtualenv '
            'on this environment to update it' % activate_this)
    fixup_scripts(home_dir)
    fixup_pth_and_egg_link(home_dir)
    ## FIXME: need to fix up distutils.cfg

OK_ABS_SCRIPTS = ['python', 'python%s' % sys.version[:3],
                  'activate', 'activate.bat', 'activate_this.py']

def fixup_scripts(home_dir):
    # This is what we expect at the top of scripts:
    shebang = '#!%s/bin/python' % os.path.normcase(os.path.abspath(home_dir))
    # This is what we'll put:
    new_shebang = '#!/usr/bin/env python%s' % sys.version[:3]
    activate = "import os; activate_this=os.path.join(os.path.dirname(__file__), 'activate_this.py'); execfile(activate_this, dict(__file__=activate_this)); del os, activate_this"
    bin_dir = os.path.join(home_dir, 'bin')
    for filename in os.listdir(bin_dir):
        filename = os.path.join(bin_dir, filename)
        f = open(filename, 'rb')
        lines = f.readlines()
        f.close()
        if not lines:
            logger.warn('Script %s is an empty file' % filename)
            continue
        if lines[0].strip() != shebang:
            if os.path.basename(filename) in OK_ABS_SCRIPTS:
                logger.debug('Cannot make script %s relative' % filename)
            elif lines[0].strip() == new_shebang:
                logger.info('Script %s has already been made relative' % filename)
            else:
                logger.warn('Script %s cannot be made relative (it\'s not a normal script that starts with %s)'
                            % (filename, shebang))
            continue
        logger.notify('Making script %s relative' % filename)
        lines = [new_shebang+'\n', activate+'\n'] + lines[1:]
        f = open(filename, 'wb')
        f.writelines(lines)
        f.close()

def fixup_pth_and_egg_link(home_dir):
    """Makes .pth and .egg-link files use relative paths"""
    home_dir = os.path.normcase(os.path.abspath(home_dir))
    for path in sys.path:
        if not path:
            path = '.'
        if not os.path.isdir(path):
            continue
        path = os.path.normcase(os.path.abspath(path))
        if not path.startswith(home_dir):
            logger.debug('Skipping system (non-environment) directory %s' % path)
            continue
        for filename in os.listdir(path):
            filename = os.path.join(path, filename)
            if filename.endswith('.pth'):
                if not os.access(filename, os.W_OK):
                    logger.warn('Cannot write .pth file %s, skipping' % filename)
                else:
                    fixup_pth_file(filename)
            if filename.endswith('.egg-link'):
                if not os.access(filename, os.W_OK):
                    logger.warn('Cannot write .egg-link file %s, skipping' % filename)
                else:
                    fixup_egg_link(filename)

def fixup_pth_file(filename):
    lines = []
    prev_lines = []
    f = open(filename)
    prev_lines = f.readlines()
    f.close()
    for line in prev_lines:
        line = line.strip()
        if (not line or line.startswith('#') or line.startswith('import ')
            or os.path.abspath(line) != line):
            lines.append(line)
        else:
            new_value = make_relative_path(filename, line)
            if line != new_value:
                logger.debug('Rewriting path %s as %s (in %s)' % (line, new_value, filename))
            lines.append(new_value)
    if lines == prev_lines:
        logger.info('No changes to .pth file %s' % filename)
        return
    logger.notify('Making paths in .pth file %s relative' % filename)
    f = open(filename, 'w')
    f.write('\n'.join(lines) + '\n')
    f.close()

def fixup_egg_link(filename):
    f = open(filename)
    link = f.read().strip()
    f.close()
    if os.path.abspath(link) != link:
        logger.debug('Link in %s already relative' % filename)
        return
    new_link = make_relative_path(filename, link)
    logger.notify('Rewriting link %s in %s as %s' % (link, filename, new_link))
    f = open(filename, 'w')
    f.write(new_link)
    f.close()

def make_relative_path(source, dest, dest_is_directory=True):
    """
    Make a filename relative, where the filename is dest, and it is
    being referred to from the filename source.

        >>> make_relative_path('/usr/share/something/a-file.pth',
        ...                    '/usr/share/another-place/src/Directory')
        '../another-place/src/Directory'
        >>> make_relative_path('/usr/share/something/a-file.pth',
        ...                    '/home/user/src/Directory')
        '../../../home/user/src/Directory'
        >>> make_relative_path('/usr/share/a-file.pth', '/usr/share/')
        './'
    """
    source = os.path.dirname(source)
    if not dest_is_directory:
        dest_filename = os.path.basename(dest)
        dest = os.path.dirname(dest)
    dest = os.path.normpath(os.path.abspath(dest))
    source = os.path.normpath(os.path.abspath(source))
    dest_parts = dest.strip(os.path.sep).split(os.path.sep)
    source_parts = source.strip(os.path.sep).split(os.path.sep)
    while dest_parts and source_parts and dest_parts[0] == source_parts[0]:
        dest_parts.pop(0)
        source_parts.pop(0)
    full_parts = ['..']*len(source_parts) + dest_parts
    if not dest_is_directory:
        full_parts.append(dest_filename)
    if not full_parts:
        # Special case for the current directory (otherwise it'd be '')
        return './'
    return os.path.sep.join(full_parts)
                


############################################################
## Bootstrap script creation:

def create_bootstrap_script(extra_text, python_version=''):
    """
    Creates a bootstrap script, which is like this script but with
    extend_parser, adjust_options, and after_install hooks.

    This returns a string that (written to disk of course) can be used
    as a bootstrap script with your own customizations.  The script
    will be the standard virtualenv.py script, with your extra text
    added (your extra text should be Python code).

    If you include these functions, they will be called:

    ``extend_parser(optparse_parser)``:
        You can add or remove options from the parser here.

    ``adjust_options(options, args)``:
        You can change options here, or change the args (if you accept
        different kinds of arguments, be sure you modify ``args`` so it is
        only ``[DEST_DIR]``).

    ``after_install(options, home_dir)``:

        After everything is installed, this function is called.  This
        is probably the function you are most likely to use.  An
        example would be::

            def after_install(options, home_dir):
                subprocess.call([join(home_dir, 'bin', 'easy_install'),
                                 'MyPackage'])
                subprocess.call([join(home_dir, 'bin', 'my-package-script'),
                                 'setup', home_dir])

        This example immediately installs a package, and runs a setup
        script from that package.

    If you provide something like ``python_version='2.4'`` then the
    script will start with ``#!/usr/bin/env python2.4`` instead of
    ``#!/usr/bin/env python``.  You can use this when the script must
    be run with a particular Python version.
    """
    filename = __file__
    if filename.endswith('.pyc'):
        filename = filename[:-1]
    f = open(filename, 'rb')
    content = f.read()
    f.close()
    py_exe = 'python%s' % python_version
    content = (('#!/usr/bin/env %s\n' % py_exe)
               + '## WARNING: This file is generated\n'
               + content)
    return content.replace('##EXT' 'END##', extra_text)

##EXTEND##

##file site.py
SITE_PY = """
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
""".decode("base64").decode("zlib")

##file distribute_setup.py
DISTRIBUTE_SETUP_PY = """
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
XzKGwS0=
""".decode("base64").decode("zlib")

##file activate.sh
ACTIVATE_SH = """
eJytU99P2zAQfvdfcaQ8ABqN+srUh6IhUYmViXSdNECum1waS6ld2U6zgva/75ykNP0xpGnkIYl9
n8/fffddB8aZtJDKHGFRWAczhMJiAqV0GQRWFyZGmEkVitjJlXAYwEVq9AJmwmYXrANrXUAslNIO
TKFAOkikwdjla8YS3JyCs3N4ZUCPTOERLhUEp/z+7gufDB/G3wd3/NtgfBvAM3wGl6GqkP7x2/1j
0DcE/lpq4yrg216hLDo4OFTFU8mqb6eu3Ga6yBNI0BHnqigQKoEXm32CMpNxBplYIQj6UCjWi4UP
u0y4Sq8mFakWizwn3ZyGOd1NMtBfqo1fLAUJ2xy1XYAfpK0uXBN2Us2bNDtALwScet4QZ0LN0UJJ
TRKJf63BC07XGrRLYo7JnrjXg4j0vNT16md0yyc3D9HwfnRE5Kq0S7Mjz9/aFPWOdSnqHTSJgAc9
inrvtqgJbyjUkE30ZjTZEjshXkSkD4HSKkHrTOGNhnvcOhBhnsIGcLJ3+9aem3t/M3J0HZTGYE6t
Vw5Wwkgxy9G2Db17MWMtnv2A89aS84A1CrSLYQf+JA1rbzeLFjrk/Ho44qPB1xvOrxpY2/psX0qf
zPeg0iuYkrNRiQXC007ep2BayUgc96XzvpIiJ2Nb9FaFAe0o8t5cxs2MayNJlAaOCJlzy6swLMuy
+4KOnLrqkptDq1NXCoOh8BlC9maZxxatKaU8SvBpOn2GuhbMLW5Pn71T1Hl9gFra8h77oJn/gHn/
z1n/9znfzDgp8gduuMqz
""".decode("base64").decode("zlib")

##file activate.bat
ACTIVATE_BAT = """
eJx9kMsOgjAQRfdN+g+zoAn8goZEDESJPBpEViSzkFbZ0IX8f+RRaVW0u5mee3PanbjeFSgpKXmI
Hqq4KC9BglFW+YjWhEgJJa2ETvXQCNl2ogFe5CkvwaUEhjPm543vcOdAiacjLxzzJFw6f2bZCsZ0
2YitXPtswawi1zwgC9II0QPD/RELyuOb1jB/Sg0rNhM31Ss4n2I+7ibLb8epQGco2Rja1Fs/zeoa
cR9nWnprJaMspOQJdBR1/g==
""".decode("base64").decode("zlib")

##file deactivate.bat
DEACTIVATE_BAT = """
eJxzSE3OyFfIT0vj4spMU0hJTcvMS01RiPf3cYkP8wwKCXX0iQ8I8vcNCFHQ4FIAguLUEgWIgK0q
FlWqXJpcICVYpGzx2OAY4oFsPpCLbjpQCLvZILVcXFaufi5cACHzOrI=
""".decode("base64").decode("zlib")

##file distutils-init.py
DISTUTILS_INIT = """
eJytVtGq4zYQfddXDAnFdrlrSvu2EArtviwspZRCH5ZF6Npyoq4jGUm5Sfr1nZEcW7Kdtg813Iuj
ORrNnJk5sjoPxnowjqn45u7T61VYrfTRwWPhZ6M7dfxVWCct7POfyoE2HgS8Kesvopf6Dc6mvfTy
BZyBq4RGaLg4CcqDN9Ap3YI/SXC+7dUrY62yWpwlHDCYehD+VI8rZHL+4lXvOK0niD+N0uUCXqZh
1Zx3qpecVy9QTG6KiqlucqKNPdNLmR9TwWEVSrnaM/mv3jPA58FZTS9lWKJn9ztmmjAzHQWDaL6K
owTh4RsHYhgkBk4EvSJTOjJEtPSmEV4ZDcLFxbvz8jw7+nFXMdk7GcPgIQXOa6WRBV9+9wKL7AJM
3mQDZpAziYHRHIrMca608uhuuBdVVVsp2rJij7YgeNI+TeCfMbbfY3a+OcHrRfUtlzcPs2tojXS6
8PBVmyuc8A9zPkofksOGQICysvHG3kdHJ8Dsr9g25urgHbXRSdi2Ma2MjBAEGbTmMnZWOFy2FFM9
WNmpG8Xcxd+98B0WkYpcoNMfvi8ic501Cat1Y85nodt6TmFMdF7Aghh8nRaCm6YXzs2gMkOMvUJP
KzsaBdGrvyQ3A1XYQelk3yUgeihuXK2RGivsnSM7jobuF6NljqRnDT3A5y8ZjP0jPmmcrDWIOyx/
zyOhL7D7hLXaVVXmLsu2XuYX01sHs039JuHTDx41JjpYriZVO8zG0JjzMfQ2top7zxiFTtrEYxuH
8Sb2CFZ/wH9WvV4ojXqFYmMx89W0mF3ozQNsHpLQEoebz8OykLzVgCasdcciOtknGidvCHDl0u8Y
1n6KLSn7CjsVbA9/nEQQ8Ub0fRw1ad9d6BqICQElxMa2xRiisOOkDcapWzH3K+0J2Y/Sv0OFyXLZ
RZ2ahG1z0+aeJWrVxo8OzoBVEnWAK0emMgfNsaCGoBKhEKNW9xhEGWhczy5haqlbd1V4axSLiItq
PcKxHlaezZssaXvFchPdFbotN8K30l+sjjD2HxoX2Vk3cz4lk64vRgUVmw93fzIar4gGHU3AOjeF
4ZiMi30lyTF3g2xUp5oDdl8szoHUbeQGSYyLa9Ub18PhqTqlZKyDzQ99HFmxZ0Hit0RrGs7H+d02
smf5p9Qs9q6YRCF+xiR9Kj1lEo1rJp1HEcWLkqxPmU1BQKL7P1K9iiqP6V+IR8Rz4hPjNvELJhd7
Z+JH85sIN2XuKrFtUJ9Yy2+FPT40NXAz+ts4ZcRO/G9/koRSFJ8+/vTh429F+L5GmZk8z1WZlj4/
wF+2FC+/uPtwcaeFm9ywpzlu1GLDyp4yuKpGyu7fmqFSJw==
""".decode("base64").decode("zlib")

##file distutils.cfg
DISTUTILS_CFG = """
eJxNj00KwkAMhfc9xYNuxe4Ft57AjYiUtDO1wXSmNJnK3N5pdSEEAu8nH6lxHVlRhtDHMPATA4uH
xJ4EFmGbvfJiicSHFRzUSISMY6hq3GLCRLnIvSTnEefN0FIjw5tF0Hkk9Q5dRunBsVoyFi24aaLg
9FDOlL0FPGluf4QjcInLlxd6f6rqkgPu/5nHLg0cXCscXoozRrP51DRT3j9QNl99AP53T2Q=
""".decode("base64").decode("zlib")

##file activate_this.py
ACTIVATE_THIS = """
eJx1UsGOnDAMvecrIlYriDRlKvU20h5aaY+teuilGo1QALO4CwlKAjP8fe1QGGalRoLEefbzs+Mk
Sb7NcvRo3iTcoGqwgyy06As+HWSNVciKaBTFywYoJWc7yit2ndBVwEkHkIzKCV0YdQdmkvShs6YH
E3IhfjFaaSNLoHxQy2sLJrL0ow98JQmEG/rAYn7OobVGogngBgf0P0hjgwgt7HOUaI5DdBVJkggR
3HwSktaqWcCtgiHIH7qHV+esW2CnkRJ+9R5cQGsikkWEV/J7leVGs9TV4TvcO5QOOrTHYI+xeCjY
JR/m9GPDHv2oSZunUokS2A/WBelnvx6tF6LUJO2FjjlH5zU6Q+Kz/9m69LxvSZVSwiOlGnT1rt/A
77j+WDQZ8x9k2mFJetOle88+lc8sJJ/AeerI+fTlQigTfVqJUiXoKaaC3AqmI+KOnivjMLbvBVFU
1JDruuadNGcPmkgiBTnQXUGUDd6IK9JEQ9yPdM96xZP8bieeMRqTuqbxIbbey2DjVUNzRs1rosFS
TsLAdS/0fBGNdTGKhuqD7mUmsFlgGjN2eSj1tM3GnjfXwwCmzjhMbR4rLZXXk+Z/6Hp7Pn2+kJ49
jfgLHgI4Jg==
""".decode("base64").decode("zlib")

if __name__ == '__main__':
    main()

## TODO:
## Copy python.exe.manifest
## Monkeypatch distutils.sysconfig
