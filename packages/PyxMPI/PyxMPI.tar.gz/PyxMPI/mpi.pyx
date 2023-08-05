"""PyxMPI: Incomplete Object Oriented Pyrex wrapper of MPI 1.1

Copyright: 2004-2007, Peter Maxwell, pm67nz@gmail.com
License: GPL

Most functionality is provided via communicator methods,
so start with the initial MPI communicator, 'world'.

There are a few other possibly useful objects in here:
The send modes: SYNC, STANDARD, READY and BUFFERED
get_processor_name()
set_buffer_size(size)
waitany(requests)
waitall(requests)
"""

__author__ = "Peter Maxwell"
__copyright__ = "Copyright 2004-2007, Peter Maxwell"
__contributors__ = ["Peter Maxwell", "Gavin Huttley"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Peter Maxwell"
__email__ = "pm67nz@gmail.com"
__status__ = "Development"

cdef extern from "Python.h":
    char *PyString_AsString(object)
    object PyString_FromStringAndSize(char *, int)
    object PyString_FromString(char *)
    void *PyMem_Malloc(int)
    void PyMem_Free(void *)
    void *PyCObject_AsVoidPtr(object)
    char *PyString_AS_STRING(object)
    #struct Py_complex:
    #    double real
    #    double imag
    int PyInt_Check(object)
    long PyInt_AsLong(object)
    int PyFloat_Check(object)
    double PyFloat_AsDouble(object)
    int PyComplex_Check(object)
    #Py_complex PyComplex_AsCComplex(object)

cdef extern from "array_interface.h":
    struct PyArrayInterface:
        int version
        int nd
        char typekind
        int itemsize
        int flags
        int *shape, *strides
        void *data

ctypedef object ArrayType


cdef extern from "mpi.h":
    ctypedef int *MPI_Comm
    MPI_Comm MPI_COMM_WORLD
    int MPI_MAX_PROCESSOR_NAME
    int MPI_ANY_SOURCE
    int MPI_ANY_TAG
    
    ctypedef int MPI_Errhandler
    MPI_Errhandler MPI_ERRORS_RETURN
    MPI_Errhandler MPI_ERRORS_ARE_FATAL
    
    ctypedef int *MPI_Datatype
    MPI_Datatype MPI_BYTE
    MPI_Datatype MPI_CHAR
    MPI_Datatype MPI_DOUBLE
    MPI_Datatype MPI_INT
    MPI_Datatype MPI_FLOAT
    MPI_Datatype MPI_LONG
    MPI_Datatype MPI_DATATYPE_NULL
    
    ctypedef int *MPI_Op
    MPI_Op MPI_MAX
    MPI_Op MPI_MIN
    MPI_Op MPI_SUM
    MPI_Op MPI_PROD
    MPI_Op MPI_LAND
    MPI_Op MPI_BAND
    MPI_Op MPI_LOR
    MPI_Op MPI_BOR
    MPI_Op MPI_LXOR
    MPI_Op MPI_BXOR
#    MPI_Op MPI_MAXLOC    # take care with result types
#    MPI_Op MPI_MINLOC    # these would require temporary arrays, or maybe Numarray.
#    MPI_Op MPI_REPLACE
    
    cdef struct _status:
        int MPI_SOURCE
        int    MPI_TAG
        int    MPI_ERROR
    ctypedef _status MPI_Status
    
    ctypedef int *MPI_Request
    
    int MPI_Init(int *, char ***)
    int MPI_Initialized(int[])
    int MPI_Comm_size(MPI_Comm, int[])
    int MPI_Comm_rank(MPI_Comm, int[])
    int MPI_Barrier(MPI_Comm)
    int MPI_Abort(MPI_Comm, int)
    int MPI_Finalize()
    int MPI_Finalized(int [])
    float MPI_Wtime()
    int MPI_Get_processor_name(char *, int[])
    
    int MPI_Errhandler_set(MPI_Comm, MPI_Errhandler)
    int MPI_Error_string(int, char *, int *)
    #int MPI_Error_class(int, int *)
    
    int MPI_Type_contiguous(int count, MPI_Datatype oldtype, MPI_Datatype *newtype)
    int MPI_Type_commit(MPI_Datatype *)
    int MPI_Type_free(MPI_Datatype *)
    
    int MPI_Buffer_attach(void *, int)
    int MPI_Buffer_detach(void *, int *)
    
    int MPI_Bcast (void *, int, MPI_Datatype, int, MPI_Comm)
    int MPI_Send (void *, int, MPI_Datatype, int, int, MPI_Comm)
    int MPI_Ssend (void *, int, MPI_Datatype, int, int, MPI_Comm)
    int MPI_Bsend (void *, int, MPI_Datatype, int, int, MPI_Comm)
    int MPI_Rsend (void *, int, MPI_Datatype, int, int, MPI_Comm)
    int MPI_Recv (void *, int, MPI_Datatype, int, int, MPI_Comm, MPI_Status *)
    
    int MPI_Sendrecv(void *, int, MPI_Datatype, int, int, void *,
            int, MPI_Datatype, int, int, MPI_Comm, MPI_Status *)
    int MPI_Probe(int, int, MPI_Comm, MPI_Status *)
    #int MPI_Sendrecv_replace (void *, int, MPI_Datatype, int, int,
    #        int, int, MPI_Comm, MPI_Status *)
    
    int MPI_Isend (void *, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request *)
    int MPI_Issend (void *, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request *)
    int MPI_Ibsend (void *, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request *)
    int MPI_Irsend (void *, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request *)
    int MPI_Irecv (void *, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request *)
    int MPI_Wait (MPI_Request *, MPI_Status *)
    int MPI_Test (MPI_Request *, int flag[], MPI_Status *)
    int MPI_Cancel (MPI_Request *)
    int MPI_Request_free (MPI_Request *)
    int MPI_Get_elements (MPI_Status *, MPI_Datatype, int[])
    
    int MPI_Waitall(int, MPI_Request[], MPI_Status[])
    int MPI_Waitany(int, MPI_Request[], int *, MPI_Status *)
    #int MPI_Waitsome(int incount, MPI_Request[], int outcount, int indices[], MPI_Status[])
    
    int MPI_Scatter (void *, int, MPI_Datatype, void *, int, MPI_Datatype, int, MPI_Comm)
    #int MPI_Scatterv (void *, int *, int *, MPI_Datatype, void *, int, MPI_Datatype, int, MPI_Comm)
    int MPI_Gather (void *, int, MPI_Datatype, void *, int, MPI_Datatype, int, MPI_Comm)
    #int MPI_Gatherv (void *, int, MPI_Datatype, void *, int *, int *, MPI_Datatype, int, MPI_Comm)
    int MPI_Allgather (void *, int, MPI_Datatype, void *, int, MPI_Datatype, MPI_Comm)
    # int MPI_Allgatherv
    int MPI_Alltoall (void *, int, MPI_Datatype, void *, int, MPI_Datatype, MPI_Comm)
    # int MPI_Alltoallv
    
    int MPI_Comm_split (MPI_Comm, int, int, MPI_Comm *)
    int MPI_Comm_dup (MPI_Comm, MPI_Comm *)
    int MPI_Comm_free (MPI_Comm *)
    
    int MPI_Allreduce (void *, void *, int, MPI_Datatype, MPI_Op, MPI_Comm)
    int MPI_Reduce (void *, void *, int, MPI_Datatype, MPI_Op, int, MPI_Comm)
    
    int MPI_MAX_ERROR_STRING

class MPIError(RuntimeError):
    pass

def _mpiErr(int err):
    cdef int resultlen, error_class
    cdef char* error_message
    error_message = <char *> PyMem_Malloc(MPI_MAX_ERROR_STRING * sizeof(char))
    MPI_Error_string(err, error_message, &resultlen)
    msg = PyString_FromStringAndSize(error_message, resultlen)
    return MPIError(msg)

import sys, atexit, warnings, cPickle, gc

# Cache empty to save name lookup
cdef object empty
import numpy
empty = numpy.empty

cdef object _finalised
_finalised = False
ctypedef int (*sender)(void *, int, MPI_Datatype, int, int, MPI_Comm)
ctypedef int (*isender)(void *, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request *)

cdef class _SendMode:
    cdef sender blocking_send
    cdef isender immediate_send
    cdef object name
    
    def __repr__(self):
        return self.name

cdef SendMode(object name, sender send, isender isend):
    cdef _SendMode m
    m = _SendMode()
    m.name = name
    m.blocking_send = send
    m.immediate_send = isend
    return m

STANDARD = SendMode('STANDARD', MPI_Send, MPI_Isend)
BUFFERED = SendMode('BUFFERED', MPI_Bsend, MPI_Ibsend)
READY = SendMode('READY', MPI_Rsend, MPI_Irsend)
SYNC = SendMode('SYNC', MPI_Ssend, MPI_Issend)


cdef int _err_check(int err) except 1:
    if err:
        raise _mpiErr(err)


cdef MPI_Datatype MY_MPI_CDOUBLE, MY_MPI_CFLOAT


cdef object measureInputArray(ArrayType array, int count[], MPI_Datatype mpi_type[],
        void *buffer[]):
    cdef int size
    cdef long long_tmp
    cdef double double_tmp
    #cdef Py_complex complex_tmp
    cdef object typecode
    
    if PyInt_Check(array):
        mpi_type[0] = MPI_LONG
        long_tmp = array
        temp_string = PyString_FromStringAndSize(<char *> (&long_tmp), sizeof(long))
        count[0] = 1
        buffer[0] = PyString_AS_STRING(temp_string)
        return (temp_string, (), int)
    elif PyFloat_Check(array):
        mpi_type[0] = MPI_DOUBLE
        double_tmp = array
        temp_string = PyString_FromStringAndSize(<char *> (&double_tmp), sizeof(double))
        count[0] = 1
        buffer[0] = PyString_AS_STRING(temp_string)
        return (temp_string, (), float)
    elif PyComplex_Check(array):
        mpi_type[0] = MY_MPI_CDOUBLE
        # This could be MUCH more efficient
        double_tmp = array.real
        temp_string1 = PyString_FromStringAndSize(<char *> (&double_tmp), sizeof(double))
        double_tmp = array.imag
        temp_string2 = PyString_FromStringAndSize(<char *> (&double_tmp), sizeof(double))
        count[0] = 1
        temp_string = temp_string1 + temp_string2
        buffer[0] = PyString_AS_STRING(temp_string)
        return (temp_string, (), complex)
    elif array is None:
        raise ValueError('Require int, float or array, not None')
    else:
        cobj = array.__array_struct__
        measureArrayCobj(cobj, count, mpi_type, buffer)
        return (array, array.shape, array.dtype)


cdef void *measureOutputArray(ArrayType array, int count[], MPI_Datatype mpi_type[]) except NULL:
    cdef object typecode
    cdef void *buffer
    if array is None:
        raise TypeError("Array required, got None")
    cobj = array.__array_struct__
    measureArrayCobj(cobj, count, mpi_type, &buffer)
    return buffer


cdef int measureArrayCobj(cobj, int count[], MPI_Datatype mpi_type[], void *data[]) except 1:
    cdef PyArrayInterface *a
    cdef int length, size
    cdef char kind
    a = <PyArrayInterface *> PyCObject_AsVoidPtr(cobj)
    if a.version != 2:
        raise ValueError("Unexpected array interface version %s" % str(a.version))
    if not a.flags & 1:
        raise ValueError ('Noncontiguous array')
    length = 1
    for i from 0 <= i < a.nd:
        length = length * a.shape[i]
    count[0] = length
    kind = a.typekind
    size = a.itemsize
    if kind == c'i' and size == sizeof(int):
        mpi_type[0] = MPI_INT
    elif kind == c'i' and size == sizeof(long):
        mpi_type[0] = MPI_LONG
    elif kind == c'f' and size == sizeof(float):
        mpi_type[0] = MPI_FLOAT
    elif kind == c'f' and size == sizeof(double):
        mpi_type[0] = MPI_DOUBLE
    elif kind == c'c' and size == 2 * sizeof(float):
        mpi_type[0] = MY_MPI_CFLOAT
    elif kind == c'c' and size == 2 * sizeof(double):
        mpi_type[0] = MY_MPI_CDOUBLE
    elif kind == c'S' and size == sizeof(char):
        mpi_type[0] = MPI_CHAR
    else:
        raise ValueError("MPI can't handle array of type %s%s" % (chr(kind), str(size)))
    
    data[0] = a.data
    return 0


cdef class _Request:
    """An outstanding request from immediate_send or immediate_receive"""
    
    cdef MPI_Request request
    cdef readonly object value
    
    def __dealloc__(self):
        global _finalised
        if not _finalised:
            MPI_Request_free(&(self.request))
    
    cdef int _err_check(self, int err) except 1:
        if err:
            raise _mpiErr(err)
    
    def wait(self):
        """Returns (source, tag) once request is done"""
        cdef int err
        cdef MPI_Status status
        err = MPI_Wait(&(self.request), &status)
        self._err_check(err)
        return (status.MPI_SOURCE, status.MPI_TAG)
    
    def test(self):
        """Returns (source, tag) if request is done, None otherwise"""
        cdef int err, flag
        cdef MPI_Status status
        err = MPI_Test(&(self.request), &flag, &status)
        self._err_check(err)
        if flag:
            return (status.MPI_SOURCE, status.MPI_TAG)
        else:
            return None
    
    def cancel(self):
        cdef int err
        err = MPI_Cancel(&(self.request))
        self._err_check(err)
    

cdef object Request(MPI_Request request, object value):
    cdef _Request result
    result = _Request()
    result.request = request
    result.value = value
    return result


cdef class _Communicator

cdef Communicator(MPI_Comm comm):
    # This should be __init__ but I can't pass non-python things to that?
    cdef _Communicator self
    cdef int err, size, rank
    self = _Communicator()
    self._collectable = 0
    self.communicator = comm
    err = MPI_Comm_rank(self.communicator, &rank)
    self._err_check(err)
    err = MPI_Comm_size(self.communicator, &size)
    self._err_check(err)
    self.rank = rank
    self.size = size
    err = MPI_Comm_dup(self.communicator, &(self.obj_communicator))
    self._err_check(err)
    self.send_mode = STANDARD
    self.parent = None
    return self


cdef class _Communicator:
    """A group of CPUs in a context"""
    # 2 MPI communicators, one for arrays and one for pickles
    cdef MPI_Comm communicator, obj_communicator
    cdef readonly int size, rank, _collectable
    cdef readonly object parent
    cdef readonly _SendMode send_mode
    
    def __dealloc__(self):
        global _finalised
        if self._collectable and not _finalised:
            MPI_Comm_free(&(self.obj_communicator))
            MPI_Comm_free(&(self.communicator))
    
    cdef int _err_check(self, int err) except 1:
        if err:
            raise _mpiErr(err)
    
    def __str__(self):
        return 'MPI(%s/%s)' % (self.rank, self.size)
    
    def setAbortOnError(self, flag):
        """Set the response to an MPI error.  If true the process exits
        immediately with whatever error output MPI produces.  If false, a
        Python MPIError exception is raised."""
        if flag:
            MPI_Errhandler_set(self.communicator, MPI_ERRORS_ARE_FATAL)
        else:
            MPI_Errhandler_set(self.communicator, MPI_ERRORS_RETURN)
    
    def setSendMode(self, _SendMode mode not None):
        """Change the default send mode for this communicator and any
        others made from it later.  'mode' must be one of the send mode
        constants defined in this module: SYNC, STANDARD, BUFFERED, READY.
        If BUFFERED is used then a global MPI buffer must also be set up
        via the function 'set_buffer_size'"""
        self.send_mode = mode
    
    def dup(self):
        """Make a clone of this communicator"""
        cdef int err
        cdef MPI_Comm comm
        cdef _Communicator result
        err = MPI_Comm_dup(self.communicator, &comm)
        self._err_check(err)
        result = Communicator(comm)
        result._collectable = 1
        result.parent = self.parent
        result.send_mode = self.send_mode
        return result
    
    def split(self, int colour, key=None):
        """Partition the processes across a family of communicators.
        Processes which pass in the same 'colour' will get back the
        same communicator"""
        cdef int err
        cdef MPI_Comm comm
        cdef _Communicator result
        if key is None:
            key = self.rank
        err = MPI_Comm_split(self.communicator, colour, key, &comm)
        self._err_check(err)
        result = Communicator(comm)
        result._collectable = 1
        result.parent = self
        result.send_mode = self.send_mode
        return result
    
    def barrier(self):
        """Pause all processes until all call 'barrier'"""
        cdef int err
        err = MPI_Barrier(self.communicator)
        self._err_check(err)
    
    def abort(self):
        """Make this communicator invalid"""
        cdef int err
        err = MPI_Abort(self.communicator, 0)
        self._err_check(err)
    
    def send(self, thing, int destination, int tag=0, _SendMode mode=None):
        """Send 'thing' to process 'destination' tagged with 'tag'.  Only
        arrays (or things that can be turned into arrays) can be sent this
        way.  'mode' overrides the default set by .setSendMode()"""
        cdef int count, err
        cdef MPI_Datatype mpi_type
        cdef void *data
        cdef ArrayType array
        (array, shape, typecode) = measureInputArray(thing, &count, &mpi_type, &data)
        if mode is None:
            mode = self.send_mode
        err = mode.blocking_send(data, count, mpi_type, destination, tag, self.communicator)
        self._err_check(err)
    
    def immediate_send(self, thing, int destination, int tag=0, _SendMode mode=None):
        """Immediately send 'thing' to process 'destination' tagged with 'tag'.
        Only arrays (or things that can be turned into arrays) can be sent this
        way.
        'mode' overrides the default set by .setSendMode().
        Returns a request object.  'thing' should not be altered until the send
        is complete, as reported by this request object."""
        cdef int count, err
        cdef MPI_Datatype mpi_type
        cdef void *data
        cdef MPI_Request request
        cdef _Request req
        cdef ArrayType array
        (array, shape, typecode) = measureInputArray(thing, &count, &mpi_type, &data)
        if mode is None:
            mode = self.send_mode
        err = mode.immediate_send(data, count, mpi_type, destination, tag, self.communicator, &request)
        self._err_check(err)
        req = Request(request, array)
        return req
    
    def receive(self, ArrayType array, source=None, tag=None):
        """Fill 'array' with a message from 'source' (default any) with tag
        'tag' (default any).  The array type and shape must match, and is
        not checked at runtime.  (source, tag) of the received message is
        returned"""
        cdef int count, err
        cdef MPI_Datatype mpi_type
        cdef void *data
        cdef MPI_Status status
        if source is None:
            source = MPI_ANY_SOURCE
        if tag is None:
            tag = MPI_ANY_TAG
        data = measureOutputArray(array, &count, &mpi_type)
        err = MPI_Recv(data, count, mpi_type, source, tag, self.communicator, &status)
        self._err_check(err)
        return (status.MPI_SOURCE, status.MPI_TAG)
    
    def immediate_receive(self, ArrayType array, source=None, tag=None):
        """Start filling 'array' with a message from 'source' (default any) with
        tag 'tag' (default any).  The array type and shape must match, and is
        not checked at runtime.
        Returns a request object.  'array' should not be trusted until the message
        is complete, as reported by this request object."""
        cdef int count, err
        cdef MPI_Datatype mpi_type
        cdef void *data
        cdef MPI_Request request
        cdef _Request req
        if source is None:
            source = MPI_ANY_SOURCE
        if tag is None:
            tag = MPI_ANY_TAG
        data = measureOutputArray(array, &count, &mpi_type)
        err = MPI_Irecv(data, count, mpi_type, source, tag, self.communicator, &request)
        self._err_check(err)
        req = Request(request, array)
        return req
    
    def send_receive(self, send_thing, int dest, int send_tag, ArrayType recv_array, source=None, recv_tag=None):
        """Does a send and a (possibly completely unrelated) receive at the same time.
        Can help avoid some deadlock problems"""
        cdef int err, send_count, recv_count
        cdef MPI_Datatype send_mpi_type, recv_mpi_type
        cdef void *send_data, *recv_data
        cdef MPI_Status status
        cdef ArrayType send_array
        (send_array, shape, typecode) = measureInputArray(
                send_thing, &send_count, &send_mpi_type, &send_data)
        recv_data = measureOutputArray(recv_array, &recv_count, &recv_mpi_type)
        if source is None:
            source = MPI_ANY_SOURCE
        if recv_tag is None:
            recv_tag = MPI_ANY_TAG
        err = MPI_Sendrecv(send_data, send_count, send_mpi_type, dest, send_tag,
                recv_data, recv_count, recv_mpi_type, source, recv_tag, self.communicator, &status)
        self._err_check(err)
        return (status.MPI_SOURCE, status.MPI_TAG)
    
    def broadcast(self, ArrayType array, int source):
        """Send/receive 'array' from/to process 'source'"""
        cdef int count, err
        cdef MPI_Datatype mpi_type
        cdef void *data
        data = measureOutputArray(array, &count, &mpi_type)
        err = MPI_Bcast(data, count, mpi_type, source, self.communicator)
        self._err_check(err)
    
    def scatter(self, thing, int source):
        """Returns the self.rank'th part of 'thing' from process 'source'.
        'thing' must be convertable to an array with an outermost
        dimension of self.size"""
        cdef int total_count, err, count
        cdef MPI_Datatype mpi_type
        cdef void *data, *recv_buffer
        cdef ArrayType array
        (array, shape, typecode) = measureInputArray(thing, &total_count, &mpi_type, &data)
        assert shape[0] == self.size, (shape, self.size)
        result = empty(shape[1:], typecode)  # xxx too slow?
        recv_buffer = measureOutputArray(result, &count, &mpi_type)
        err = MPI_Scatter(data, count, mpi_type, recv_buffer, count,
            mpi_type, source, self.communicator)
        self._err_check(err)
        return result
    
    def gather(self, thing, int source=-1, concat=0):
        """Returns an array of the 'thing's from all processes.  Each
        'thing' must be of the same type and shape.
        If 'source' is given then only that process will get a valid
        result, others will get None.  By default all processes get the result.
        If 'concat' is true then the result will have the
        same number of dimensions as the 'thing's, but the outermost
        dimension will be self.size times larger."""
        cdef int recv_count, send_count, err
        cdef MPI_Datatype mpi_type
        cdef void *send_buffer, *recv_buffer
        cdef ArrayType send_array
        (send_array, send_shape, typecode) = measureInputArray(thing, &send_count, &mpi_type, &send_buffer)
        if source == -1 or self.rank == source:
            if concat:
                result_shape = (self.size * send_shape[0],) + send_shape[1:]
            else:
                result_shape = (self.size,)+send_shape
            result = empty(result_shape, typecode)  # xxx too slow?
            recv_buffer = measureOutputArray(result, &recv_count, &mpi_type)
        else:
            result = None
            recv_buffer = NULL
        if source == -1:
            err = MPI_Allgather(send_buffer, send_count, mpi_type, recv_buffer,
                    send_count, mpi_type, self.communicator)
        else:
            err = MPI_Gather(send_buffer, send_count, mpi_type, recv_buffer,
                    send_count, mpi_type, source, self.communicator)
        self._err_check(err)
        return result
    
    def transpose(self, thing):
        """MPI_Alltoall: Transpose rank with outermost dimension.  The outermost
        dimension must be equal to self.size"""
        cdef int recv_count, send_count, err
        cdef MPI_Datatype mpi_type
        cdef void *send_buffer, *recv_buffer
        cdef ArrayType send_array
        (send_array, send_shape, typecode) = measureInputArray(
                thing, &send_count, &mpi_type, &send_buffer)
        assert send_shape[0] == self.size
        send_count = send_count / self.size
        result = empty(send_shape, typecode)  # xxx too slow?
        recv_buffer = measureOutputArray(result, &recv_count, &mpi_type)
        err = MPI_Alltoall(send_buffer, send_count, mpi_type, recv_buffer,
                send_count, mpi_type, self.communicator)
        self._err_check(err)
        return result
    
    cdef reduce(self, thing, MPI_Op mpi_op, int dest):
        cdef MPI_Datatype mpi_type
        cdef void *data, *recv_buffer
        cdef int err, count, recv_count
        cdef ArrayType array
        (array, send_shape, typecode) = measureInputArray(thing, &count, &mpi_type, &data)
        if dest == -1 or self.rank == dest:
            result = empty(send_shape, typecode)  # xxx too slow?
            recv_buffer = measureOutputArray(result, &recv_count, &mpi_type)
        else:
            result = None
            recv_buffer = NULL
        if dest == -1:
            err = MPI_Allreduce(data, recv_buffer, count, mpi_type, mpi_op, self.communicator)
        else:
            err = MPI_Reduce(data, recv_buffer, count, mpi_type, mpi_op, dest, self.communicator)
        self._err_check(err)
         
         # If input was a scalar return a scalar
        if result is not None and result.shape == ():
            result = result.reshape([1])[0]
        
        return result
    
    def sum(self, array, int dest=-1):
        """Sum 'array' across the processes.  If 'dest' is given only that
        process will get the result.  'array' can be a scalar."""
        return self.reduce(array, MPI_SUM, dest)
    
    def prod(self, array, int dest=-1):
        """Multiply 'array' across the processes.  If 'dest' is given only that
        process will get the result.  'array' can be a scalar."""
        return self.reduce(array, MPI_PROD, dest)
    
    def min(self, array, int dest=-1):
        """The minimum value of each 'array' element across the processes.
        If 'dest' is given only that process will get the result.
        'array' can be a scalar."""
        return self.reduce(array, MPI_MIN, dest)
    
    def max(self, array, int dest=-1):
        """The maximum value of each 'array' element across the processes.
        If 'dest' is given only that process will get the result.
        'array' can be a scalar."""
        return self.reduce(array, MPI_MAX, dest)
    
    def logical_and(self, array, int dest=-1):
        """'array' true on every processes.  If 'dest' is given only that
        process will get the result.  'array' can be a scalar."""
        return self.reduce(array, MPI_LAND, dest)
    
    def logical_or(self, array, int dest=-1):
        """'array' true on any processes.  If 'dest' is given only that
        process will get the result.  'array' can be a scalar."""
        return self.reduce(array, MPI_LOR, dest)
    
    def send_obj(self, obj, int destination, int tag=0, _SendMode mode=None):
        """Like 'send', only for generic Python objects.  Must be matched with a
        receive_obj() call."""
        cdef int err, count
        cdef void *data
        pickle = cPickle.dumps(obj, 2)
        count = len(pickle)
        data = PyString_AsString(pickle)
        if mode is None:
            mode = self.send_mode
        err = mode.blocking_send(data, count, MPI_BYTE, destination, tag, self.obj_communicator)
        self._err_check(err)
    
    def receive_obj(self, source=None, tag=None, return_status=False):
        """Must be matched with a send_obj() call.  Unlike 'receive' the result
        is the sent object, not a (source, tag) tuple.  If 'return_status' is
        true the result is a tuple of (sent_object, (source, tag))"""
        cdef int err, count
        cdef MPI_Status status
        cdef char *data
        if source is None:
            source = MPI_ANY_SOURCE
        if tag is None:
            tag = MPI_ANY_TAG
        err = MPI_Probe(source, tag, self.obj_communicator, &status)
        self._err_check(err)
        err = MPI_Get_elements(&status, MPI_BYTE, &count)
        self._err_check(err)
        data = <char *> PyMem_Malloc(count)
        try:
            err = MPI_Recv(data, count, MPI_BYTE, source, tag, self.obj_communicator, &status)
            self._err_check(err)
            buf = PyString_FromStringAndSize(data, count)
            result = cPickle.loads(buf)
        finally:
            PyMem_Free(data)
        if return_status:
            result = (result, (status.MPI_SOURCE, status.MPI_TAG))
        return result
    
    def broadcast_obj(self, obj, int source):
        """Like 'broadcast' only for generic Python objects"""
        # Only source knows the size, and can't use MPI_Probe, so have to send 2 messages
        cdef int err, count
        cdef char *data
        if self.rank == source:
            pickle = cPickle.dumps(obj, 2)
            count = len(pickle) + 1
            err = MPI_Bcast(&count, 1, MPI_INT, source, self.obj_communicator)
            self._err_check(err)
            data = PyString_AsString(pickle)
            err = MPI_Bcast(data, count, MPI_BYTE, source, self.obj_communicator)
            self._err_check(err)
            result = obj
        else:
            err = MPI_Bcast(&count, 1, MPI_INT, source, self.obj_communicator)
            self._err_check(err)
            data = <char *> PyMem_Malloc(count)
            try:
                err = MPI_Bcast(data, count, MPI_BYTE, source, self.obj_communicator)
                self._err_check(err)
                pickle = PyString_FromStringAndSize(data, count)
                result = cPickle.loads(pickle)
            finally:
                PyMem_Free(data)
        return result
        
    

def get_processor_name():
    cdef int err, namelen
    cdef char *processor_name
    processor_name = <char *> PyMem_Malloc(MPI_MAX_PROCESSOR_NAME)
    try:
        err = MPI_Get_processor_name(processor_name, &namelen)
        if err:
            raise _mpiErr(err)
        result = PyString_FromString(processor_name)
    finally:
        PyMem_Free(processor_name)
    return result


def set_buffer_size(int size):
    """Allocate a buffer of 'size' bytes for use by the BUFFERED send mode,
    safely deallocating any pre-existing buffer.  If 'size' is 0 then
    BUFFERED mode can not be used."""
    cdef void *buffer
    cdef int err, old_size
    err = MPI_Buffer_detach(&buffer, &old_size)
    if err:
        raise _mpiErr(err)
    if old_size:
        PyMem_Free(buffer)
    if size > 0:
        buffer = PyMem_Malloc(size)
        err = MPI_Buffer_attach(buffer, size)
        if err:
            raise _mpiErr(err)

def waitany(requests):
    """Return (index, source, tag) from the first of the 'requests' to
    complete.  Request objects are made by the non-blocking communicator
    methods 'immediate_send' and 'immediate_receive'"""
    cdef MPI_Request *mpi_requests
    cdef MPI_Status status
    cdef _Request req
    cdef int i, index, err
    mpi_requests = <MPI_Request *> PyMem_Malloc(sizeof(MPI_Request) * len(requests))
    try:
        i = 0
        for req in requests:
            mpi_requests[i] = req.request
            i = i + 1
        err = MPI_Waitany(i, mpi_requests, &index, &status)
        if err:
            raise _mpiErr(err)
    finally:
        PyMem_Free(mpi_requests)
    return (index, status.MPI_SOURCE, status.MPI_TAG)


def waitall(requests):
    cdef MPI_Request *mpi_requests
    cdef MPI_Status *mpi_statuses
    cdef _Request req
    cdef int N, i, err
    N = len(requests)
    mpi_requests = <MPI_Request *> PyMem_Malloc(sizeof(MPI_Request) * N)
    mpi_statuses = <MPI_Status *> PyMem_Malloc(sizeof(MPI_Status) * N)
    result = []
    try:
        i = 0
        for req in requests:
            mpi_requests[i] = req.request
            i = i + 1
        err = MPI_Waitall(i, mpi_requests, mpi_statuses)
        if err:
            raise _mpiErr(err)
        for i from 0 <= i < N:
            result.append((mpi_statuses[i].MPI_SOURCE, mpi_statuses[i].MPI_TAG))
    finally:
        PyMem_Free(mpi_requests)
        PyMem_Free(mpi_statuses)
    return result


def time():
    return MPI_Wtime()

def initialized():
    cdef int err, init
    err = MPI_Initialized(&init)
    if err:
        raise _mpiErr(err)
    return init

cdef _init():
    cdef int err, argc
    cdef char **argv
    
    argv = <char **> PyMem_Malloc(sizeof(char *) * (len(sys.argv)+1))
    
    for (i, arg) in enumerate(sys.argv):
        argv[i] = arg
    argv[i+1] = NULL
    argc = i
    err = MPI_Init(&argc, &argv)
    _err_check(err)
    
    # Complex number types aren't defined in my mpi.h, so:
    global MY_MPI_CDOUBLE, MY_MPI_CFLOAT
    err = MPI_Type_contiguous(2, MPI_DOUBLE, &MY_MPI_CDOUBLE)
    _err_check(err)
    err = MPI_Type_contiguous(2, MPI_FLOAT, &MY_MPI_CFLOAT)
    _err_check(err)
    err = MPI_Type_commit(&MY_MPI_CDOUBLE)
    _err_check(err)
    err = MPI_Type_commit(&MY_MPI_CFLOAT)
    _err_check(err)


def finalize():
    cdef int err, done, init
    global _finalised
    if _finalised:
        return
    world.barrier()
    gc.collect() # free any communicators etc.
    err = MPI_Type_free(&MY_MPI_CDOUBLE)
    _err_check(err)
    err = MPI_Type_free(&MY_MPI_CFLOAT)
    _err_check(err)
    err = MPI_Finalize()
    _err_check(err)
    _finalised = True


_init()
world = Communicator(MPI_COMM_WORLD)
world.setAbortOnError(False)
atexit.register(finalize)
