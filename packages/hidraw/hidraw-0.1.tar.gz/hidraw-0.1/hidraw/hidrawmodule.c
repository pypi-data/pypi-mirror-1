#include <Python.h>
#include <sys/ioctl.h>
#include <linux/hidraw.h>

static PyObject* get_info(PyObject *self, PyObject *args)
{
	struct hidraw_devinfo info;
	unsigned FD;

	if(!PyArg_ParseTuple(args, "I", &FD))
		return NULL;
	if(ioctl(FD, HIDIOCGRAWINFO, &info) == -1) {
		PyErr_SetFromErrno(PyExc_OSError);
		return NULL;
	}
	return Py_BuildValue("Iii", (unsigned) info.bustype, (int) info.vendor, (int) info.product);
}
/* TODO:
#define HIDIOCGRDESCSIZE        _IOR('H', 0x01, int)
#define HIDIOCGRDESC            _IOR('H', 0x02, struct hidraw_report_descriptor
*/

static PyMethodDef HIDRAWMethods[] = {
	{"get_info",  get_info, METH_VARARGS, "Get HIDRAW device info."},
	{NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
init_hidraw(void)
{
	PyObject *m;

	m = Py_InitModule("_hidraw", HIDRAWMethods);
	if (m == NULL)
		return;

	/*SpamError = PyErr_NewException("spam.error", NULL, NULL);*/
	/*PyModule_AddObject(m, "error", SpamError);*/
}

