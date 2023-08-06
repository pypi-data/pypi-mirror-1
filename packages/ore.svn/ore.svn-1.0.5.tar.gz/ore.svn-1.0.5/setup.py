import os

from setuptools import setup, find_packages

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
Programming Language :: Python
Topic :: Software Development :: Version Control
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Microsoft :: Windows
Operating System :: Unix
"""

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="ore.svn",
    version="1.0.5",
    packages=find_packages('src', exclude=["*.tests"]),
    install_requires=['transaction', 'zope.interface'],
    extras_require = { 'test':['zope.schema', 'zope.component'] },
    package_dir= {'':'src'},
    namespace_packages=['ore'],
    include_package_data = True,
    zip_safe=True,
    url="https://svn.objectrealms.net/svn/public/ore.svn",
    author='Kapil Thangavelu',
    author_email='kapil.foss@objectrealms.net',
    classifiers = filter( None, classifiers.split('\n') ),
    description="An object oriented api for subversion with support for r/w",
    long_description=( read("src","ore","svn","readme.txt") + '\n\n' + read('changes.txt') ),
    license='http://www.apache.org/licenses/LICENSE-2.0',
    keywords="zope svn subversion",
    )
