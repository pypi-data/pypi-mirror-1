#include <Python.h>
#include <structmember.h>
#include <sys/msg.h>
#include <sys/sem.h>
#include <sys/shm.h>

typedef struct {
	PyObject_HEAD
	int msqid;
	pid_t pid;
} MessageQueueObject;

typedef struct {
	PyObject_HEAD
	int semid;
	pid_t pid;
} SemaphoreObject;

typedef struct {
	PyObject_HEAD
	int shmid;
	pid_t pid;
	size_t size;
	void *buffer;
} SharedBufferObject;

static PyTypeObject MessageQueue_Type;
static PyTypeObject Semaphore_Type;
static PyTypeObject SharedBuffer_Type;

int _set_err(int status){
	if(status == -1)
		PyErr_SetFromErrno(PyExc_OSError);
	return status;
}

static MessageQueueObject *MessageQueue_new(PyTypeObject *type){
	MessageQueueObject *new;
	if(!PyType_IsSubtype(type, &MessageQueue_Type))
		goto fail_1;
	new = (MessageQueueObject *)type->tp_alloc(type, 0);
	if(!new)
		goto fail_1;
	new->msqid = _set_err(msgget(IPC_PRIVATE, 0666));
	if(new->msqid == -1)
		goto fail_2;
	new->pid = getpid();
	return new;

 fail_2:
	type->tp_free(new);
 fail_1:
	return NULL;
}

static void MessageQueue_dealloc(MessageQueueObject *self){
	if(getpid() == self->pid)
		msgctl(self->msqid, IPC_RMID, NULL);
	self->ob_type->tp_free(self);
}

static PyObject *MessageQueue_snd__(MessageQueueObject *self, long type,
				    const char *text, size_t msgsz, int flags){
	struct msgbuf *msgp;
	int status;
	PyObject *res;
	msgp = (struct msgbuf *)PyMem_Malloc(sizeof(int) + msgsz);
	if(!msgp)
		return PyErr_NoMemory();
	msgp->mtype = type;
	memcpy(&msgp->mtext, text, msgsz);
	Py_BEGIN_ALLOW_THREADS;
	status = msgsnd(self->msqid, msgp, msgsz, flags);
	Py_END_ALLOW_THREADS;
	if(status)
		if(flags & IPC_NOWAIT && errno == EAGAIN)
			res = Py_False;
		else{
			_set_err(status);
			res = NULL;
		}
	else
		res = flags & IPC_NOWAIT ? Py_True : Py_None;
	PyMem_Free(msgp);
	Py_XINCREF(res);
	return res;
}

static char MessageQueue_post_doc[] =
	"x.post(type[, text = \"\"[, flags = 0]]) -> None | bool";

static PyObject *MessageQueue_post(MessageQueueObject *self, PyObject *args){
	int flags = 0;
	long type;
	char *text = NULL;
	size_t msgsz = 0;
	if(!PyArg_ParseTuple(args, "l|s#i", &type, &text, &msgsz, &flags))
		return NULL;
	return MessageQueue_snd__(self, type, text, msgsz, flags);
}

static PyObject *MessageQueue_rcv__(MessageQueueObject *self,
				    long type, int flags){
	struct msgbuf *_msg, *msg = NULL;
	size_t msgsz = 1 << 10;
	ssize_t size;
	PyObject *res;
	do{
		_msg = (struct msgbuf *)PyMem_Realloc(msg, sizeof(int) +
						      (msgsz <<= 1));
		if(!_msg){
			PyMem_Free(msg);
			return PyErr_NoMemory();
		}
		Py_BEGIN_ALLOW_THREADS;
		size = msgrcv(self->msqid, msg = _msg, msgsz, type, flags);
		Py_END_ALLOW_THREADS;
	}while(size == -1 && errno == E2BIG);
	if(size == -1)
		if(flags & IPC_NOWAIT && errno == ENOMSG){
			Py_INCREF(Py_False);
			res = Py_False;
		}else{
			_set_err(size);
			res = NULL;
		}
	else
		res = Py_BuildValue("ls#", msg->mtype, &msg->mtext, size);
	PyMem_Free(msg);
	return res;
}

static char MessageQueue_get_doc[] =
	"x.get([type = 0[, flags = 0]]) -> (type, text) | False";

static PyObject *MessageQueue_get(MessageQueueObject *self, PyObject *args){
	long type = 0;
	int flags = 0;
	if(PyArg_ParseTuple(args, "|li", &type, &flags))
		return MessageQueue_rcv__(self, type, flags);
	else
		return NULL;
}

static PyObject *MessageQueue_iternext(MessageQueueObject *self){
	return MessageQueue_rcv__(self, 0, 0);
}

static int MessageQueue_length(MessageQueueObject *self){
	struct msqid_ds buf;
	if(_set_err(msgctl(self->msqid, IPC_STAT, &buf)))
		return -1;
	return buf.msg_qnum;
}

static PyObject *MessageQueue_item(MessageQueueObject *self, int i){
	return MessageQueue_rcv__(self, i, 0);
}

static int MessageQueue_ass_item(MessageQueueObject *self, int i, PyObject *v){
	char *text;
	int length;
	PyObject *res;
	if(!v){
		PyErr_SetNone(PyExc_TypeError);
		return -1;
	}
	if(PyString_AsStringAndSize(v, &text, &length))
		return -1;
	res = MessageQueue_snd__(self, i, text, length, 0);
	if(res){
		Py_DECREF(res);
		return 0;
	}else
		return -1;
}

static PyObject *MessageQueue_repr(MessageQueueObject *self){
	return PyString_FromFormat("<%s 0x%08x>",
				   self->ob_type->tp_name, self->msqid);
}

static PyMethodDef MessageQueue_methods[] = {
	{"post", (PyCFunction)MessageQueue_post, METH_VARARGS,
	 MessageQueue_post_doc},
	{"get", (PyCFunction)MessageQueue_get, METH_VARARGS,
	 MessageQueue_get_doc},
	{}
};

static PySequenceMethods MessageQueue_as_sequence = {
	.sq_length = (inquiry)MessageQueue_length,
	.sq_item = (intargfunc)MessageQueue_item,
	.sq_ass_item = (intobjargproc)MessageQueue_ass_item,
};

static char MessageQueue_doc[] =
	"MessageQueue() -> new message queue\n"
	"\n"
	"msq[type] <==> msq.get(type) -- get message from queue\n"
	"msq[type] = text <==> msq.post(type, text) -- post message to queue\n"
	"len(msq) -- number of messages in queue\n"
	"iter(msq) -- infinite loop of msq.get()";

static PyTypeObject MessageQueue_Type = {
	PyObject_HEAD_INIT(&PyType_Type)
	.tp_name = "ipc.MessageQueue",
	.tp_doc = MessageQueue_doc,
	.tp_basicsize = sizeof(MessageQueueObject),
	.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
	.tp_new = (newfunc)MessageQueue_new,
	.tp_dealloc = (destructor)MessageQueue_dealloc,
	.tp_methods = MessageQueue_methods,
	.tp_as_sequence = &MessageQueue_as_sequence,
	.tp_iter = PyObject_SelfIter,
	.tp_iternext = (iternextfunc)MessageQueue_iternext,
	.tp_repr = (reprfunc)MessageQueue_repr,
};

static SemaphoreObject *Semaphore_new(PyTypeObject *type, PyObject *args){
	SemaphoreObject *new;
	int val = 0;
	if(!PyType_IsSubtype(type, &Semaphore_Type))
		goto fail_1;
	new = (SemaphoreObject *)type->tp_alloc(type, 0);
	if(!new)
		goto fail_1;
	new->semid = _set_err(semget(IPC_PRIVATE, 1, 0666));
	if(new->semid == -1)
		goto fail_2;
	if(!PyArg_ParseTuple(args, "|i", &val))
		PyErr_Clear();
	if(_set_err(semctl(new->semid, 0, SETVAL, val)) == -1)
		goto fail_3;
	new->pid = getpid();
	return new;

 fail_3:
	semctl(new->semid, 0, IPC_RMID);
 fail_2:
	type->tp_free(new);
 fail_1:
	return NULL;
}

static void Semaphore_dealloc(SemaphoreObject *self){
	if(getpid() == self->pid)
		semctl(self->semid, 0, IPC_RMID);
	self->ob_type->tp_free(self);
}

static PyObject *Semaphore_op__(SemaphoreObject *self,
				short sem_op, int flags){
	struct sembuf sops = {
		.sem_num = 0,
		.sem_op = sem_op,
		.sem_flg = flags,
	};
	int status;
	Py_BEGIN_ALLOW_THREADS;
	status = semop(self->semid, &sops, 1);
	Py_END_ALLOW_THREADS;
	if(status)
		if(flags & IPC_NOWAIT && errno == EAGAIN)
			return Py_INCREF(Py_False), Py_False;
		else
			return _set_err(status), NULL;
	else
		if(flags & IPC_NOWAIT)
			return Py_INCREF(Py_True), Py_True;
		else
			return Py_INCREF(Py_None), Py_None;
}

static char Semaphore_P_doc[] =
	"x.P() -> None";

static PyObject *Semaphore_P(SemaphoreObject *self){
	return Semaphore_op__(self, -1, 0);
}

static char Semaphore_V_doc[] =
	"x.V() -> None";

static PyObject *Semaphore_V(SemaphoreObject *self){
	return Semaphore_op__(self, 1, 0);
}

static PyObject *Semaphore_call(SemaphoreObject *self, PyObject *args){
	short val = 0, flags = 0;
	if(!PyArg_ParseTuple(args, "|hh", &val, &flags))
		return NULL;
	else
		return Semaphore_op__(self, val, flags);
}

static PyObject *Semaphore_int(SemaphoreObject *self){
	int val = _set_err(semctl(self->semid, 0, GETVAL));
	if(val == -1)
		return NULL;
	return PyInt_FromLong(val);
}

static PyObject *Semaphore_inplace_add(PyObject *self, PyObject *v){
	short val;
	PyObject *tmp;
	if(!PyObject_IsInstance(self, (PyObject *)&Semaphore_Type))
		return NULL;
	val = PyInt_AsLong(v);
	if(PyErr_Occurred())
		return NULL;
	tmp = Semaphore_op__((SemaphoreObject *)self, val, 0);
	if(tmp){
		Py_DECREF(tmp);
		Py_INCREF(self);
		return self;
	}else
		return NULL;
}

static PyObject *Semaphore_repr(SemaphoreObject *self){
	return PyString_FromFormat("<%s 0x%08x>",
				   self->ob_type->tp_name, self->semid);
}

static PyNumberMethods Semaphore_as_number = {
	.nb_inplace_add = (binaryfunc)Semaphore_inplace_add,
	.nb_int = (unaryfunc)Semaphore_int,
};

static PyMethodDef Semaphore_methods[] = {
	{"P", (PyCFunction)Semaphore_P, METH_NOARGS, Semaphore_P_doc},
	{"V", (PyCFunction)Semaphore_V, METH_NOARGS, Semaphore_V_doc},
	{}
};

static char Semaphore_doc[] =
	"Semaphore([value = 0]) -> new semaphore\n"
	"\n"
	"sem([value = 0[, flags = 0]]) -- perform an operation\n"
	"sem += value <==> sem(value)\n"
	"int(sem) -- current semaphore value";

static PyTypeObject Semaphore_Type = {
	PyObject_HEAD_INIT(&PyType_Type)
	.tp_name = "ipc.Semaphore",
	.tp_doc = Semaphore_doc,
	.tp_basicsize = sizeof(SemaphoreObject),
	.tp_flags = Py_TPFLAGS_DEFAULT |
	Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES,
	.tp_new = (newfunc)Semaphore_new,
	.tp_dealloc = (destructor)Semaphore_dealloc,
	.tp_as_number = &Semaphore_as_number,
	.tp_methods = Semaphore_methods,
	.tp_call = (ternaryfunc)Semaphore_call,
	.tp_repr = (reprfunc)Semaphore_repr,
};

static SharedBufferObject *SharedBuffer_new(PyTypeObject *type,
					    PyObject *args){
	SharedBufferObject *new;
	if(!PyType_IsSubtype(type, &SharedBuffer_Type))
		goto fail_1;
	new = (SharedBufferObject *)type->tp_alloc(type, 0);
	if(!new)
		goto fail_1;
	if(!PyArg_ParseTuple(args, "I", &new->size))
		goto fail_2;
	if(_set_err(new->shmid = shmget(IPC_PRIVATE, new->size, 0666)) == -1)
		goto fail_2;
	if((new->buffer = shmat(new->shmid, NULL, 0)) == (void *)-1){
		_set_err(-1);
		goto fail_3;
	}
	new->pid = getpid();
	return new;

 fail_3:
	shmctl(new->shmid, IPC_RMID, NULL);
 fail_2:
	type->tp_free(new);
 fail_1:
	return NULL;
}

static void SharedBuffer_dealloc(SharedBufferObject *self){
	shmdt(self->buffer);
	if(getpid() == self->pid)
		shmctl(self->shmid, IPC_RMID, NULL);
	self->ob_type->tp_free(self);
}

static int SharedBuffer_length(SharedBufferObject *self){
	return self->size;
}

static PyObject *SharedBuffer_item(SharedBufferObject *self, int i){
	if(i < 0)
		i += self->size;
	if(0 <= i && i < self->size)
		return PyString_FromStringAndSize((char *)self->buffer + i, 1);
	PyErr_SetNone(PyExc_IndexError);
	return NULL;
}

static int SharedBuffer_ass_item(SharedBufferObject *self, int i, PyObject *v){
	char *buffer;
	int length;
	if(!v){
		PyErr_SetNone(PyExc_TypeError);
		return -1;
	}
	if(i < 0)
		i += self->size;
	if(0 > i || i >= self->size){
		PyErr_SetNone(PyExc_IndexError);
		return -1;
	}
	if(PyString_AsStringAndSize(v, &buffer, &length))
		return -1;
	if(length > self->size - i){
		PyErr_SetNone(PyExc_ValueError);
		return -1;
	}
	memcpy((char *)self->buffer + i, buffer, length);
	return 0;
}

static PyObject *SharedBuffer_slice(SharedBufferObject *self, int i1, int i2){
	if(i1 < 0)
		i1 += self->size;
	if(i1 < 0)
		i1 = 0;
	if(i2 < 0)
		i2 += self->size;
	if(i2 > self->size)
		i2 = self->size;
	if(i1 > i2){
		PyErr_SetNone(PyExc_IndexError);
		return NULL;
	}else
		return PyString_FromStringAndSize((char *)self->buffer + i1,
						  i2 - i1);
}

static PyObject *SharedBuffer_repr(SharedBufferObject *self){
	return PyString_FromFormat("<%s 0x%08x at %p:%p>",
				   self->ob_type->tp_name, self->shmid,
				   self->buffer, self->buffer + self->size);
}

static PyObject *SharedBuffer_str(SharedBufferObject *self){
	return PyString_FromStringAndSize(self->buffer, self->size);
}

static PySequenceMethods SharedBuffer_as_sequence = {
	.sq_length = (inquiry)SharedBuffer_length,
	.sq_item = (intargfunc)SharedBuffer_item,
	.sq_ass_item = (intobjargproc)SharedBuffer_ass_item,
	.sq_slice = (intintargfunc)SharedBuffer_slice,
};

static char SharedBuffer_doc[] =
	"SharedBuffer(size) -> new shared buffer\n"
	"\n"
	"len(buf) -- length of buffer\n"
	"buf[i] -- i-th byte as one-char string\n"
	"buf[i] = s -- store string in buffer starting from i-th byte\n"
	"buf[i:j] -- slice as string\n"
	"str(buf) <==> buf[:] -- entire buffer as string";

static PyTypeObject SharedBuffer_Type = {
	PyObject_HEAD_INIT(&PyType_Type)
	.tp_name = "ipc.SharedBuffer",
	.tp_doc = SharedBuffer_doc,
	.tp_basicsize = sizeof(SharedBufferObject),
	.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
	.tp_new = (newfunc)SharedBuffer_new,
	.tp_dealloc = (destructor)SharedBuffer_dealloc,
	.tp_as_sequence = &SharedBuffer_as_sequence,
	.tp_repr = (reprfunc)SharedBuffer_repr,
	.tp_str = (reprfunc)SharedBuffer_str,
};

static PyMethodDef methods[] = {
	{}
};

static char doc[] =
	"System V interprocess communication mechanisms\n"
	"\n"
	"Refer to ipc(5) manpage and http://tldp.org/LDP/lpg/node21.html\n"
	"for more information about System V IPC.";

PyMODINIT_FUNC initipc(void){
	PyObject *module;
	if(PyType_Ready(&MessageQueue_Type) ||
	   PyType_Ready(&Semaphore_Type) ||
	   PyType_Ready(&SharedBuffer_Type))
		return;
	module = Py_InitModule3("ipc", methods, doc);
	if(module == NULL)
		return;
	Py_INCREF(&MessageQueue_Type);
	PyModule_AddObject(module, "MessageQueue",
			   (PyObject *)&MessageQueue_Type);
	Py_INCREF(&Semaphore_Type);
	PyModule_AddObject(module, "Semaphore",
			   (PyObject *)&Semaphore_Type);
	Py_INCREF(&SharedBuffer_Type);
	PyModule_AddObject(module, "SharedBuffer",
			   (PyObject *)&SharedBuffer_Type);
	PyModule_AddIntConstant(module, "IPC_NOWAIT", IPC_NOWAIT);
	PyModule_AddIntConstant(module, "MSG_EXCEPT", MSG_EXCEPT);
	PyModule_AddStringConstant(module, "__revision__",
				   "$Id: ipc.c 151 2006-07-19 21:24:45Z const $");
}
