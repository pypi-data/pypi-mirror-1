from subprocess import Popen
from os import environ, pathsep
from os.path import isdir, isfile, join
from sys import argv, exit, stderr


__version__ = '0.1.3'

sysdrive = environ['SYSTEMDRIVE']


def get_python_dir(version):
    python_dir = '%s%s%s' % (sysdrive, '\python', version)
    if (
        isdir(python_dir) and
        isfile(join(python_dir, 'python.exe'))
    ):
        return python_dir
    else:
        stderr.write('python%s not found\n' % version)
        exit(1)


def get_python_dirs(version):
    root = get_python_dir(version)
    subdirs = []
    for dirname in ['DLLs', 'Scripts']:
        subdir = join(root, dirname)
        if isdir(subdir):
            subdirs.append(subdir)
    return [root] + subdirs


def not_python_dir(path):
    python_prefix = ('%s\python' % sysdrive).lower()
    is_ok = not path.lower().startswith(python_prefix)
    return is_ok


def get_new_paths(version):
    python_dirs = get_python_dirs(version)
    orig_paths = environ['PATH'].split(pathsep)
    new_paths = python_dirs + list(filter(not_python_dir, orig_paths))
    return pathsep.join(new_paths)


def start_new_shell(version, paths):
    commands = [
        'set PROMPT=(Py%s) %%PROMPT%%' % (version,),
        'set PATH=%s' % (paths,),
    ]
    # Early version of Python don't support -V
    if version not in ['15', '16']:
        commands.append('python -V')
    command = '&&'.join(commands)

    print command
    process = Popen(
        'cmd.exe /k "%s"' % (command,),
        shell=False,
    )
    process.wait()


def main():
    if len(argv) != 2:
        stderr.write('USAGE: pychoose XX\n')
        stderr.write('where XX is a two digit Python version, eg. 26 or 31\n')
        exit(2)
    version = argv[1]
    paths = get_new_paths(version)
    start_new_shell(version, paths)


if __name__ == '__main__':
    main()
