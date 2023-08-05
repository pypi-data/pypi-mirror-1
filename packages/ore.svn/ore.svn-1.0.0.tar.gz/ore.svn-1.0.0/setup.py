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

setup(
    name="ore.svn",
    version="1.0.0",
    packages=find_packages('src', exclude=["*.tests"]),
#    install_requires="ZODB3 >= 3.6.0",
    package_dir= {'':'src'},
    namespace_packages=['ore'],
    package_data = {
    '': ['*.txt', '*.zcml', '*.pt'],
    },
    zip_safe=True,
    url="http://objectrealms.net",
    test_suite="ore.svn.tests.all.test_suite",
    author='ObjectRealms, LLC',
    author_email='info@objectrealms.net',
    classifiers = filter( None, classifiers.split('\n') ),
    description="""\
ore.svn is an easier mechanism to utilize the native python subversion
binding, without worrying about memory pools, and fufilling the zope3
dictionary container interface.
""",
    license='LGPL',
    keywords="zope svn subversion",
    )
