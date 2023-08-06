# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='except_py_client',
    version='0.1.2',
    packages=['except_py_client',
              'except_py_client.django'],
    install_requires=['simplejson'],
    author='Viktor Kotseruba',
    author_email='barbuzaster@gmail.com',
    description='except.py client library',
    license='MIT',
    keywords='exceptions logging errors',
)

