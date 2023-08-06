#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from argvalidate import __version__ as argvalidate_version

try:
    import nose
    argvalidate_test_suite = 'nose.collector'
except ImportError:
    argvalidate_test_suite = 'argvalidate_tests.ArgvalidateTestSuite'


from setuptools import setup

setup(
    name="argvalidate",
    version=argvalidate_version,
    py_modules = ['argvalidate'],
    author="Stephan Peijnik",
    author_email="stephan@peijnik.at",
    description="Simple argument validator library",
    license="LGPLv3+",
    url="http://bitbucket.org/sp/python-argvalidate",
    test_suite=argvalidate_test_suite,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Utilities',
        ],
    )
