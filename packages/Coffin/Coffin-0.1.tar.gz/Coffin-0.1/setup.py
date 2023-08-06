import os
# setuptools lets us have dependancies
from setuptools import setup, find_packages
#from distutils.core import setup

import coffin

# def find_packages(root):
#     # so we don't depend on setuptools; from the Storm ORM setup.py
#     packages = []
#     for directory, subdirectories, files in os.walk(root):
#         if '__init__.py' in files:
#             packages.append(directory.replace(os.sep, '.'))
#     return packages

setup(
    name='Coffin',
    version=".".join(map(str, coffin.__version__)),
    description='Jinja2 adapter for Django',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='http://www.github.com/dcramer/coffin',
    packages=find_packages(),
    install_requires=[
        'Jinja2',
        'django>=1.0',
    ]
)
