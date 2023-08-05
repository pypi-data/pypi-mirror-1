import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

version = open('VERSION').read().strip()

setup(name="NetCIDR",
    version=version,
    description="Object representations, operations and logic for hosts, networks, and collections of networks.",
    author="Duncan McGreggor",
    author_email="duncan@adytum.us",
    url="http://projects.adytum.us/tracs/NetCIDR",
    license="BSD",
    long_description='''There are five major chunks of functionality to this library:
    * create CIDR addresses for hosts and net blocks
    * get node counts for any given netblock
    * get ranges of addresses for net blocks
    * create collections of networks (list subclass)
    * determine if a CIDR address is in a given network or set of networks (__contains__ override)
    ''',
    packages=[
        'netcidr',
    ],
    classifiers = [f.strip() for f in """
    Development Status :: 3 - Alpha
    Environment :: Console
    Intended Audience :: Developers
    Intended Audience :: Information Technology
    Intended Audience :: System Administrators
    Intended Audience :: Telecommunications Industry
    License :: OSI Approved :: BSD License
    Natural Language :: English
    Operating System :: OS Independent
    Programming Language :: Python
    Topic :: Database
    Topic :: Internet
    Topic :: Multimedia :: Graphics :: Presentation
    Topic :: Software Development :: Libraries :: Python Modules
    Topic :: System :: Monitoring
    Topic :: System :: Networking :: Monitoring
    Topic :: System :: Systems Administration
    Topic :: Utilities
    """.splitlines() if f.strip()],
)
