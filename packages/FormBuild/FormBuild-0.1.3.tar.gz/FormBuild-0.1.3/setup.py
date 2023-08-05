from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

setup(
    name="FormBuild",
    version='0.1.3',
    description='Form generation tools to complement FormEncode',
    long_description="""
Form generation tools to complement FormEncode
""",
    license = 'MIT',
    author='James Gardner',
    author_email='james@pythonweb.org',
    url='http://www.3aims.com/formbuild/',
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    install_requires=[
        "WebHelpers>=0.1",
    ],
)
