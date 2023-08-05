/* $Id: annodexmodule.c,v 1.2 2003/11/15 07:40:17 benjl Exp $
 *
 * python interface to libannodex (the mpeg audio decoder library)
 *
 * Copyright (c) 2006 Ben Leslie
 *
 * This program is free software, you may copy and/or modify as per
 * the GNU General Public License (version 2, or at your discretion,
 * any later version).  This is the same license as libannodex.
 */


/*

Stuff to implement:
anx_core.h:
  parse_time
  anx_list functions

anx_general.h
  error handling -> exceptions
  !! anx_open/openfd/new
  flush
  destroy
  ready
  eos
  {set|get}_head
  anx_tell
  anx_seek_id
  anx_{get|set}_timebase
  anx_tell_time
  anx_seek_time
  anx_get_track_list
  Track:
    anx_get_content_type
    anx_get_nr_headers
    anx_get_granule_rate
  anx_snprint_{head|clip}
  anx_{head|clip|meta|desc}_{free|clone}

anx_import.h
  < not needed >

anx_read.h
  callbacks: read_stream, read_track, read_head, read_clip, read_media
  anx_read | anx_reader_input

anx_write.h


*/

#include <Python.h>
#include <annodex/annodex.h>

#include "pyannodex.h"

static PyObject * py_annodex_init_importers(PyObject * self, PyObject * args);

PyObject *annodex_error = NULL;

static PyMethodDef annodex_methods[] = {
	{ "init_importers", py_annodex_init_importers, METH_VARARGS, ""},
	{ NULL, 0, 0, NULL }
};

/* this handy tool for passing C constants to Python-land from
 * http://starship.python.net/crew/arcege/extwriting/pyext.html
 */
//#define PY_CONST(x) PyDict_SetItemString(dict, #x, PyInt_FromLong(MAD_##x))

PyObject *anxtypes_dict;

void
init_annodex(void)
{
	PyObject *module, *dict;
	PyObject *anxtypes_module;

	module = Py_InitModule("_annodex", annodex_methods);

	/* Get the a reference to anx_types */
	anxtypes_module = PyImport_AddModule("annodex.anx_types");
        anxtypes_dict = PyModule_GetDict(anxtypes_module);
	Py_INCREF(anxtypes_dict);

	/* Setup the Anx type */
	if (PyType_Ready(&PyAnxType) < 0)
		return;
	Py_INCREF(&PyAnxType);
	PyModule_AddObject(module, "Anx", (PyObject *)&PyAnxType);

	dict = PyModule_GetDict(module);
	
	PyDict_SetItemString(dict, "__version__",
			     PyString_FromString(VERSION));

	/* Create stuff */
	annodex_error = PyErr_NewException("annodex.error", NULL, NULL);
	PyDict_SetItemString(dict, "error", annodex_error);

	if (PyErr_Occurred())
		PyErr_SetString(PyExc_ImportError, "annodex: init failed");
}

PyObject *
py_annodex_init_importers(PyObject * self, PyObject * args)
{

	char *mime_string;

	if (PyArg_ParseTuple(args, "s", &mime_string)) {
		anx_init_importers(mime_string);
		Py_INCREF(Py_None);
		return Py_None;
	} else {
		return NULL;
	}
}
