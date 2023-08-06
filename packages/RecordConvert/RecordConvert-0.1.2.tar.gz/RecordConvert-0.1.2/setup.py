try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.1.2'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "RecordConvert\n"
    "+++++++++++++\n\n.. contents ::\n\n"
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
    name='RecordConvert',
    version=version,
    description="Tools for handling nested sets of records of the type you might encounter frequently when dealing with relational database management systems. Includes tools for working with the Repeatable Nested Records data model. Built on ConversionKit.",
    long_description=long_description,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[],
    keywords='',
    author='James Gardner',
    author_email='',
    url='http://jimmyg.org/work/code/recordconvert/index.html',
    license='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "ConversionKit",
        "BareNecessities",
    ],
    entry_points="""
    """,
)
