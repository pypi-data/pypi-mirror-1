from distutils.core import setup
from sudokulib import __version__

setup(
    name='sudokulib',
    version=__version__,
    description='Tools for generating solutions and starting grids for Sudoku.',
    long_description=u"""sudokulib is a collection of tools that are useful for 
generating solutions to Sudoku puzzles.  It uses a recursive backtracking 
algorithm (originally written by Jeremy Brown, Cel Destept), and is 
capable of generating a 3x3 Sudoku in ~0.015 seconds.  It can also generate 
4x4 Sudokus in ~0.100 seconds (sometimes longer).

Some 5x5 grids have been generated in a matter of seconds using this library, 
but I've also seen the program run for hours without successfully generating 
a 5x5.  Anything beyond 5x5 always seems to take a long time.

The library also provides utilities for generating starting grids, so you can 
play Sudoku instead of just generating solutions.  There are several difficulty 
levels to choose from.""",
    keywords='sudoku',
    author='Josh VanderLinden',
    author_email='codekoala at gmail com',
    license='BSD',
    package_dir={'sudokulib': 'sudokulib'},
    packages=['sudokulib'],
    platforms=['Windows', 'Linux', 'OSX'],
)

