"""
py.test plugin for reporting test coverage using the 'figleaf' package.

Usage
---------------

after installation (e.g. via ``pip install pytest-figleaf``) you can type::

    py.test --figleaf [...]

to enable figleaf coverage.  A default ".figleaf" data file
and "html" directory will be created.  You can use ``--fig-data`` 
and ``fig-html`` to modify the paths. 
"""

from setuptools import setup

setup(
    name="pytest-figleaf",
    version="1.0",
    description='py.test figleaf coverage plugin',
    long_description=__doc__,
    license='MIT',
    author='holger krekel',
    author_email='py-dev@codespeak.net,holger@merlinux.eu', 
    url='http://bitbucket.org/hpk42/pytest-figleaf',
    platforms=['linux', 'osx', 'win32'],
    py_modules=['pytest_figleaf'],
    entry_points = {'pytest11': ['pytest_figleaf = pytest_figleaf'],},
    zip_safe=False,
    install_requires = ['figleaf', 'py>=1.1.1'],
    classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS :: MacOS X',
    'Topic :: Software Development :: Testing',
    'Topic :: Software Development :: Quality Assurance',
    'Topic :: Utilities',
    'Programming Language :: Python',
    ],
)
