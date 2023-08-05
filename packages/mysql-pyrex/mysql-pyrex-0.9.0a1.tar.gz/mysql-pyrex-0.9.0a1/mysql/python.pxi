# $Header: /home/cvs2/mysql/mysql/python.pxi,v 1.3 2006/08/26 22:17:06 ehuss Exp $

# XXX:
# - Need to support "long long" definitions that are different for different platforms.
# - Support unicode platform dependencies.
# - Add unicode calls.

cdef extern from "sys/types.h":
    ctypedef unsigned int size_t

cdef extern from "stdio.h":
    ctypedef struct FILE:
        pass

cdef extern from "Python.h":

    # XXX: This is platform dependent.
    ctypedef unsigned short Py_UNICODE

    ctypedef struct PyTypeObject:
        pass

    ctypedef struct PyObject:
        int ob_refcnt
        PyTypeObject * ob_type

    ###############################################################################################
    # bool
    ###############################################################################################
    PyObject * Py_False
    PyObject * Py_True
    PyTypeObject PyBool_Type
    int                 PyBool_Check                    (object)                    # Always succeeds.
    object              PyBool_FromLong                 (long)

    ###############################################################################################
    # buffer
    ###############################################################################################
    PyTypeObject PyBuffer_Type
    int Py_END_OF_BUFFER
    int                 PyBuffer_Check                  (object)                    # Always succeeds.
    object              PyBuffer_FromMemory             (void *, int)
    object              PyBuffer_FromObject             (object, int, int)
    object              PyBuffer_FromReadWriteMemory    (void *, int)
    object              PyBuffer_FromReadWriteObject    (object, int, int)
    object              PyBuffer_New                    (int)
    int                 PyObject_AsCharBuffer           (object, char **, int *)    except -1
    int                 PyObject_AsReadBuffer           (object, void **, int *)    except -1
    int                 PyObject_AsWriteBuffer          (object, void **, int *)    except -1
    int                 PyObject_CheckReadBuffer        (object)                    # Always succeeds.

    ###############################################################################################
    # cobject
    ###############################################################################################
    PyTypeObject PyCObject_Type

    int                 PyCObject_Check(object)                                     # Always succeeds.
    object              PyCObject_FromVoidPtr(void *, void (*)(void*))
    object              PyCObject_FromVoidPtrAndDesc(void *, void *, void (*)(void*,void*))
    void *              PyCObject_AsVoidPtr(object)                                 except NULL
    void *              PyCObject_GetDesc(object)                                   except NULL
    void *              PyCObject_Import(char *, char *)                            except NULL

    ###############################################################################################
    # complex
    ###############################################################################################
    ctypedef struct Py_complex:
        double real
        double imag

    PyTypeObject PyComplex_Type

    Py_complex          PyComplex_AsCComplex            (object)                    # Always succeeds.
    int                 PyComplex_Check                 (object)                    # Always succeeds.
    int                 PyComplex_CheckExact            (object)                    # Always succeeds.
    object              PyComplex_FromCComplex          (Py_complex)
    object              PyComplex_FromDoubles           (double, double)
    double              PyComplex_ImagAsDouble          (object)                    except? -1
    double              PyComplex_RealAsDouble          (object)                    except? -1
    Py_complex          _Py_c_diff                      (Py_complex, Py_complex)
    Py_complex          _Py_c_neg                       (Py_complex)
    Py_complex          _Py_c_pow                       (Py_complex, Py_complex)
    Py_complex          _Py_c_prod                      (Py_complex, Py_complex)
    Py_complex          _Py_c_quot                      (Py_complex, Py_complex)
    Py_complex          _Py_c_sum                       (Py_complex, Py_complex)

    ###############################################################################################
    # dict
    ###############################################################################################
    PyTypeObject PyDict_Type

    int                 PyDict_Check                    (object)                    # Always succeeds.
    int                 PyDict_CheckExact               (object)                    # Always succeeds.
    void                PyDict_Clear                    (object)
    int                 PyDict_Contains                 (object, object)            except -1
    object              PyDict_Copy                     (object)
    int                 PyDict_DelItem                  (object, object)            except -1
    int                 PyDict_DelItemString            (object, char *)            except -1
    object              PyDict_Items                    (object)
    object              PyDict_Keys                     (object)
    int                 PyDict_Merge                    (object, object, int)       except -1
    int                 PyDict_MergeFromSeq2            (object, object, int)       except -1
    object              PyDict_New                      ()
    # XXX: Pyrex doesn't support pointer to a python object?
    #int                 PyDict_Next                     (object, int *, object *, object *) # Always succeeds.
    int                 PyDict_SetItem                  (object, object, object)    except -1
    int                 PyDict_SetItemString            (object, char *, object)    except -1
    int                 PyDict_Size                     (object)                    except -1
    int                 PyDict_Update                   (object, object)            except -1
    object              PyDict_Values                   (object)
    # XXX: Borrowed reference.  No exception on NULL.
    #object              PyDict_GetItem                  (object, object)
    # XXX: Borrowed reference.  No exception on NULL
    #object              PyDict_GetItemString            (object, char *)


    ###############################################################################################
    # float
    ###############################################################################################
    PyTypeObject PyFloat_Type
    int                 _PyFloat_Pack4                  (double, unsigned char *, int)  except -1
    int                 _PyFloat_Pack8                  (double, unsigned char *, int)  except -1
    double              _PyFloat_Unpack4                (unsigned char *, int)      except? -1
    double              _PyFloat_Unpack8                (unsigned char *, int)      except? -1
    double              PyFloat_AS_DOUBLE               (object)
    double              PyFloat_AsDouble                (object)                    except? -1
    void                PyFloat_AsReprString            (char*, object)
    void                PyFloat_AsString                (char*, object)
    int                 PyFloat_Check                   (object)                    # Always succeeds.
    int                 PyFloat_CheckExact              (object)                    # Always succeeds.
    object              PyFloat_FromDouble              (double)
    object              PyFloat_FromString              (object, char**)

    ###############################################################################################
    # int
    ###############################################################################################
    PyTypeObject PyInt_Type
    long                PyInt_AS_LONG                   (object)                    # Always succeeds.
    long                PyInt_AsLong                    (object)                    except? -1
    unsigned long long  PyInt_AsUnsignedLongLongMask    (object)                    except? -1
    unsigned long       PyInt_AsUnsignedLongMask        (object)                    except? -1
    int                 PyInt_Check                     (object)                    # Always succeeds.
    int                 PyInt_CheckExact                (object)                    # Always succeeds.
    object              PyInt_FromLong                  (long)
    object              PyInt_FromString                (char*, char**, int)
    object              PyInt_FromUnicode               (Py_UNICODE*, int, int)
    long                PyInt_GetMax                    ()                      # Always succeeds.

    ###############################################################################################
    # iterator
    ###############################################################################################
    int                 PyIter_Check                    (object)                    # Always succeeds.
    object              PyIter_Next                     (object)

    ###############################################################################################
    # list
    ###############################################################################################
    PyTypeObject PyList_Type
    int                 PyList_Append                   (object, object)            except -1
    object              PyList_AsTuple                  (object)
    int                 PyList_Check                    (object)                    # Always succeeds.
    int                 PyList_CheckExact               (object)                    # Always succeeds.
    int                 PyList_GET_SIZE                 (object)                    # Always suceeds.
    object              PyList_GetSlice                 (object, int, int)
    int                 PyList_Insert                   (object, int, object)       except -1
    object              PyList_New                      (int)
    int                 PyList_Reverse                  (object)                    except -1
    int                 PyList_SetSlice                 (object, int, int, object)  except -1
    int                 PyList_Size                     (object)                    except -1
    int                 PyList_Sort                     (object)                    except -1

    ###############################################################################################
    # long
    ###############################################################################################
    PyTypeObject PyLong_Type
    int                 _PyLong_AsByteArray             (object, unsigned char *, size_t, int, int) except -1
    object              _PyLong_FromByteArray           (unsigned char *, size_t, int, int)
    size_t              _PyLong_NumBits                 (object)                    except -1
    int                 _PyLong_Sign                    (object)                    # No error.
    long                PyLong_AsLong                   (object)                    except? -1
    long long           PyLong_AsLongLong               (object)                    except? -1
    unsigned long       PyLong_AsUnsignedLong           (object)                    except? -1
    unsigned long       PyLong_AsUnsignedLongMask       (object)                    except? -1
    unsigned long long  PyLong_AsUnsignedLongLong       (object)                    except? -1
    unsigned long long  PyLong_AsUnsignedLongLongMask   (object)                    except? -1
    int                 PyLong_Check                    (object)                    # Always succeeds.
    int                 PyLong_CheckExact               (object)                    # Always succeeds.
    object              PyLong_FromDouble               (double)
    object              PyLong_FromLong                 (long)
    object              PyLong_FromLongLong             (long long)
    object              PyLong_FromUnsignedLong         (unsigned long)
    object              PyLong_FromUnsignedLongLong     (unsigned long long)
    double              PyLong_AsDouble                 (object)                    except? -1
    object              PyLong_FromVoidPtr              (void *)
    void *              PyLong_AsVoidPtr                (object)                    except NULL
    object              PyLong_FromString               (char *, char **, int)
    object              PyLong_FromUnicode              (Py_UNICODE*, int, int)

    ###############################################################################################
    # mapping
    ###############################################################################################
    int                 PyMapping_Check                 (object)                    # Always succeeds.
    int                 PyMapping_DelItem               (object, object)            except -1
    int                 PyMapping_DelItemString         (object, char *)            except -1
    object              PyMapping_GetItemString         (object, char *)
    int                 PyMapping_HasKey                (object, object)            # Always succeeds.
    int                 PyMapping_HasKeyString          (object, char *)            # Always succeeds.
    object              PyMapping_Items                 (object)
    object              PyMapping_Keys                  (object)
    int                 PyMapping_Length                (object)                    except -1
    int                 PyMapping_SetItemString         (object, char *, object)    except -1
    int                 PyMapping_Size                  (object)                    except -1
    object              PyMapping_Values                (object)

    ###############################################################################################
    # mem
    ###############################################################################################
    void                PyMem_Free                      (void * p)
    void *              PyMem_Malloc                    (size_t n)                  except NULL
    void *              PyMem_Realloc                   (void *, size_t)            except NULL

    ###############################################################################################
    # modsupport
    ###############################################################################################
    object              Py_BuildValue                   (char *, ...)
    object              Py_VaBuildValue                 (char *, va_list)

    ###############################################################################################
    # number
    ###############################################################################################
    object              PyNumber_Absolute               (object)
    object              PyNumber_Add                    (object, object)
    object              PyNumber_And                    (object, object)
    int                 PyNumber_Check                  (object)                    # Always succeeds.
    # XXX: Pyrex doesn't support pointer to python object?
    #int                 PyNumber_Coerce                 (object*, object*)          except -1
    object              PyNumber_Divide                 (object, object)
    object              PyNumber_Divmod                 (object, object)
    object              PyNumber_Float                  (object)
    object              PyNumber_FloorDivide            (object, object)
    object              PyNumber_InPlaceAdd             (object, object)
    object              PyNumber_InPlaceAnd             (object, object)
    object              PyNumber_InPlaceDivide          (object, object)
    object              PyNumber_InPlaceFloorDivide     (object, object)
    object              PyNumber_InPlaceLshift          (object, object)
    object              PyNumber_InPlaceMultiply        (object, object)
    object              PyNumber_InPlaceOr              (object, object)
    object              PyNumber_InPlacePower           (object, object, object)
    object              PyNumber_InPlaceRemainder       (object, object)
    object              PyNumber_InPlaceRshift          (object, object)
    object              PyNumber_InPlaceSubtract        (object, object)
    object              PyNumber_InPlaceTrueDivide      (object, object)
    object              PyNumber_InPlaceXor             (object, object)
    object              PyNumber_Int                    (object)
    object              PyNumber_Invert                 (object)
    object              PyNumber_Long                   (object)
    object              PyNumber_Lshift                 (object, object)
    object              PyNumber_Multiply               (object, object)
    object              PyNumber_Negative               (object)
    object              PyNumber_Or                     (object, object)
    object              PyNumber_Positive               (object)
    object              PyNumber_Power                  (object, object, object)
    object              PyNumber_Remainder              (object, object)
    object              PyNumber_Rshift                 (object, object)
    object              PyNumber_Subtract               (object, object)
    object              PyNumber_TrueDivide             (object, object)
    object              PyNumber_Xor                    (object, object)

    ###############################################################################################
    # object
    ###############################################################################################
    int                 PyCallable_Check                (object)                    # Always succeeds.
    int                 PyObject_AsFileDescriptor       (object)                    except -1
    object              PyObject_Call                   (object, object, object)
    object              PyObject_CallFunction           (object, char *, ...)
    object              PyObject_CallFunctionObjArgs    (object, ...)
    object              PyObject_CallMethod             (object, char *, char *, ...)
    object              PyObject_CallMethodObjArgs      (object, object, ...)
    object              PyObject_CallObject             (object, object)
    int                 PyObject_Cmp                    (object, object, int *result)   except -1
    # Use PyObject_Cmp instead.
    #int                 PyObject_Compare                (object, object)
    int                 PyObject_DelAttr                (object, object)            except -1
    int                 PyObject_DelAttrString          (object, char *)            except -1
    int                 PyObject_DelItem                (object, object)            except -1
    int                 PyObject_DelItemString          (object, char *)            except -1
    object              PyObject_Dir                    (object)
    object              PyObject_GetAttr                (object, object)
    object              PyObject_GetAttrString          (object, char *)
    object              PyObject_GetItem                (object, object)
    object              PyObject_GetIter                (object)
    int                 PyObject_HasAttr                (object, object)            # Always succeeds.
    int                 PyObject_HasAttrString          (object, char *)            # Always succeeds.
    long                PyObject_Hash                   (object)                    except -1
    int                 PyObject_IsInstance             (object, object)            except -1
    int                 PyObject_IsSubclass             (object, object)            except -1
    int                 PyObject_IsTrue                 (object)                    except -1
    int                 PyObject_Length                 (object)                    except -1
    int                 PyObject_Not                    (object)                    except -1
    int                 PyObject_Print                  (object, FILE *, int)       except -1
    object              PyObject_Repr                   (object)
    object              PyObject_RichCompare            (object, object, int)
    int                 PyObject_RichCompareBool        (object, object, int)       except -1
    int                 PyObject_SetAttr                (object, object, object)    except -1
    int                 PyObject_SetAttrString          (object, char *, object)    except -1
    int                 PyObject_SetItem                (object, object, object)    except -1
    int                 PyObject_Size                   (object)                    except -1
    object              PyObject_Str                    (object)
    object              PyObject_Type                   (object)
    int                 PyObject_TypeCheck              (object, object)            # Always succeeds.
    object              PyObject_Unicode                (object)

    ###############################################################################################
    # pyerrors
    ###############################################################################################
    int                 PyErr_BadArgument               ()
    void                PyErr_BadInternalCall           ()
    int                 PyErr_CheckSignals              ()
    void                PyErr_Clear                     ()
    int                 PyErr_ExceptionMatches          (object)
    object              PyErr_Format                    (object, char *, ...)
    int                 PyErr_GivenExceptionMatches     (object, object)
    object              PyErr_NoMemory                  ()
    object              PyErr_Occurred                  ()
    void                PyErr_Restore                   (object, object, object)
    object              PyErr_SetFromErrno              (object)
    object              PyErr_SetFromErrnoWithFilename  (object, char *)
    object              PyErr_SetFromErrnoWithFilenameObject    (object, object)
    void                PyErr_SetInterrupt              ()
    void                PyErr_SetNone                   (object)
    void                PyErr_SetObject                 (object, object)
    void                PyErr_SetString                 (object, char *)
    int                 PyErr_Warn                      (object, char *)
    int                 PyErr_WarnExplicit              (object, char *, char *, int, char *, object)
    void                PyErr_WriteUnraisable           (object)

    ###############################################################################################
    # pyeval
    # Be extremely careful with these functions.
    ###############################################################################################

    ctypedef struct PyThreadState:
        pass

    void                PyEval_AcquireLock              ()
    void                PyEval_ReleaseLock              ()
    void                PyEval_AcquireThread            (PyThreadState *)
    void                PyEval_ReleaseThread            (PyThreadState *)
    PyThreadState*      PyEval_SaveThread               ()
    void                PyEval_RestoreThread            (PyThreadState *)

    ###############################################################################################
    # pystate
    # Be extremely careful with these functions.  Read PEP 311 for more detail.
    ###############################################################################################

    ctypedef int PyGILState_STATE
    PyGILState_STATE    PyGILState_Ensure               ()
    void                PyGILState_Release              (PyGILState_STATE)

    ctypedef struct PyInterpreterState:
        pass

    PyThreadState*      PyThreadState_New               (PyInterpreterState *)
    void                PyThreadState_Clear             (PyThreadState *)
    void                PyThreadState_Delete            (PyThreadState *)
    PyThreadState*      PyThreadState_Get               ()
    PyThreadState*      PyThreadState_Swap              (PyThreadState *tstate)
    # XXX: Borrowed reference.
    #object              PyThreadState_GetDict          ()

    ###############################################################################################
    # run
    # Functions for embedded interpreters are not included.
    ###############################################################################################
    ctypedef struct PyCompilerFlags:
        int cf_flags

    ctypedef struct _node:
        pass

    ctypedef void (*PyOS_sighandler_t)(int)

    void                PyErr_Display                   (object, object, object)
    void                PyErr_Print                     ()
    void                PyErr_PrintEx                   (int)
    char *              PyOS_Readline                   (FILE *, FILE *, char *)
    PyOS_sighandler_t   PyOS_getsig                     (int)
    PyOS_sighandler_t   PyOS_setsig                     (int, PyOS_sighandler_t)
    _node *             PyParser_SimpleParseFile        (FILE *, char *, int)       except NULL
    _node *             PyParser_SimpleParseFileFlags   (FILE *, char *, int,
                                                         int)                       except NULL
    _node *             PyParser_SimpleParseString      (char *, int)               except NULL
    _node *             PyParser_SimpleParseStringFlagsFilename(char *, char *,
                                                         int, int)                  except NULL
    _node *             PyParser_SimpleParseStringFlags (char *, int, int)          except NULL
    int                 PyRun_AnyFile                   (FILE *, char *)            except -1
    int                 PyRun_AnyFileEx                 (FILE *, char *, int)       except -1
    int                 PyRun_AnyFileExFlags            (FILE *, char *, int,
                                                         PyCompilerFlags *)         except -1
    int                 PyRun_AnyFileFlags              (FILE *, char *,
                                                         PyCompilerFlags *)         except -1
    object              PyRun_File                      (FILE *, char *, int,
                                                         object, object)
    object              PyRun_FileEx                    (FILE *, char *, int,
                                                         object, object, int)
    object              PyRun_FileExFlags               (FILE *, char *, int,
                                                         object, object, int,
                                                         PyCompilerFlags *)
    object              PyRun_FileFlags                 (FILE *, char *, int,
                                                         object, object,
                                                         PyCompilerFlags *)
    int                 PyRun_InteractiveLoop           (FILE *, char *)            except -1
    int                 PyRun_InteractiveLoopFlags      (FILE *, char *,
                                                         PyCompilerFlags *)         except -1
    int                 PyRun_InteractiveOne            (FILE *, char *)            except -1
    int                 PyRun_InteractiveOneFlags       (FILE *, char *,
                                                         PyCompilerFlags *)         except -1
    int                 PyRun_SimpleFile                (FILE *, char *)            except -1
    int                 PyRun_SimpleFileEx              (FILE *, char *, int)       except -1
    int                 PyRun_SimpleFileExFlags         (FILE *, char *, int,
                                                         PyCompilerFlags *)         except -1
    int                 PyRun_SimpleString              (char *)                    except -1
    int                 PyRun_SimpleStringFlags         (char *, PyCompilerFlags *) except -1
    object              PyRun_String                    (char *, int, object,
                                                         object)
    object              PyRun_StringFlags               (char *, int, object,
                                                         object, PyCompilerFlags *)
    int                 Py_AtExit                       (void (*func)())
    object              Py_CompileString                (char *, char *, int)
    object              Py_CompileStringFlags           (char *, char *, int, PyCompilerFlags *)
    void                Py_Exit                         (int)
    int                 Py_FdIsInteractive              (FILE *, char *)            # Always succeeds.
    char *              Py_GetBuildInfo                 ()
    char *              Py_GetCompiler                  ()
    char *              Py_GetCopyright                 ()
    char *              Py_GetExecPrefix                ()
    char *              Py_GetPath                      ()
    char *              Py_GetPlatform                  ()
    char *              Py_GetPrefix                    ()
    char *              Py_GetProgramFullPath           ()
    char *              Py_GetProgramName               ()
    char *              Py_GetPythonHome                ()
    char *              Py_GetVersion                   ()

    ###############################################################################################
    # sequence
    ###############################################################################################
    int                 PySequence_Check                (object)                    # Always succeeds.
    object              PySequence_Concat               (object, object)
    int                 PySequence_Contains             (object, object)            except -1
    int                 PySequence_Count                (object, object)            except -1
    int                 PySequence_DelItem              (object, int)               except -1
    int                 PySequence_DelSlice             (object, int, int)          except -1
    object              PySequence_Fast                 (object, char *)
    int                 PySequence_Fast_GET_SIZE        (object)
    object              PySequence_GetItem              (object, int)
    object              PySequence_GetSlice             (object, int, int)
    object              PySequence_ITEM                 (object, int)
    int                 PySequence_In                   (object, object)            except -1
    object              PySequence_InPlaceConcat        (object, object)
    object              PySequence_InPlaceRepeat        (object, int)
    int                 PySequence_Index                (object, object)            except -1
    int                 PySequence_Length               (object)                    except -1
    object              PySequence_List                 (object)
    object              PySequence_Repeat               (object, int)
    int                 PySequence_SetItem              (object, int, object)       except -1
    int                 PySequence_SetSlice             (object, int, int, object)  except -1
    int                 PySequence_Size                 (object)                    except -1
    object              PySequence_Tuple                (object)

    ###############################################################################################
    # string
    ###############################################################################################
    PyTypeObject PyString_Type
    # Pyrex cannot support resizing because you have no choice but to use
    # realloc which may call free() on the object, and there's no way to tell
    # Pyrex to "forget" reference counting for the object.
    #int                 _PyString_Resize                (object *, int)             except -1
    char *              PyString_AS_STRING              (object)                    # Always succeeds.
    object              PyString_AsDecodedObject        (object, char *, char *)
    object              PyString_AsEncodedObject        (object, char *, char *)
    object              PyString_AsEncodedString        (object, char *, char *)
    char *              PyString_AsString               (object)                    except NULL
    int                 PyString_AsStringAndSize        (object, char **, int *)    except -1
    int                 PyString_Check                  (object)                    # Always succeeds.
    int                 PyString_CHECK_INTERNED         (object)                    # Always succeeds.
    int                 PyString_CheckExact             (object)                    # Always succeeds.
    # XXX: Pyrex doesn't support pointer to a python object?
    #void                PyString_Concat                 (object *, object)
    # XXX: Pyrex doesn't support pointer to a python object?
    #void                PyString_ConcatAndDel           (object *, object)
    object              PyString_Decode                 (char *, int, char *, char *)
    object              PyString_DecodeEscape           (char *, int, char *, int, char *)
    object              PyString_Encode                 (char *, int, char *, char *)
    object              PyString_Format                 (object, object)
    object              PyString_FromFormat             (char*, ...)
    object              PyString_FromFormatV            (char*, va_list)
    object              PyString_FromString             (char *)
    object              PyString_FromStringAndSize      (char *, int)
    int                 PyString_GET_SIZE               (object)                    # Always succeeds.
    object              PyString_InternFromString       (char *)
    # XXX: Pyrex doesn't support pointer to a python object?
    #void                PyString_InternImmortal         (object*)
    # XXX: Pyrex doesn't support pointer to a python object?
    #void                PyString_InternInPlace          (object*)
    object              PyString_Repr                   (object, int)
    int                 PyString_Size                   (object)                    except -1

    ###############################################################################################
    # tuple
    ###############################################################################################
    PyTypeObject PyTuple_Type
    # See PyString_Resize note about resizing.
    #int                 _PyTuple_Resize                 (object*, int)              except -1
    int                 PyTuple_Check                   (object)                    # Always succeeds.
    int                 PyTuple_CheckExact              (object)                    # Always succeeds.
    int                 PyTuple_GET_SIZE                (object)                    # Always succeeds.
    object              PyTuple_GetSlice                (object, int, int)
    object              PyTuple_New                     (int)
    object              PyTuple_Pack                    (int, ...)
    int                 PyTuple_Size                    (object)                    except -1

    ###############################################################################################
    # Dangerous things!
    # Do not use these unless you really, really know what you are doing.
    ###############################################################################################
    void                Py_INCREF                       (object)
    void                Py_XINCREF                      (object)
    void                Py_DECREF                       (object)
    void                Py_XDECREF                      (object)
    void                Py_CLEAR                        (object)

    # XXX: Stolen reference.
    void                PyTuple_SET_ITEM                (object, int, value)
    # XXX: Borrowed reference.
    object              PyTuple_GET_ITEM                (object, int)
    # XXX: Borrowed reference.
    object              PyTuple_GetItem                 (object, int)
    # XXX: Stolen reference.
    int                 PyTuple_SetItem                 (object, int, object)       except -1

    # XXX: Steals reference.
    int                 PyList_SetItem                  (object, int, object)       except -1
    # XXX: Borrowed reference
    object              PyList_GetItem                  (object, int)
    # XXX: Borrowed reference, no NULL on error.
    object              PyList_GET_ITEM                 (object, int)
    # XXX: Stolen reference.
    void                PyList_SET_ITEM                 (object, int, object)

    # XXX: Borrowed reference.
    object              PySequence_Fast_GET_ITEM        (object, int)
