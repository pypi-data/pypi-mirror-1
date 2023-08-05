__version__ = '0.1'

from setuptools import setup

setup(
    name="eggtestinfo",
    version=__version__,
    description="Add test information to .egg-info",
    author="Tres Seaver",
    author_email="tseaver@palladion.com",
    license="PSF or ZPL",
    long_description = open('README.txt').read(),
    keywords = "setuptools eggs testing",
    url = "http://pypi.python.org/pypi/eggtestinfo",
    packages = (),
    py_modules = ['eggtestinfo'],
    zip_safe = True,

    entry_points = {

        "egg_info.writers": [
            "test_info.txt = eggtestinfo:write_test_info",
        ],

    },

    classifiers = [f.strip() for f in """
    Development Status :: 3 - Alpha
    Intended Audience :: Developers
    License :: OSI Approved :: Python Software Foundation License
    License :: OSI Approved :: Zope Public License
    Operating System :: OS Independent
    Programming Language :: Python
    Topic :: Software Development :: Libraries :: Python Modules
    Topic :: System :: Archiving :: Packaging""".splitlines() if f.strip()],
)
