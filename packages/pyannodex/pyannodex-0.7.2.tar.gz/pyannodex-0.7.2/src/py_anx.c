/* $Id: py_anx.c,v 1.1 2003/11/23 23:50:40 andre Exp $
 *
 * python interface to libannodex
 *
 * Copyright (c) 2003-2006 Ben Leslie <benno@benno.id.au>
 *
 */

#include <Python.h>
#include <annodex/annodex.h>

#include "pyannodex.h"

struct py_anx {
	PyObject_HEAD
	ANNODEX *anx;
	int type;
	PyObject *file_obj;
	PyObject *stream_callback;
	PyObject *track_callback;
	PyObject *head_callback;
	PyObject *clip_callback;
	PyObject *raw_callback;

	PyObject *stream_callback_data;
	PyObject *track_callback_data;
	PyObject *head_callback_data;
	PyObject *clip_callback_data;
	PyObject *raw_callback_data;

	int exception_occurred;
}; /* Anx */

#define PY_ANX(x) ((struct py_anx *) x)

/* Forward declarations */
static PyObject * py_anx_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int py_anx_init(PyObject * self, PyObject * args, PyObject *kwds);
static PyObject * py_anx_getattr(PyObject * self, char * name);
static PyObject * py_anx_get_duration (PyObject * self);
static PyObject * py_anx_get_basetime (PyObject * self);
static PyObject * py_anx_get_presentation_time (PyObject * self);
static PyObject * py_anx_get_bitrate (PyObject * self);
static PyObject * py_anx_tell_time (PyObject * self);
static PyObject * py_anx_writer_import(PyObject * self, PyObject * args,
					   PyObject *kw);
static void py_anx_dealloc(PyObject * self, PyObject * args);
static PyObject * py_anx_insert_clip(PyObject * self, 
				    PyObject * args, PyObject *kw);
static PyObject * py_anx_write(PyObject *self, PyObject *args);
static PyObject * py_anx_read(PyObject *self, PyObject *args);
static PyObject * py_anx_set_read_stream_callback(PyObject *self, PyObject *args);
static PyObject * py_anx_set_read_track_callback(PyObject *self, PyObject *args);
static PyObject * py_anx_set_read_head_callback(PyObject *self, PyObject *args);
static PyObject * py_anx_set_read_clip_callback(PyObject *self, PyObject *args);
static PyObject * py_anx_set_read_raw_callback(PyObject *self, PyObject *args);
static PyObject * py_anx_get_track_list(PyObject *self, PyObject *args);

/* py_anx type */
PyTypeObject PyAnxType = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,
    "annodex.Anx",
    sizeof(struct py_anx),
    0,
    (destructor) py_anx_dealloc,
    (printfunc) 0,
    (getattrfunc) py_anx_getattr,
    (setattrfunc) 0,
    (cmpfunc) 0,
    (reprfunc) 0,
    0, /* as number */
    0, /* as sequence */
    0, /* as mapping */
    0, /* hash */
    0, /* binary */
    0, /* repr */
    0, /* getattro */
    0, /* setattro */
    0, /* as buffer */
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Anx objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    0,                         /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)py_anx_init,       /* tp_init */
    0,                         /* tp_alloc */
    py_anx_new,                 /* tp_new */
};

static PyMethodDef anx_methods[] = {
	{ "get_duration", (PyCFunction)py_anx_get_duration,
	  METH_VARARGS, "" },
	{ "get_bitrate", (PyCFunction)py_anx_get_bitrate,
	  METH_VARARGS, "" },
	{ "get_presentation_time", (PyCFunction)py_anx_get_presentation_time,
	  METH_VARARGS, "" },
	{ "get_basetime", (PyCFunction)py_anx_get_basetime,
	  METH_VARARGS, "" },
	{ "tell_time", (PyCFunction)py_anx_tell_time,
	  METH_VARARGS, "" },
	{ "writer_import", (PyCFunction)py_anx_writer_import, 
	  METH_VARARGS | METH_KEYWORDS, "" },
	{ "insert", (PyCFunction)py_anx_insert_clip, 
	  METH_VARARGS | METH_KEYWORDS, "" },
	{ "write", py_anx_write, METH_VARARGS, "" },
	{ "read", py_anx_read, METH_VARARGS, "" },
	{ "set_read_stream_callback", py_anx_set_read_stream_callback,
	  METH_VARARGS, "" },
	{ "set_read_track_callback", py_anx_set_read_track_callback,
	  METH_VARARGS, "" },
	{ "set_read_head_callback", py_anx_set_read_head_callback, 
	  METH_VARARGS, "" },
	{ "set_read_clip_callback", py_anx_set_read_clip_callback, 
	  METH_VARARGS, "" },
	{ "set_read_raw_callback", py_anx_set_read_raw_callback, 
	  METH_VARARGS, "" },
	{ "get_track_list", py_anx_get_track_list, METH_VARARGS, "" },
	{ NULL, 0, 0, NULL }
};

/* Generic function */
static int
anx_flags(char *flags)
{
	int anx_flags = ANX_READ;
	if (flags != NULL) {
		if (strchr(flags, 'r') != NULL) {
			anx_flags = ANX_READ;
		} 
		if (strchr(flags, 'w') != NULL) {
			anx_flags = ANX_WRITE;
		} 
	}
	return anx_flags;
}

static PyObject *
py_anx_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	struct py_anx *self;
	self = (struct py_anx *)type->tp_alloc(type, 0);
	if (self != NULL) {
		/* Initialise */
	}
	
	return (PyObject *)self;
}

int
py_anx_init(PyObject * self, PyObject * args, PyObject *kwds)
{
	struct py_anx * mf = PY_ANX(self);
	ANNODEX * anx = NULL;
	char *flags = NULL;
	PyObject *file_obj;
	char *filename = NULL;
	int fd;
	int type;

	static char *kwlist[] = {"file_obj", "mode", NULL};

	if (PyArg_ParseTupleAndKeywords(args, kwds, "i|s:Anx", kwlist,
			     &fd, &flags)) {
		/* FIXME: Do the mode correctly
		erro check correctly
		 */
		anx = anx_open_stdio(fdopen(fd, flags), anx_flags(flags));
		type = 0;
	} 
	else if (PyArg_ParseTupleAndKeywords(args, kwds, "s|s:Anx", kwlist,
				  &filename, &flags)) {
		PyErr_Clear();
		anx = anx_open(filename, anx_flags(flags));
		type = 0;
	} else if (PyArg_ParseTupleAndKeywords(args, kwds, "O|s:Anx", kwlist,
				    &file_obj, &flags)) {
		PyErr_Clear();
		anx = anx_new(anx_flags(flags));
		/*
		  We may want to check this now, or maybe later? 
		if (!PyObject_HasAttrString(fobject, "read")) {
			Py_DECREF(fobject);
			PyErr_SetString(PyExc_IOError, 
					"Object must have a read method");
			return NULL;
		}
		*/
		type = 1;
	} else {
		/* Raise an exception ?? */
		return -1;
	}
  
	if (anx == NULL) {
		/* Raise an exception ?? */
		return -1;
	}

	/* This means on callbacks user_data will be the python wrapper */
	/* anx_set_user_data(anx, mf); */

	mf->anx = anx;
	mf->type = type;

	mf->head_callback = NULL;


	if (type == 1) {
		Py_INCREF(file_obj);
		mf->file_obj = file_obj;
	} else {
		mf->file_obj = NULL;
	}

	return 0;
}

/* Destructor */
static void
py_anx_dealloc(PyObject * self, PyObject * args)
{
    if (PY_ANX(self)->anx) {
	    anx_close(PY_ANX(self)->anx);
	    /* Check it closed properly */
    }
    Py_XDECREF(PY_ANX(self)->file_obj);

    Py_XDECREF(PY_ANX(self)->stream_callback);
    Py_XDECREF(PY_ANX(self)->track_callback);
    Py_XDECREF(PY_ANX(self)->head_callback);
    Py_XDECREF(PY_ANX(self)->clip_callback);
    Py_XDECREF(PY_ANX(self)->raw_callback);

    Py_XDECREF(PY_ANX(self)->stream_callback_data);
    Py_XDECREF(PY_ANX(self)->track_callback_data);
    Py_XDECREF(PY_ANX(self)->head_callback_data);
    Py_XDECREF(PY_ANX(self)->clip_callback_data);

    PyObject_DEL(self);
}

static void *
get_string(PyObject *obj, char *key)
{
	PyObject *val;
	char *ret = NULL;
	val = PyMapping_GetItemString(obj, key);
	if (val == NULL) return NULL;
		
	if (PyString_Check(val)) {
		ret = PyString_AsString(val);
	}
	Py_DECREF(val);
	return ret;
}

static PyObject *
get_object(PyObject *obj, char *key)
{
	PyObject *val;
	val = PyObject_GetAttrString(obj, key);
	if (val == NULL) return NULL;
	return val;
}

static void
pyanchor_to_clip(PyObject *pyanchor, AnxClip *clip)
{
	PyObject *cdata;

	if (pyanchor == NULL) return;
	clip->anchor_id = get_string(pyanchor, "id");
	clip->anchor_lang = get_string(pyanchor, "lang");
	clip->anchor_dir = get_string(pyanchor, "dir");
	clip->anchor_class = get_string(pyanchor, "class");
	clip->anchor_href = get_string(pyanchor, "href");

	cdata = get_object (pyanchor, "cdata");
	if (PyString_Check(cdata)) {
		clip->anchor_text = PyString_AsString(cdata);
	}
	Py_DECREF(pyanchor);
}

static void
pyclip_to_clip(PyObject *pyclip, AnxClip *clip)
{
	/* Set the clip structure properly */
	clip->clip_id = get_string(pyclip, "id");
	clip->lang = get_string(pyclip, "lang");
	clip->dir = get_string(pyclip, "dir");
	clip->track = get_string(pyclip, "track");
	/* Anchor */
	pyanchor_to_clip(get_object(pyclip, "anchor"), clip);
	/* Img */

	/* Desc */

	/* Meta */
}


static PyObject *
py_anx_get_presentation_time (PyObject * self)
{
  double ret;

  ret = anx_get_presentation_time (PY_ANX(self)->anx);

  return PyFloat_FromDouble(ret);
}

static PyObject *
py_anx_get_basetime (PyObject * self)
{
  double ret;

  ret = anx_get_basetime (PY_ANX(self)->anx);

  return PyFloat_FromDouble(ret);
}

static PyObject *
py_anx_get_bitrate (PyObject * self)
{
  double ret;

  ret = anx_get_bitrate (PY_ANX(self)->anx);

  return PyFloat_FromDouble(ret);
}

/* Get duration */
static PyObject *
py_anx_get_duration (PyObject * self)
{
  double ret;

  ret = anx_get_duration (PY_ANX(self)->anx);

  return PyFloat_FromDouble(ret);
}

/* Tell time */
static PyObject *
py_anx_tell_time (PyObject * self)
{
  double ret;

  ret = anx_tell_time (PY_ANX(self)->anx);

  return PyFloat_FromDouble(ret);
}

/* Insert a clip */
PyObject * 
py_anx_insert_clip(PyObject * self, PyObject * args, PyObject *kw)
{
	PyObject *pyclip = NULL;
	double start = 0.0, stop = 0.0;
	int ret;
	
	static char *kwlist[] = {"clip",
				 "start", 
				 "stop", 
				 NULL};
	
	struct _AnxClip clip;

	memset(&clip, 0, sizeof(struct _AnxClip));
	
	if (! PyArg_ParseTupleAndKeywords(args, kw,
					  "Od|d", kwlist,
					  &pyclip,
					  &start, 
					  &stop)) {
		printf("Failed?!\n");
		return NULL;
	}
	
	pyclip_to_clip(pyclip, &clip);

	ret = anx_insert_clip(PY_ANX(self)->anx, start, &clip);

	if (ret != 0) {
		/* raise an exception here */
		printf("%d RAISE AN EXCEPTION! %d\n", __LINE__, ret);
	}
	
	if (stop != 0.0) {
		ret = anx_insert_clip(PY_ANX(self)->anx, stop, NULL);
		
		if (ret != 0) {
			/* raise an exception here */
			printf("%d RAISE AN EXCEPTION! %d\n", __LINE__, ret);
		}
	}
	Py_INCREF(Py_None);
	return Py_None;
}

/* Writer import */
static PyObject * 
py_anx_writer_import(PyObject *self, PyObject *args, PyObject *kw)
{
	char *filename = NULL, *id = NULL, *mime_type = NULL;
	double offset = 0, end = -1;
	int flags = 0, ret;
	static char *kwlist[] = {"filename", "id", "mime_type", 
				 "offset", "end", "flags", NULL};
	
	if (! PyArg_ParseTupleAndKeywords(args, kw, "s|ssddi", kwlist,
					  &filename, &id, &mime_type,
					  &offset, &end, &flags)) {
		printf("Failed?\n");
		return NULL;
	}

	ret = anx_write_import(PY_ANX(self)->anx, filename, id, mime_type,
				offset, end, flags);

	if (ret != 0) {
		/* raise an exception here */
		PyErr_SetString(annodex_error, anx_strerror(PY_ANX(self)->anx));
		return NULL;
	}

	Py_INCREF(Py_None);
	return Py_None;
}

static void *
get_address(PyObject *pybuf)
{
	void *buffer;
	int buffer_len;
	PyObject_AsWriteBuffer(pybuf, &buffer, &buffer_len);
	return buffer;
}

static PyObject * 
py_anx_write(PyObject *self, PyObject *args)
{
	int size, ret = 0;

	PyObject *pybuf = NULL;
	PyObject *write_res = NULL;
	if (PyArg_ParseTuple(args, "")) {
		size = -1;
	} else if (! PyArg_ParseTuple(args, "i", &size)) {
		return NULL;
	}

	if (PY_ANX(self)->type == 0) {
		if (size == -1) {
			do {
				ret = anx_write(PY_ANX(self)->anx, 1024);
			} while (ret > 0);
		} else {
			ret = anx_write(PY_ANX(self)->anx, size);
		}
		if (ret == -1) {
			PyErr_SetString(annodex_error, anx_strerror(PY_ANX(self)->anx));
			return NULL;
		}
	} else if (PY_ANX(self)->type == 1) {
		/* There should be a more effecient way to do this stuff 
		   but I don't know what it is */
		void *addr;
		pybuf = PyBuffer_New(size);
		addr = get_address(pybuf);
		ret = anx_write_output(PY_ANX(self)->anx, 
					addr, size);

		if (ret == -1) {
			/* raise an exception here */
			PyErr_SetString(annodex_error, anx_strerror(PY_ANX(self)->anx));
			return NULL;
		}
		if (ret < size) {
			pybuf = PyBuffer_FromObject(pybuf, 0, ret);
		}

		/* This bit works, however I'm not sure what I should be
		   checking with the write_res thing. I need to make sure
		   everything is written
		*/
		write_res = PyObject_CallMethod(PY_ANX(self)->file_obj,
						"write", "O", pybuf);
		if (write_res == NULL) {
			printf("An error occured?!\n");
			return NULL;
		}
	}

	return PyInt_FromLong(ret);
}

static PyObject * 
py_anx_read(PyObject *self, PyObject *args)
{
	int size, ret = 0;

	if (! PyArg_ParseTuple(args, "i", &size)) {
		return NULL;
	}

	if (PY_ANX(self)->type == 0) {
		PY_ANX(self)->exception_occurred = 0;
		ret = anx_read(PY_ANX(self)->anx, size);
		if (ret == -1) {
			/* raise an exception here */
			PyErr_SetString(annodex_error, anx_strerror(PY_ANX(self)->anx));
			return NULL;
		}
		if (PY_ANX(self)->exception_occurred == 1) {
			return NULL;
		}
	} else if (PY_ANX(self)->type == 1) {
		PyObject *o_read;
		void *buf;
		long n;
		/* It probably leaks here */
		o_read = PyObject_CallMethod(PY_ANX(self)->file_obj,
						"read", "i", size);
		PyObject_AsReadBuffer(o_read, &buf, &n);
		ret = anx_read_input(PY_ANX(self)->anx, buf, n);
	}
	return PyInt_FromLong(ret);
}

static PyObject *
py_new_anx_type(char *name)
{
	PyObject *cons, *new_obj;

        cons = PyDict_GetItemString(anxtypes_dict, name);
	new_obj = PyObject_CallObject(cons, NULL);
	
	return new_obj;
}

static void
py_set_dict(PyObject *dict, char *key, const char *value)
{
	PyObject *obj;

	if (value == NULL) {
		obj = Py_None;
	} else {
		obj = PyString_FromString(value);
	}

	PyMapping_SetItemString(dict, key, obj);
}

/*
 py_anxclip_pyobject:
   This function task an AnxClip pointer and returns a python object
*/
static PyObject *
py_anxclip_pyobject(const AnxClip *clip)
{
        PyObject *pClip = NULL, *pAnchor = NULL, *pImg = NULL, *pDesc = NULL;

	pClip = py_new_anx_type("Clip");

	py_set_dict(pClip, "id", clip->clip_id);
	py_set_dict(pClip, "lang", clip->lang);
	py_set_dict(pClip, "dir", clip->dir);
	py_set_dict(pClip, "track", clip->track);

	if (clip->anchor_href != NULL) {
	        pAnchor = py_new_anx_type("Anchor");
		PyObject_SetAttrString(pClip, "anchor", pAnchor);
		PyObject_SetAttrString(pAnchor, "cdata",
				       PyString_FromString(clip->anchor_text));
		py_set_dict(pAnchor, "id", clip->anchor_id);
		py_set_dict(pAnchor, "lang", clip->anchor_lang);
		py_set_dict(pAnchor, "dir", clip->anchor_dir);
		py_set_dict(pAnchor, "class", clip->anchor_class);
		py_set_dict(pAnchor, "href", clip->anchor_href);
	}

	if (clip->img_src != NULL) {
	        pImg = py_new_anx_type("Img");
		PyObject_SetAttrString(pClip, "img", pImg);
		py_set_dict(pImg, "id", clip->img_id);
		py_set_dict(pImg, "lang", clip->img_lang);
		py_set_dict(pImg, "dir", clip->img_dir);
		py_set_dict(pImg, "src", clip->img_src);
		py_set_dict(pImg, "alt", clip->img_alt);
	}

	if (clip->desc_text != NULL) {
		pDesc = py_new_anx_type("Desc");
		PyObject_SetAttrString(pClip, "desc", pDesc);
		PyObject_SetAttrString(pDesc, "cdata",
				       PyString_FromString(clip->desc_text));
		py_set_dict(pDesc, "id", clip->desc_id);
		py_set_dict(pDesc, "lang", clip->desc_lang);
		py_set_dict(pDesc, "dir", clip->desc_dir);
	}

	/* XXX: meta */

	return pClip;
}

static PyObject *
py_anxmeta_pyobject(const AnxMetaElement *meta)
{
	PyObject *pMeta = NULL;
	pMeta = py_new_anx_type("Meta");
	py_set_dict(pMeta, "id", meta->id);
	py_set_dict(pMeta, "lang", meta->lang);
	py_set_dict(pMeta, "dir", meta->dir);
	py_set_dict(pMeta, "name", meta->name);
	py_set_dict(pMeta, "content", meta->content);
	py_set_dict(pMeta, "scheme", meta->scheme);
	return pMeta;
}

/*
 py_anxhead_pyobject:
   This function takes an AnxHead pointer and returns a python object
*/
static PyObject *
py_anxhead_pyobject(const AnxHead *head)
{
	PyObject *pHead = NULL, *pTitle = NULL;
	PyObject *meta_list = PyList_New(0);
	AnxList * meta;

	pHead = py_new_anx_type("Head");

	py_set_dict(pHead, "id", head->head_id);
	py_set_dict(pHead, "lang", head->lang);
	py_set_dict(pHead, "dir", head->dir);
	/* FIXME: Where did lang go ?  py_set_dict(pHead, "dfltlang", head->defltlang); */
	py_set_dict(pHead, "profile", head->profile);

	if (head->title != NULL) {
		pTitle = py_new_anx_type("Title");
		PyObject_SetAttrString(pHead, "title", pTitle);
		PyObject_SetAttrString(pTitle, "cdata", 
				       PyString_FromString(head->title));
		py_set_dict(pTitle, "id", head->title_id);
		py_set_dict(pTitle, "lang", head->title_lang);
		py_set_dict(pTitle, "dir", head->title_dir);
	}

	/* XXX: base */

	/* meta */
	PyObject_SetAttrString(pHead, "meta", meta_list);
	for (meta = head->meta; meta != NULL; meta = meta->next) {
		PyObject *obj = 
			py_anxmeta_pyobject((AnxMetaElement *)(meta->data));
		PyList_Append(meta_list, obj);
	}

	return pHead;
}

/*
 py_anxhead_pyobject:
   This function takes an AnxHead pointer and returns a python object
*/
static PyObject *
py_anxtrack_pyobject(const AnxTrack *track)
{
	PyObject *pTrack = NULL;

	pTrack = py_new_anx_type("Track");

	py_set_dict(pTrack, "id", track->id);
	py_set_dict(pTrack, "content_type", track->content_type);
	PyMapping_SetItemString(pTrack, "serialno", PyInt_FromLong(track->serialno));
	PyMapping_SetItemString(pTrack, "nr_header_packets", PyLong_FromLong(track->nr_header_packets));
	PyMapping_SetItemString(pTrack, "granule_rate_n", PyLong_FromLongLong(track->granule_rate_n));
	PyMapping_SetItemString(pTrack, "granule_rate_d", PyLong_FromLongLong(track->granule_rate_d));
	PyMapping_SetItemString(pTrack, "basegranule", PyLong_FromLongLong(track->basegranule));
	PyMapping_SetItemString(pTrack, "preroll", PyInt_FromLong(track->preroll));
	PyMapping_SetItemString(pTrack, "granuleshift", PyInt_FromLong(track->granuleshift));

	return pTrack;
}

static int 
AnxReadStream_callback (ANNODEX * annodex, double timebase, char * utc, void * user_data)
{
	PyObject *ret;
	struct py_anx *py_anx = PY_ANX(user_data);
	if (py_anx->stream_callback_data) {
		ret = PyObject_CallFunction(py_anx->stream_callback, "OdzO",
					    (PyObject*)user_data,
					    timebase, utc,
					    py_anx->track_callback_data);
	} else {
		ret = PyObject_CallFunction(py_anx->stream_callback, "Odz",
					    (PyObject*) user_data,
					    timebase, utc);
	}

	if (ret == NULL) {
		py_anx->exception_occurred = 1;
		return ANX_STOP_ERR;
	} 

	return ANX_CONTINUE;
}

static int 
AnxReadTrack_callback (ANNODEX * annodex, long serialno,
			     char * id, char * content_type,
			     anx_int64_t granule_rate_n,
			     anx_int64_t granule_rate_d,
			     int nr_header_packets,
			     void * user_data)
{
	PyObject *ret;
	struct py_anx *py_anx = PY_ANX(user_data);
	if (py_anx->track_callback_data) {
		ret = PyObject_CallFunction(py_anx->track_callback, "OlssLLiO", 
					    (PyObject*)user_data,
					    serialno, id, content_type, granule_rate_n, 
					    granule_rate_d, nr_header_packets,
					    py_anx->track_callback_data);
	} else {
		ret = PyObject_CallFunction(py_anx->track_callback, "OlssLLi", 
					    (PyObject*) user_data,
					    serialno, id, content_type, granule_rate_n, 
					    granule_rate_d, nr_header_packets);
	}

	if (ret == NULL) {
		py_anx->exception_occurred = 1;
		return ANX_STOP_ERR;
	} 

	return ANX_CONTINUE;
}

/* This is the callback received from libannodex */
static int 
AnxReadHead_callback (ANNODEX * annodex, const AnxHead * head, void *user_data)
{
	struct py_anx *py_anx = PY_ANX(user_data);
	PyObject *py_head;
	PyObject *ret;

	py_head = py_anxhead_pyobject(head);

	if (py_anx->head_callback_data) {
		ret = PyObject_CallFunction(py_anx->head_callback, "OOO", 
					    (PyObject*) user_data,
					    py_head, py_anx->head_callback_data);
	} else {
		ret = PyObject_CallFunction(py_anx->head_callback, "OO", 
					    (PyObject*) user_data, py_head);
	}
	if (ret == NULL) {
		py_anx->exception_occurred = 1;
		return ANX_STOP_ERR;
	}
	return ANX_CONTINUE;
}

static int 
AnxReadClip_callback (ANNODEX * annodex, const AnxClip * clip, void * user_data)
{
	struct py_anx *py_anx = PY_ANX(user_data);
	PyObject *py_clip;
	PyObject *ret;

	py_clip = py_anxclip_pyobject(clip);

	if (py_anx->clip_callback_data) {
		ret = PyObject_CallFunction(py_anx->clip_callback, "OOO", 
					    (PyObject*) user_data,
					    py_clip, py_anx->clip_callback_data);
	} else {
		ret = PyObject_CallFunction(py_anx->clip_callback, "OO", 
					    (PyObject*) user_data, py_clip);
	}
	if (ret == NULL) {
		py_anx->exception_occurred = 1;
		return ANX_STOP_ERR;
	}
	return ANX_CONTINUE;
}

static int 
AnxReadRaw_callback (ANNODEX * annodex, unsigned char *buf, long n, long serialno, 
		     anx_int64_t granulepos, void *user_data)
{
	PyObject *ret;
	struct py_anx *py_anx = PY_ANX(user_data);
	if (py_anx->raw_callback_data) {
		ret = PyObject_CallFunction(py_anx->raw_callback, "Os#lLO", 
					    (PyObject*)user_data,
					    buf, n, serialno, granulepos,
					    py_anx->raw_callback_data);
	} else {
		ret = PyObject_CallFunction(py_anx->raw_callback, "Os#lL", 
					    (PyObject*)user_data,
					    buf, n, serialno, granulepos);
	}

	if (ret == NULL) {
		py_anx->exception_occurred = 1;
		return ANX_STOP_ERR;
	} 

	return ANX_CONTINUE;
}

/* Do a callback */
static PyObject * 
py_anx_set_callback(PyObject *self, PyObject *args, 
		    int (*fn)(ANNODEX *, void *, void *), 
		    void *cb_fn, PyObject **last_cb, PyObject **last_cb_data)
{
	PyObject *callback = NULL;
	PyObject *callback_data = NULL;
	struct py_anx *mf = PY_ANX(self);

	if (PyArg_ParseTuple(args, "OO", &callback, &callback_data)) {
		Py_INCREF(callback);
		Py_INCREF(callback_data);
	} else if (PyArg_ParseTuple(args, "O", &callback)) {
		PyErr_Clear();
		Py_INCREF(callback);
	} else {
		return NULL;
	}

	if (*last_cb == NULL) {
		fn(PY_ANX(self)->anx, cb_fn, mf);
	} else {
		Py_DECREF(*last_cb);
	}

	if (*last_cb_data != NULL) {
		Py_DECREF(*last_cb_data);
	}

	if (callback == Py_None) {
		/* If callback is NONE then we disable the callback */
		if (callback_data) { 
			Py_DECREF(callback_data);
		}
		fn(PY_ANX(self)->anx, NULL, NULL);
	} else {
		*last_cb = callback;
		*last_cb_data = callback_data;
	}

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject * 
py_anx_set_read_stream_callback(PyObject *self, PyObject *args)
{
	return py_anx_set_callback(self, args, 
				   (void*)anx_set_read_stream_callback, 
				   AnxReadStream_callback, 
				   &PY_ANX(self)->stream_callback,
				   &PY_ANX(self)->stream_callback_data);
}

static PyObject * 
py_anx_set_read_track_callback(PyObject *self, PyObject *args)
{
	return py_anx_set_callback(self, args, 
				   (void*)anx_set_read_track_callback, 
				   AnxReadTrack_callback, 
				   &PY_ANX(self)->track_callback,
				   &PY_ANX(self)->track_callback_data);
}

static PyObject * 
py_anx_set_read_head_callback(PyObject *self, PyObject *args)
{
	return py_anx_set_callback(self, args, 
				   (void*)anx_set_read_head_callback, 
				   AnxReadHead_callback, 
				   &PY_ANX(self)->head_callback,
				   &PY_ANX(self)->head_callback_data);
}

static PyObject * 
py_anx_set_read_clip_callback(PyObject *self, PyObject *args)
{
	return py_anx_set_callback(self, args,
				   (void*)anx_set_read_clip_callback, 
				   AnxReadClip_callback, 
				   &PY_ANX(self)->clip_callback,
				   &PY_ANX(self)->clip_callback_data);
}

static PyObject * 
py_anx_set_read_raw_callback(PyObject *self, PyObject *args)
{
	return py_anx_set_callback(self, args,
				   (void*)anx_set_read_raw_callback, 
				   AnxReadRaw_callback, 
				   &PY_ANX(self)->raw_callback,
				   &PY_ANX(self)->raw_callback_data);
}

static PyObject *
py_anx_getattr(PyObject * self, char * name) {
    return Py_FindMethod(anx_methods, self, name);
}

static PyObject *
py_anx_get_track_list(PyObject *self, PyObject *args)
{
	struct py_anx * pyanx = PY_ANX(self);
	AnxList *track;
	PyObject *list = PyList_New(0);
	for (track = anx_get_track_list (pyanx->anx);
	     track != NULL;
	     track = track->next) {
		int r;
		PyObject *obj = py_anxtrack_pyobject((AnxTrack *)(track->data));
		r = PyList_Append(list, obj);
		if (r == -1) {
			return -1;
		}
	}
	return list;
}

