#include <Python.h>
#include <glob.h>
#include <stdio.h>

static PyObject *_glob_glob(PyObject *self, PyObject *args)

{
  char *pattern;
  glob_t glob_buffer;
  PyObject* filename_list = NULL;
 
  if (!PyArg_ParseTuple(args, "s", &pattern))
    return NULL;

  glob(pattern, 0, NULL, &glob_buffer);
  filename_list = PyList_New(glob_buffer.gl_pathc);

  for (int i = 0; i < glob_buffer.gl_pathc; i++)
  {
    PyList_SetItem(filename_list, i,
                   PyString_FromString(glob_buffer.gl_pathv[i])); /* steals ref */
  }

  globfree(&glob_buffer);

  return filename_list;
}

static PyMethodDef _GlobMethods[] =
{
  {"glob", _glob_glob, METH_VARARGS, "glob a pattern"},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC init_glob(void)
{
  (void) Py_InitModule("_glob", _GlobMethods);
}
