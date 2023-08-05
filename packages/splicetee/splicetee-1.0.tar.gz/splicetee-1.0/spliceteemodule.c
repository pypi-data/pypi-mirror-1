/* py-splicetee file : spliceteemodule.c
   A Python module interface to 'splice' and 'tee' system calls.

   This is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License 
   as published by the Free Software Foundation; either
   version 2.1 of the License, or (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software 
	 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA

	 .- */

#include <Python.h>

#if defined(__i386__)
#define __NR_splice 313
#define __NR_tee  315
#elif defined(__ia64__)
#define __NR_splice 1297
#define __NR_tee 1301
#elif defined(__x86_64__) || defined(__amd64__)
#define __NR_splice 275
#define __NR_tee  276
#elif defined(__powerpc__) || defined(__powerpc64__)
#define __NR_splice 283
#define __NR_tee  284
#else
#error unsupported arch (supported ones are i386, ia64, x86_64, powerpc)
#endif

#define SPLICE_F_MOVE	(0x01)
#define SPLICE_F_NONBLOCK (0x02)
#define SPLICE_F_MORE (0x04)
#define SPLICE_F_GIFT (0x08)

static inline ssize_t splice(int fdin, loff_t *off_in, int fdout, 
		loff_t *off_out, size_t len, unsigned int flags) {
	return syscall(__NR_splice, fdin, off_in, fdout, off_out, len, flags);
}

static inline ssize_t tee(int fdin, int fdout, size_t len, unsigned int flags) {
	return syscall(__NR_tee, fdin, fdout, len, flags);
}

static PyObject *
method_splice(PyObject *self, PyObject *args)
{
	int in_fd, out_fd;
	loff_t off_in, off_out;
	loff_t *p_in = NULL, *p_out = NULL;
	size_t len;
	unsigned int flags;

	ssize_t sts;

	if(!PyArg_ParseTuple(args, "iLiLki", &in_fd, &off_in, &out_fd, &off_out, &len,
				&flags))
		return NULL;

	if(len < 0) {
		PyErr_SetString(PyExc_ValueError, "transfer size must be positive.");
		return NULL;
	}
	
	if(off_in)
		p_in = &off_in;
	if(off_out)
		p_out = &off_out;
	
	Py_BEGIN_ALLOW_THREADS;
	sts = splice(in_fd, p_in, out_fd, p_out, len, flags);
	Py_END_ALLOW_THREADS;
	if(sts == -1) {
		PyErr_SetFromErrno(PyExc_OSError);
		return NULL;
	} else {
		return Py_BuildValue("LLk", off_in, off_out, sts);
	}
}

static PyObject *
method_tee(PyObject *self, PyObject *args)
{
	int in_fd, out_fd;
	size_t len;
	unsigned int flags;

	ssize_t sts;

	if(!PyArg_ParseTuple(args, "iiki", &in_fd, &out_fd, &len, &flags))
		return NULL;

	if(len < 0) {
		PyErr_SetString(PyExc_ValueError, "transfer size must be positive.");
		return NULL;
	}
	
	Py_BEGIN_ALLOW_THREADS;
	sts = tee(in_fd, out_fd, len, flags);
	Py_END_ALLOW_THREADS;

	if(sts == -1) {
		PyErr_SetFromErrno(PyExc_OSError);
		return NULL;
	} else {
		return Py_BuildValue("k", sts);
	}
}



static PyMethodDef SpliceTeeMethods[] = {
	{"splice",  method_splice, METH_VARARGS,
"splice(in_fd, off_in, out_fd, off_out, count, flags) = [position_in, \
	position_out, sent]\n"
"\n"
"A splice() is a system call mechanism used by the Linux kernel to request \
the application program to generate service from the operating system in \
order to transfer information in kernel space without the use of user space \
and copying. It is seen as a way of improving I/O performance.\n"
"The core idea is that a process could open a file descriptor for a data \
source, and another for a data sink. Then, with a call to splice(), those two \
streams could be connected to each other, and the data could flow from the \
source to the sink entirely within the kernel, with no need for user-space \
involvement and with minimal (or no) copying.\n"
"\n"
"'in_fd' and 'out_fd' are the file descriptors while 'off_in' and 'off_out' \
are the positions. A call tu splice() will cause the kernel to move up to \
'count' bytes from the data source in_fd to out_fd.\n"
"The 'flags' argument modifies how the copy is done. Currently implemented \
flags are :\n"
"  SPLICE_F_NONBLOCK : makes the splice() operations non-blocking. A call to \
splice() could still block, however, especially if either of the file \
descriptors has not been set for non-blocking I/O.\n"
"  SPLICE_F_MORE : a hint to the kernel that more data will come in a \
subsequent splice() call.\n"
"  SPLICE_F_MOVE : if the output is a file, this flag will cause the kernel \
to attempt to move pages directly from the input pipe buffer into the output \
address space, avoiding a copy operation.\n"
"\n"
"Actually one cannot call splice with in_fd referring to a socket nor with \
in_fd or out_fd referring to files on a network file system (since splice \
operations are undefined on those contexts).\n"
"Internally, splice() works using the pipe buffer mechanism added by Linus in \
early 2005 - that is why one side of the operation is required to be a pipe \
for now.\n"
},
	{"tee", method_tee, METH_VARARGS,
"tee(in_fd, out_fd, cout, flags) = [sent]\n"
"\n"
"'in_fd' and 'out_fd' are the file descriptors. This call requires that both \
file descriptors be pipes. It simply connects fdin to fdout, transferring up \
to len bytes between them. Unlike splice(), however, tee() does not consume \
the input, enabling the input data to be read normally later on by the \
calling process.\n"
"The 'flags' used are the SPLICE_F_* variants, currently the only applicable \
one is SPLICE_F_NONBLOCK. \n"
"\n"
"Now, the advantage of splice()/tee() is that you can do zero-copy movement\
of data, and unlike sendfile() you can do it on _arbitrary_ data (and, as \
shown by 'tee()', it's more than just sending the data to somebody else: you \
can duplicate the data and choose to forward it to two or more different \
users - for things like logging etc).\n"
"So while sendfile() can send files (surprise surprise), splice() really is \
a general 'read/write in user space' and then some, so you can forward data \
from one socket to another, without ever copying it into user space.\n"
"Or, rather than just a boring socket->socket forwarding, you could, for \
example, forward data that comes from a MPEG-4 hardware encoder, and tee() it \
to duplicate the stream, and write one of the streams to disk, and the other \
one to a socket for a real-time broadcast. Again, all without actually \
physically copying it around in memory.\n"
},	
	{NULL, NULL, 0, NULL}        /* Sentinel */
};

static void
insint (PyObject *d, char *name, int value)
{
    PyObject *v = PyInt_FromLong((long) value);
    if (!v || PyDict_SetItemString(d, name, v))
        PyErr_Clear();

    Py_XDECREF(v);
}

PyMODINIT_FUNC
initsplicetee(void)
{
    PyObject *m = Py_InitModule("splicetee", SpliceTeeMethods);

    PyObject *d = PyModule_GetDict (m);

		insint (d, "SPLICE_F_MOVE", SPLICE_F_MOVE);
		insint (d, "SPLICE_F_NONBLOCK", SPLICE_F_NONBLOCK);
		insint (d, "SPLICE_F_MORE", SPLICE_F_MORE);
    PyModule_AddStringConstant(m, "__doc__", "Direct interface to Linux \
				2.6.17+ splice and tee system calls.");
    PyModule_AddStringConstant(m, "__version__", "1.0");
}
