.. line-block::

    PyPI package page: http://pypi.python.org/pypi/pychoose
    Subversion repository: http://code.google.com/p/pychoose/


Description
-----------

From the command-line, run::

    > pychoose XY

This will make Python version X.Y active, if it is installed, for subsequent
commands from the same prompt. The change is local to this shell.

The prompt is modified to indicate the modified environment.

To revert to the previously used version of Python, type 'exit'

This works by starting a new Cmd shell with a modified PATH, by prepending
C:\\PythonXY and its subdirectories, and importantly by removing any other
C:\\PythonZZ directories and subdirectories.

Multiple invocations of pychoose can be nested.


Dependencies
------------

No dependencies other than Python itself.

Can be used to switch TO any version of Python at all (and then back with 'exit'.)
However, the version of Python you are switching FROM must be from 2.4 to 3.1.


Installing
----------

Windows users may download and double-click a graphical installer from
http://pypi.python.org/pypi/pychoose.

Command-line jockeys with setuptools installed may use:

    ``easy_install pychoose``

or, if pip is installed:

    ``pip install pychoose``

or download a zip of the source from http://pypi.python.org/pypi/pychoose and use:

    ``python setup.py install``

Alternatively, to check out the latest unstable source from subversion,
including tests, see:

    http://code.google.com/p/pychoose/source/checkout.


Experiment on WindowsXP shows that pychoose only needs to be installed once,
on your default version of Python, not on all installed versions of Python.
After running pychoose, it is no longer on your PATH, however it is still
found by future invocations - presumably the shell caches locations of
executables or somesuch.



Known Problems
--------------

Doesn't work in a Cygwin shell, nor on other platforms.

Should get install dirs of various Python versions from the registry, insted of
assuming they are all variations on C:\\PythonXX.

Can't switch from versions of Python prior to 2.4, since we use 'subprocess' to
launch the new shell.

Doesn't affect Windows .py filetype associations. Perhaps this could be tackled by
inserting an environment variable into the registry keys, set the env var in the
registry (to persist its default value) and then change that value temporarily
and locally in this script.

Haven't tested how it interacts with virtualenv.

Currently adds all subdirectories of PythonXX to the PATH. This is probably
overkill. Can we filter out desired subdirectories with any reliability?


License
-------

Pychoose is distributed under the BSD license. Live long and prosper.
