The :class:`GPUArray` Array Class
=================================

.. module:: pycuda.gpuarray

.. class:: GPUArray(shape, dtype, stream=None)

  A :class:`numpy.ndarray` work-alike that stores its data and performs its
  computations on the compute device.  *shape* and *dtype* work exactly as in
  :mod:`numpy`.  Arithmetic methods in :class:`GPUArray` support the
  broadcasting of scalars. (e.g. `array+5`) If the
  :class:`pycuda.driver.Stream` *stream* is specified, all computations on
  *self* are sequenced into it.

  .. method :: set(ary, stream=None)

    Transfer the contents the :class:`numpy.ndarray` object *ary*
    onto the device, optionally sequenced on *stream*.

    *ary* must have the same dtype and size (not necessarily shape) as *self*.

  .. method :: get(ary=None, stream=None, pagelocked=False)

    Transfer the contents of *self* into *ary* or a newly allocated
    :mod:`numpy.ndarray`. If *ary* is given, it must have the right
    size (not necessarily shape) and dtype. If it is not given,
    *pagelocked* specifies whether the new array is allocated 
    page-locked.

  .. method :: mul_add(self, selffac, other, otherfac, add_timer=None):
    
    Return `selffac*self + otherfac*other`. *add_timer*, if given, 
    is invoked with the result from 
    :meth:`pycuda.driver.Function.prepared_timed_call`.

  .. method :: __add__(other)
  .. method :: __sub__(other)
  .. method :: __iadd__(other)
  .. method :: __isub__(other)
  .. method :: __neg__(other)
  .. method :: __mul__(other)
  .. method :: __div__(other)
  .. method :: __rdiv__(other)
  .. method :: __pow__(other)

  .. method :: __abs__()

    Return a :class:`GPUArray` containing the absolute value of each
    element of *self*.

  .. UNDOC reverse()
  
  .. method :: fill(scalar)

    Fill the array with *scalar*.

  .. method:: bind_to_texref(texref)

    Bind *self* to the :class:`TextureReference` *texref*.
    
Constructing :class:`GPUArray` Instances
----------------------------------------

.. function:: to_gpu(ary, stream=None)
  
  Return a :class:`GPUArray` that is an exact copy of the :class:`numpy.ndarray`
  instance *ary*. Optionally sequence on *stream*.
  
.. function:: empty(shape, dtype, stream)

  A synonym for the :class:`GPUArray` constructor.

.. function:: zeros(shape, dtype, stream)

  Same as :func:`empty`, but the :class:`GPUArray` is zero-initialized before
  being returned.

.. function:: arange(start, stop, step, dtype=numpy.float32)

  Create a :class:`GPUArray` filled with numbers spaced `step` apart,
  starting from `start` and ending at `stop`.
  
  For floating point arguments, the length of the result is
  `ceil((stop - start)/step)`.  This rule may result in the last
  element of the result being greater than `stop`.

Elementwise Functions on :class:`GPUArrray` Instances
-----------------------------------------------------

.. module:: pycuda.cumath

The :mod:`pycuda.cumath` module contains elementwise 
workalikes for the functions contained in :mod:`math`.

Rounding and Absolute Value
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. function:: fabs(array)
.. function:: ceil(array)
.. function:: floor(array)

General Transcendental Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. function:: exp(array)
.. function:: log(array)
.. function:: log10(array)
.. function:: sqrt(array)

Trigonometric Functions
^^^^^^^^^^^^^^^^^^^^^^^

.. function:: sin(array)
.. function:: cos(array)
.. function:: tan(array)
.. function:: asin(array)
.. function:: acos(array)
.. function:: atan(array)

Hyperbolic Functions
^^^^^^^^^^^^^^^^^^^^

.. function:: sinh(array)
.. function:: cosh(array)
.. function:: tanh(array)

Floating Point Decomposition and Assembly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. function:: fmod(arg, mod)

    Return the floating point remainder of the division `arg/mod`,
    for each element in `arg` and `mod`.

.. function:: frexp(arg)

    Return a tuple `(significands, exponents)` such that 
    `arg == significand * 2**exponent`.
    
.. function:: ldexp(significand, exponent)

    Return a new array of floating point values composed from the
    entries of `significand` and `exponent`, paired together as
    `result = significand * 2**exponent`.
        
.. function:: modf(arg)

    Return a tuple `(fracpart, intpart)` of arrays containing the
    integer and fractional parts of `arg`. 

Generating Arrays of Random Numbers
-----------------------------------

.. module:: pycuda.curandom

.. function:: rand(shape, dtype=numpy.float32)

  Return an array of `shape` filled with random values of `dtype`
  in the range [0,1).

