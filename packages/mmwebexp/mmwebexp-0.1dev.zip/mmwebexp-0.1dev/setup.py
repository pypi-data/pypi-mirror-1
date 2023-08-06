"""
Mailman Web Exporter
-----------------------

A simple command line utility to log into a Mailman web control panel and
extract all subscribers/members found there.

"""

import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = "mmwebexp",
    version = "0.1dev",
    description = "A screen scraper to extract subscribers/members from a Mailman web control panel",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "randy@rcs-comp.com",
    url='http://pypi.python.org/pypi/mmwebexp/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    py_modules=['mmwebexp'],
    entry_points="""
    [console_scripts]
    mmwebexp = mmwebexp:main
    """,
    zip_safe=False
)