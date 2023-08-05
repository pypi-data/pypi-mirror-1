from distutils.core import setup
setup(name='magic_square',
      version='0.1',
      description='Simple operations with magic squares.',
      author='Alec Mihailovs',
      author_email='alec@mihailovs.com',
      url='http://mihailovs.com/Alec/',
      long_description="""Simple operations with magic squares.

PREREQUISITES:
    NumPy

FUNCTIONS:
    ismagic(A) -- test whether A is a magic square.
    magic(N) -- create an N-by-N magic square.
    magic_constant(A) -- calculate the magic constant of A.
""",
      download_url='http://mihailovs.com/Alec/Python/magic_square.html',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License' ,
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

