#include <Python.h>
#include <stdio.h>
#include <ctype.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <inttypes.h>

#include "losetupmodule.h"

static PyObject *LosetupError;


static PyObject *
losetup_mount(PyObject *self, PyObject *args)
{
	int ffd, fd;
	int mode = O_RDWR;
	struct loop_info64 loopinfo64;
	const char *device, *filename;

    // Check parameters
	if (!PyArg_ParseTuple(args, "ss", &device, &filename)) {
		return NULL;
	}

	// Initialize loopinfo64 struct, and set filename
	memset(&loopinfo64, 0, sizeof(loopinfo64));
	strncpy((char *)loopinfo64.lo_file_name, filename, LO_NAME_SIZE-1);
	loopinfo64.lo_file_name[LO_NAME_SIZE-1] = 0;


	// Open image file
	if ((ffd = open(filename, O_RDWR)) < 0) {
		if (errno == EROFS) // Try to reopen as read-only on EROFS
			ffd = open(filename, mode = O_RDONLY);
		if (ffd < 0) {
			return PyErr_SetFromErrno(LosetupError);
		}
		loopinfo64.lo_flags |= LO_FLAGS_READ_ONLY;
	}

	// Open loopback device
	if ((fd = open(device, mode)) < 0) {
		close(ffd);
		return PyErr_SetFromErrno(LosetupError);
	}

	// Set image
	if (ioctl(fd, LOOP_SET_FD, ffd) < 0) {
		close(fd);
		close(ffd);
		return PyErr_SetFromErrno(LosetupError);
	}
	close (ffd);


	// Set metadata
	if (ioctl(fd, LOOP_SET_STATUS64, &loopinfo64)) {
		ioctl (fd, LOOP_CLR_FD, 0);
		close (fd);
		return PyErr_SetFromErrno(LosetupError);
	}
	close(fd);

	return Py_BuildValue("");
}

static PyObject *
losetup_unmount(PyObject *self, PyObject *args)
{
	int fd;
	const char *device;

	if (!PyArg_ParseTuple(args, "s", &device)) {
		return NULL;
	}

	if ((fd = open (device, O_RDONLY)) < 0) {
		return PyErr_SetFromErrno(LosetupError);
	}
	if (ioctl (fd, LOOP_CLR_FD, 0) < 0) {
		int err = errno;
		close(fd);
		errno = err;
		return PyErr_SetFromErrno(LosetupError);
	}
	close (fd);
	return Py_BuildValue("");
}

static PyObject *
losetup_is_used(PyObject *self, PyObject *args)
{
	int fd, is_used;
	const char *device;
	struct loop_info64 li;

	if (!PyArg_ParseTuple(args, "s", &device)) {
		return NULL;
	}

	if ((fd = open (device, O_RDONLY)) < 0) {
		return PyErr_SetFromErrno(LosetupError);
	}

	is_used = ioctl(fd, LOOP_GET_STATUS64, &li) == 0;

	close(fd);
	return Py_BuildValue("i", is_used);
}

static PyMethodDef LosetupMethods[] = {
    {"mount",  losetup_mount, METH_VARARGS,
     "Mount image to device. Usage _losetup.mount(loop_device, file)."},
    {"unmount",  losetup_unmount, METH_VARARGS,
     "Unmount image from device.  Usage _losetup.unmount(loop_device)."},
    {"is_used", losetup_is_used, METH_VARARGS,
     "Returns True is loopback device is in use."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


PyMODINIT_FUNC
init_losetup(void)
{
    PyObject *m;

    m = Py_InitModule("_losetup", LosetupMethods);
    if (m == NULL)
        return;

    LosetupError = PyErr_NewException("_losetup.error", NULL, NULL);
    Py_INCREF(LosetupError);
    PyModule_AddObject(m, "error", LosetupError);
}
