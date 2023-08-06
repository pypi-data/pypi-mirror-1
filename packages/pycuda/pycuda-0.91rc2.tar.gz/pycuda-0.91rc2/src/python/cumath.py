import pycuda.gpuarray as gpuarray
import pycuda._kernel as _kernel
import numpy
import math

def _make_unary_array_func(name):
    def f(array):
        result = gpuarray.GPUArray(array.shape, array.dtype, array.stream)
        
        func = _kernel.get_unary_func_kernel(name)
        func.set_block_shape(*array._block)
        func.prepared_async_call(array._grid, array.stream,
                array.gpudata, result.gpudata, array.size)
        
        return result
    return f

fabs = _make_unary_array_func("fabs")
ceil = _make_unary_array_func("ceil")
floor = _make_unary_array_func("floor")
exp = _make_unary_array_func("exp")
log = _make_unary_array_func("log")
log10 = _make_unary_array_func("log10")
sqrt = _make_unary_array_func("sqrt")

sin = _make_unary_array_func("sin")
cos = _make_unary_array_func("cos")
tan = _make_unary_array_func("tan")
asin = _make_unary_array_func("asin")
acos = _make_unary_array_func("acos")
atan = _make_unary_array_func("atan")

sinh = _make_unary_array_func("sinh")
cosh = _make_unary_array_func("cosh")
tanh = _make_unary_array_func("tanh")
        
def fmod(arg, mod):
    """Return the floating point remainder of the division `arg/mod`,
    for each element in `arg` and `mod`."""
    result = gpuarray.GPUArray(arg.shape, arg.dtype)
    
    func = _kernel.get_fmod_kernel()
    func.set_block_shape(*arg._block)
    func.prepared_async_call(arg._grid, arg.stream,
            arg.gpudata, mod.gpudata, result.gpudata, arg.size)
    
    return result

def frexp(arg):
    """Return a tuple `(significands, exponents)` such that 
    `arg == significand * 2**exponent`.
    """
    sig = gpuarray.GPUArray(arg.shape, arg.dtype)
    expt = gpuarray.GPUArray(arg.shape, arg.dtype)
    
    func = _kernel.get_frexp_kernel()
    func.set_block_shape(*arg._block)
    func.prepared_async_call(arg._grid, arg.stream,
            arg.gpudata, sig.gpudata, expt.gpudata, arg.size)
    
    return sig, expt
    
def ldexp(significand, exponent):
    """Return a new array of floating point values composed from the
    entries of `significand` and `exponent`, paired together as
    `result = significand * 2**exponent`.
    """
    result = gpuarray.GPUArray(significand.shape, significand.dtype)
    
    func = _kernel.get_ldexp_kernel()
    func.set_block_shape(*significand._block)
    func.prepared_async_call(significand._grid, significand.stream,
            significand.gpudata, exponent.gpudata, result.gpudata, 
            significand.size)
    
    return result
        
def modf(arg):
    """Return a tuple `(fracpart, intpart)` of arrays containing the
    integer and fractional parts of `arg`. 
    """

    intpart = gpuarray.GPUArray(arg.shape, arg.dtype)
    fracpart = gpuarray.GPUArray(arg.shape, arg.dtype)
    
    func = _kernel.get_modf_kernel()
    func.set_block_shape(*arg._block),
    func.prepared_async_call(arg._grid, arg.stream,
            arg.gpudata, intpart.gpudata, fracpart.gpudata,
            arg.size)
    
    return fracpart, intpart
