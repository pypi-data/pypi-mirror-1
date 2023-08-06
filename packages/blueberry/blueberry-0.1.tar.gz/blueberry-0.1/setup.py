# blueberry - Yet another Python web framework.
#
#       http://code.google.com/p/blueberrypy
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the BSD license. See
# the LICENSE file for full text.

try:
    from setuptools import setup, find_packages
except ImportError:
    raise SystemExit('Please install setuptools first.')

setup(
    name='blueberry',
    version='0.1',
    description='Blueberry Web Framework',
    long_description='Yet another Python web framework',
    license='BSD',
    author='David Reynolds',
    author_email='david@alwaysmovefast.com',
    url='http://code.google.com/p/blueberrypy',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'WebHelpers>=0.6.4',
        'Mako>=0.2.4',
        'WebOb>=0.9.6.1',
        'nose>=0.10.4',
        'WebTest>=1.1'
    ]
)
