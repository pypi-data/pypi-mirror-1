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
    "ConfigConvert\n"
    "+++++++++++++\n\n.. contents ::\n"
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
    name='ConfigConvert',
    version=version,
    description="Tools for managing config files. Built on ConversionKit.",
    long_description=long_description,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[],
    keywords='',
    author='James Gardner',
    author_email='',
    url='http://jimmyg.org/work/code/configconvert/index.html',
    license='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "BareNecessities",
        "ConversionKit",
        "NestedRecord",
    ],
    entry_points="""
    """,
)
