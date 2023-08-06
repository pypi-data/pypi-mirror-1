# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Setup script.
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = "rod.recipe.appengine",
    version = "1.0.0b2",
    author = "Tobias Rodaebel",
    author_email = "rodaebel@users.sourceforge.net",
    description = "ZC Buildout recipe for building, testing and deploying GAE projects.",
    license = "GPLv3",
    keywords = "appengine zc.buildout recipe",
    url='http://cheeseshop.python.org/pypi/rod.recipe.appengine',
    long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Documentation\n'
        '*************\n'
        + '\n' +
        read('rod', 'recipe', 'appengine', 'README.txt')
        ),
    classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 4 - Beta',
        ],
    packages = find_packages(),
    include_package_data = True,
    package_data = {'rod.recipe.appengine': ['README.txt']},
    data_files = [('.', ['README.txt']),],
    namespace_packages = ['rod', 'rod.recipe'],
    install_requires = [
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg'],
    entry_points = {'zc.buildout': ['default = rod.recipe.appengine:Recipe']},
    zip_safe = True,
    )
