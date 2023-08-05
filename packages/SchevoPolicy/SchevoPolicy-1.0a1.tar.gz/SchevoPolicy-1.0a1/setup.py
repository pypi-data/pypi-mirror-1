__version__ = '1.0a1'

from setuptools import setup, Extension, find_packages
import sys, os
import textwrap


setup(
    name="SchevoPolicy",

    version=__version__,

    description="Context-sensitive security policy enforcement "
                "for Schevo databases",

    long_description=textwrap.dedent("""
    SchevoPolicy provides security policy enforcement for Schevo
    databases.

    * Policies are separate from the database itself.  More than one
      policy may be enforced for a given database.

    * Generic functions are used to give a wide array of flexibility
      in defining policies, while maintaining readability.

    * The API used by client code is the same as that of the database
      itself.  For example, accessing the list of extent names
      directly and through a security policy that allows it::

        >>> db.extent_names()
        ['Bar', 'Foo']

        >>> policy = SecurityPolicy()
        >>> context = dict(username='jdoe')
        >>> dbp = policy(context)
        >>> dbp.extent_names()
        ['Bar', 'Foo']
    
    You can also get the `latest development version
    <http://getschevo.org/hg/repos.cgi/schevopolicy-dev/archive/tip.tar.gz#egg=SchevoPolicy-dev>`__.
    """),

    classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Database :: Database Engines/Servers',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],

    keywords='database dbms',

    author='Orbtech, L.L.C. and contributors',
    author_email='schevo@googlegroups.com',

    url='http://schevo.org/wiki/Schevo',

    license='LGPL',

    platforms=['UNIX', 'Windows'],

    packages=find_packages(exclude=['doc', 'tests']),

    include_package_data=True,

    zip_safe=False,

    install_requires=[
    'Schevo >= 3.1a1',
    'RuleDispatch == dev, >= 0.5a0dev-r2306',
    'DecoratorTools',
    ],

    tests_require=[
    'nose >= 0.10.1',
    ],
    test_suite='nose.collector',

    extras_require={
    },

    dependency_links = [
    'http://turbogears.org/download/filelist.html',
    ],

    entry_points = """
    [paste.filter_factory]
    policywrapper = schevopolicy.wrapper:filter_factory
    """,
    )
