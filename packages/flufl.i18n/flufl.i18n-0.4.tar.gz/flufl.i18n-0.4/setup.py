# Copyright (C) 2009 by the Free Software Foundation, Inc.
#
# This file is part of flufl.i18n
#
# flufl.i18n is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# flufl.i18n is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with flufl.i18n.  If not, see <http://www.gnu.org/licenses/>.

import ez_setup
ez_setup.use_setuptools()

import sys
from setuptools import setup, find_packages

if sys.hexversion < 0x20600f0:
    print 'Python 2.6 or better is required'
    sys.exit(1)


def description(*docname):
    res = []
    for value in docname:
        if value.endswith('.txt'):
            with open(value) as fp:
                value = fp.read()
        res.append(value)
        if not value.endswith('\n'):
            res.append('')
    return '\n'.join(res)


sys.path.insert(0, 'src')
from flufl.i18n import __version__


setup(
    name='flufl.i18n',
    version=__version__,
    namespace_packages=['flufl'],
    packages=find_packages('src'),
    package_dir={'':'src'},
    include_package_data=True,
    zip_safe=False,
    maintainer='Barry Warsaw',
    maintainer_email='barry@python.org',
    description=open('README.txt').readline().strip(),
    long_description=description(
        'src/flufl/i18n/README.txt',
        'src/flufl/i18n/NEWS.txt'),
    license='LGPL v3',
    install_requires=[
        'setuptools',
        'zope.interface',
        ],
    url='https://launchpad.net/flufl.i18n',
    download_url= 'https://launchpad.net/flufl.i18n/+download',
    extras_require=dict(
        docs=['Sphinx', 'z3c.recipe.sphinxdoc'],
        ),
    # This does not play nicely with buildout because it downloads but does
    # not cache the package.
    #setup_requires=['eggtestinfo', 'setuptools_bzr'],
    test_suite='flufl.i18n.tests',
    )
