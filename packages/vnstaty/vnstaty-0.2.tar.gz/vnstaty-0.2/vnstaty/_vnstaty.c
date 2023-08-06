#include <Python.h>
#include "ifinfo.h"

static PyObject *
vnstaty_getifinfo(PyObject *self, PyObject *args) {
    IFINFO ifinfo;
    unsigned long rx;
    unsigned long tx;
    unsigned long rxp;
    unsigned long txp;
    char *iface;
    
    if (!PyArg_ParseTuple(args, "s", &iface)) 
        return NULL;

    ifinfo.filled = 0;
    ifinfo = getifinfo(iface);

    if(!ifinfo.filled) {
        return Py_BuildValue("");
    } 
    
    rx = Py_SAFE_DOWNCAST(ifinfo.rx, Py_ssize_t, unsigned long);
    tx = Py_SAFE_DOWNCAST(ifinfo.tx, Py_ssize_t, unsigned long);
    rxp = Py_SAFE_DOWNCAST(ifinfo.rxp, Py_ssize_t, unsigned long);
    txp = Py_SAFE_DOWNCAST(ifinfo.txp, Py_ssize_t, unsigned long);
     
    return Py_BuildValue("{s:n,s:n,s:n,s:n}", 
                         "bytes_in", rx, 
                         "bytes_out", tx, 
                         "packages_in", rxp, 
                         "packages_out", txp);
}

static PyMethodDef vnstatyMethods[] = {
    {"getifinfo",  vnstaty_getifinfo, METH_VARARGS,
     "Get the transfered bytes and packages from the networn interface."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
init_vnstaty(void)
{
    (void) Py_InitModule("_vnstaty", vnstatyMethods);
}

