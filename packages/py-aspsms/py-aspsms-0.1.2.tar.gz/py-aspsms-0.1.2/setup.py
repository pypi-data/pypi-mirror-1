#!/usr/bin/env python

import sys
from distutils.core import setup

if sys.hexversion < 0x02040000:
    raise RuntimeError, "Python 2.4.0 or higher required"

setup(name='py-aspsms',
    version='0.1.2',
    description='py-aspsms: Python interface to the aspsms.com services',
    long_description='''
aspsms (www.aspsms.com) is a Swiss company that offers SMS gateway
services for a fair price. Py-aspsms is a Python interface for this
service. Currently, only basic operations are supported (e.g. sending
a simple SMS or getting information about the remaining credit) but I
am currently extending it. If you have specific neeeds (e.g. sending a
ringtone or an operator logo) just put your request on the issue tracker
or send me an e-mail.
'''.strip(),
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

