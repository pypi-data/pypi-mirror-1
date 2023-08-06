#!/usr/bin/env python

from distutils.core import setup

setup(name='py-aspsms',
    version='0.1.1',
    description='aspsms',
    author='Jacques Supcik',
    author_email='jacques@supcik.org',
    url='http://code.google.com/p/py-aspsms/',
    download_url='http://code.google.com/p/py-aspsms/downloads/list',
    scripts=['send_sms', 'show_sms_credit'],
    packages=['aspsms'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)

