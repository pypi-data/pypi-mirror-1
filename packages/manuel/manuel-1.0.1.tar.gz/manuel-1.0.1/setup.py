from setuptools import setup, find_packages
import os

long_description = (
    open('README.txt').read()
    + '\n\n'
    + open('CHANGES.txt').read()
    )

setup(
    name='manuel',
    version='1.0.1',
    url = 'http://pypi.python.org/pypi/manuel',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    author='Benji York',
    author_email='benji@benjiyork.com',
    description=
        'Manuel lets you mix and match traditional doctests with custom test '
        'syntax.',
    license='ZPL',
    install_requires=[
        'setuptools',
        'zope.testing',
        ],
    include_package_data=True,
    long_description = long_description,
    )
