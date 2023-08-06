# Copyright (c) 2008 - 2009 David Pratt
# All Rights Reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
"""Distutils setup
"""

from setuptools import setup, find_packages
import os

def read(*rnames):
    try:
        return open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    except:
        return open(os.path.join(os.getcwd(), *rnames)).read()

__version__ = '1.0a6'

name = 'repoze.cssutils'

requires = ['setuptools',
            'nose',
           ]

setup(name=name,
      version=__version__,
      description = 'CSS parsing and utilities',
      long_description=(read('README.txt')+'\n\n'+read('CHANGES.txt')),
      keywords = "css repoze parsing",
      author = "David Pratt",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD (refer to /docs/LICENSE.txt)",
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Python Modules',      
          ],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages = ['repoze'],
      install_requires=requires,
      tests_require=requires,
      test_suite='nose.collector',
      include_package_data = True,
      zip_safe = False,
     )

