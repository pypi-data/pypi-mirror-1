from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

setup(
    name="FormBuild",
    version='0.1.6b',
    description='Form generation tools to complement FormEncode',
    long_description="""
Form generation tools to complement FormEncode

`Development version <http://formbuild.org/svn/FormBuild/trunk#egg=FormBuild-dev>`_
""",
    license = 'MIT',
    author='James Gardner',
    author_email='james@pythonweb.org',
    url='http://formbuild.org',
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    install_requires=[
        "WebHelpers>=0.1",
    ],
)
