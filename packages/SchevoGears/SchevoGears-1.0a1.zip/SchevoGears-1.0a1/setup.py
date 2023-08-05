__version__ = '1.0a1'

from setuptools import setup, find_packages
import sys, os
import textwrap


setup(
    name="SchevoGears",

    version=__version__,

    description="Schevo tools for TurboGears",

    long_description=textwrap.dedent("""
    Provides integration between Schevo_ and TurboGears_.

    .. _Schevo: http://schevo.org/

    .. _TurboGears: http://turbogears.org/

    You can also get the `latest development version
    <http://getschevo.org/hg/repos.cgi/schevogears-dev/archive/tip.tar.gz#egg=SchevoGears-dev>`__.
    """),

    classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Database :: Database Engines/Servers',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],

    keywords='',

    author='Orbtech, L.L.C. and contributors',
    author_email='schevo@googlegroups.com',

    url='http://schevo.org/wiki/SchevoGears',

    license='LGPL',

    platforms=['UNIX', 'Windows'],

    packages=find_packages(exclude=['doc', 'tests']),

    include_package_data=True,

    zip_safe=False,

    install_requires=[
    'Schevo >= 3.0',
    'TurboGears < 1.1, >= 1.0b2',
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
    [schevo.schevo_command]
    tg = schevogears.script:start

    [turbogears.identity.provider]
    schevo = schevogears.identity:SchevoIdentityProvider

    [turbogears.visit.manager]
    schevo = schevogears.visit:SchevoVisitManager
    """,
    )
