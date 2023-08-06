#include <windows.h>
#include <dia2.h>
#include <string>
#include <atlbase.h>
#include <atlconv.h>
#include <malloc.h>

#include <Python.h>

using namespace std;

static PyObject* newdiasymbol(IDiaSymbol *obj);
static PyObject* newdiaenumsymbols(IDiaEnumSymbols *obj);

/********************************** Property Helpers ****************************/

PyObject* comresult_BOOL(HRESULT hr, BOOL* val, char* propname)
{
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "%s failed (%x)", propname, hr);
        return NULL;
    }
    return PyBool_FromLong(*val);
}

PyObject* comresult_DWORD(HRESULT hr, DWORD* val, char* propname)
{
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "%s failed (%x)", propname, hr);
        return NULL;
    }
    return PyLong_FromUnsignedLong(*val);
}

PyObject* comresult_LONG(HRESULT hr, LONG* val, char* propname)
{
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "%s failed (%x)", propname, hr);
        return NULL;
    }
    return PyLong_FromLong(*val);
}

PyObject* comresult_ULONGLONG(HRESULT hr, ULONGLONG* val, char* propname)
{
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "%s failed (%x)", propname, hr);
        return NULL;
    }
    return PyLong_FromUnsignedLongLong(*val);
}

PyObject* comresult_BSTR(HRESULT hr, BSTR* val, char* propname)
{
    PyObject *result;
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "%s failed (%x)", propname, hr);
        return NULL;
    }
    if (val == NULL)
        /* By convention, NULL is the same as an empty string. */
        return PyUnicode_FromUnicode(NULL, 0);
    result = PyUnicode_FromWideChar(*val, SysStringLen(*val));
    SysFreeString(*val);
    return result;
}

PyObject* comresult_VARIANT(HRESULT hr, VARIANT* val, char* propname)
{
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "%s failed (%x)", propname, hr);
        return NULL;
    }
    /* XXX not yet */
    PyErr_SetString(PyExc_NotImplementedError, "returning VARIANT");
    return NULL;
}

PyObject* comresult_GUID(HRESULT hr, GUID* val, char* propname)
{
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "%s failed (%x)", propname, hr);
        return NULL;
    }
    return PyString_FromStringAndSize((char*)val, sizeof(GUID));
}

typedef IDiaSymbol *PIDiaSymbol;
PyObject* comresult_PIDiaSymbol(HRESULT hr, PIDiaSymbol* val, char* propname)
{
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "%s failed (%x)", propname, hr);
        return NULL;
    }
    return newdiasymbol(*val);
}

/********************************** EnumSymbols *********************************/

struct diaenumsymbols{
    PyObject_HEAD
    IDiaEnumSymbols*    obj;
};

extern "C" static PyObject*
diaenumsymbols_Item(PyObject* _self, PyObject* args)
{
    struct diaenumsymbols* self = (struct diaenumsymbols*)_self;
    HRESULT hr;
    int index;
    IDiaSymbol *res;

    if (!PyArg_ParseTuple(args, "i:Item", &index))
        return NULL;

    if (index < 0)
        return PyErr_Format(PyExc_ValueError, "negative index");

    hr = self->obj->Item(index,&res);
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "Item failed (%x)", hr);
        return NULL;
    }
    return newdiasymbol(res);
}

extern "C" static PyObject*
diaenumsymbols_Next(PyObject* _self, PyObject* args)
{
    struct diaenumsymbols* self = (struct diaenumsymbols*)_self;
    HRESULT hr;
    int count;
    ULONG fetched;
    PyObject *list;

    if (!PyArg_ParseTuple(args, "i:Next", &count))
        return NULL;

    if (count < 0)
        return PyErr_Format(PyExc_ValueError, "negative count");

    IDiaSymbol **res = (IDiaSymbol**)_alloca(sizeof(IDiaSymbol*)*count);
    if (res == NULL)
        return PyErr_Format(PyExc_MemoryError, "too many symbols requested");

    hr = self->obj->Next(count, res, &fetched);
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "Item failed (%x)", hr);
        return NULL;
    }

    list = PyList_New(fetched);
	if (!list) {
		for (unsigned int i = 0; i < fetched; i++) {
			res[i]->Release();
		}
		return NULL;
	}

	for (unsigned int i = 0; i < fetched; i++) {
		PyObject* obj = newdiasymbol(res[i]);

		if (obj != NULL) {
			PyList_SetItem(list, i, obj);
		} else {
			for (unsigned int k = i + 1; k < fetched; k++) {
				res[i]->Release();
			}
			Py_CLEAR(list);
			return NULL;
		}
	}

    return list;
}

extern "C" static PyObject*
diaenumsymbols_Skip(PyObject* _self, PyObject* args)
{
    struct diaenumsymbols* self = (struct diaenumsymbols*)_self;
    HRESULT hr;
    int count;

    if (!PyArg_ParseTuple(args, "i:Skip", &count))
        return NULL;

    if (count < 0)
        return PyErr_Format(PyExc_ValueError, "negative count");

    hr = self->obj->Skip(count);
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "Skip failed (%x)", hr);
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

extern "C" static PyObject*
diaenumsymbols_Reset(PyObject* _self, PyObject* args)
{
    struct diaenumsymbols* self = (struct diaenumsymbols*)_self;
    HRESULT hr;

    hr = self->obj->Reset();
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "Reset failed (%x)", hr);
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

extern "C" static PyObject*
diaenumsymbols_Clone(PyObject* _self, PyObject* args)
{
    struct diaenumsymbols* self = (struct diaenumsymbols*)_self;
    HRESULT hr;
    IDiaEnumSymbols *res;

    hr = self->obj->Clone(&res);
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "Clone failed (%x)", hr);
        return NULL;
    }
    return newdiaenumsymbols(res);
}

static PyMethodDef diaenumsymbols_methods[] = {
    {"Item",    (PyCFunction)diaenumsymbols_Item,	METH_VARARGS,
        "Item(index) -> symbol"},
    {"Next",    (PyCFunction)diaenumsymbols_Next,	METH_VARARGS,
        "Next(count) -> list of symbol"},
    {"Skip",    (PyCFunction)diaenumsymbols_Skip,	METH_VARARGS,
        "Skip(count) -> None"},
    {"Reset",    (PyCFunction)diaenumsymbols_Reset,	METH_NOARGS,
        "Reset() -> None"},
    {"Clone",    (PyCFunction)diaenumsymbols_Clone,	METH_NOARGS,
        "Clone() -> enumsymbols"},
    {NULL,    	NULL}		/* sentinel */
};


extern "C" static void
diaenumsymbols_dealloc(PyObject *_diaenumsymbols)
{
    struct diaenumsymbols *diaenumsymbols = (struct diaenumsymbols*)_diaenumsymbols;
    diaenumsymbols->obj->Release();
    PyObject_Del(_diaenumsymbols);
}

static PyTypeObject diaenumsymbols_type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyObject_HEAD_INIT(NULL)
    0,
    "dia.EnumSymbols",		/*tp_name*/
    sizeof(struct diaenumsymbols),	/*tp_basicsize*/
    0,			/*tp_itemsize*/
    /* methods */
    diaenumsymbols_dealloc, /*tp_dealloc*/
    0,			/*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0,			/*tp_compare*/
    0,			/*tp_repr*/
    0,			/*tp_as_number*/
    0,			/*tp_as_sequence*/
    0,			/*tp_as_mapping*/
    0,			/*tp_hash*/
    0,                      /*tp_call*/
    0,                      /*tp_str*/
    PyObject_GenericGetAttr,                      /*tp_getattro*/
    0,                      /*tp_setattro*/
    0,                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,     /*tp_flags*/
    0,                      /*tp_doc*/
    0,                      /*tp_traverse*/
    0,                      /*tp_clear*/
    0,                      /*tp_richcompare*/
    0,                      /*tp_weaklistoffset*/
    0,                      /*tp_iter*/
    0,                      /*tp_iternext*/
    diaenumsymbols_methods,      /*tp_methods*/
    0,                      /*tp_members*/
    0,                      /*tp_getset*/
    0,                      /*tp_base*/
    0,                      /*tp_dict*/
    0,                      /*tp_descr_get*/
    0,                      /*tp_descr_set*/
    0,                      /*tp_dictoffset*/
    0,                      /*tp_init*/
    0,                      /*tp_alloc*/
    0,                      /*tp_new*/
    0,                      /*tp_free*/
    0,                      /*tp_is_gc*/
};

static PyObject*
newdiaenumsymbols(IDiaEnumSymbols *obj)
{
    struct diaenumsymbols *rv;

    rv = PyObject_New(struct diaenumsymbols, &diaenumsymbols_type);
    if (rv == NULL)
    	return NULL;
    rv->obj = obj;
    return (PyObject *)rv;
}

/********************************** Symbol *********************************/

struct diasymbol{
    PyObject_HEAD
    IDiaSymbol*    obj;
};

extern "C" static PyObject*
diasymbol_findChildren(PyObject* _self, PyObject* args)
{
    struct diasymbol* self = (struct diasymbol*)_self;
    HRESULT hr;
    int symtag;
    Py_UNICODE* name;
    unsigned int compareFlags;
    IDiaEnumSymbols *enumsyms;

    if (!PyArg_ParseTuple(args, "iuI", &symtag, &name, &compareFlags))
        return NULL;

    hr = self->obj->findChildren((enum SymTagEnum)symtag, 
                                  (LPCOLESTR)name, compareFlags, &enumsyms);
    if (hr != S_OK) {
        PyErr_Format(PyExc_ValueError, "findChildren failed (%x)", hr);
        return NULL;
    }
    return newdiaenumsymbols(enumsyms);
}


static PyMethodDef diasymbol_methods[] = {
    {"findChildren",    (PyCFunction)diasymbol_findChildren,	METH_VARARGS,
        "findChildren() -> enumsymbols"},
    {NULL,    	NULL}		/* sentinel */
};

#define mkgetter(type,name) \
    extern "C" static PyObject* diasymbol_get_##name(PyObject *_self, void*ignored){ \
        struct diasymbol *self = (struct diasymbol*)_self;                       \
        type resval;                                                             \
        HRESULT hr = self->obj->get_##name(&resval);                             \
        return comresult_##type(hr, &resval, #name);                             \
    }

mkgetter(DWORD, symIndexId)
mkgetter(DWORD, symTag)
mkgetter(BSTR, name)
mkgetter(PIDiaSymbol, lexicalParent)
mkgetter(PIDiaSymbol, classParent)
mkgetter(PIDiaSymbol, type)
mkgetter(DWORD, dataKind)
mkgetter(DWORD, locationType)
mkgetter(DWORD, addressSection)
mkgetter(DWORD, addressOffset)
mkgetter(DWORD, relativeVirtualAddress)
mkgetter(ULONGLONG, virtualAddress)
mkgetter(DWORD, registerId)
mkgetter(LONG, offset)
mkgetter(ULONGLONG, length)
mkgetter(DWORD, slot)
mkgetter(BOOL, volatileType)
mkgetter(BOOL, constType)
mkgetter(BOOL, unalignedType)
mkgetter(DWORD, access)
mkgetter(BSTR, libraryName)
mkgetter(DWORD, platform)
mkgetter(DWORD, language)
mkgetter(BOOL, editAndContinueEnabled)
mkgetter(DWORD, frontEndMajor)
mkgetter(DWORD, frontEndMinor)
mkgetter(DWORD, frontEndBuild)
mkgetter(DWORD, backEndMajor)
mkgetter(DWORD, backEndMinor)
mkgetter(DWORD, backEndBuild)
mkgetter(BSTR, sourceFileName)
mkgetter(BSTR, unused)
mkgetter(DWORD, thunkOrdinal)
mkgetter(LONG, thisAdjust)
mkgetter(DWORD, virtualBaseOffset)
mkgetter(BOOL, virtual)
mkgetter(BOOL, intro)
mkgetter(BOOL, pure)
mkgetter(DWORD, callingConvention)
mkgetter(VARIANT, value)
mkgetter(DWORD, baseType)
mkgetter(DWORD, token)
mkgetter(DWORD, timeStamp)
mkgetter(GUID, guid)
mkgetter(BSTR, symbolsFileName)
mkgetter(BOOL, reference)
mkgetter(DWORD, count)
mkgetter(DWORD, bitPosition)
mkgetter(PIDiaSymbol, arrayIndexType)
mkgetter(BOOL, packed)
mkgetter(BOOL, constructor)
mkgetter(BOOL, overloadedOperator)
mkgetter(BOOL, nested)
mkgetter(BOOL, hasNestedTypes)
mkgetter(BOOL, hasAssignmentOperator)
mkgetter(BOOL, hasCastOperator)
mkgetter(BOOL, scoped)
mkgetter(BOOL, virtualBaseClass)
mkgetter(BOOL, indirectVirtualBaseClass)
mkgetter(LONG, virtualBasePointerOffset)
mkgetter(PIDiaSymbol, virtualTableShape)
mkgetter(DWORD, lexicalParentId)
mkgetter(DWORD, classParentId)
mkgetter(DWORD, typeId)
mkgetter(DWORD, arrayIndexTypeId)
mkgetter(DWORD, virtualTableShapeId)
mkgetter(BOOL, code)
mkgetter(BOOL, function)
mkgetter(BOOL, managed)
mkgetter(BOOL, msil)
mkgetter(DWORD, virtualBaseDispIndex)
mkgetter(BSTR, undecoratedName)
mkgetter(DWORD, age)
mkgetter(DWORD, signature)
mkgetter(BOOL, compilerGenerated)
mkgetter(BOOL, addressTaken)
mkgetter(DWORD, rank)
mkgetter(PIDiaSymbol, lowerBound)
mkgetter(PIDiaSymbol, upperBound)
mkgetter(DWORD, lowerBoundId)
mkgetter(DWORD, upperBoundId)
mkgetter(DWORD, targetSection)
mkgetter(DWORD, targetOffset)
mkgetter(DWORD, targetRelativeVirtualAddress)
mkgetter(ULONGLONG, targetVirtualAddress)
mkgetter(DWORD, machineType)
mkgetter(DWORD, oemId)
mkgetter(DWORD, oemSymbolId)
mkgetter(PIDiaSymbol, objectPointerType)
mkgetter(DWORD, udtKind)
mkgetter(BOOL, noReturn)
mkgetter(BOOL, customCallingConvention)
mkgetter(BOOL, noInline)
mkgetter(BOOL, optimizedCodeDebugInfo)
mkgetter(BOOL, notReached)
mkgetter(BOOL, interruptReturn)
mkgetter(BOOL, farReturn)
mkgetter(BOOL, isStatic)
mkgetter(BOOL, hasDebugInfo)
mkgetter(BOOL, isLTCG)
mkgetter(BOOL, isDataAligned)
mkgetter(BOOL, hasSecurityChecks)
mkgetter(BSTR, compilerName)
mkgetter(BOOL, hasAlloca)
mkgetter(BOOL, hasSetJump)
mkgetter(BOOL, hasLongJump)
mkgetter(BOOL, hasInlAsm)
mkgetter(BOOL, hasEH)
mkgetter(BOOL, hasSEH)
mkgetter(BOOL, hasEHa)
mkgetter(BOOL, isNaked)
mkgetter(BOOL, isAggregated)
mkgetter(BOOL, isSplitted)
mkgetter(PIDiaSymbol, container)
mkgetter(BOOL, inlSpec)
mkgetter(BOOL, noStackOrdering)
mkgetter(PIDiaSymbol, virtualBaseTableType)
mkgetter(BOOL, hasManagedCode)
mkgetter(BOOL, isHotpatchable)
mkgetter(BOOL, isCVTCIL)
mkgetter(BOOL, isMSILNetmodule)
mkgetter(BOOL, isCTypes)
mkgetter(BOOL, isStripped)
//mkgetter(DWORD, frontEndQFE) XXX fails to compile
//mkgetter(DWORD, backEndQFE)  XXX
//mkgetter(BOOL, wasInlined) XXX
//mkgetter(BOOL, strictGSCheck) XXX
//mkgetter(BOOL, isCxxReturnUdt) XXX
//mkgetter(BOOL, isConstructorVirtualBase) XXX


#undef mkgetter
#define mkgetter(type, name) {#name, diasymbol_get_##name, NULL, NULL, NULL},

static struct PyGetSetDef diasymbol_getset[] = {
mkgetter(DWORD, symIndexId)
mkgetter(DWORD, symTag)
mkgetter(BSTR, name)
mkgetter(PIDiaSymbol, lexicalParent)
mkgetter(PIDiaSymbol, classParent)
mkgetter(PIDiaSymbol, type)
mkgetter(DWORD, dataKind)
mkgetter(DWORD, locationType)
mkgetter(DWORD, addressSection)
mkgetter(DWORD, addressOffset)
mkgetter(DWORD, relativeVirtualAddress)
mkgetter(ULONGLONG, virtualAddress)
mkgetter(DWORD, registerId)
mkgetter(LONG, offset)
mkgetter(ULONGLONG, length)
mkgetter(DWORD, slot)
mkgetter(BOOL, volatileType)
mkgetter(BOOL, constType)
mkgetter(BOOL, unalignedType)
mkgetter(DWORD, access)
mkgetter(BSTR, libraryName)
mkgetter(DWORD, platform)
mkgetter(DWORD, language)
mkgetter(BOOL, editAndContinueEnabled)
mkgetter(DWORD, frontEndMajor)
mkgetter(DWORD, frontEndMinor)
mkgetter(DWORD, frontEndBuild)
mkgetter(DWORD, backEndMajor)
mkgetter(DWORD, backEndMinor)
mkgetter(DWORD, backEndBuild)
mkgetter(BSTR, sourceFileName)
mkgetter(BSTR, unused)
mkgetter(DWORD, thunkOrdinal)
mkgetter(LONG, thisAdjust)
mkgetter(DWORD, virtualBaseOffset)
mkgetter(BOOL, virtual)
mkgetter(BOOL, intro)
mkgetter(BOOL, pure)
mkgetter(DWORD, callingConvention)
mkgetter(VARIANT, value)
mkgetter(DWORD, baseType)
mkgetter(DWORD, token)
mkgetter(DWORD, timeStamp)
mkgetter(GUID, guid)
mkgetter(BSTR, symbolsFileName)
mkgetter(BOOL, reference)
mkgetter(DWORD, count)
mkgetter(DWORD, bitPosition)
mkgetter(PIDiaSymbol, arrayIndexType)
mkgetter(BOOL, packed)
mkgetter(BOOL, constructor)
mkgetter(BOOL, overloadedOperator)
mkgetter(BOOL, nested)
mkgetter(BOOL, hasNestedTypes)
mkgetter(BOOL, hasAssignmentOperator)
mkgetter(BOOL, hasCastOperator)
mkgetter(BOOL, scoped)
mkgetter(BOOL, virtualBaseClass)
mkgetter(BOOL, indirectVirtualBaseClass)
mkgetter(LONG, virtualBasePointerOffset)
mkgetter(PIDiaSymbol, virtualTableShape)
mkgetter(DWORD, lexicalParentId)
mkgetter(DWORD, classParentId)
mkgetter(DWORD, typeId)
mkgetter(DWORD, arrayIndexTypeId)
mkgetter(DWORD, virtualTableShapeId)
mkgetter(BOOL, code)
mkgetter(BOOL, function)
mkgetter(BOOL, managed)
mkgetter(BOOL, msil)
mkgetter(DWORD, virtualBaseDispIndex)
mkgetter(BSTR, undecoratedName)
mkgetter(DWORD, age)
mkgetter(DWORD, signature)
mkgetter(BOOL, compilerGenerated)
mkgetter(BOOL, addressTaken)
mkgetter(DWORD, rank)
mkgetter(PIDiaSymbol, lowerBound)
mkgetter(PIDiaSymbol, upperBound)
mkgetter(DWORD, lowerBoundId)
mkgetter(DWORD, upperBoundId)
mkgetter(DWORD, targetSection)
mkgetter(DWORD, targetOffset)
mkgetter(DWORD, targetRelativeVirtualAddress)
mkgetter(ULONGLONG, targetVirtualAddress)
mkgetter(DWORD, machineType)
mkgetter(DWORD, oemId)
mkgetter(DWORD, oemSymbolId)
mkgetter(PIDiaSymbol, objectPointerType)
mkgetter(DWORD, udtKind)
mkgetter(BOOL, noReturn)
mkgetter(BOOL, customCallingConvention)
mkgetter(BOOL, noInline)
mkgetter(BOOL, optimizedCodeDebugInfo)
mkgetter(BOOL, notReached)
mkgetter(BOOL, interruptReturn)
mkgetter(BOOL, farReturn)
mkgetter(BOOL, isStatic)
mkgetter(BOOL, hasDebugInfo)
mkgetter(BOOL, isLTCG)
mkgetter(BOOL, isDataAligned)
mkgetter(BOOL, hasSecurityChecks)
mkgetter(BSTR, compilerName)
mkgetter(BOOL, hasAlloca)
mkgetter(BOOL, hasSetJump)
mkgetter(BOOL, hasLongJump)
mkgetter(BOOL, hasInlAsm)
mkgetter(BOOL, hasEH)
mkgetter(BOOL, hasSEH)
mkgetter(BOOL, hasEHa)
mkgetter(BOOL, isNaked)
mkgetter(BOOL, isAggregated)
mkgetter(BOOL, isSplitted)
mkgetter(PIDiaSymbol, container)
mkgetter(BOOL, inlSpec)
mkgetter(BOOL, noStackOrdering)
mkgetter(PIDiaSymbol, virtualBaseTableType)
mkgetter(BOOL, hasManagedCode)
mkgetter(BOOL, isHotpatchable)
mkgetter(BOOL, isCVTCIL)
mkgetter(BOOL, isMSILNetmodule)
mkgetter(BOOL, isCTypes)
mkgetter(BOOL, isStripped)
//mkgetter(DWORD, frontEndQFE) XXX fails to compile
//mkgetter(DWORD, backEndQFE)  XXX
//mkgetter(BOOL, wasInlined) XXX
//mkgetter(BOOL, strictGSCheck) XXX
//mkgetter(BOOL, isCxxReturnUdt) XXX
//mkgetter(BOOL, isConstructorVirtualBase) XXX
    {NULL} /* Sentinel */
};


extern "C" static void
diasymbol_dealloc(PyObject *_diasymbol)
{
    struct diasymbol *diasymbol = (struct diasymbol*)_diasymbol;
    diasymbol->obj->Release();
    PyObject_Del(_diasymbol);
}

static PyTypeObject diasymbol_type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyObject_HEAD_INIT(NULL)
    0,
    "dia.Symbol",		/*tp_name*/
    sizeof(struct diasymbol),	/*tp_basicsize*/
    0,			/*tp_itemsize*/
    /* methods */
    diasymbol_dealloc, /*tp_dealloc*/
    0,			/*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0,			/*tp_compare*/
    0,			/*tp_repr*/
    0,			/*tp_as_number*/
    0,			/*tp_as_sequence*/
    0,			/*tp_as_mapping*/
    0,			/*tp_hash*/
    0,                      /*tp_call*/
    0,                      /*tp_str*/
    PyObject_GenericGetAttr,                      /*tp_getattro*/
    0,                      /*tp_setattro*/
    0,                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,     /*tp_flags*/
    0,                      /*tp_doc*/
    0,                      /*tp_traverse*/
    0,                      /*tp_clear*/
    0,                      /*tp_richcompare*/
    0,                      /*tp_weaklistoffset*/
    0,                      /*tp_iter*/
    0,                      /*tp_iternext*/
    diasymbol_methods,      /*tp_methods*/
    0,                      /*tp_members*/
    diasymbol_getset,       /*tp_getset*/
    0,                      /*tp_base*/
    0,                      /*tp_dict*/
    0,                      /*tp_descr_get*/
    0,                      /*tp_descr_set*/
    0,                      /*tp_dictoffset*/
    0,                      /*tp_init*/
    0,                      /*tp_alloc*/
    0,                      /*tp_new*/
    0,                      /*tp_free*/
    0,                      /*tp_is_gc*/
};

static PyObject*
newdiasymbol(IDiaSymbol *obj)
{
    struct diasymbol *rv;

    rv = PyObject_New(struct diasymbol, &diasymbol_type);
	if (rv == NULL) {
		obj->Release();
    	return NULL;
	}
    rv->obj = obj;
    return (PyObject *)rv;
}

/********************************** Session *********************************/

struct diasession{
    PyObject_HEAD
    IDiaSession*	obj;
};

extern "C" static PyObject*
diasession_loadAddress(PyObject* _self, void* ignored)
{
    struct diasession* self = (struct diasession*)_self;
    HRESULT hr;
    ULONGLONG val;
    hr = self->obj->get_loadAddress(&val);
    return comresult_ULONGLONG(hr, &val, "loadAddress");
}

extern "C" static PyObject*
diasession_globalScope(PyObject* _self, void* ignored)
{
    struct diasession* self = (struct diasession*)_self;
    HRESULT hr;
    IDiaSymbol *globalScope;

    hr = self->obj->get_globalScope(&globalScope);
    if (hr != S_OK) {
    	PyErr_Format(PyExc_ValueError, "globalScope failed (%x)", hr);
    	return NULL;
    }
    return newdiasymbol(globalScope);
}


static PyMethodDef diasession_methods[] = {
    {NULL,		NULL}		/* sentinel */
};

static PyGetSetDef diasession_getset[] = {
    {"loadAddress", diasession_loadAddress, NULL, NULL, NULL},
    {"globalScope", diasession_globalScope, NULL, NULL, NULL},
    {NULL,		NULL}		/* sentinel */
};


extern "C" static void
diasession_dealloc(PyObject *_diasession)
{
    struct diasession *diasession = (struct diasession*)_diasession;
    diasession->obj->Release();
    PyObject_Del(_diasession);
}

static PyTypeObject diasession_type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyObject_HEAD_INIT(NULL)
    0,
    "dia.Session",		/*tp_name*/
    sizeof(struct diasession),	/*tp_basicsize*/
    0,			/*tp_itemsize*/
    /* methods */
    diasession_dealloc, /*tp_dealloc*/
    0,			/*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0,			/*tp_compare*/
    0,			/*tp_repr*/
    0,			/*tp_as_number*/
    0,			/*tp_as_sequence*/
    0,			/*tp_as_mapping*/
    0,			/*tp_hash*/
    0,                      /*tp_call*/
    0,                      /*tp_str*/
    PyObject_GenericGetAttr,                      /*tp_getattro*/
    0,                      /*tp_setattro*/
    0,                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,     /*tp_flags*/
    0,                      /*tp_doc*/
    0,                      /*tp_traverse*/
    0,                      /*tp_clear*/
    0,                      /*tp_richcompare*/
    0,                      /*tp_weaklistoffset*/
    0,                      /*tp_iter*/
    0,                      /*tp_iternext*/
    diasession_methods,      /*tp_methods*/
    0,                      /*tp_members*/
    diasession_getset,      /*tp_getset*/
    0,                      /*tp_base*/
    0,                      /*tp_dict*/
    0,                      /*tp_descr_get*/
    0,                      /*tp_descr_set*/
    0,                      /*tp_dictoffset*/
    0,                      /*tp_init*/
    0,                      /*tp_alloc*/
    0,                      /*tp_new*/
    0,                      /*tp_free*/
    0,                      /*tp_is_gc*/
};

static PyObject*
newdiasession(IDiaSession *obj)
{
    struct diasession *rv;

    rv = PyObject_New(struct diasession, &diasession_type);
	if (rv == NULL) {
		obj->Release();
    	return NULL;
	}
    rv->obj = obj;
    return (PyObject *)rv;
}

/******************************* Source *********************************************/

struct diasource{
    PyObject_HEAD
    IDiaDataSource*	obj;
};

extern "C" static PyObject*
diasource_loadDataFromPdb(PyObject* _self, PyObject* args)
{
    struct diasource* self = (struct diasource*)_self;
    Py_UNICODE* filename;
    HRESULT hr;

    if (!PyArg_ParseTuple(args, "u:loadDataFromPdb", &filename))
    	return NULL;
    hr = self->obj->loadDataFromPdb((LPCOLESTR)filename); 
    if (hr != S_OK) {
    	PyErr_Format(PyExc_ValueError, "loadDataFromPdb failed (%x)", hr);
    	return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

extern "C" static PyObject*
diasource_openSession(PyObject* _self, PyObject* args)
{
    struct diasource* self = (struct diasource*)_self;
    IDiaSession* session;
    HRESULT hr;

    hr = self->obj->openSession(&session); 
    if (hr != S_OK) {
    	PyErr_Format(PyExc_ValueError, "opensession failed (%x)", hr);
    	return NULL;
    }
    return newdiasession(session);
}

extern "C" static PyObject*
diasource_get_lastError(PyObject *_self, void* ignored)
{
    struct diasource *self = (struct diasource*)_self;
    BSTR resval;
    HRESULT hr = self->obj->get_lastError(&resval);
    return comresult_BSTR(hr, &resval, "lastError");
}

static PyMethodDef diasource_methods[] = {
    {"loadDataFromPdb",	(PyCFunction)diasource_loadDataFromPdb,	METH_VARARGS,
    	"loadDataFromPdb(unicode_filename) -> None"},
    {"openSession",	(PyCFunction)diasource_openSession,	METH_NOARGS,
    	"openSession() -> session"},
    {NULL,		NULL}		/* sentinel */
};

static struct PyGetSetDef diasource_getset[] = {
    {"lastError", diasource_get_lastError, NULL, NULL, NULL},
    {NULL}
};

static PyObject* newdiasource(); // forward declaration
extern "C" static PyObject*
diasource_new(PyTypeObject *type, PyObject *args, PyObject *kw)
{
    /* XXX process args, check type for subtypes */
    return newdiasource();
}

extern "C" static void
diasource_dealloc(PyObject *_diasource)
{
    struct diasource *diasource = (struct diasource*)_diasource;
    diasource->obj->Release();
    PyObject_Del(_diasource);
}

static PyTypeObject diasource_type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyObject_HEAD_INIT(NULL)
    0,
    "dia.DataSource",		/*tp_name*/
    sizeof(struct diasource),	/*tp_basicsize*/
    0,			/*tp_itemsize*/
    /* methods */
    diasource_dealloc, /*tp_dealloc*/
    0,			/*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0,			/*tp_compare*/
    0,			/*tp_repr*/
    0,			/*tp_as_number*/
    0,			/*tp_as_sequence*/
    0,			/*tp_as_mapping*/
    0,			/*tp_hash*/
    0,                      /*tp_call*/
    0,                      /*tp_str*/
    PyObject_GenericGetAttr,                      /*tp_getattro*/
    0,                      /*tp_setattro*/
    0,                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,     /*tp_flags*/
    0,                      /*tp_doc*/
    0,                      /*tp_traverse*/
    0,                      /*tp_clear*/
    0,                      /*tp_richcompare*/
    0,                      /*tp_weaklistoffset*/
    0,                      /*tp_iter*/
    0,                      /*tp_iternext*/
    diasource_methods,      /*tp_methods*/
    0,                      /*tp_members*/
    diasource_getset,       /*tp_getset*/
    0,                      /*tp_base*/
    0,                      /*tp_dict*/
    0,                      /*tp_descr_get*/
    0,                      /*tp_descr_set*/
    0,                      /*tp_dictoffset*/
    0,                      /*tp_init*/
    0,                      /*tp_alloc*/
    diasource_new,                      /*tp_new*/
    0,                      /*tp_free*/
    0,                      /*tp_is_gc*/
};

static PyObject*
newdiasource()
{
    struct diasource *rv;
    HRESULT hr;

    rv = PyObject_New(diasource, &diasource_type);
    if (rv == NULL)
    	return NULL;

    // Create main DIA object
    hr = CoCreateInstance(__uuidof(DiaSource), NULL, CLSCTX_INPROC_SERVER, 
    	__uuidof(IDiaDataSource), (LPVOID*)&rv->obj);
    if (hr != S_OK) {
    	PyErr_Format(PyExc_ValueError, "CoCreateInstance failed with HRESULT 0x%x\n", hr);
    	PyObject_Del(rv);
    	return NULL;
    }
    return (PyObject *)rv;
}

static PyMethodDef dia_methods[] = {
    {NULL,		NULL}		/* sentinel */
};

PyMODINIT_FUNC
initdia(void)
{
    PyObject *m;
    CoInitialize(NULL);
    m = Py_InitModule3("dia", dia_methods, "");
    if (PyType_Ready(&diasource_type) < 0)
    	return;
    PyModule_AddObject(m, "DataSource", (PyObject *)&diasource_type);

#define aic(s) PyModule_AddIntConstant(m, #s, s)
    aic(SymTagNull);
    aic(SymTagExe);
    aic(SymTagCompiland);
    aic(SymTagCompilandDetails);
    aic(SymTagCompilandEnv);
    aic(SymTagFunction);
    aic(SymTagBlock);
    aic(SymTagData);
    aic(SymTagAnnotation);
    aic(SymTagLabel);
    aic(SymTagPublicSymbol);
    aic(SymTagUDT);
    aic(SymTagEnum);
    aic(SymTagFunctionType);
    aic(SymTagPointerType);
    aic(SymTagArrayType);
    aic(SymTagBaseType);
    aic(SymTagTypedef);
    aic(SymTagBaseClass);
    aic(SymTagFriend);
    aic(SymTagFunctionArgType);
    aic(SymTagFuncDebugStart);
    aic(SymTagFuncDebugEnd);
    aic(SymTagUsingNamespace);
    aic(SymTagVTableShape);
    aic(SymTagVTable);
    aic(SymTagCustom);
    aic(SymTagThunk);
    aic(SymTagCustomType);
    aic(SymTagManagedType);
    aic(SymTagDimension);

    aic(LocIsNull);
    aic(LocIsStatic);
    aic(LocIsTLS);
    aic(LocIsRegRel);
    aic(LocIsThisRel);
    aic(LocIsEnregistered);
    aic(LocIsBitField);
    aic(LocIsSlot);
    aic(LocIsIlRel);
    aic(LocInMetaData);
    aic(LocIsConstant);
    aic(LocTypeMax);

    aic(DataIsUnknown);
    aic(DataIsLocal);
    aic(DataIsStaticLocal);
    aic(DataIsParam);
    aic(DataIsObjectPtr);
    aic(DataIsFileStatic);
    aic(DataIsGlobal);
    aic(DataIsMember);
    aic(DataIsStaticMember);
    aic(DataIsConstant);

    aic(UdtStruct);
    aic(UdtClass);
    aic(UdtUnion);
	
    aic(btNoType);
    aic(btVoid);
    aic(btChar);
    aic(btWChar);
    aic(btInt);
    aic(btUInt);
    aic(btFloat);
    aic(btBCD);
    aic(btBool);
    aic(btLong);
    aic(btULong);
    aic(btCurrency);
    aic(btDate);
    aic(btVariant);
    aic(btComplex);
    aic(btBit);
    aic(btBSTR);
    aic(btHresult);

    aic(nsNone);
    aic(nsfCaseSensitive);
    aic(nsfCaseInsensitive);
    aic(nsfFNameExt);
    aic(nsfRegularExpression);
    aic(nsfUndecoratedName);
    aic(nsCaseSensitive);
    aic(nsCaseInsensitive);
    aic(nsFNameExt);
    aic(nsRegularExpression);
    aic(nsCaseInRegularExpression);
}
