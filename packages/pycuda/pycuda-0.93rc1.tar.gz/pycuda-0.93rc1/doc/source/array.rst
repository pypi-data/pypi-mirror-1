The :class:`GPUArray` Array Class
=================================

.. module:: pycuda.gpuarray

.. class:: GPUArray(shape, dtype, allocator=None)

  A :class:`numpy.ndarray` work-alike that stores its data and performs its
  computations on the compute device.  *shape* and *dtype* work exactly as in
  :mod:`numpy`.  Arithmetic methods in :class:`GPUArray` support the
  broadcasting of scalars. (e.g. `array+5`) If the

  *allocator* is a callable that, upon being called with an argument of the number
  of bytes to be allocated, returns an object that can be cast to an
  :class:`int` representing the address of the newly allocated memory.
  Observe that both :func:`pycuda.driver.mem_alloc` and 
  :meth:`pycuda.tools.DeviceMemoryPool.alloc` are a model of this interface.

  .. attribute :: gpudata
    
    The :class:`pycuda.driver.DeviceAllocation` instance created for the memory that backs
    this :class:`GPUArray`.

  .. attribute :: shape

    The tuple of lengths of each dimension in the array.

  .. attribute :: dtype 
    
    The :class:`numpy.dtype` of the items in the GPU array.
    
  .. attribute :: size
    
    The number of meaningful entries in the array. Can also be computed by
    multiplying up the numbers in :attr:`shape`.

  .. attribute :: mem_size
    
    The total number of entries, including padding, that are present in
    the array. Padding may arise for example because of pitch adjustment by 
    :func:`pycuda.driver.mem_alloc_pitch`.

  .. attribute :: nbytes
    
    The size of the entire array in bytes. Computed as :attr:`size` times 
    ``dtype.itemsize``.

  .. method :: __len__()
    
    Returns the size of the leading dimension of *self*.

    .. warning ::
      
      This method existed in version 0.93 and below, but it returned the value
      of :attr:`size` instead of its current value. The change was made in order
      to match :mod:`numpy`.

  .. method :: set(ary)

    Transfer the contents the :class:`numpy.ndarray` object *ary*
    onto the device.

    *ary* must have the same dtype and size (not necessarily shape) as *self*.

  .. method :: set_async(ary, stream=None)

    Asynchronously transfer the contents the :class:`numpy.ndarray` object *ary*
    onto the device, optionally sequenced on *stream*.

    *ary* must have the same dtype and size (not necessarily shape) as *self*.


  .. method :: get(ary=None, stream=None, pagelocked=False)

    Transfer the contents of *self* into *ary* or a newly allocated
    :mod:`numpy.ndarray`. If *ary* is given, it must have the right
    size (not necessarily shape) and dtype. If it is not given,
    a *pagelocked* specifies whether the new array is allocated 
    page-locked.

  .. method :: get_async(ary=None, stream=None)

    Transfer the contents of *self* into *ary* or a newly allocated
    :mod:`numpy.ndarray`. If *ary* is given, it must have the right
    size (not necessarily shape) and dtype. If it is not given,
    a page-locked* array is newly allocated.

  .. method :: mul_add(self, selffac, other, otherfac, add_timer=None, stream=None):
    
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
  
  .. method :: fill(scalar, stream=None)

    Fill the array with *scalar*.

  .. method:: bind_to_texref(texref)

    Bind *self* to the :class:`pycuda.driver.TextureReference` *texref*.

    .. note::

      For more comprehensive functionality, consider using
      :meth:`bind_to_texref_ext`.

  .. method:: bind_to_texref_ext(texref, channels=1)

    Bind *self* to the :class:`pycuda.driver.TextureReference` *texref*.
    In addition, set the texture reference's format to match :attr:`dtype`
    and its channel count to *channels*. This routine also sets the
    texture reference's :data:`pycuda.driver.TRSF_READ_AS_INTEGER` flag, 
    if necessary.

    (Added in version 0.93.)
    
Constructing :class:`GPUArray` Instances
----------------------------------------

.. function:: to_gpu(ary, allocator=None)
  
  Return a :class:`GPUArray` that is an exact copy of the :class:`numpy.ndarray`
  instance *ary*.

  See :class:`GPUArray` for the meaning of *allocator*.

.. function:: to_gpu_async(ary, allocator=None, stream=None)
  
  Return a :class:`GPUArray` that is an exact copy of the :class:`numpy.ndarray`
  instance *ary*. The copy is done asynchronously, optionally sequenced into
  *stream*.

  See :class:`GPUArray` for the meaning of *allocator*.
  
.. function:: empty(shape, dtype)

  A synonym for the :class:`GPUArray` constructor.

.. function:: zeros(shape, dtype)

  Same as :func:`empty`, but the :class:`GPUArray` is zero-initialized before
  being returned.

.. function:: empty_like(other_ary)

  Make a new, uninitialized :class:`GPUArray` having the same properties 
  as *other_ary*.

.. function:: zeros_like(other_ary)

  Make a new, zero-initialized :class:`GPUArray` having the same properties
  as *other_ary*.

.. function:: arange(start, stop, step, dtype=None, stream=None)

  Create a :class:`GPUArray` filled with numbers spaced `step` apart,
  starting from `start` and ending at `stop`.
  
  For floating point arguments, the length of the result is
  `ceil((stop - start)/step)`.  This rule may result in the last
  element of the result being greater than `stop`.

  *dtype*, if not specified, is taken as the largest common type
  of *start*, *stop* and *step*.

.. function:: take(a, indices, stream=None)
  
  Return the :class:`GPUArray` ``[a[indices[0]], ..., a[indices[n]]]``.
  For the moment, *a* must be a type that can be bound to a texture.

.. function:: sum(a, dtype=None, stream=None)

.. function:: dot(a, b, dtype=None, stream=None)

.. function:: subset_dot(subset, a, b, dtype=None, stream=None)

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

Exponentials, Logarithms and Roots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

.. function:: rand(shape, dtype=numpy.float32, stream=None)

  Return an array of `shape` filled with random values of `dtype`
  in the range [0,1).

Single-pass Expression Evaluation
---------------------------------

.. warning::

  The following functionality is included in this documentation in the 
  hope that it may be useful, but its interface may change in future
  revisions. Feedback is welcome.

.. module:: pycuda.elementwise

Evaluating involved expressions on :class:`GPUArray` instances can be
somewhat inefficient, because a new temporary is created for each 
intermediate result. The functionality in the module :mod:`pycuda.elementwise`
contains tools to help generate kernels that evaluate multi-stage expressions
on one or several operands in a single pass.

.. class:: ElementwiseKernel(arguments, operation, name="kernel", keep=False, options=[])

    Generate a kernel that takes a number of scalar or vector *arguments*
    and performs the scalar *operation* on each entry of its arguments, if that 
    argument is a vector.

    *arguments* is specified as a string formatted as a C argument list. 
    *operation* is specified as a C assignment statement, without a semicolon. 
    Vectors in *operation* should be indexed by the variable *i*.

    *name* specifies the name as which the kernel is compiled, *keep*
    and *options* are passed unmodified to :class:`pycuda.driver.SourceModule`.

    .. method:: __call__(*args)

        Invoke the generated scalar kernel. The arguments may either be scalars or
        :class:`GPUArray` instances.

Here's a usage example::

    import pycuda.gpuarray as gpuarray
    import pycuda.driver as cuda
    import pycuda.autoinit
    import numpy
    from pycuda.curandom import rand as curand

    a_gpu = curand((50,))
    b_gpu = curand((50,))

    from pycuda.elementwise import ElementwiseKernel
    lin_comb = ElementwiseKernel(
            "float a, float *x, float b, float *y, float *z",
            "z[i] = a*x[i] + b*y[i]",
            "linear_combination")

    c_gpu = gpuarray.empty_like(a_gpu)
    lin_comb(5, a_gpu, 6, b_gpu, c_gpu)

    import numpy.linalg as la
    assert la.norm((c_gpu - (5*a_gpu+6*b_gpu)).get()) < 1e-5

(You can find this example as :file:`examples/demo_elementwise.py` in the PyCuda 
distribution.)

Reductions
----------

.. module:: pycuda.reduction

.. class:: ReductionKernel(dtype_out, neutral, reduce_expr, map_expr=None, arguments=None, name="reduce_kernel", keep=False, options=[])

    .. method __call__(*args, stream=None)

Here's a usage example::

    a = gpuarray.arange(400, dtype=numpy.float32)
    b = gpuarray.arange(400, dtype=numpy.float32)

    krnl = ReductionKernel(numpy.float32, neutral="0", 
            reduce_expr="a+b", map_expr="a[i]*b[i]", 
            arguments="float *a, float *b")

    my_dot_prod = krnl(a, b).get()
