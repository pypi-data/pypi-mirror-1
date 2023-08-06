# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.extension import Extension

setup(
    name='cbase62',
    description='base62 encode/decode',
    version='0.1',
    author='Viktor Kotseruba',
    author_email='barbuzaster@gmail.com',
    license='MIT',
    keywords='web',
    url='http://bitbucket.org/barbuza/cbase62/',
    ext_modules=[Extension('cbase62', ['cbase62.c'])]
)
