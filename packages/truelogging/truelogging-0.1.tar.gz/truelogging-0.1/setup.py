# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='truelogging',
    version='0.1',
    py_modules=['truelogging'],
    install_requires=['django'],
    author='Viktor Kotseruba',
    author_email='barbuzaster@gmail.com',
    description='makes django to log all 500 to defined error log',
    license='MIT',
    keywords='logging web django',
)