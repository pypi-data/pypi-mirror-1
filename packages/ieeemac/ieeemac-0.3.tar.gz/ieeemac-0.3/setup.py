from setuptools import setup
import sys, os
from glob import glob

version = '0.3'

setup(name='ieeemac',
    version=version,
    description="Parse and convert MAC addresses",
    long_description="""\
Parses, finds, and converts MAC addresses between the following formats:
 * bare:    001122334455
 * windows: 00-11-22-33-44-55
 * unix:    00:11:22:33:44:55
 * cisco:   0011.2233.4455
""",
    classifiers=[
        "Topic :: System :: Networking",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
    ],
    keywords='MAC ethernet',
    author='Justin Azoff',
    author_email='JAzoff@uamail.albany.edu',
    url='',
    license='MIT',
    packages = ["ieeemac"], 
    include_package_data=True,
    zip_safe=True,
    #install_requires=[
        # -*- Extra requirements: -*-
    #],
    test_suite='nose.collector',
    entry_points = {
        'console_scripts': [
            'ieeemac  = ieeemac:main',
            'ieeemac-extract  = ieeemac.mac_extract:main',
        ]
    }
)
