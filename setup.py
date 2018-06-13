import re
import sys

from setuptools import setup


try:
    import pypandoc
    LONG_DESCRIPTION = '\n'.join([
        pypandoc.convert('README.md', 'rst'),
    ])
except (IOError, ImportError):
    LONG_DESCRIPTION = ''

main_py = open('iostat/main.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", main_py))

setup(
    name='iostat-tool',
    version=metadata['version'],
    description='parse and structuralize iostat output',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
    ],
    keywords=['iostat'],
    author='Tetsuya Morimoto',
    author_email='tetsuya dot morimoto at gmail dot com',
    url='https://github.com/t2y/iostat-parser',
    license='Apache License 2.0',
    platforms=['unix', 'linux', 'osx', 'windows'],
    packages=['iostat'],
    include_package_data=True,
    install_requires=['matplotlib'],
    tests_require=['tox', 'pytest', 'pytest-pep8', 'pytest-flakes'],
    entry_points = {
        'console_scripts': [
            'iostat-cli=iostat.main:main',
        ],
    },
)
