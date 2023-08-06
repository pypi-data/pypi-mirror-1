/* Copyright 2008 (C)
 * Luís Pedro Coelho <lpc@cmu.edu>
 * License GPL Version 2.
 */

#include <iterator>
extern "C" {
    #include <Python.h>
    #include <numpy/ndarrayobject.h>
}

#include <stdio.h>

namespace numpy_utils {

template <typename BaseType>
struct numpy_iterator_base : std::iterator<std::forward_iterator_tag, BaseType>{
    public:
        BaseType* data;
        int nd;
        // steps is similar to strides, but more useful for iteration, see implementation of operator ++
        // Also, I divide by sizeof(BaseType)
        int steps[NPY_MAXDIMS];
        int dimensions[NPY_MAXDIMS];
        int position[NPY_MAXDIMS];

    public:
        numpy_iterator_base() {
            for (int i = 0; i != NPY_MAXDIMS; ++i) position[i]=0;
        }
        BaseType& operator *() {
            return *data;
        }

        void simplify() {
            int i =1;
            while (i != nd) {
                if (steps[i] == 0) { // remove
                    dimensions[i-1] *= dimensions[i];
                    --nd;
                    for (int j = i; j != nd; ++j) {
                        dimensions[j] = dimensions[j+1];
                        steps[j] = steps[j+1];
                    }
                } else {
                    ++i;
                }
            }
        }

        numpy_iterator_base& operator ++ () {
            for (int i = 0; i != nd; ++i) {
                data += steps[i];
                ++position[i];
                if (position[i] != dimensions[i]) {
                    return *this;
                }
                position[i] = 0;
            }
            return *this;
        }

        //bool operator == (const numpy_iterator_type& other) { return !std::memcmp(this->position,other.position,sizeof(int)*this->nd); }
        //bool operator != (const numpy_iterator_type& other) { return !(*this == other); }
};

template <typename BaseType>
struct numpy_iterator_type : numpy_iterator_base<BaseType> {
    public:
        numpy_iterator_type(PyArrayObject* array) {
            assert(PyArray_ISALIGNED(array));
            this->nd = array->nd;
            this->data=reinterpret_cast<BaseType*>(array->data);
            unsigned cummul = 0;
            for (int i = 0; i != this->nd; ++i) {
                this->dimensions[i] = array->dimensions[this->nd-i-1];
                this->steps[i] = array->strides[this->nd-i-1]/sizeof(BaseType)-cummul;
                cummul *= array->dimensions[this->nd-i-1];
                cummul += this->steps[i]*array->dimensions[this->nd-i-1];
            }
            //for (int i = 0; i != this->nd; ++i) printf("steps[%d] = %d\n",i,this->steps[i]);
            //printf("\n");
        }

        //bool operator == (const numpy_iterator_type& other) { return !std::memcmp(this->position,other.position,sizeof(int)*this->nd); }
        //bool operator != (const numpy_iterator_type& other) { return !(*this == other); }
};

template <typename BaseType>
inline
numpy_iterator_type<BaseType> get_iterator(PyArrayObject* array) {
    numpy_iterator_type<BaseType> iter(array);
    iter.simplify();
    return iter;
}

template <typename BaseType>
struct circle_iterator_type : numpy_iterator_base<BaseType> {
    private:
        unsigned diameter_;
    public:
        unsigned diameter() const {
            return diameter_;
        }

        circle_iterator_type(PyArrayObject* orig, BaseType* data, int axis)
        {
            unsigned N = PyArray_SIZE(orig);
            unsigned axis_size = PyArray_DIM(orig,axis);
            if (axis_size) diameter_ = N/axis_size;
            else diameter_ = N;
            assert(axis < orig->nd);
            this->nd = orig->nd;
            this->data = data;
            unsigned cummul = 1;
            axis = this->nd-axis-1;
            for (int i = 0; i != this->nd; ++i) {
                this->dimensions[i] = orig->dimensions[this->nd-i-1];
                if (i == axis) {
                    //printf("cummul<1>: %d (%d.%d)\n",cummul,i,axis);
                    //printf("\n");
                    this->steps[i] = -cummul;
                } else if (i == (axis+1)) {
                    //printf("cummul<2>: %d (%d.%d)\n",cummul,i,axis);
                    //printf("\n");
                    this->steps[i] = cummul;
                } else {
                    this->steps[i] = 0;
                    cummul *= orig->dimensions[this->nd-i-1];
                    //printf("cummul<3>: %d (%d.%d)\n",cummul,i,axis);
                    //printf("\n");
                }
            }
            ++this->steps[0];
            //for (int i = 0; i != this->nd; ++i) printf("steps[%d] = %d\n",i,this->steps[i]);
            //printf("\n");
        }
};

template <typename BaseType>
circle_iterator_type<BaseType> circle_iterator_like(PyArrayObject* array, PyArrayObject* orig, int axis) {
    circle_iterator_type<BaseType> res(orig,reinterpret_cast<BaseType*>(array->data),axis);
    return res;
}

template <typename BaseType>
circle_iterator_type<BaseType> circle_iterator_like(BaseType* array, PyArrayObject* orig, int axis) {
    circle_iterator_type<BaseType> res(orig,array,axis);
    return res;
}

template <typename BaseType>
inline
BaseType* get_start_pointer(PyArrayObject* array) {
    return reinterpret_cast<BaseType*>(array->data);
}

template <typename T>
struct no_iterator_type {
    public:
        no_iterator_type(T& o):obj(&o) { }
        T& operator * () { return *obj; }
        no_iterator_type& operator ++ () { return *this; }
        no_iterator_type& operator ++ (int) { return *this; }

    private:
        T* obj;
};

template <typename T>
inline
no_iterator_type<T> no_iterator(T& obj) {
    return no_iterator_type<T>(obj);
}

template <typename T>
inline
PyObject* build_pyobject(T val)
{
    return PyBool_FromLong(val);
}

template<>
inline
PyObject* build_pyobject(bool val) {
    return PyBool_FromLong(val);
}

template<>
inline
PyObject* build_pyobject(int val) {
    return PyInt_FromLong(val);
}

template<>
inline
PyObject* build_pyobject(char val) {
    return PyInt_FromLong(val);
}

template<>
inline
PyObject* build_pyobject(unsigned char val) {
    return PyInt_FromLong(val);
}

template<>
inline
PyObject* build_pyobject(unsigned short val) {
    return PyInt_FromLong(val);
}

template<>
inline
PyObject* build_pyobject(short val) {
    return PyInt_FromLong(val);
}

template<>
inline
PyObject* build_pyobject(double val) {
    return PyFloat_FromDouble(val);
}

template<>
inline
PyObject* build_pyobject(float val) {
    return PyFloat_FromDouble(val);
}

} // namespace numpy_utils
