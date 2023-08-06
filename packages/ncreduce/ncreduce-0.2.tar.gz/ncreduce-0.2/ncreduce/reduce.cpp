/* Copyright 2008 (C)
 * Luís Pedro Coelho <lpc@cmu.edu>
 * License GPL Version 2.
 */

#include <iterator>
#include <vector>
#include <cmath>
extern "C" {
    #include <Python.h>
    #include <numpy/ndarrayobject.h>
}

#include "numpy_utils.hpp"
using namespace numpy_utils;

// FIXME
typedef unsigned size_type;

namespace {
struct EmptyType {
};

struct NoExtraParams {
    typedef EmptyType ExtraParamsType;
    static
    EmptyType build_extra() { return EmptyType(); }
};

struct ZeroInit {
    template <typename ResultsType>
    static
    ResultsType initial_value() { return ResultsType(); }
};

struct SumCompute : NoExtraParams, ZeroInit {
    template <typename IteratorType, typename ResultIteratorType>
    static
    void compute(PyArrayObject* array, int axis, IteratorType data, const size_type N, ResultIteratorType result, EmptyType /* ignore */ ) {
        for (size_type i = 0; i != N; ++i) {
            *result += *data;
            ++data;
            ++result;
        }
    }
};


struct ProdCompute : NoExtraParams {
    template <typename ResultsType>
    static
    ResultsType initial_value() { return ResultsType(1); }

    template <typename IteratorType, typename ResultIteratorType>
    static
    void compute(PyArrayObject* array, int axis, IteratorType data, const size_type N, ResultIteratorType result, EmptyType /* ignore */ ) {
        for (size_type i = 0; i != N; ++i) {
            *result *= *data;
            ++data;
            ++result;
        }
    }
};

struct StdVarCompute : ZeroInit {
    struct ExtraParamsType {
        int ddof;
        bool is_std;
    };
    static
    ExtraParamsType build_extra(int ddof, bool std) {
        ExtraParamsType extra;
        extra.ddof = ddof;
        extra.is_std = std;
        return extra;
    }

    template <typename T>
    static
    T conjugate(T val) { return val; }

    template <typename BaseTypeIterator, typename ResultsType>
    static 
    void compute(PyArrayObject* array, int axis, BaseTypeIterator data, const size_type N, no_iterator_type<ResultsType> result, ExtraParamsType extra) {
        typedef typename std::iterator_traits<BaseTypeIterator>::value_type BaseType;
        ResultsType mu = ResultsType();
        const BaseTypeIterator first = data;
        for (size_type i = 0; i != N; ++i) {
            mu += *data;
            ++data;
        }
        mu /= N;
        data = first;
        for (size_type i = 0; i != N; ++i) {
            BaseType delta = (*data-mu);
            *result += delta*conjugate(delta);
            ++data;
        }
        *result /= N;
        if (extra.is_std) {
            *result = std::sqrt(*result);
        }
    }

    template<typename T1, typename T2>
    static
    T1 divide(T1 val, T2 val2) { return val/val2; }

    template<typename T2>
    static
    bool divide(bool val, T2 val2) { return val; }


    template <typename BaseTypeIterator, typename ResultsType>
    static 
    void compute(PyArrayObject* array, int axis, BaseTypeIterator data, const size_type N, circle_iterator_type<ResultsType> result, ExtraParamsType extra) {
        typedef typename std::iterator_traits<BaseTypeIterator>::value_type BaseType;

        ResultsType* first_result = result.data;
        const BaseTypeIterator first = data;
        const size_type ArrSize = PyArray_SIZE(array);
        ResultsType* mu = new ResultsType[result.diameter()]; // I tried using std::vector, but std::vector<bool> bit me in the back
        for (unsigned i = 0; i != result.diameter(); ++i) mu[i] = ResultsType();
        circle_iterator_type<ResultsType> mu_iter = circle_iterator_like(mu,array,axis);
        for (size_type i = 0; i != N; ++i) {
            *mu_iter += *data;
            ++data;
            ++mu_iter;
        }
        for (unsigned i = 0; i != result.diameter(); ++i) {
            mu[i] = divide(mu[i],ArrSize/result.diameter());
        }
        data = first;
        mu_iter = circle_iterator_like(mu,array,axis);
        for (size_type i = 0; i != N; ++i) {
            BaseType delta = (*data-*mu_iter);
            *result += delta*conjugate(delta);
            ++result;
            ++data;
            ++mu_iter;
        }
        for (unsigned i = 0; i != result.diameter(); ++i) {
            first_result[i] = divide(first_result[i],ArrSize/result.diameter());
            if (extra.is_std) {
                first_result[i] = sqrt(first_result[i]);
            }
        }
        
        delete [] mu;
    }

};

struct AnyCompute : NoExtraParams, ZeroInit {
    template <typename IteratorType, typename ResultIteratorType>
    static
    void compute(PyArrayObject* array, int axis, IteratorType data, const size_type N, ResultIteratorType result, EmptyType /* ignore */ ) {
        for (size_type i = 0; i != N; ++i) {
            if (*data) *result = true;
            ++data;
            ++result;
        }
    }
    template <typename IteratorType, typename ResultsType>
    static
    void compute(PyArrayObject* array, int axis, IteratorType data, size_type N, no_iterator_type<ResultsType> result, EmptyType /* ignore */ ) {
        for (size_type i = 0; i != N; ++i) {
            if (*data) {
                *result = true;
                break;
            }
            ++data;
        }
    }
};

struct AllCompute : NoExtraParams {
    template<typename ResultsType>
    static ResultsType initial_value() { return true; } 
    template <typename IteratorType, typename ResultIteratorType>
    static
    void compute(PyArrayObject* array, int axis, IteratorType data, size_type N, ResultIteratorType result, EmptyType /* ignore */ ) {
        for (size_type i = 0; i != N; ++i) {
            if (!*data) *result = false;
            ++data;
            ++result;
        }
    }
    template <typename IteratorType, typename ResultsType>
    static
    void compute(PyArrayObject* array, int axis, IteratorType data, size_type N, no_iterator_type<ResultsType> result, EmptyType /* ignore */ ) {
        for (size_type i = 0; i != N; ++i) {
            if (!*data) {
                *result = false;
                break;
            }
            ++data;
        }
    }
};
struct MinCompute : NoExtraParams {
    template<typename ResultsType>
    static ResultsType initial_value() { return std::numeric_limits<ResultsType>::max(); }
    template <typename IteratorType, typename ResultIteratorType>
    static
    void compute(PyArrayObject* array, int axis, IteratorType data, size_type N, ResultIteratorType result, EmptyType /* ignore */ ) {
        for (size_type i = 0; i != N; ++i) {
            if (*data < *result) *result = *data;
            ++data;
            ++result;
        }
    }
};
struct MaxCompute : NoExtraParams {
    template<typename ResultsType>
    static ResultsType initial_value() { return std::numeric_limits<ResultsType>::min(); }
    template <typename IteratorType, typename ResultIteratorType>
    static
    void compute(PyArrayObject* array, int axis, IteratorType data, size_type N, ResultIteratorType result, EmptyType /* ignore */ ) {
        for (size_type i = 0; i != N; ++i) {
            if (*data > *result) *result = *data;
            ++data;
            ++result;
        }
    }
};
inline
bool is_any_contiguous(PyArrayObject* array) {
    return PyArray_ISCONTIGUOUS(array) || PyArray_ISFORTRAN(array);
}


template <typename TraitsObject, typename BaseType, typename ResultsType>
PyObject* reduce(PyArrayObject* array, PyArrayObject* out, int axis, int rtype, typename TraitsObject::ExtraParamsType extra_params) {
    const ResultsType initial = TraitsObject::template initial_value<ResultsType>();
    //printf("reduce 0\n");
    if (!PyArray_ISBEHAVED(array)) {
        //printf("reduce 1\n");
        // The best way to implement this is to simply write an iterator type that understands misbehaved arrays and then
        // call TraitsObject::compute
        PyErr_SetString(PyExc_NotImplementedError,"No Copy Reduce only works with aligned arrays. You should use traditional reduction for non-aligned arrays.");
        return NULL;
    }
    if (out && !PyArray_ISCARRAY(out)) {
        //printf("reduce 2\n");
        // This can be implemented either by making the output iterators different
        // or by first computing the result into a nice memory array and copying. I (LPC) favour copying.
        PyErr_SetString(PyExc_NotImplementedError,"No Copy Reduce only works with output C-arrays. You should use traditional reduction for non-contiguous output.");
        return NULL;
    }
    if (is_any_contiguous(array) && (axis == NPY_MAXDIMS)) {
        //printf("reduce 3\n");
        BaseType* data = get_start_pointer<BaseType>(array);
        const size_type N  = PyArray_SIZE(array);
        if (out) {
            ResultsType* result = get_start_pointer<ResultsType>(out);
            *result = initial;
            TraitsObject::compute(array,axis,data,N,no_iterator(*result),extra_params);
            return build_pyobject(*result);
        } else {
            ResultsType result = initial;
            TraitsObject::compute(array,axis,data,N,no_iterator(result),extra_params);
            return build_pyobject(result);
        }
    } else if (PyArray_ISCONTIGUOUS(array) && (axis == array->nd-1)) {
        //printf("reduce 4\n");
        // Actually is is-fortran && axis == 0, we can use the same technique
        // Not implemented for now
        PyArrayObject* results_array;
        if (out && PyArray_ISCARRAY(out)) {
            //printf("got out\n");
            results_array = out;
        } else {
            results_array = reinterpret_cast<PyArrayObject*>(PyArray_EMPTY(array->nd-1,array->dimensions,rtype,false));
        }
        // initialize result:
        BaseType* data = get_start_pointer<BaseType>(array);
        ResultsType* results = get_start_pointer<ResultsType>(results_array);
        const int result_size = PyArray_SIZE(array)/(array->dimensions[array->nd-1] ? array->dimensions[array->nd-1] : 1);
        const size_type step = array->dimensions[array->nd-1];
        //printf("STEP: %d\n",(int)step);
        //printf("RESULTS SIZE: %d\n",(int)result_size);
        //printf("STRIDE(n-1): %d\n",array->strides[array->nd-2]);
        //printf("SIZEOF(n-1): %d\n",sizeof(BaseType));
        for (int i = 0; i != int(result_size); ++i) {
            results[i] = initial;
            TraitsObject::compute(array,axis,data,step,no_iterator(results[i]),extra_params);
            data += step;
        }
        return PyArray_Return(results_array);
    } else if (axis == NPY_MAXDIMS) {
        //printf("reduce 5\n");
        numpy_iterator_type<BaseType> data = get_iterator<BaseType>(array);
        ResultsType result = initial;
        no_iterator_type<ResultsType> riter = no_iterator(result);
        if (out) {
            riter = no_iterator(*get_start_pointer<ResultsType>(out));
        }
        TraitsObject::compute(array,axis,data,PyArray_SIZE(array),riter,extra_params);
        return build_pyobject(result);
    } else { // axis != NPY_MAXDIMS and not contiguous
        //printf("reduce 6\n");
        numpy_iterator_type<BaseType> data = get_iterator<BaseType>(array);
        PyArrayObject* results_array;
        if (out) {
            results_array = out;
        } else {
            npy_intp* dims = new npy_intp[array->nd-1];
            int iter=0;
            //printf("reduce 6.001\n");
            for (int i = 0; i != array->nd; ++i) {
                if (i != axis) dims[iter++] = PyArray_DIM(array,i);
            }
            //printf("reduce 6.002\n");
            results_array = reinterpret_cast<PyArrayObject*>(PyArray_EMPTY(array->nd-1,dims,rtype,false));
            //printf("reduce 6.003\n");
            delete [] dims;
        }
        //printf("reduce 6.01\n");
        ResultsType* resultsdata = reinterpret_cast<ResultsType*>(results_array->data);
        //printf("reduce 6.02\n");
        const unsigned N = PyArray_SIZE(results_array);
        //printf("reduce 6.03 (%d)\n",int(N));
        for (unsigned i = 0; i != N; ++i) resultsdata[i]=initial;
        //printf("reduce 6.1\n");
        circle_iterator_type<ResultsType> results = circle_iterator_like<ResultsType>(results_array,array,axis);
        //printf("reduce 6.2\n");
        TraitsObject::compute(array,axis,data,PyArray_SIZE(array),results,extra_params);
        //printf("reduce 6.3\n");
        return PyArray_Return(results_array);
    }
}

#define TYPE_CASE(typecode,type) \
    case typecode: \
    { \
        HANDLE_TYPE(type); \
    } \
    break;

#define SWITCH_ON_TYPE(type) \
    do { \
        int t = (type); \
        switch (t) { \
            TYPE_CASE(NPY_BOOL,bool); \
            TYPE_CASE(NPY_BYTE,char); \
            TYPE_CASE(NPY_UBYTE,unsigned char); \
            TYPE_CASE(NPY_USHORT,unsigned short); \
            TYPE_CASE(NPY_SHORT,short); \
            TYPE_CASE(NPY_UINT,unsigned int); \
            TYPE_CASE(NPY_INT,int); \
            TYPE_CASE(NPY_LONG,npy_long); \
            TYPE_CASE(NPY_ULONG,npy_ulong); \
            TYPE_CASE(NPY_FLOAT,float); \
            TYPE_CASE(NPY_DOUBLE,double); \
            default: \
                fprintf(stderr,"Something weird happened: type = %d.\n",t);\
        } \
    } while(0)


template <typename TraitsObject,typename ResultsType>
PyObject* reduce_dispatch2(PyArrayObject* array, PyArrayObject* out, int axis, int rtype, typename TraitsObject::ExtraParamsType extra) {
#define HANDLE_TYPE(type) \
        return reduce<TraitsObject,type,ResultsType>(array,out,axis,rtype,extra);
    SWITCH_ON_TYPE(PyArray_TYPE(array));
#undef HANDLE_TYPE
    assert(0);
    return 0;
}

template <typename TraitsObject>
PyObject* reduce_dispatch(PyArrayObject* array, PyArrayObject* out, int axis, int rtype, typename TraitsObject::ExtraParamsType extra) {
#define HANDLE_TYPE(type) \
        return reduce_dispatch2<TraitsObject,type>(array,out,axis,rtype,extra);
    SWITCH_ON_TYPE(rtype);
#undef HANDLE_TYPE
    assert(0);
    return 0;
}


/* Return typenumber from dtype2 unless it is NULL, then return
 *    NPY_DOUBLE if dtype1->type_num is integer or bool
 *       and dtype1->type_num otherwise.
 *       */
static int
_get_type_num_double(PyArray_Descr *dtype1, PyArray_Descr *dtype2)
{
    if (dtype2 != NULL) return dtype2->type_num;

    /* For integer or bool data-types */
    if (dtype1->type_num < NPY_FLOAT) {
        return NPY_DOUBLE;
    } else {
        return dtype1->type_num;
    }
}



PyObject* ncr_stddev(PyArrayObject *self, PyObject *args, PyObject *kwds)
{
    int axis=NPY_MAXDIMS;
    PyArray_Descr *dtype=NULL;
    PyArrayObject *out=NULL;
    int ddof = 0;
    static char *kwlist[] = {"array", "axis", "dtype", "out", "ddof", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O&O&O&i", kwlist,
                                     &self,
                                     PyArray_AxisConverter,&axis,
                                     PyArray_DescrConverter2, &dtype,
                                     PyArray_OutputConverter, &out,
                                     &ddof)) {
        Py_XDECREF(dtype);
        return NULL;
    }

    int num = _get_type_num_double(self->descr, dtype);
    Py_XDECREF(dtype);
    return reduce_dispatch<StdVarCompute>(self, out, axis, num, StdVarCompute::build_extra(ddof,true));
}


PyObject* ncr_var(PyArrayObject *self, PyObject *args, PyObject *kwds)
{
    int axis=NPY_MAXDIMS;
    PyArray_Descr *dtype=NULL;
    PyArrayObject *out=NULL;
    int ddof = 0;
    static char *kwlist[] = {"array", "axis", "dtype", "out", "ddof", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O&O&O&i", kwlist,
                                     &self,
                                     PyArray_AxisConverter,&axis,
                                     PyArray_DescrConverter2, &dtype,
                                     PyArray_OutputConverter, &out,
                                     &ddof)) {
        Py_XDECREF(dtype);
        return NULL;
    }

    int num = _get_type_num_double(self->descr, dtype);
    Py_XDECREF(dtype);
    return reduce_dispatch<StdVarCompute>(self, out, axis, num, StdVarCompute::build_extra(ddof,false));
}

PyObject* ncr_mean(PyArrayObject *self, PyObject *args, PyObject *kwds)
{
    int axis=NPY_MAXDIMS;
    PyArray_Descr *dtype=NULL;
    PyArrayObject *out=NULL;
    int num;
    static char *kwlist[] = {"arrat","axis", "dtype", "out", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O&O&O&", kwlist,
                                     &self,
                                     PyArray_AxisConverter, &axis,
                                     PyArray_DescrConverter2, &dtype,
                                     PyArray_OutputConverter, &out)) {
        Py_XDECREF(dtype);
        return NULL;
    }

    num = _get_type_num_double(self->descr, dtype);
    Py_XDECREF(dtype);
    PyObject* output = reduce_dispatch<SumCompute>(self, out, axis, num, EmptyType());
    if (!output) return NULL;
    unsigned N;
    if (axis == NPY_MAXDIMS) { N = PyArray_SIZE(self); }
    else { N = self->dimensions[axis]; }
    PyObject* Nobj = PyInt_FromLong(N);
    if (!Nobj) {
        Py_XDECREF(output);
        return NULL;
    }
    PyObject* output2 = PyNumber_InPlaceDivide(output,Nobj);
    Py_XDECREF(Nobj);
    Py_XDECREF(output);
    return output2;
}

PyObject* ncr_ptp(PyArrayObject *self, PyObject *args, PyObject *kwds)
{
    int axis=NPY_MAXDIMS;
    PyArray_Descr *dtype=NULL;
    PyArrayObject *out=NULL;
    int num;
    static char *kwlist[] = {"arrat","axis", "dtype", "out", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O&O&O&", kwlist,
                                     &self,
                                     PyArray_AxisConverter, &axis,
                                     PyArray_DescrConverter2, &dtype,
                                     PyArray_OutputConverter, &out)) {
        Py_XDECREF(dtype);
        return NULL;
    }

    num = _get_type_num_double(self->descr, dtype);
    Py_XDECREF(dtype);
    PyObject* output = reduce_dispatch<MaxCompute>(self, out, axis, num, EmptyType());
    if (!output) return NULL;
    PyObject* minarray = reduce_dispatch<MinCompute>(self, 0, axis, num, EmptyType());
    PyObject* output2 = PyNumber_InPlaceSubtract(output,minarray);
    Py_XDECREF(minarray);
    Py_XDECREF(output);
    return output2;
}

PyObject* ncr_any(PyArrayObject *self, PyObject *args, PyObject *kwds)
{
    int axis=NPY_MAXDIMS;
    PyArray_Descr *dtype=NULL;
    PyArrayObject *out=NULL;
    static char *kwlist[] = {"array","axis", "out", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O&O&", kwlist,
                                     &self,
                                     PyArray_AxisConverter,&axis,
                                     PyArray_OutputConverter, &out)) {
        return NULL;
    }
   
    //if (out && !type(out) is bool) {
    //    PyErr_SetString("ncreduce.any: out must be a boolean array!");
    //    return NULL;
    //}
    return reduce_dispatch2<AnyCompute,bool>(self, out, axis, NPY_BOOL, EmptyType());
}

PyObject* ncr_all(PyArrayObject *self, PyObject *args, PyObject *kwds)
{
    int axis=NPY_MAXDIMS;
    PyArray_Descr *dtype=NULL;
    PyArrayObject *out=NULL;
    static char *kwlist[] = {"array","axis", "out", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O&O&", kwlist,
                                     &self,
                                     PyArray_AxisConverter,&axis,
                                     PyArray_OutputConverter, &out)) {
        return NULL;
    }
    //if (out && !type(out) is bool) {
    //    PyErr_SetString("ncreduce.all: out must be a boolean array!");
    //    return NULL;
    //}
   
    return reduce_dispatch2<AllCompute,bool>(self, out, axis, NPY_BOOL, EmptyType());
}

#define BASIC_FUNC(fname,computeclass) \
PyObject* fname(PyArrayObject *self, PyObject *args, PyObject *kwds) \
{ \
    int axis=NPY_MAXDIMS; \
    PyArray_Descr *dtype=NULL; \
    PyArrayObject *out=NULL; \
    static char *kwlist[] = {"array","axis", "dtype", "out", NULL}; \
\
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O&O&O&", kwlist, \
                                     &self, \
                                     PyArray_AxisConverter,&axis, \
                                     PyArray_DescrConverter2, &dtype,\
                                     PyArray_OutputConverter, &out)) { \
        Py_XDECREF(dtype); \
        return NULL; \
    } \
    \
    int num = _get_type_num_double(self->descr, dtype); \
    Py_XDECREF(dtype); \
    return reduce_dispatch<computeclass>(self, out, axis, num, EmptyType()); \
}

BASIC_FUNC(ncr_sum,SumCompute)
BASIC_FUNC(ncr_prod,ProdCompute)
BASIC_FUNC(ncr_max,MaxCompute)
BASIC_FUNC(ncr_min,MinCompute)

const char * ncr_sum_doc = 
    "S = ncreduce.sum(array,axis=None,out=None,dtype=None)\n"
    "\n"
    "Computes the sum for the whole array (if axis is None) or across\n"
    "the given axis.\n"
    ;

const char * ncr_prod_doc = 
    "P = ncreduce.prod(array,axis=None,out=None,dtype=None)\n"
    "\n"
    "Computes the product for the whole array (if axis is None) or across\n"
    "the given axis.\n"
    "\n"
    "This function will easily over- or underflow for large arrays. Consider\n"
    "computing the sum of logs instead."
    ;

const char * ncr_std_doc =
    "Sigma = ncreduce.std(array,axis=None,out=None,dtype=None,ddof=0)"
    "\n"
    "Computes the standard deviation according to the formula:\n"
    "       Sigma = sqrt ( sum( (x_i - mu)^2 )/(N - ddof) ) \n"
    "\n"
    "see: ncreduce.var\n"
    ;

const char * ncr_var_doc =
    "Sigma2 = ncreduce.std(array,axis=None,out=None,dtype=None,ddof=0)"
    "\n"
    "Computes the samplevariance according to the formula:\n"
    "       Sigma = sum( (x_i - mu)^2 )/(N - ddof)\n"
    "\n"
    "see: ncreduce.std\n"
    "\n"
    ;

const char * ncr_mean_doc =
    "Mu = ncreduce.mean(array,axis=None,out=None,dtype=None)\n"
    "\n"
    "Compute the sample mean along the given axis or for the whole array.\n"
    ;


const char * ncr_any_doc =
    "Any = ncreduce.any(array,axis=None,out=None)\n"
    "\n"
    "Returns true if any element of array is true.\n"
    "Return value is Boolean. out (if given) must be a Boolean array."
    ;

const char * ncr_all_doc =
    "All = ncreduce.all(array,axis=None,out=None)\n"
    "\n"
    "Returns true if all elements are true.\n"
    "Return value is Boolean. out (if given) must be a Boolean array"
    ;

const char * ncr_max_doc =
    "Max = ncreduce.max(array,axis=None,out=None)\n"
    "\n"
    "Max function.\n"
    ;

const char * ncr_min_doc =
    "Min = ncreduce.min(array,axis=None,out=None)\n"
    "\n"
    "Min function.\n"
    ;

const char * ncr_ptp_doc =
    "Ptp= ncreduce.ptp(array,axis=None,dtype=None,out=None)\n"
    "\n"
    "Ptp function. Ptp = max(array,axis,dtype,out)-min(array,axis,dtype,out).\n"
    ;

PyMethodDef methods[] = {
  {"std",(PyCFunction)ncr_stddev, (METH_VARARGS|METH_KEYWORDS) , ncr_std_doc},
  {"var",(PyCFunction)ncr_var, (METH_VARARGS|METH_KEYWORDS) , ncr_var_doc},
  {"sum",(PyCFunction)ncr_sum, (METH_VARARGS|METH_KEYWORDS), ncr_sum_doc},
  {"prod",(PyCFunction)ncr_prod, (METH_VARARGS|METH_KEYWORDS), ncr_prod_doc},
  {"mean",(PyCFunction)ncr_mean, (METH_VARARGS|METH_KEYWORDS), ncr_mean_doc},
  {"any",(PyCFunction)ncr_any, (METH_VARARGS|METH_KEYWORDS), ncr_any_doc},
  {"all",(PyCFunction)ncr_all, (METH_VARARGS|METH_KEYWORDS), ncr_all_doc},
  {"max",(PyCFunction)ncr_max, (METH_VARARGS|METH_KEYWORDS), ncr_max_doc},
  {"min",(PyCFunction)ncr_min, (METH_VARARGS|METH_KEYWORDS), ncr_min_doc},
  {"ptp",(PyCFunction)ncr_ptp, (METH_VARARGS|METH_KEYWORDS), ncr_ptp_doc},
  {NULL, NULL,0,NULL},
};

const char * module_doc = 
    "Fast numpy reduce operations.\n"
    "\n"
    "This module contains several reduce operations implemented in a way that is fast and\n"
    "unlike the traditional numpy operations, does not allocate additional memory.\n"
    ;
} // namespace
extern "C"
void initncreduce()
  {
    import_array();
    (void)Py_InitModule3("ncreduce", methods, module_doc);
  }


