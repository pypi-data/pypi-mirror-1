try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.3.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "ConversionKit\n"
    "+++++++++++++\n"
    "\n.. contents ::\n"
    "\n"+read('doc/index.txt')
    + '\n'
    + read('CHANGELOG.txt')
    + '\n'
    + 'License\n'
    + '=======\n'
    + read('LICENSE.txt')
    + '\n'
    'Download\n'
    '========\n'
)


setup(
    name='ConversionKit',
    version=version,
    description="A general purpose conversion library",
    long_description=long_description,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[],
    keywords='',
    author='James Gardner',
    author_email='',
    url='http://jimmyg.org/work/code/conversionkit/index.html',
    licensme='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'example', 'test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    entry_points="""
    """,
)

