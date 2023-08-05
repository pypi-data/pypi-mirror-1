#include <Python.h>
#include <sys/epoll.h>

typedef struct {
	PyObject_HEAD
	int fd;
} epollObject;

static PyTypeObject epoll_Type;

static epollObject *epoll_new(PyTypeObject *type, PyObject *args){
	epollObject *new;
	int size = 1;
	if(!PyType_IsSubtype(type, &epoll_Type))
		return NULL;
	if(!PyArg_ParseTuple(args, "|i", &size))
		return NULL;
	new = (epollObject *)type->tp_alloc(type, 0);
	if(new == NULL)
		return NULL;
	new->fd = epoll_create(size);
	if(new->fd == -1){
		Py_DECREF(new);
		PyErr_SetFromErrno(PyExc_OSError);
		return NULL;
	}
	return new;
}

static void epoll_dealloc(epollObject *self){
	close(self->fd);
	self->ob_type->tp_free(self);
}

static int epoll_ass_subscript(epollObject *self,
			       PyObject *key, PyObject *value){
	int fd, res;
	fd = PyInt_AsLong(key);
	if(PyErr_Occurred())
		return -1;
	if(value == NULL){
		res = epoll_ctl(self->fd, EPOLL_CTL_DEL, fd, NULL);
	}else{
		struct epoll_event event;
		event.data.fd = fd;
		event.events = PyInt_AsLong(value);
		if(PyErr_Occurred())
			return -1;
		res = epoll_ctl(self->fd, EPOLL_CTL_ADD, fd, &event);
		if(res == -1 && errno == EEXIST)
			res = epoll_ctl(self->fd, EPOLL_CTL_MOD, fd, &event);
	}
	if(res == -1){
		PyErr_SetFromErrno(PyExc_OSError);
		return -1;
	}
	return 0;
}

static PyObject *epoll_call(epollObject *self, PyObject *args){
	struct epoll_event event;
	int ret, timeout = -1;
	if(!PyArg_ParseTuple(args, "|i", &timeout))
		return NULL;
	Py_BEGIN_ALLOW_THREADS;
	ret = epoll_wait(self->fd, &event, 1, timeout);
	Py_END_ALLOW_THREADS;
	switch(ret){
	case 1:
		return Py_BuildValue("(ii)", event.data.fd, event.events);
	case 0:
		Py_RETURN_NONE;
	default:
		PyErr_SetFromErrno(PyExc_OSError);
		return NULL;
	}
}

static PyMappingMethods epoll_as_mapping = {
	.mp_ass_subscript = (objobjargproc)epoll_ass_subscript,
};

static char epoll_doc[] =
	"epoll([size]) -> epoll file descriptor.\n"
	"\n"
	"e[fd] = mask\n"
	"    Add (or modify) file descriptor @fd to epoll descriptor @e\n"
	"    with event mask @mask.\n"
	"del e[fd]\n"
	"    Remove file descriptor @fd from epoll descriptor @e.\n"
	"e([timeout]) -> (fd, mask) or None\n"
	"    Wait for an event on epoll descriptor @e and return file\n"
	"    descriptor @fd and event mask @mask, or None if there were\n"
	"    no events during requested @timeout (default: -1) milliseconds.";

static PyTypeObject epoll_Type = {
	PyObject_HEAD_INIT(&PyType_Type)
	.tp_name = "epoll.epoll",
	.tp_doc = epoll_doc,
	.tp_basicsize = sizeof(epollObject),
	.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
	.tp_new = (newfunc)epoll_new,
	.tp_dealloc = (destructor)epoll_dealloc,
	.tp_as_mapping = &epoll_as_mapping,
	.tp_call = (ternaryfunc)epoll_call,
};

static PyMethodDef methods[] = {
	{}
};

static char doc[] =
	"I/O event notification facility\n"
	"\n"
	"Refer to epoll(4) man page for details.";

PyMODINIT_FUNC initepoll(void){
	PyObject *module = Py_InitModule3("epoll", methods, doc);
	if(module == NULL)
		return;
	if(PyType_Ready(&epoll_Type) == 0){
		Py_INCREF(&epoll_Type);
		PyModule_AddObject(module, "epoll", (PyObject *)&epoll_Type);
	}
	PyModule_AddIntConstant(module, "EPOLLIN", EPOLLIN);
	PyModule_AddIntConstant(module, "EPOLLOUT", EPOLLOUT);
	PyModule_AddIntConstant(module, "EPOLLPRI", EPOLLPRI);
	PyModule_AddIntConstant(module, "EPOLLERR", EPOLLERR);
	PyModule_AddIntConstant(module, "EPOLLHUP", EPOLLHUP);
	PyModule_AddIntConstant(module, "EPOLLET", EPOLLET);
	PyModule_AddIntConstant(module, "EPOLLONESHOT", EPOLLONESHOT);
	PyModule_AddStringConstant(module, "__revision__",
				   "$Id: epoll.c 142 2006-07-10 20:09:48Z const $");
}
