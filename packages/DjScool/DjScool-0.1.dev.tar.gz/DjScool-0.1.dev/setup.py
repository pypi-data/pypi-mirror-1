#!/usr/bin/env python

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

setup(
    name='DjScool',
    version='0.1.dev',
    author='The DjScool Team',
    author_email='djscool@alerts.assembla.com',
    url='http://assembla.com/spaces/DjScool',
    packages=['djscool', 'djscool.school'],
    package_data={'djscool': ['templates/*.html', 'templates/*/*.html']},
)
