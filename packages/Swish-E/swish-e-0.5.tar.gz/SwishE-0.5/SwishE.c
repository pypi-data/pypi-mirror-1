/* $Id: SwishE.c,v 1.4 2005/08/18 11:33:48 jibe Exp jibe $ */

/* Adaptations for Python 2.1 & Debian GNU/Linux by Gianluigi Tiesi
 * Code cleanup, fixes and the "query" function by Jean-François Piéronne 
 */

/*
 * Copyright (c) 2003, 2005 JB Robertson
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 * THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */


#include <Python.h>
#include <swish-e.h>

/* python 2.1 compatibility */
#ifndef METH_NOARGS
#define METH_NOARGS   0x0004
#endif

#define VERSION "0.5"

#define MSW_ERROR(sw_handle)						\
      if (SwishError(sw_handle)) {					\
          PyErr_SetString(SwishE_Error, SwishErrorString(sw_handle));	\
          return NULL;							\
      }

/* types defined here */
staticforward PyTypeObject HANDLETYPE;
staticforward PyTypeObject SEARCHTYPE;
staticforward PyTypeObject RESULTSTYPE;
staticforward PyTypeObject RESULTTYPE;

/* exception we use to raise when things happen */
static PyObject *SwishE_Error;

/* the handle object has just a SW_HANDLE */
typedef struct {
    PyObject_HEAD
    SW_HANDLE sw_handle;
} HANDLEOBJECT;

/* we need to keep a reference to a HANDLEOBJECT and Py_INCREF and DECREF
 * it, otherwise weird things happen 
 */
 
typedef struct {
    PyObject_HEAD
    SW_SEARCH sw_search;
    PyObject *handle;
} SEARCHOBJECT;

/* same, keep a ref to a SEARCHOBJECT and HANDLEOBJECT */
typedef struct {
    PyObject_HEAD
    SW_RESULTS sw_results;
    PyObject *handle;
    PyObject *search;
} RESULTSOBJECT;

/* same, keep a ref to a RESULTSOBJECT */
typedef struct {
    PyObject_HEAD
    SW_RESULT sw_result;
    PyObject *handle;
    PyObject *results;
} RESULTOBJECT;


static SEARCHOBJECT* search_new(HANDLEOBJECT*, char*);
static RESULTSOBJECT* results_new(SEARCHOBJECT*, char*);
static RESULTOBJECT* result_new(RESULTSOBJECT*, SW_RESULT, HANDLEOBJECT*);

/*                         utilities                                    */

/* that's to decode Swish-e header values, shamelessly inspired from
 * `decode_header_value' from perl/API.xs in the distribution. 
 */
 
static PyObject*
decode_header_value(SWISH_HEADER_VALUE *header_value, 
                    SWISH_HEADER_TYPE header_type)
{
   PyObject *result;
   char **idx;
   switch( header_type) {
      case SWISH_STRING:
         if ( header_value->string && header_value->string[0] ) {
            result = PyString_FromString((char *)header_value->string);
         } else {
            Py_INCREF(Py_None);
            result = Py_None;
         }   
         break;
      case SWISH_NUMBER: /* TODO: check this*/
         result = PyInt_FromLong(header_value->number);
         break;
      case SWISH_BOOL:
         result = PyInt_FromLong(header_value->boolean ? 1 : 0);
         break;
      case SWISH_LIST: 
         result =  PyList_New(0);
         idx = (char**) header_value->string_list;
         while( *idx != NULL ) {
            if( 0 != PyList_Append(result, PyString_FromString(*idx)) ) {
               PyErr_SetString(SwishE_Error, "Can't append to list.." );
               return NULL;
            }
            idx++;
         }
         break;
      default: /* including SWISH_HEADER_ERROR - TODO: this should change */
         result = NULL;   
   }
   return result;       
}  

/*              methods related to the Handle object                        */

static PyObject*
handle_new(PyObject* self, PyObject* args)
{
   HANDLEOBJECT* sw;
   char *flist;
   SW_HANDLE sw_handle;
   
   if (!PyArg_ParseTuple(args,"s", &flist)) 
      return NULL;

   /* init the swish handle */

   SwishErrorsToStderr();
   sw_handle = SwishInit(flist);
   MSW_ERROR(sw_handle);
   
   /* alloc the python object, etc.*/
   sw = PyObject_New(HANDLEOBJECT, &HANDLETYPE);
   sw->sw_handle = sw_handle;

   return (PyObject*)sw;
}

static void
handle_dellaoc(PyObject* self)
{
   SW_HANDLE sw_handle = ((HANDLEOBJECT*)self)->sw_handle;
   SwishClose(sw_handle);
   PyObject_Del(self);
}

static PyObject*
handle_search(PyObject* self, PyObject* args)
{
   char *query;
   
   if (!PyArg_ParseTuple(args,"s", &query)) 
      return NULL;
   
   return (PyObject*)search_new((HANDLEOBJECT*)self, query);
}

static PyObject*
handle_query(PyObject* self, PyObject* args)
{
   char *query;
   SW_RESULTS sw_results;
   RESULTSOBJECT *resultsobj;
   HANDLEOBJECT* handleobj = (HANDLEOBJECT*)self;
   SW_HANDLE sw_handle = handleobj->sw_handle;
   
   if (!PyArg_ParseTuple(args,"s", &query)) 
      return NULL;
   
   sw_results = SwishQuery(sw_handle, query);
   MSW_ERROR(sw_handle);

   resultsobj= PyObject_New(RESULTSOBJECT, &RESULTSTYPE);
   resultsobj->sw_results = sw_results;
   resultsobj->search = NULL;
   resultsobj->handle = (PyObject*)handleobj;
   
   Py_INCREF(handleobj);

   return (PyObject *)resultsobj;
}

static PyObject*
handle_headerNames(PyObject* self)
{
   PyObject *list;
   char **idx;
   SW_HANDLE sw_handle = ((HANDLEOBJECT*)self)->sw_handle;

   char **header_names = (char**) SwishHeaderNames(sw_handle);
   MSW_ERROR(sw_handle);

   if( NULL == (list = PyList_New(0))) {
      PyErr_SetString(SwishE_Error, "Error while allocating the list" );
      return NULL;
   }
   
   idx = header_names;
   while( *idx != NULL ) {
      if( 0 != PyList_Append(list, PyString_FromString(*idx)) ) {
         PyErr_SetString(SwishE_Error, "Can't append to list.." );
         return NULL;
      }
      idx++;
   }
   
   return list;
}

static PyObject*
handle_indexNames(PyObject* self)
{
   PyObject *list;
   char **idx;
   SW_HANDLE sw_handle = ((HANDLEOBJECT*)self)->sw_handle;

   char **index_names =(char**) SwishIndexNames(sw_handle); 
   MSW_ERROR(sw_handle);   
   
   if( NULL == (list = PyList_New(0))) {
      PyErr_SetString(SwishE_Error, "Error while allocating the list" );
      return NULL;
   }
   
   idx = index_names;
   while( *idx != NULL ) {
      if( 0 != PyList_Append(list, PyString_FromString(*idx)) ) {
         PyErr_SetString(SwishE_Error, "Can't append to list.." );
         return NULL;
      }
      idx++;
   }
   
   return list;
}                         

static PyObject*
handle_headerValue(PyObject* self, PyObject* args)
{
   /* debug with swish-e -f t/swish.conf -w madrid -H 2 */
   char *index_name, *header_name;
   SWISH_HEADER_TYPE header_type;
   SWISH_HEADER_VALUE header_value;
   SW_HANDLE sw_handle = ((HANDLEOBJECT*)self)->sw_handle;
   
   if (!PyArg_ParseTuple(args,"ss", &index_name, &header_name)) 
      return NULL;   
   
   header_value = SwishHeaderValue(sw_handle, index_name, 
                                   header_name, &header_type);
   MSW_ERROR(sw_handle)

   return decode_header_value(&header_value, header_type);
}

static PyObject*
handle_metalist(PyObject* self, PyObject* args)
{
   PyObject *list;
   SWISH_META_LIST meta_names;
   SWISH_META_LIST idx;
   SW_HANDLE sw_handle = ((HANDLEOBJECT*)self)->sw_handle;
   char *index_name;

   if (!PyArg_ParseTuple(args,"s", &index_name))
      return NULL;

   meta_names = SwishMetaList(sw_handle, index_name); 
   MSW_ERROR(sw_handle)
   
   if( NULL == (list = PyList_New(0))) {
      PyErr_SetString(SwishE_Error, "Error while allocating the list" );
      return NULL;
   }
   
   idx = meta_names;
   while( *idx ) {
      const char *name = SwishMetaName((SW_META)*idx);
      if( 0 != PyList_Append(list, PyString_FromString(name))) {
         PyErr_SetString(SwishE_Error, "Can't append to list.." );
         return NULL;
      }
      idx++;
   }
   
   return list;
}        


static PyMethodDef handle_methods[] = {
   {"search", (PyCFunction)handle_search, METH_VARARGS, 
    "Return a search object."},
   {"headerNames", (PyCFunction)handle_headerNames, METH_NOARGS, 
    "Return a list of the header names."},
   {"indexNames", (PyCFunction)handle_indexNames, METH_NOARGS, 
    "Return a list of the index names."},
   {"headerValue", (PyCFunction)handle_headerValue, METH_VARARGS, 
    "Fetches the header value for the given index file, and the header name."},
   {"metaList", (PyCFunction)handle_metalist, METH_VARARGS, 
    "Returns the list of meta entries for the given index file."}, 
   {"query", (PyCFunction)handle_query, METH_VARARGS, 
    "Return a result object."},
   {NULL, NULL, 0, NULL}           /* sentinel */
};

static PyObject *
handle_getattr(PyObject *obj, char *name)
{
   return Py_FindMethod(handle_methods, (PyObject *)obj, name);
}

static PyTypeObject HANDLETYPE = {
    PyObject_HEAD_INIT(NULL)
    0,
    "Handle",
    sizeof(HANDLEOBJECT),
    0,
    handle_dellaoc, /*tp_dealloc*/
    0,          /*tp_print*/
    handle_getattr,          /*tp_getattr*/
    0,          /*tp_setattr*/
    0,          /*tp_compare*/
    0,          /*tp_repr*/
    0,          /*tp_as_number*/
    0,          /*tp_as_sequence*/
    0,          /*tp_as_mapping*/
    0,          /*tp_hash */
};

/*                  methods related to the search object                    */

static SEARCHOBJECT*
search_new(HANDLEOBJECT* handleobj, char* query) 
{
   SEARCHOBJECT *searchobj;

   SW_SEARCH sw_search = New_Search_Object(handleobj->sw_handle, query);
   MSW_ERROR(handleobj->sw_handle);
      
   searchobj = PyObject_New(SEARCHOBJECT, &SEARCHTYPE);
   searchobj->sw_search = sw_search;
   searchobj->handle = (PyObject*)handleobj;
   Py_INCREF(handleobj);
   return searchobj;
}

static void
search_dellaoc(PyObject* self)
{
   SW_SEARCH sw_search = ((SEARCHOBJECT*)self)->sw_search;
   Free_Search_Object(sw_search);
   Py_DECREF( ((SEARCHOBJECT*)self)->handle);
   PyObject_Del(self);
}

static PyObject*
search_execute(PyObject* self, PyObject* args)
{
   char *query;
      
   if (!PyArg_ParseTuple(args,"s", &query)) 
      return NULL;
      
   return (PyObject*)results_new((SEARCHOBJECT*)self, query);
}

static PyObject*
search_setSort(PyObject* self, PyObject* args)
{
   char *str;
   SW_SEARCH sw_search = ((SEARCHOBJECT*)self)->sw_search;
   SW_HANDLE sw_handle = ((HANDLEOBJECT*)((SEARCHOBJECT*)self)->handle)->sw_handle;
      
   if (!PyArg_ParseTuple(args,"s", &str)) 
      return NULL;
   
   SwishSetSort(sw_search, str);
   MSW_ERROR(sw_handle)
   
   Py_INCREF(Py_None);   
   return Py_None;
}

static PyObject*
search_setPhraseDelimiter(PyObject* self, PyObject* args)
{
   char *delimiter;
   SW_SEARCH sw_search = ((SEARCHOBJECT*)self)->sw_search;
   SW_HANDLE sw_handle = ((HANDLEOBJECT*)((SEARCHOBJECT*)self)->handle)->sw_handle;
      
   if (!PyArg_ParseTuple(args,"c", &delimiter)) 
      return NULL;
      
   SwishPhraseDelimiter(sw_search, delimiter[0]);
   MSW_ERROR(sw_handle)
   
   Py_INCREF(Py_None);   
   return Py_None;
}

static PyObject*
search_setStructure(PyObject* self, PyObject* args)
{
   int structure;
   SW_SEARCH sw_search = ((SEARCHOBJECT*)self)->sw_search;
   SW_HANDLE sw_handle = ((HANDLEOBJECT*)((SEARCHOBJECT*)self)->handle)->sw_handle;
      
   if (!PyArg_ParseTuple(args,"i", &structure)) 
      return NULL;
      
   SwishSetStructure(sw_search, structure);
   MSW_ERROR(sw_handle)
   
   Py_INCREF(Py_None);   
   return Py_None;
}
 
static PyMethodDef search_methods[] = {
   {"execute", (PyCFunction)search_execute, METH_VARARGS, 
    "Run a search object."},
   {"setSort", (PyCFunction)search_setSort, METH_VARARGS, 
    "Sets the sort order of the results."},
   {"setPhraseDelimiter", (PyCFunction)search_setPhraseDelimiter, METH_VARARGS,
    "Sets the phrase delimiter character. The default is double-quotes."},
   {"setStructure", (PyCFunction)search_setStructure, METH_VARARGS, 
    "Sets the ``structure'' flag in the search object."},
    {NULL, NULL, 0, NULL}           /* sentinel */
};

static PyObject *
search_getattr(PyObject *obj, char *name)
{
   return Py_FindMethod(search_methods, (PyObject *)obj, name);
}

static PyTypeObject SEARCHTYPE = {
    PyObject_HEAD_INIT(NULL)
    0,
    "Search",
    sizeof(SEARCHOBJECT),
    0,
    search_dellaoc, /*tp_dealloc*/
    0,          /*tp_print*/
    search_getattr,          /*tp_getattr*/
    0,          /*tp_setattr*/
    0,          /*tp_compare*/
    0,          /*tp_repr*/
    0,          /*tp_as_number*/
    0,          /*tp_as_sequence*/
    0,          /*tp_as_mapping*/
    0,          /*tp_hash */
};

/*                methods related to the results objects                     */

static RESULTSOBJECT*
results_new(SEARCHOBJECT* searchobj, char* query)
{
   SW_RESULTS sw_results;
   RESULTSOBJECT *resultsobj;
   HANDLEOBJECT *handleobj = (HANDLEOBJECT *)(searchobj->handle);
   SW_HANDLE sw_handle = handleobj->sw_handle;
   
   sw_results = SwishExecute(searchobj->sw_search, query);
   MSW_ERROR(sw_handle)
   
   resultsobj= PyObject_New(RESULTSOBJECT, &RESULTSTYPE);
   resultsobj->sw_results = sw_results;
   resultsobj->search = (PyObject*)searchobj;
   resultsobj->handle = (PyObject*)handleobj;
   
   Py_INCREF(searchobj);
   Py_INCREF(handleobj);
   return resultsobj;
}

static void
results_dellaoc(PyObject* self)
{ 
   Free_Results_Object(((RESULTSOBJECT*)self)->sw_results);
   if (((RESULTSOBJECT*)self)->search) Py_DECREF(((RESULTSOBJECT*)self)->search);
   Py_DECREF((PyObject *)((RESULTSOBJECT*)self)->handle);
   PyObject_Del(self);
}

static PyObject*
results_hits(PyObject* self)
{  
   int nb;
   SW_RESULTS sw_results = ((RESULTSOBJECT *)self)->sw_results;
   SW_HANDLE sw_handle = ((HANDLEOBJECT *)((RESULTSOBJECT *)self)->handle)->sw_handle;
   
   nb = SwishHits(sw_results);
   MSW_ERROR(sw_handle)

   return Py_BuildValue("i", nb);
}

static PyObject*
results_nextresult(PyObject* self)
{
   SW_RESULTS sw_results = ((RESULTSOBJECT *)self)->sw_results;
   SW_RESULT sw_result = SwishNextResult(sw_results);
   HANDLEOBJECT* handleobj = (HANDLEOBJECT*)((RESULTSOBJECT *)self)->handle;

   SW_HANDLE sw_handle = handleobj->sw_handle;
   MSW_ERROR(sw_handle)
   
   if( sw_result == NULL) {
#if PY_MINOR_VERSION > 1
      PyErr_SetString(PyExc_StopIteration, "No more results");
#else
      PyErr_SetString(SwishE_Error, "No more results");
#endif
      return NULL;     
   }
   
   return (PyObject*)result_new((RESULTSOBJECT*)self, sw_result, handleobj);
}

#if PY_MINOR_VERSION > 1
static PyObject*
results_iter(PyObject* self)
{
   Py_INCREF(self);  
   return self;
}
#endif

static PyObject*
results_seek(PyObject* self, PyObject* args)
{
   int i;
   SW_RESULTS sw_results = ((RESULTSOBJECT*)self)->sw_results;
   SW_HANDLE sw_handle = ((HANDLEOBJECT *)((RESULTSOBJECT *)self)->handle)->sw_handle;
   
   if (!PyArg_ParseTuple(args,"i", &i)) 
      return NULL;
   
   SwishSeekResult(sw_results, i);
   MSW_ERROR(sw_handle)
   
   Py_INCREF(Py_None);
   return Py_None;
}

static PyMethodDef results_methods[] = {
   {"hits", (PyCFunction)results_hits, METH_NOARGS, 
    "Return the number of hits in a result"},
   {"next", (PyCFunction)results_nextresult, METH_NOARGS, 
    "Return the next result, also used to implement the iterator protocol."},
   {"seek", (PyCFunction)results_seek, METH_VARARGS, 
    "Seek in the list of result objects"},
   {NULL, NULL, 0, NULL}           /* sentinel */
};

static PyObject *
results_getattr(PyObject *obj, char *name)
{
   return Py_FindMethod(results_methods, (PyObject *)obj, name);
}

static PyTypeObject RESULTSTYPE = {
    PyObject_HEAD_INIT(NULL)
    0,
    "Results",
    sizeof(RESULTSOBJECT),
    0,
    results_dellaoc, /*tp_dealloc*/
    0,          /*tp_print*/
    results_getattr,          /*tp_getattr*/
    0,          /*tp_setattr*/
    0,          /*tp_compare*/
    0,          /*tp_repr*/
    0,          /*tp_as_number*/
    0,          /*tp_as_sequence*/
    0,          /*tp_as_mapping*/
    0,          /*tp_hash */
	0,			/* tp_call */
	0,			/* tp_str */
	0,		    /* tp_getattro */
	0,		    /* tp_setattro */
	0,			/* tp_as_buffer */
#if PY_MINOR_VERSION > 1
	Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_ITER,/* tp_flags */
#else
	Py_TPFLAGS_DEFAULT,/* tp_flags */
#endif
	0,			/* tp_doc */
	0,		    /* tp_traverse */
 	0,			/* tp_clear */
	0,			/* tp_richcompare */
	0,			/* tp_weaklistoffset */
#if PY_MINOR_VERSION > 1
	results_iter,					/* tp_iter */
	results_nextresult,				/* tp_iternext */
	0,			/* tp_methods */
	0,			/* tp_members */
	0,			/* tp_getset */
	0,			/* tp_base */
	0,			/* tp_dict */
	0,			/* tp_descr_get */
	0,			/* tp_descr_set */
	0,			/* tp_dictoffset */
	0,			/* tp_init */
	0,			/* tp_alloc */
	0,			/* tp_new */
#endif
};


/*                methods related to the results objects                     */

static RESULTOBJECT*
result_new(RESULTSOBJECT* resultSobj, SW_RESULT res, HANDLEOBJECT* handleobj)
{
   RESULTOBJECT* resultobj;
   resultobj = PyObject_New(RESULTOBJECT, &RESULTTYPE);
   resultobj->sw_result = res;
   resultobj->handle = (PyObject*) handleobj;
   resultobj->results = (PyObject*) resultSobj;
   Py_INCREF(resultSobj);
   Py_INCREF(handleobj);
   return resultobj;
}

static void
result_dellaoc(PyObject* self)
{ 
   /* SW_RESULT does not need to be freed */
   Py_DECREF(((RESULTOBJECT*)self)->results);
   Py_DECREF(((RESULTOBJECT*)self)->handle);
   PyObject_Del(self);
}

static PyObject*
result_getproperty(PyObject* self, PyObject* args)
{  
   /* TODO: have a closer look here about (null) and ulong */
   char *key; 
   PropValue *val;
   PyObject *objval = NULL;
   
   if (!PyArg_ParseTuple(args,"s", &key)) 
      return NULL;
      
   if((val = getResultPropValue(((RESULTOBJECT*)self)->sw_result, key, 0))
         == NULL) {
      PyErr_SetString(SwishE_Error,
                      "property name is not defined in the index");
      return NULL;
   }
   
   switch (val->datatype) {
      case PROP_INTEGER:
         objval = Py_BuildValue("i", val->value.v_int);
         break;
      case PROP_ULONG:
         objval = Py_BuildValue("i", val->value.v_ulong);
         break;
       case PROP_STRING:
         objval = Py_BuildValue("s", val->value.v_str);
         break;
      case PROP_DATE:
         objval = Py_BuildValue("i", val->value.v_date);
         break;         
      default:
         freeResultPropValue(val);
         PyErr_SetString(SwishE_Error,"unknown data type");
         return NULL;
   }   
   
   freeResultPropValue(val);
   return objval;
}

static PyObject*
result_indexValue(PyObject* self, PyObject* args)
{
   /* debug with swish-e -f t/swish.conf -w madrid -H 2 */
   char *header_name;
   SWISH_HEADER_TYPE header_type;
   SWISH_HEADER_VALUE header_value;
   SW_RESULT sw_result = ((RESULTOBJECT*)self)->sw_result;
   SW_HANDLE sw_handle = ((HANDLEOBJECT*)((RESULTOBJECT*)self)->handle)->sw_handle;
   
   if (!PyArg_ParseTuple(args,"s", &header_name)) 
      return NULL;   
      
   header_value = SwishResultIndexValue(sw_result, header_name, &header_type);
   MSW_ERROR(sw_handle)

   return decode_header_value(&header_value, header_type);
}

static PyObject*
result_metalist(PyObject* self)
{
   PyObject *list;
   SWISH_META_LIST meta_names;
   SWISH_META_LIST idx;
   SW_RESULT sw_result = ((RESULTOBJECT*)self)->sw_result;
   SW_HANDLE sw_handle = ((HANDLEOBJECT*)((RESULTOBJECT*)self)->handle)->sw_handle;

   meta_names = SwishResultMetaList(sw_result); 
   MSW_ERROR(sw_handle);
   
   if( NULL == (list = PyList_New(0))) {
      PyErr_SetString(SwishE_Error, "Error while allocating the list" );
      return NULL;
   }
   
   idx = meta_names;
   while( *idx ) {
      const char *name = SwishMetaName(*idx);
      /* I don't think there's anything we can do with the ID and the type
         of the meta thingy, so let's not return them.
         int id = SwishMetaID((SW_META)*idx);
         int type = SwishMetaType((SW_META)*idx);*/

      if( 0 != PyList_Append(list, PyString_FromString(name))) {
         PyErr_SetString(SwishE_Error, "Can't append to list.." );
         return NULL;
      }
      idx++;
   }
   
   return list;
}      

static PyMethodDef result_methods[] = {
   {"getproperty", (PyCFunction)result_getproperty, METH_VARARGS, 
    "Return a property of the result"},
   {"metaList", (PyCFunction)result_metalist, METH_VARARGS, 
    "Returns the list of meta entries for the given result."},
   {"indexValue", (PyCFunction)result_indexValue, METH_VARARGS, 
    "Fetches the header value for the given result and the header name"}, 
   {NULL, NULL, 0, NULL}           /* sentinel */
};

static PyObject *
result_getattr(PyObject *obj, char *name)
{
   return Py_FindMethod(result_methods, (PyObject *)obj, name);
}

static PyTypeObject RESULTTYPE = {
    PyObject_HEAD_INIT(NULL)
    0,
    "Result",
    sizeof(RESULTOBJECT),
    0,
    result_dellaoc, /*tp_dealloc*/
    0,          /*tp_print*/
    result_getattr,          /*tp_getattr*/
    0,          /*tp_setattr*/
    0,          /*tp_compare*/
    0,          /*tp_repr*/
    0,          /*tp_as_number*/
    0,          /*tp_as_sequence*/
    0,          /*tp_as_mapping*/
    0,          /*tp_hash */
};
 
static PyMethodDef SwishE_methods[] = {
    {"new", handle_new, METH_VARARGS, 
     "Create a new SwishE object. The argument is a string\n"
     "containing the list of index files to open. Something\n"
     "like 'f1.index foobar/boo.idx /tmp/myindex'." },
    {NULL, NULL, 0, NULL}
};

static char* module_doc = 
"An SWISH-E interface for Python\n\n"
"Not too much documentation so far, please see the examples in\n"
"the 'examples/' directory of the source distribution for more\n"
"information.\n\n"
"   All function may raise a SwishE.error exception.\n"
"\n"
"   h = new('swish.idx tmp/bleh.idx')\n"
"      returns a new Handle object\n\n"
"   h.headerNames()\n"
"      returns the list of possible header names. This list\n"
"      is the same for all index files of a given version of Swish-e.\n"
"   h.headerValue()\n"
"      fetches the header value for the given index file,\n"
"      and the header name.\n"
"   h.indexValue()\n"
"      returns a list of index files opened. This is just the\n"
"      list of index files specified in the new() call\n"
"   r = h.query(' .. a query ..')\n"
"      query the databases and put the results in r\n"
"   s = h.search('')\n"
"      returns a new search object.\n"
"\n"
"   r.setSort( ... )\n"
"   r.setPhraseDelimiter( ... )\n"
"   r.setStructure( ... )\n"
"   r = s.execute(' .. a query ..')\n"
"      query the databases and put the results in r\n"
"   \n"
"   r.hits()\n"
"      returns the number of hits of the search.\n"
"   r.seek()\n"
"      seeks the results.\n"
"   r0 = r.next()\n"
"      returns the next result, may throw a StopIteration exception (as in\n"
"      the iterator protocol).\n"
"   r.__iter__()\n"
"      that's when you want to write 'for r0 in r', see the iterator protocol\n"
"      in the Python documentation.  Note that it returns self, so that if \n"
"      you put r.next() in the iteration, you'll end with a mess.\n"
"   \n"
"   r0.getProperty( ... )\n"
"      returns a property of the result. \n" 
"   r0.indexValue(name)\n"
"      return the index value 'name' for result r0\n" 
"\nExample:\n"
"--------\n"
"$ python\n"
"Python 2.2.3 (#1, Jul 15 2003, 15:44:20) \n"
"[GCC 2.95.3 20010125 (prerelease, propolice)] on openbsd3\n"
"Type \"help\", \"copyright\", \"credits\" or \"license\" for more information.\n"
">>> import SwishE\n"
">>> handle = SwishE.new('t/swish.idx')\n"
">>> search = handle.search('')\n"
">>> results = search.execute('madrid')\n"
">>> for r in results:\n"
"...    print r.getproperty('swishtitle')\n"
"... \n"
"Argentina Centro de Medios Independientes\n"
"Indymedia Barcelona: home\n"
"San Francisco Bay Area Independent Media Center\n"
"Independent Media Center -\n"
">>> again = search.execute('lluita')\n"
">>> for r in again:\n"
"...    print r.getproperty('swishdocpath')\n"
"... \n"
"1.html\n"
"";

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
initSwishE(void) 
{
   PyObject *m, *d, *doc, *version;
   HANDLETYPE.ob_type = &PyType_Type;
   SEARCHTYPE.ob_type = &PyType_Type;
   RESULTSTYPE.ob_type = &PyType_Type;
   m = Py_InitModule("SwishE", SwishE_methods);
   d = PyModule_GetDict(m);
   
   /* exception stuff */
   SwishE_Error = PyErr_NewException("SwishE.error", NULL, NULL);
   Py_INCREF(SwishE_Error);
   PyModule_AddObject(m, "error", SwishE_Error);
   
   doc = Py_BuildValue("s", module_doc);
   version = Py_BuildValue("s", VERSION);
   
   PyDict_SetItemString(d, "__doc__", doc);
   PyDict_SetItemString(d, "__version__", version);
}
