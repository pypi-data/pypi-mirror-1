#include <Python.h>
#include <sys/msg.h>
#include <sys/sem.h>

typedef struct {
  PyObject_HEAD
  int msqid;
} MessageQueueObject;

typedef struct {
  PyObject_HEAD
  int semid;
} SemaphoreObject;

static PyTypeObject MessageQueue_Type;
static PyTypeObject Semaphore_Type;

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
  return new;

 fail_2:
  type->tp_free(new);
 fail_1:
  return NULL;
}

static void MessageQueue_dealloc(MessageQueueObject *self){
  msgctl(self->msqid, IPC_RMID, NULL);
  self->ob_type->tp_free(self);
}

static char MessageQueue_send_doc[] =
  "msq.send(type, text, [flags = 0]) -> bool\n"
  "\n"
  "Send a message (type, text).";

static PyObject *MessageQueue_send(MessageQueueObject *self, PyObject *args){
  struct msgbuf *msgp;
  int type, status, flags = 0;
  char *text;
  size_t msgsz;
  PyObject *res;
  if(!PyArg_ParseTuple(args, "is#|i", &type, &text, &msgsz, &flags))
    goto fail_1;
  msgp = (struct msgbuf *)PyMem_Malloc(sizeof(int) + msgsz);
  if(!msgp)
    goto fail_1;
  msgp->mtype = type;
  memcpy(&msgp->mtext, text, msgsz);
  status = msgsnd(self->msqid, msgp, msgsz, flags);
  if(status)
    if(flags & IPC_NOWAIT && errno == EAGAIN)
      res = Py_False;
    else{
      _set_err(status);
      res = NULL;
    }
  else
    res = Py_True;
  PyMem_Free(msgp);
  Py_XINCREF(res);
  return res;

 fail_1:
  return NULL;
}

static char MessageQueue_recv_doc[] =
  "msq.recv(type, [flags = 0]) -> (type, text) | False\n"
  "\n"
  "Receive a message from queue according to given type.";

static PyObject *MessageQueue_recv(MessageQueueObject *self, PyObject *args){
  struct msgbuf *_msg, *msg = NULL;
  int type, flags = 0;
  size_t msgsz = 1 << 12;
  ssize_t size;
  PyObject *res;
  if(!PyArg_ParseTuple(args, "i|i", &type, &flags))
    goto fail_1;
  do{
    _msg = (struct msgbuf *)PyMem_Realloc(msg, sizeof(int) + (msgsz <<= 1));
    if(!_msg)
      goto fail_1;
    msg = _msg;
    size = msgrcv(self->msqid, msg, msgsz, type, flags);
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
    res = Py_BuildValue("is#", msg->mtype, &msg->mtext, size);
  return res;

 fail_1:
  PyMem_Free(msg);
  return NULL;
}

static PyMethodDef MessageQueue_methods[] = {
  {"send", (PyCFunction)MessageQueue_send, METH_VARARGS, MessageQueue_send_doc},
  {"recv", (PyCFunction)MessageQueue_recv, METH_VARARGS, MessageQueue_recv_doc},
  {}
};

static char MessageQueue_doc[] =
  "MessageQueue() -> new message queue";

static PyTypeObject MessageQueue_Type = {
  PyObject_HEAD_INIT(&PyType_Type)
  .tp_name = "ipc.MessageQueue",
  .tp_doc = MessageQueue_doc,
  .tp_basicsize = sizeof(MessageQueueObject),
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_new = (newfunc)MessageQueue_new,
  .tp_dealloc = (destructor)MessageQueue_dealloc,
  .tp_methods = MessageQueue_methods,
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
  return new;

 fail_3:
  semctl(new->semid, 0, IPC_RMID);
 fail_2:
  type->tp_free(new);
 fail_1:
  return NULL;
}

static void Semaphore_dealloc(SemaphoreObject *self){
  semctl(self->semid, 0, IPC_RMID);
  self->ob_type->tp_free(self);
}

static PyObject *Semaphore_int(SemaphoreObject *self){
  int val = _set_err(semctl(self->semid, 0, GETVAL));
  if(val == -1)
    goto fail_1;
  return PyInt_FromLong(val);

 fail_1:
  return NULL;
}

static PyObject *Semaphore_op(SemaphoreObject *self, short sem_op, int flags){
  struct sembuf sops = {
    .sem_num = 0,
    .sem_op = sem_op,
    .sem_flg = 0,
  };
  int status = semop(self->semid, &sops, 1);
  if(status)
    if(flags & IPC_NOWAIT && errno == EAGAIN)
      return Py_INCREF(Py_False), Py_False;
    else
      return _set_err(status), NULL;
  else
    return Py_INCREF(Py_True), Py_True;
}

static char Semaphore_post_doc[] =
  "sem.post() -> True\n"
  "\n"
  "Increment.";

static PyObject *Semaphore_post(SemaphoreObject *self){
  return Semaphore_op(self, 1, 0);
}

static char Semaphore_wait_zero_doc[] =
  "sem.wait_zero([flags = 0]) -> bool\n"
  "\n"
  "Wait for zero value.";

static PyObject *Semaphore_wait_zero(SemaphoreObject *self, PyObject *args){
  int flags = 0;
  if(!PyArg_ParseTuple(args, "|i", &flags))
    return NULL;
  else
    return Semaphore_op(self, 0, flags);
}

static char Semaphore_wait_doc[] =
  "sem.wait([flags = 0]) -> bool\n"
  "\n"
  "Wait for positive value and decrement.";

static PyObject *Semaphore_wait(SemaphoreObject *self, PyObject *args){
  int flags = 0;
  if(!PyArg_ParseTuple(args, "|i", &flags))
    return NULL;
  else
    return Semaphore_op(self, -1, flags);
}

static PyNumberMethods Semaphore_as_number = {
  .nb_int = (unaryfunc)Semaphore_int,
};

static PyMethodDef Semaphore_methods[] = {
  {"post", (PyCFunction)Semaphore_post, METH_NOARGS, Semaphore_post_doc},
  {"wait_zero", (PyCFunction)Semaphore_wait_zero, METH_VARARGS, Semaphore_wait_zero_doc},
  {"wait", (PyCFunction)Semaphore_wait, METH_VARARGS, Semaphore_wait_doc},
  {}
};

static char Semaphore_doc[] =
  "Semaphore([value = 0]) -> new semaphore";

static PyTypeObject Semaphore_Type = {
  PyObject_HEAD_INIT(&PyType_Type)
  .tp_name = "ipc.Semaphore",
  .tp_doc = Semaphore_doc,
  .tp_basicsize = sizeof(SemaphoreObject),
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_new = (newfunc)Semaphore_new,
  .tp_dealloc = (destructor)Semaphore_dealloc,
  .tp_as_number = &Semaphore_as_number,
  .tp_methods = Semaphore_methods,
};

static PyMethodDef methods[] = {
  {}
};

static char doc[] =
  "System V IPC bindings: massage queues, semaphores.\n"
  "\n"
  "See IPC documentation for more information.\n"
  "\n"
  "For methods which accept argument flags, if IPC_NOWAIT\n"
  "in flags and requested operation can not be done\n"
  "immediately then method returns False instead of waiting.";

PyMODINIT_FUNC initipc(void){
  PyObject *module;
  if(PyType_Ready(&MessageQueue_Type))
    goto fail_1;
  if(PyType_Ready(&Semaphore_Type))
    goto fail_1;
  module = Py_InitModule3("ipc", methods, doc);
  if(!module)
    goto fail_1;
  if(!PyModule_AddObject(module, "MessageQueue", (PyObject *)&MessageQueue_Type))
    Py_INCREF(&MessageQueue_Type);
  if(!PyModule_AddObject(module, "Semaphore", (PyObject *)&Semaphore_Type))
    Py_INCREF(&Semaphore_Type);
  PyModule_AddIntConstant(module, "IPC_NOWAIT", IPC_NOWAIT);
  PyModule_AddIntConstant(module, "MSG_EXCEPT", MSG_EXCEPT);
  PyModule_AddStringConstant(module, "__revision__", "$Id: ipc.c 2 2005-07-31 20:41:23Z root $");
  return;

 fail_1:
  return;
}
