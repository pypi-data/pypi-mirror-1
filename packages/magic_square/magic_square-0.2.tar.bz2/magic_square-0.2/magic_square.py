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
r"""
*Simple operations with magic squares.*

**Prerequisites:**
    - NumPy_

**Functions:**
    - `ismagic(A)` -- test whether *A* is a magic square.
    - `magic(N)` -- create an *N* by *N* magic square.
    - `magic_constant(A)` -- calculate the magic constant of *A*.

**Examples:**
    >>> from magic_square import *
    >>> print magic(3)
    [[8 1 6]
     [3 5 7]
     [4 9 2]]
    >>> magic_constant()
    15
    >>> ismagic(magic(4))
    True
    >>> magic_constant()
    34
    >>> magic_constant([1, 1, 1, 1])
    2
    >>> ismagic([[1, 2], [3, 4]])
    False
    
**Notes:**
    (1) Function `magic(N)` produces the same magic squares as Matlab 
    and Octave command ``magic(N)``.  The speed of calculations for *N* 
    close to 1000 is about 100--200 times faster than in Octave.

    (2) Integer arithmetic in NumPy_ is done modulo ``2**32``.  That 
    can give a false positive in `ismagic(A)` for integer arrays with
    overflowing in row, column, or diagonal sums.  To avoid that and to
    avoid wrong answers in `magic_constant(A)`, in such cases the 
    array's ``dtype`` should be changed to ``'int64'``, or if 
    ``'int64'`` also overflows, to ``'object'``.

**Screenshots:** 

    That's how it looks in SAGE_:

    |SAGE|

    And that's how it looks in IDLE_:

    |IDLE|

**Author:**
    `Alec Mihailovs`_ <alec@mihailovs.com> 

**Last Updated:**
    February 22, 2007.

.. _NumPy: http://www.scipy.org/Download

.. _SAGE: http://sage.math.washington.edu/sage/

.. _IDLE: http://www.python.org/idle/

.. |SAGE| image:: sage.png 

.. |IDLE| image:: idle.png

.. _`Alec Mihailovs`: http://mihailovs.com/Alec/
"""

__version__ = "0.2"
"""Development Status :: 3 - Alpha"""

__author__ = "Alec Mihailovs <alec@mihailovs.com>"
"""
`Alec Mihailovs`_ <alec@mihailovs.com>

.. _`Alec Mihailovs`: http://mihailovs.com/Alec/
"""

__docformat__ = "restructuredtext"
"""http://docutils.sourceforge.net/rst.html"""

from numpy import arange, asarray, flipud, r_, tile 
from math import sqrt

_constant = None    # to avoid an exception in magic_square._constant
"""Last calculated magic constant."""

def ismagic(A):
    r"""
    Test whether the given array is a magic square.

    **Input:**
        *A* -- 2D array, or a sequence that can be interpreted as such.

    **Output:**
        ``bool`` or ``NotImplementedType`` -- ``True`` if *A* is a 
        magic square, ``NotImplemented`` if the number of dimensions of 
        *A* is not 2 or 1, or the size is not a perfect square in the 
        1D case, and ``False`` otherwise. 

    **Examples:**
        >>> from magic_square import *
        >>> ismagic(magic(3))
        True
        >>> ismagic([1, 1, 1, 1])
        True
        >>> ismagic([[8, 1, 6], [3, 5, 7], [4, 9, 2]])
        True
        >>> ismagic(1)            # 0 dimensions
        NotImplemented
        >>> ismagic('[[1]]')      # a string gives 0 dimensions
        NotImplemented
        >>> ismagic([[[1]]])      # 3 dimensions
        NotImplemented        
        >>> ismagic(array([[1, 2], [3, 4]]))
        False

    **Notes:**
        Integer arithmetic in NumPy_ is done modulo ``2**32`` as in the
        following example:

        >>> from numpy import array
        >>> array([2**16])
        array([65536])
        >>> _*_
        array([0])

        That can give a false positive in `ismagic(A)` for integer
        arrays with overflowing in row, column, or diagonal sums.
        To avoid that, in such cases the array's ``dtype`` should be
        changed to either ``'int64'``, or ``'object'``, see 
        `magic_constant(A)` Notes.

    .. _NumPy: http://www.scipy.org/Download            
    """
    global _constant
    _constant = None         # may be commented out if desirable
    a = asarray(A)
    if a.ndim == 2:
        m = flipud(a).trace()
        t = (r_[a.sum(axis=0), a.sum(axis=1), a.trace()] == m).all()
        if t == True:        # not "is" because t is a NumPy boolean  
            _constant = m
            return True      # not "return t",
        else:                # to make sure that
            return False     # the return value is of the bool type     
    elif a.ndim == 1:
        s = sqrt(a.size)
        if a.size == s*s:
            return ismagic(a.reshape(s,s))
        else:
            return NotImplemented
    else:
        return NotImplemented

def magic_constant(A=None):
    r"""
    Magic constant of the magic square.

    **Input:**
        *A* -- 2D array, or a sequence that can be interpreted as such.
        If not entered, the last constructed `magic(n)` or last array 
        *A* tested in `ismagic(A)` is used.

    **Output:**
        ``dtype`` of the array, or Python ``long``, or ``NoneType`` -- 
        the magic constant if the array is a magic square, or ``None`` 
        otherwise. Python ``long`` can occur if *A* is ``None`` and the
        magic constant is calculated for the last constructed 
        `magic(n)` with large *n*.

    **Examples:**
        >>> from magic_square import *
        >>> magic_constant([1, 1, 1, 1])
        2
        >>> print magic_constant([1, 2, 3, 4])
        None
        >>> ismagic(magic(6))
        True
        >>> magic_constant()
        111
        >>> a = magic(5000)
        >>> magic_constant()
        62500002500L

    **Notes:**
        Integer arithmetic in NumPy_ is done modulo ``2**32``.  That 
        makes `magic_constant(A)` to return wrong answers for integer 
        arrays with overflowing in row, column, or diagonal sums. For 
        example,

        >>> magic_constant(magic(5000))
        -1924506940
        >>> ismagic(magic(5000))
        True
        >>> magic_constant()
        -1924506940

        Note that
        
        >>> 62500002500L % 2**32 == -1924506940 % 2**32
        True

        To avoid such wrong answers, the array's ``dtype`` can be 
        changed to ``'int64'``, or if ``'int64'`` also overflows, to
        ``'object'`` (that one significantly slows down the 
        calculations.)  In this example,

        >>> from numpy import array
        >>> magic_constant(array(magic(5000), dtype='int64'))
        62500002500
        >>> magic_constant(array(magic(5000), dtype='object'))  # long
        62500002500L

    .. _NumPy: http://www.scipy.org/Download
    """
    if A is None or ismagic(A) is True:    # avoiding NotImplemented
        return _constant

def magic(N):
    r"""
    Create an *N* by *N* magic square.

    **Input:** 
        *N* -- an integer in some form, may be float or quotted.

    **Output:** 
        an ``'int32'`` *N* by *N* array -- the same magic square as in
        Matlab and Octave ``magic(N)`` commands.  In particular, the 
        Siamese method is used for odd *N* (but with a different 
        implementation.)

    **Examples:**
        >>> from magic_square import *
        >>> magic(4)
        array([[16,  2,  3, 13],
               [ 5, 11, 10,  8],
               [ 9,  7,  6, 12],
               [ 4, 14, 15,  1]])
        >>> magic_constant()
        34       
        >>> magic(5.0)                     # can be float
        array([[17, 24,  1,  8, 15],
               [23,  5,  7, 14, 16],
               [ 4,  6, 13, 20, 22],
               [10, 12, 19, 21,  3],
               [11, 18, 25,  2,  9]])       
        >>> print magic('6')               # can be quotted 
        [[35  1  6 26 19 24]
         [ 3 32  7 21 23 25]
         [31  9  2 22 27 20]
         [ 8 28 33 17 10 15]
         [30  5 34 12 14 16]
         [ 4 36 29 13 18 11]]
        >>> magic(2)                       # consistent with Octave
        Traceback (most recent call last):
        TypeError: No such magic squares exist.
        >>> magic(0)
        array([], shape=(0, 0), dtype=int32)
        >>> magic_constant()               # the empty sum is 0
        0

    **Notes:**
         The calculations for *n* close to 1000 are about 100--200 
         times faster than in Octave.
    """
    global _constant
    n = int(N)
    if n < 0 or n == 2:                    # consistent with Octave
        raise TypeError("No such magic squares exist.")
    elif n%2 == 1:
        m = n>>1
        b = n*n + 1
        _constant = n*b>>1
        return (tile(arange(1,b,n),n+2)[m:-m-1].reshape(n,n+1)[...,1:]+
              tile(arange(n),n+2).reshape(n,n+2)[...,1:-1]).transpose()
    elif n%4 == 0:
        b = n*n + 1
        _constant = n*b>>1
        d=arange(1, b).reshape(n, n)
        d[0:n:4, 0:n:4] = b - d[0:n:4, 0:n:4]
        d[0:n:4, 3:n:4] = b - d[0:n:4, 3:n:4]
        d[3:n:4, 0:n:4] = b - d[3:n:4, 0:n:4]
        d[3:n:4, 3:n:4] = b - d[3:n:4, 3:n:4]
        d[1:n:4, 1:n:4] = b - d[1:n:4, 1:n:4]
        d[1:n:4, 2:n:4] = b - d[1:n:4, 2:n:4]
        d[2:n:4, 1:n:4] = b - d[2:n:4, 1:n:4]
        d[2:n:4, 2:n:4] = b - d[2:n:4, 2:n:4]
        return d
    else:
        m = n>>1
        k = m>>1
        b = m*m
        d = tile(magic(m), (2,2))          # that changes the _constant
        _constant = _constant*8 - n - m     
        d[:m, :k] += 3*b
        d[m:,k:m] += 3*b
        d[ k,  k] += 3*b
        d[ k,  0] -= 3*b
        d[m+k, 0] += 3*b
        d[m+k, k] -= 3*b
        d[:m,m:n-k+1] += b+b
        d[m:,m:n-k+1] += b
        d[:m, n-k+1:] += b
        d[m:, n-k+1:] += b+b
        return d

##################################################################
# Python 2.5 (r25:51908, Sep 19 2006, 09:52:17) [MSC v.1310 32 bit
# (Intel)] on win32
#
# >>> from magic_square import *
# >>> from time import clock
# >>> t=clock(); a=magic(1000); clock()-t
# 0.0191592494101839
# >>> t=clock(); a=magic(1001); clock()-t
# 0.018718461322123403
# >>> t=clock(); a=magic(1002); clock()-t
# 0.027449660797152831
# >>> t=clock(); ismagic(a); clock()-t
# True
# 0.021589410496389405
#################################################################
# $ ipython
# Python 2.5 (r25:51908, Jan 11 2007, 22:47:00)
# IPython 0.7.3.svn -- An enhanced Interactive Python.
#
# In [1]: from magic_square import *
#
# In [2]: time a=magic(1000)
# CPU times: user 0.02 s, sys: 0.00 s, total: 0.02 s
# Wall time: 0.02
#
# In [3]: time a=magic(1001)
# CPU times: user 0.00 s, sys: 0.01 s, total: 0.01 s
# Wall time: 0.02
#
# In [4]: time a=magic(1002)
# CPU times: user 0.00 s, sys: 0.02 s, total: 0.02 s
# Wall time: 0.03
#
# In [5]: time ismagic(a)
# CPU times: user 0.01 s, sys: 0.00 s, total: 0.01 s
# Wall time: 0.02
################################################################
# $ octave
# GNU Octave, version 2.1.73 (i686-pc-cygwin).
#
# octave:1> t=cputime();a=magic(1000);cputime()-t
# ans = 2
# octave:2> t=cputime();a=magic(1001);cputime()-t
# ans = 4.1410
# octave:3> t=cputime();a=magic(1002);cputime()-t
# ans = 4.9840
################################################################
