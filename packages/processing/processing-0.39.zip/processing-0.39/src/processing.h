#ifndef PROCESSING_H
#define PROCESSING_H

static PyObject*
processing_rwbuffer(PyObject *self, PyObject *args)
{
    PyObject *obj;
    Py_ssize_t offset = 0, size = Py_END_OF_BUFFER;
    
    if (!PyArg_ParseTuple(args, "O|" N_FMT N_FMT, &obj, &offset, &size))
        return NULL;

    return PyBuffer_FromReadWriteObject(obj, offset, size);
}

static PyObject*
processing_address_of_buffer(PyObject *self, PyObject *obj)
{
    void *buffer;
    Py_ssize_t buffer_len;
    
    if (PyObject_AsWriteBuffer(obj, &buffer, &buffer_len) < 0)
        return NULL;

    return Py_BuildValue(N_FMT N_FMT, buffer, buffer_len);
}

#endif /* PROCESSING_H */
