import os
import re

from setuptools import setup

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

main_py = open('iostat/main.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", main_py))

setup(
    name='iostat-tool',
    version=metadata['version'],
    description='parse and visualize iostat output',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
    ],
    keywords=['iostat'],
    author='Tetsuya Morimoto',
    author_email='tetsuya.morimoto@gmail.com',
    url='https://github.com/t2y/iostat-tool',
    license='Apache License 2.0',
    platforms=['unix', 'linux', 'osx', 'windows'],
    packages=['iostat'],
    include_package_data=True,
    install_requires=['matplotlib'],
    tests_require=['tox', 'pytest', 'pytest-pep8', 'pytest-flakes'],
    entry_points={
        'console_scripts': [
            'iostat-cli=iostat.main:main',
        ],
    },
)
