#include <Python.h>
#include <string.h>
#include <math.h>

const char const* alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
const int base = 62;

static PyObject* cbase62_encode(PyObject *self, PyObject *args) {
    long num;
    if (!PyArg_ParseTuple(args, "l", &num))
        return NULL;
    int i = 6;
    static char buf[8];
    buf[7] = 0;
    for(; num && i ; --i, num /= base)
        buf[i] = alphabet[num % base];
    return Py_BuildValue("s", &buf[i+1]);
}

static PyObject* cbase62_decode(PyObject *self, PyObject *args) {
    const char* encoded;
    if (!PyArg_ParseTuple(args, "s", &encoded))
        return NULL;
    int len = strlen(encoded), pos = 0;
    long result = 0;
    for(; pos < len; pos ++)
        result += (strchr(alphabet, encoded[len - 1 - pos]) - alphabet) * powl(base, pos);
    return Py_BuildValue("l", result);
}

static PyMethodDef cbase62Methods[] = {
    {"encode", cbase62_encode, METH_VARARGS, "encode int in base62"},
    {"decode", cbase62_decode, METH_VARARGS, "decode base62 string"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initcbase62(void) {
    (void) Py_InitModule("cbase62", cbase62Methods);
}