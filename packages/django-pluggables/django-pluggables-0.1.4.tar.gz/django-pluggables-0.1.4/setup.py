import os
from setuptools import setup, find_packages

version = '0.1.4'

setup(
    name='django-pluggables',
    version=version,
    description='A design pattern for Django that allows you to build "Pluggable" Reusable Applications',
    long_description='django-pluggables is a design pattern for Django that allows you to build "Pluggable" Reusable Applications',
    author='Nowell Strite',
    author_email='nowell@strite.org',
    url='http://github.com/nowells/django-pluggables/',
    packages=find_packages(),
    zip_safe=False,
    platforms=["any"],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
    )
