try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '2.2.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "FormBuild\n"
    "+++++++++\n\n.. contents ::\n\n"
    "\n"+read('doc/index.txt')
    + '\n'
    + read('CHANGELOG.txt')
    + '\n'
    'License\n'
    '=======\n'
    + read('LICENSE.txt')
    + '\n'
    'Download\n'
    '========\n'
)

setup(
    name='FormBuild',
    version=version,
    description="Build forms quickly and easily using groups of simple helper functions.",
    long_description=long_description,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=['Development Status :: 4 - Beta'],
    keywords='',
    author='James Gardner',
    author_email='',
    url='http://jimmyg.org/work/code/formbuild/index.html',
    license='GPLv3',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "WebHelpers>=0.6.1,<0.6.99"
    ],
    entry_points="""
    """,
)
