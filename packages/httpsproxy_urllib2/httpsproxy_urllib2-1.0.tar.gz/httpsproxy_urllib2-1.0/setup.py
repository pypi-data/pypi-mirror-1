from setuptools import setup
import os

version = '1.0'

setup(
    name='httpsproxy_urllib2',
    version=version,
    description="Python 2.5 urllib2 patched to use CONNECT for https proxies",
    long_description=open("README.txt").read(),
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='urllib2 https proxy CONNECT',
    url='http://pypi.python.org/pypi/httpsproxy_urllib2',
    maintainer='Jarn AS',
    maintainer_email='info@jarn.com',
    license='Python',
    py_modules=[
        'urllib2',
        'httplib',
    ]
)
