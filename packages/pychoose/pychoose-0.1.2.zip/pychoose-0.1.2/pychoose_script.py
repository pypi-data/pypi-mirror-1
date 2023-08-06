from subprocess import Popen
from os import environ, pathsep
from os.path import isdir, isfile, join
from sys import argv, exit


__version__ = '0.1.2'

sysdrive = environ['SYSTEMDRIVE']


def not_python_dir(path):
    return not path.lower().startswith('%s\python' % sysdrive)


def get_python_dir(version):
    python_dir = '%s%s%s' % (sysdrive, '\python', version)
    if (
        isdir(python_dir) and
        isfile(join(python_dir, 'python.exe'))
    ):
        return python_dir
    else:
        print 'python%s not found' % version
        exit(1)


def get_python_dirs(version):
    root = get_python_dir(version)
    subdirs = [
        join(root, dirname)
        for dirname in ['DLLs', 'Scripts']
        if isdir(join(root, dirname))
    ]
    return [root] + subdirs


def get_new_paths(version):
    python_dirs = get_python_dirs(version)

    orig_paths = environ['PATH'].split(pathsep)
    new_paths = python_dirs + filter(not_python_dir, orig_paths)
    return pathsep.join(new_paths)


def start_new_shell(version, paths):
    command = '&&'.join([
        'set PROMPT=(Py%s) %%PROMPT%%' % (version,),
        'set PATH=%s' % (paths,),
        'python -V',
    ])
    process = Popen(
        'cmd.exe /k "%s"' % (command,),
        shell=False,
    )
    process.wait()


def main():
    if len(argv) != 2:
        print 'USAGE: pychoose XX'
        print 'where XX is a two digit Python version, eg. 26 or 31'
        exit(2)
    version = argv[1]
    paths = get_new_paths(version)
    start_new_shell(version, paths)


if __name__ == '__main__':
    main()
