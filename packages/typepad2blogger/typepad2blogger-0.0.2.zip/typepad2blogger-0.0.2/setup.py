""" typepad2blogger - insert typepad exported entries (moveable type import/export) into blogger

Since blogger doesn't have a formal import widget,
use the published google blogger apis to 
insert exported typepad entries into blogger.

Main script is mt2blogger.py
since easy_install chokes on a script of the same name as a module.

Currently doesn't import comments,
but the groundwork is there.

Happy Mother's Day, Carrie!
xxoo,
-e
"""

#from typepad2blogger import version
# isn't it more like __version__ ?        
version = '0.0.2'
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

print "test/data examples (c) copyright their respective authors"
print "moveable type contributors and Carrie Kirby"

scripts = ["src/scripts/mt2blogger.py"]

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Topic :: Utilities',
    ]

packages = find_packages('src')

package_dir = {'':'src'}

package_data = {'typepad2blogger': ['test/data/*data']}
description = "typepad2blogger - insert typepad exported entries (moveable type import/export) into blogger"

long_description = """\
Since blogger doesn't have a formal import widget,
use the published google blogger apis to 
insert exported typepad entries into blogger."""

name = "typepad2blogger"

author = "Erik Purins"

author_email = "erik@purins.com"

url = "http://www.piratehaven.org/~epu/index#typepad2blogger"

license = "http://www.gnu.org/licenses/gpl.txt"

install_requires = ['gdata.py >= 1.0.12.1']

zip_safe = False

test_suite = 'typepad2blogger.test'

setup_args = {
    'author':           author,
    'author_email':     author_email,
    'classifiers':      classifiers,
    'description':      description,
    'install_requires': install_requires,
    'license':          license,
    'long_description': long_description,
    'name' :            name,
    'packages':         packages,
    'package_dir':      package_dir,
    'package_data':     package_data,
    'scripts':          scripts,
    'test_suite':       test_suite,
    'url':              url,
    'version':          version,
    'zip_safe':         zip_safe,
    }

setup(**setup_args)
