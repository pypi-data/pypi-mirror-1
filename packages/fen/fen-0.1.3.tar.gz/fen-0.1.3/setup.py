#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name = "fen",
    version = "0.1.3",
    author = "Patrick Sabin",
    author_email = "patricksabin@gmx.at",
    url = "http://pypi.python.org/pypi/fen",
    scripts = ["fen.py"],
    data_files=[('images', ['images/black_king.svg',
                            'images/black_queen.svg',
                            'images/black_rook.svg',
                            'images/black_knight.svg',
                            'images/black_bishop.svg',
                            'images/black_pawn.svg',
                            'images/white_king.svg',
                            'images/white_queen.svg',
                            'images/white_rook.svg',
                            'images/white_knight.svg',
                            'images/white_bishop.svg',
                            'images/white_pawn.svg'
                            ])],
    description = "Generate chessboard images from fen descriptions",
    requires = ["argparse"],
    long_description = """\
Chessboard Image Generator
-------------------------------------
This tool takes a fen string and generates a fen image.

This version requires Python 2.
""",
    classifiers = [
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 2 - Pre-Alpha"
    ],
)

