/*
   $Header: /home/cvs2/mysql/mysql/util/_c_only.c,v 1.3 2006/08/26 20:19:52 ehuss Exp $
   Copyright (c) 2006, Eric Huss
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
   2. Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
   3. Neither the name of Eric Huss nor the names of any contributors may be
      used to endorse or promote products derived from this software without
      specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
   ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
   LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
   SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
   INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
   POSSIBILITY OF SUCH DAMAGE.
*/

/*
   This module is for functions implemented in C that are too hard or
   inefficient to be implemented in Pyrex.
*/

#include "Python.h"

static char VERSION_STRING[] = "$Revision: 1.3 $";


PyDoc_STRVAR (module_doc,
    "Internal module of C helper functions.\n"
);


/*****************************************************************************/
/*                            Python Functions                               */
/*****************************************************************************/


PyDoc_STRVAR (py_escape_doc,
    "Escape a string suitable for values in MySQL statements.\n"
    "\n"
    ":Parameters:\n"
    "    - `value`: A string to escape.\n"
    "\n"
    ":Return:\n"
    "    Returns an escaped string with enclosing single quotes.\n"
);

static
PyObject *
py_escape(PyObject * self, PyObject * args)
{
    PyObject * value;
    char * value_ptr;
    int length;
    PyObject * new_value;
    char * original_new_value_ptr;
    char * new_value_ptr;
    int new_length;
    int i;
    int m;

    if(!PyArg_ParseTuple(args, "O!", &PyString_Type, &value)) {
        return NULL;
    }

    if(PyString_AsStringAndSize(value, &value_ptr, &length)) {
        return NULL;
    }

    // Pessimistic approach.  +2 for enclosing quotes
    new_length = length*2 + 2;

    new_value = PyString_FromStringAndSize(NULL, new_length);
    if(new_value == NULL) {
        return NULL;
    }

    new_value_ptr = PyString_AS_STRING(new_value);
    // Stow this away so we can compute the final length.
    original_new_value_ptr = new_value_ptr;

    *new_value_ptr++ = '\'';

    for(i=0; i<length; i++) {
        switch(value_ptr[i]) {
            case 0:
                *new_value_ptr++ = '\\';
                *new_value_ptr++ = '0';
                break;
            case '\'':
                *new_value_ptr++ = '\\';
                *new_value_ptr++ = '\'';
                break;
            case '\n':
                *new_value_ptr++ = '\\';
                *new_value_ptr++ = 'n';
                break;
            case '\r':
                *new_value_ptr++ = '\\';
                *new_value_ptr++ = 'r';
                break;
            case '\\':
                *new_value_ptr++ = '\\';
                *new_value_ptr++ = '\\';
                break;
            case '"':
                *new_value_ptr++ = '\\';
                *new_value_ptr++ = '"';
                break;
            default:
                *new_value_ptr++ = value_ptr[i];
                break;
        }
    }

    *new_value_ptr++ = '\'';

    if(_PyString_Resize(&new_value, (new_value_ptr - original_new_value_ptr))) {
        return NULL;
    }

    return new_value;
}

/*****************************************************************************/
/*                              Module Setup                                 */
/*****************************************************************************/

static PyMethodDef module_methods[] = {
    {"escape",  py_escape, METH_VARARGS, py_escape_doc},
    {0, 0},
};

void init_c_only(void)
{
    PyObject *m;

    m = Py_InitModule3("_c_only", module_methods, module_doc);
    PyModule_AddStringConstant(m, "__version__", VERSION_STRING);
}
