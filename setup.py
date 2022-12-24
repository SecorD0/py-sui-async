from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as fh:
    long_description = '\n' + fh.read()

setup(
    name='py-sui-async',
    version='1.1.1',
    license='Apache-2.0',
    author='SecorD',
    description='',
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=find_packages(),
    install_requires=['aiohttp', 'beautifulsoup4', 'bip-utils', 'fake-useragent',
                      'pretty-utils @ git+https://github.com/SecorD0/pretty-utils@main', 'PyNaCl', 'requests'],
    keywords=['sui', 'sdk', 'pysui', 'py-sui', 'suipy', 'sui-py', 'py-sui-async', 'async-sui', 'async-py-sui'],
)
