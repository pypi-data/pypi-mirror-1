#     Copyright (C) 2009
#     Associated Universities, Inc.  Washington DC, USA.
#
#     Copying and distribution of this file, with or without modification,
#     are permitted in any medium without royalty provided the copyright
#     notice and this notice are preserved.  This file is offered as-is,
#     without any warranty.

from setuptools import setup, find_packages

packages=find_packages()

setup(
    name="caslib",
    version='0.1',
    # uncomment the following lines if you fill them out in release.py
    description='caslib provides a python interface to CAS',
    author='Kai Groner',
    author_email='kgroner@nrao.edu',
    # FIXME: warning: sdist: missing required meta-data: url
    url='http://pypi.python.org/pypi/caslib',
    #download_url=download_url,
    license='LGPL',

    install_requires=[
	# Require SSL module or Python >= 2.6, does setuptools support this?
	"SSL >= 1.14",
	# "Python >= 2.6",
    ],

    extras_require=dict(
	# Earlier versions untested
	HTML=["lxml >= 2.2"],
    ),

    # Probably?  Not tested.
    zip_safe=False,
    packages=packages,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
	'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    ],
    # test_suite='nose.collector',
)
