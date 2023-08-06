"""initd: module for simplifying creation of initd daemons.

This module provides functionality for starting, stopping and
restarting daemons.  It also provides a simple utility for reading the
command line arguments and determining which action to perform from
them.
"""

from setuptools import setup

doclines = __doc__.splitlines()

setup(
    name = 'initd',
    version = '0.0.1',
    py_modules = ['initd'],
    platforms = ['POSIX'],

    install_requires = ['daemon>=1.0.1'],

    author = 'Michael Andreas Dagitses',
    author_email = 'michael.dagitses@gmail.com',

    description = doclines[0],
    long_description = '\n'.join(doclines[2:]),

    license = 'http://www.gnu.org/licenses/gpl.html',
    url = 'http://pypi.python.org/pypi/initd/0.0.1',
    test_suite = 'test.test_initd.suite',

    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Boot :: Init',
    ],
)