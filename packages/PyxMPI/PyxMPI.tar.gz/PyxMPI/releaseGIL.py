# Make a munged copy of mpi.pyx to release the Python GIL during MPI calls.  
# SWIG is much better for this kind of thing.

defns = """

cdef extern from "pythread.h"
    ctypedef struct PyThreadState
    PyThreadState *PyEval_SaveThread()
    void PyEval_RestoreThread(PyThreadState *_saved_thread)

"""

out = open('mpi_mt.pyx', 'w')

out.write("# This file was made from mpi.pyx by releaseGIL.py\n\n")

for line in open('mpi.pyx'):
    if line.startswith ('__version__'):
        out.write(line)
        out.write(defns)
    elif line.strip().startswith('cdef int') and \
            'err' in line and ":" not in line:
        indent = line[:line.index('c')]
        out.write(line)
        out.write(indent + 'cdef PyThreadState *_saved_thread\n')
    elif line.strip().startswith('err =') and not (
            'MPI_Comm_rank' in line or 'MPI_Comm_size' in line):
        indent = line[:line.index('e')]
        out.write(indent + '_saved_thread = PyEval_SaveThread()\n')
        out.write(line)
        out.write(indent + 'PyEval_RestoreThread(_saved_thread)\n')
    else:
        out.write(line)

# Should do this too:

#ifdef HAVE_THREADS
#include "pythread.h"
#else
#define PyThreadState int
#define PyEval_SaveThread() NULL
#define PyEval_RestoreThread(_save) 0
#endif