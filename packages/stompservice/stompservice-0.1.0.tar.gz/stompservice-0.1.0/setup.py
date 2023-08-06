from setuptools import setup, find_packages
import os, sys


_install_requires = [ "stomper" ]


setup(
    name='stompservice',
    version='0.1.0',
    author='Michael Carter',
    author_email='CarterMichael@gmail.com',
    license='MIT License',
    description='A simple stomper-based STOMP service api',
    long_description='',
    packages= ['stompservice'],
    zip_safe = True,
    install_requires = [ "stomper" ],    
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],        
)
