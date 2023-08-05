import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

version = open('VERSION').read().strip()

setup(name="Adytum-NetCIDR",
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
    namespace_packages = ['adytum'],
    packages=[
        'adytum',
        'adytum.netcidr',
    ],
    package_dir = {
        'adytum': 'lib',
    },
)
'''
    classifiers = [f.strip() for f in """
    License :: OSI-Approved Open Source :: BSD License
    Development Status :: 4 - Alpha
    Intended Audience :: by End-User Class :: System Administrators
    Intended Audience :: Developers
    Intended Audience :: by End-User Class :: Advanced End Users
    Intended Audience :: by Industry or Sector :: Information Technology
    Intended Audience :: by Industry or Sector :: Telecommunications Industry
    Programming Language :: Python
    Topic :: Software Development :: Object Oriented
    Topic :: System :: Networking
    Topic :: System :: Systems Administration
    Operating System :: Grouping and Descriptive Categories :: All POSIX (Linux/BSD/UNIX-like OSes)
    """.splitlines() if f.strip()],
'''
