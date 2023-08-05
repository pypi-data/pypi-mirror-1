# =============
# magic_square_
# ============= 
#
# *Simple operations with magic squares.*
#
# Copyright (c) 2007 `Alec Mihailovs`_ <alec@mihailovs.com>
#     All rights reserved. Licensed under the `MIT License`_ .
#
# .. _magic_square: http://mihailovs.com/Alec/Python/magic_square.html
#
# .. _`Alec Mihailovs`: http://mihailovs.com/Alec/ 
#     
# .. _`MIT License`: http://opensource.org/licenses/mit-license.php
#
########################################################################

from distutils.core import setup

setup(name='magic_square',
      version='0.2',
      description='Simple operations with magic squares.',
      author='Alec Mihailovs',
      author_email='alec@mihailovs.com',
      url='http://mihailovs.com/Alec/',
      long_description="""Simple operations with magic squares
      
      **Prerequisites:**
          - NumPy_

      **Functions:**
          - `ismagic(A)` -- test whether *A* is a magic square.
          - `magic(N)` -- create an *N* by *N* magic square.
          - `magic_constant(A)` -- calculate the magic constant of *A*.

      .. _NumPy: http://www.scipy.org/Download""",
      download_url='http://mihailovs.com/Alec/Python/magic_square.html',
      license='MIT License',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Education',
          'Topic :: Games/Entertainment',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      py_modules=['magic_square'],
      )

