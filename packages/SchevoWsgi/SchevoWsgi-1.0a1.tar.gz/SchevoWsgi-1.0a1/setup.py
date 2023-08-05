__version__ = '1.0a1'

from setuptools import setup, find_packages
import sys, os
import textwrap


setup(
    name="SchevoWsgi",

    version=__version__,

    description="Schevo tools for WSGI",

    long_description=textwrap.dedent("""
    Provides integration between Schevo_ and WSGI_ apps.

    .. _Schevo: http://schevo.org/

    .. _WSGI: http://www.python.org/peps/pep-0333.html

    You can also get the `latest development version
    <http://getschevo.org/hg/repos.cgi/schevowsgi-dev/archive/tip.tar.gz#egg=SchevoWsgi-dev>`__.
    """),

    classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Database :: Database Engines/Servers',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],

    keywords='',

    author='Orbtech, L.L.C. and contributors',
    author_email='schevo@googlegroups.com',

    url='http://schevo.org/wiki/SchevoWsgi',

    license='LGPL',

    platforms=['UNIX', 'Windows'],

    packages=find_packages(exclude=['doc', 'tests']),

    include_package_data=True,

    zip_safe=False,

    install_requires=[
    'Schevo >= 3.0',
    ],

    tests_require=[
    'nose >= 0.10.1',
    ],
    test_suite='nose.collector',

    extras_require={
    },

    dependency_links = [
    ],

    entry_points = """
    [paste.filter_factory]
    dbopener = schevowsgi.dbopener:filter_factory
    """,
    )
