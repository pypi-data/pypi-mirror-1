# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages

name = 'gocept.cxoracle'

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Environment :: Plugins',
    'Framework :: Buildout',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Zope Public License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: C',
    'Programming Language :: Python',
    'Topic :: Software Development :: Build Tools',
    'Topic :: System :: Software Distribution',
]

setup(
    name = name,
    version = '0.1',
    author = 'Christian Zagrodnick',
    author_email = 'cz@gocept.com',
    description = \
    'zc.buildout recipe for installing cx_Oracle',
    long_description = (
        open('README.txt').read() +
        '\n\n' +
        open(os.path.join('src', 'gocept', 'cxoracle', 'README.txt')).read() +
        '\n\n' +
        open('CHANGES.txt').read()),
    license = 'ZPL 2.1',
    classifiers = classifiers,
    url = 'http://pypi.python.org/pypi/gocept.cxoracle',
    download_url = 'http://pypi.python.org/pypi/gocept.cxoracle',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'': 'src'},
    namespace_packages = ['gocept'],
    install_requires = ['zc.buildout', 'setuptools'],
    extras_require = {'test': ['zope.testing']},
    entry_points = {'zc.buildout': ['default = %s.recipe:CxOracle' % name,],},
    )

