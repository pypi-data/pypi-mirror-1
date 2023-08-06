from setuptools import setup, find_packages
import sys, os

version = '1.3'

setup(name='minifb',
    version=version,
    description="mini facebook api",
    long_description="""\
A minimal API for writing web applications with Facebook in Python.
The two functions in the module are all that should be needed to generate
and validate information with the Facebook server. 
""",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='facebook',
    author='Peter Shinners',
    author_email='pete@shinners.org',
    url='http://code.google.com/p/minifb/',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    )

