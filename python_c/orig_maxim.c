#include <stdio.h>
// #include <cstdint>
#include <Python.h>

static PyObject* calculate(PyObject *self, PyObject *args)
{
    PyObject *irDataObj, *redDataObj;
    PyObject *irValueObj, *redValueObj;
    PyObject *resultObj;
    uint32_t ir_buffer[100];
    uint32_t red_buffer[100];
    if (!PyArg_ParseTuple(args, "O!O!O!", &PyList_Type, &irDataObj, &PyList_Type, &redDataObj, &PyList_Type, &resultObj))
        return NULL;

    int irDataSize = PyList_Size(irDataObj);
    int redDataSize = PyList_Size(redDataObj);
    if(irDataSize < 0 || redDataSize < 0 || irDataSize != redDataSize)
    {
        printf("Invalid input lists or lists of different sizes!\n");
        return NULL;
    }
    for(int i = 0; i < irDataSize; i++)
    {
        irValueObj = PyList_GetItem(irDataObj, i);
        redValueObj = PyList_GetItem(redDataObj, i);
        if(PyLong_Check(irValueObj))
            ir_buffer[i] = PyLong_AsUnsignedLong(irValueObj);
        else printf("Nan-value in list!\n");
        if(PyLong_Check(redValueObj))
            red_buffer[i] = PyLong_AsUnsignedLong(redValueObj);
        else printf("Nan value in list!\n");
    }

    
    int irRet = PyList_SetItem(resultObj, 0, PyLong_FromLong(irDataSize));
    int redRet = PyList_SetItem(resultObj, 1, PyLong_FromLong(redDataSize));
    if(irRet && redRet)
        Py_RETURN_TRUE;
    else Py_RETURN_FALSE;
}

static PyMethodDef maxim_methods[] = {
    {   
        "calculate", calculate, METH_VARARGS,
        "Maxim Algorithms"
    },  
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef hello_definition = { 
    PyModuleDef_HEAD_INIT,
    "maxim",
    "Maxim Algorithms",
    -1, 
    maxim_methods
};

PyMODINIT_FUNC PyInit_maxim(void) {
    Py_Initialize();
    return PyModule_Create(&hello_definition);
}