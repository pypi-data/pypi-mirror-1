from distutils.core import setup
from sudokulib import __version__
import os

setup(
    name='sudokulib',
    version=__version__,
    description='Tools for generating solutions and starting grids for Sudoku.',
    long_description=open('README', 'r').read(),
    keywords='sudoku',
    author='Josh VanderLinden',
    author_email='codekoala at gmail com',
    license='BSD',
    package_dir={'sudokulib': 'sudokulib'},
    packages=['sudokulib'],
    platforms=['Windows', 'Linux', 'OSX'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Games/Entertainment :: Puzzle Games",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)

