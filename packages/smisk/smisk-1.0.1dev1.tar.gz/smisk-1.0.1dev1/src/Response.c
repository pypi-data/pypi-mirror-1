/*
Copyright (c) 2007-2008 Rasmus Andersson and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/
#include "__init__.h"
#include "utils.h"
#include "Response.h"
#include "Application.h"
#include "SessionStore.h"
#include <structmember.h>
#include <ctype.h>
#include <fastcgi.h>


#pragma mark Private C

typedef struct FCGX_Stream_Data {
    unsigned char *buff;      /* buffer after alignment */
    int bufflen;              /* number of bytes buff can store */
    unsigned char *mBuff;     /* buffer as returned by Malloc */
    unsigned char *buffStop;  /* reader: last valid byte + 1 of entire buffer.
                               * stop generally differs from buffStop for
                               * readers because of record structure.
                               * writer: buff + bufflen */
    int type;                 /* reader: FCGI_PARAMS or FCGI_STDIN
                               * writer: FCGI_STDOUT or FCGI_STDERR */
    int eorStop;              /* reader: stop stream at end-of-record */
    int skip;                 /* reader: don't deliver content bytes */
    int contentLen;           /* reader: bytes of unread content */
    int paddingLen;           /* reader: bytes of unread padding */
    int isAnythingWritten;    /* writer: data has been written to ipcFd */
    int rawWrite;             /* writer: write data without stream headers */
    FCGX_Request *reqDataPtr; /* request data not specific to one stream */
} FCGX_Stream_Data;


static int _begin_if_needed(void *_self) {
  smisk_Response *self = (smisk_Response *)_self;
  if ( (self->has_begun == Py_False) && (PyObject_CallMethod((PyObject *)self, "begin", NULL) == NULL) )
    return -1;
  return 0;
}


// Called by Application.run just after a successful accept() 
// and just before calling service().
int smisk_Response_reset (smisk_Response *self) {
  log_trace("ENTER");
  REPLACE_OBJ(self->has_begun, Py_False, PyObject);
  Py_XDECREF(self->headers);
  self->headers = NULL;
  return 0;
}


// Called by Application.run() after a successful call to service()
int smisk_Response_finish(smisk_Response *self) {
  log_trace("ENTER");
  return _begin_if_needed((void *)self);
}


#pragma mark -
#pragma mark Initialization & deallocation


PyObject * smisk_Response_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
  log_trace("ENTER");
  smisk_Response *self;
  
  if ((self = (smisk_Response *)type->tp_alloc(type, 0)) == NULL)
    return NULL;  
  
  if (smisk_Response_reset(self) != 0) {
    Py_DECREF(self);
    return NULL;
  }
  
  // Construct a new Stream for out
  self->out = (smisk_Stream*)smisk_Stream_new(&smisk_StreamType, NULL, NULL);
  if (self->out == NULL) {
    Py_DECREF(self);
    return NULL;
  }
  
  return (PyObject *)self;
}

int smisk_Response_init(smisk_Response* self, PyObject *args, PyObject *kwargs) {
  log_trace("ENTER");
  return 0;
}

void smisk_Response_dealloc(smisk_Response* self) {
  log_trace("ENTER");
  
  smisk_Response_reset(self);
  
  Py_XDECREF(self->has_begun);
  Py_XDECREF(self->headers);
  Py_XDECREF(self->out);
  
  self->ob_type->tp_free((PyObject*)self);
}


#pragma mark -
#pragma mark Methods


PyDoc_STRVAR(smisk_Response_send_file_DOC,
  "Send a file to the client in a performance optimal way.\n"
  "\n"
  "Please not you can *not* combine any output when responding using this method.\n"
  "\n"
  ":param  filename: If this is a relative path, the host server defines the behaviour.\n"
  ":type   filename: string\n"
  ":raises EnvironmentError: If smisk does not know how to perform *sendfile* through "
    "the current host server.\n"
  ":raises `IOError`:\n"
  ":rtype: None");
PyObject *smisk_Response_send_file(smisk_Response* self, PyObject *filename) {
  log_trace("ENTER");
  int rc;
  
  if (!filename || !PyString_Check(filename))
    return PyErr_Format(PyExc_TypeError, "first argument must be a string");
  
  char *server = NULL;
  if (smisk_current_app)
    server = FCGX_GetParam( "SERVER_SOFTWARE", smisk_current_app->request->envp );
  
  if (server == NULL)
    server = "unknown server software";
  
  if (strstr(server, "lighttpd/1.4")) {
    FCGX_PutStr("X-LIGHTTPD-send-file: ", 22, self->out->stream);
  }
  else if (strstr(server, "lighttpd/") || strstr(server, "Apache/2")) {
    FCGX_PutStr("X-Sendfile: ", 12, self->out->stream);
  }
  else {
    return PyErr_Format(PyExc_EnvironmentError, "sendfile not supported by host server ('%s')", server);
  }
  
  FCGX_PutStr(PyString_AsString(filename), PyString_Size(filename), self->out->stream);
  rc = FCGX_PutStr("\r\n\r\n", 4, self->out->stream);
  REPLACE_OBJ(self->has_begun, Py_True, PyObject);
  
  // Check for errors
  if (rc == -1)
    return PyErr_SET_FROM_ERRNO;
  
  Py_RETURN_NONE;
}


PyDoc_STRVAR(smisk_Response_begin_DOC,
  "Begin response - send headers.\n"
  "\n"
  "Automatically called on by mechanisms like `write()` and `Application.run()`."
  "\n"
  ":rtype: None");
PyObject *smisk_Response_begin(smisk_Response* self) {
  log_trace("ENTER");
  int rc;
  Py_ssize_t num_headers, i;
  
  // Note: self->headers can be NULL at this point and that's by design.
  
  IFDEBUG(if (self->headers) 
    assert_refcount(self->headers, > 0);
  )
  
  // Set session cookie?
  if (smisk_current_app->request->session_id && (smisk_current_app->request->initial_session_hash == 0)) {
    log_debug("New session - sending SID with Set-Cookie: %s=%s;Version=1;Path=/",
      PyString_AS_STRING(((smisk_SessionStore *)smisk_current_app->sessions)->name),
      PyString_AS_STRING(smisk_current_app->request->session_id));
    // First-time session!
    if (!PyString_Check(((smisk_SessionStore *)smisk_current_app->sessions)->name)) {
      PyErr_SetString(PyExc_TypeError, "sessions.name is not a string");
      return NULL;
    }
    assert(smisk_current_app->request->session_id);
    FCGX_FPrintF(self->out->stream, "Set-Cookie: %s=%s;Version=1;Path=/\r\n",
      PyString_AS_STRING(((smisk_SessionStore *)smisk_current_app->sessions)->name),
      PyString_AS_STRING(smisk_current_app->request->session_id)
    );
  }
  
  // Headers?
  if (self->headers && PyList_Check(self->headers) && (num_headers = PyList_GET_SIZE(self->headers))) {
    // Iterate over headers
    PyObject *str;
    for (i=0;i<num_headers;i++) {
      str = PyList_GET_ITEM(self->headers, i);
      if (str && PyString_Check(str)) {
        FCGX_PutStr(PyString_AS_STRING(str), PyString_GET_SIZE(str), self->out->stream);
        FCGX_PutChar('\r', self->out->stream);
        FCGX_PutChar('\n', self->out->stream);
      }
    }
  }
  else {
    // No headers
    FCGX_PutChar('\r', self->out->stream);
    FCGX_PutChar('\n', self->out->stream);
  }
  
  // Header-Body separator
  FCGX_PutChar('\r', self->out->stream);
  rc = FCGX_PutChar('\n', self->out->stream);
  
  REPLACE_OBJ(self->has_begun, Py_True, PyObject);
  
  // Errors?
  if (rc == -1)
    return PyErr_SET_FROM_ERRNO;
  
  log_debug("EXIT smisk_Response_begin");
  Py_RETURN_NONE;
}


PyDoc_STRVAR(smisk_Response_write_DOC,
  "Write data to the output buffer.\n"
  "\n"
  "If `begin()` has not yet been called, it will be before ``write()`` "
    "actually performs the writing to `out`."
  "\n"
  ":param    string: Data.\n"
  ":type     string: string\n"
  ":raises   `IOError`:\n"
  ":rtype:   None");
PyObject *smisk_Response_write(smisk_Response* self, PyObject *str) {
  log_trace("ENTER");
  Py_ssize_t length;
  
  if (!str || !PyString_Check(str))
    return PyErr_Format(PyExc_TypeError, "first argument must be a string");
  
  // TODO: make this method accept a length argument and use that instead if available
  length = PyString_GET_SIZE(str);
  if (!length) // No data/Empty string
    Py_RETURN_NONE;
  
  // Send HTTP headers
  if (_begin_if_needed((void *)self) != 0)
    return NULL;
  
  // Write data
  if ( smisk_Stream_perform_write(self->out, str, PyString_GET_SIZE(str)) == -1 )
    return NULL;
  
  Py_RETURN_NONE;
}


PyDoc_STRVAR(smisk_Response_writelines_DOC,
  "Write a sequence of strings to the stream.\n"
  "\n"
  "The sequence can be any iterable object producing strings, typically a ''list'' of strings. There is no return value. (The name is intended to match readlines(); writelines() and alike does not add line separators.)\n"
  "\n"
  "This method esentially calls self.begin() if not has_begun, then calls self.out.writelines(sequence). Which means the difference between calling self.writelines (this method) and self.out.writelines is that the latter will not call begin() if needed. You should always use this method instead of self.out.writelines, unless you are certain begin() has been called. (begin() is automatically called upon after a service() call if it has not been called, so you can not count on it not being called at all.)"
  "\n"
  ":type   sequence: list\n"
  ":param  sequence: A sequence of strings\n"
  ":rtype: None\n"
  ":raises IOError:");
PyObject *smisk_Response_writelines(smisk_Response* self, PyObject *sequence) {
  log_trace("ENTER");
  return smisk_Stream_perform_writelines(self->out, sequence, &_begin_if_needed, (void *)self);
}

/* XXX: How do we add documentation for __call__?
PyDoc_STRVAR(smisk_Response___call___DOC,
  "Respond with a series of strings.\n"
  "\n"
  "This is equivalent of calling `writelines((arg1, arg2 ...))`, thus if `begin()` has not yet been called, it will be. Calling without any arguments has no effect. Note that the arguments must be strings, as this method actually uses writelines."
  "\n"
  ":type     string: string\n"
  ":raises   `IOError`:\n"
  ":rtype:   None");*/
PyObject *smisk_Response___call__(smisk_Response* self, PyObject *args, PyObject *kwargs) {
  log_trace("ENTER");
  // As we can get the length here, we return directly if nothing is to be written.
  if (PyTuple_GET_SIZE(args) < 1)
    Py_RETURN_NONE;
  return smisk_Stream_perform_writelines(self->out, args, &_begin_if_needed, (void *)self);
}


PyDoc_STRVAR(smisk_Response_find_header_DOC,
  "Find a header in the list of 'headers' matching 'prefix' in a case-insensitive manner.\n"
  "\n"
  ":returns: Index in 'headers' or -1 if not found.\n"
  ":rtype:   int");
PyObject *smisk_Response_find_header(smisk_Response* self, PyObject *prefix) {
  log_trace("ENTER");
  if (self->headers == NULL)
    return PyInt_FromLong(-1L);
  return smisk_find_string_by_prefix_in_dict(self->headers, prefix);
}


PyDoc_STRVAR(smisk_Response_set_cookie_DOC,
  "Send a cookie.\n"
  "\n"
  "Note:\n"
  "  Setting a cookie will cause the response not to be cached by proxies and peer "
  "  browsers, as required by `RFC 2109 <http://www.faqs.org/rfcs/rfc2109.html>`__.\n"
  "\n"
  "See also:\n"
  "  `RFC 2109 <http://www.faqs.org/rfcs/rfc2109.html>`__ - *HTTP State Management Mechanism*\n"
  "\n"
  ":type  name:    string\n"
  ":param name:    Required. The name of the state information (*cookie*). names "
    "that begin with $ are reserved for other uses and must not be used by applications.\n"
  "\n"
  ":type  value:   string\n"
  ":param value:   Opaque to the user agent and may be anything the "
    "origin server chooses to send, possibly in a server-selected printable ASCII encoding. "
    "*Opaque* implies that the content is of interest and relevance only to the origin server. "
    "The content may, in fact, be readable by anyone that examines the Set-Cookie header.\n"
  "\n"
  ":type  comment: string\n"
  ":param comment: Optional. Because cookies can contain private information about a user, the "
    "Cookie attribute allows an origin server to document its intended use of a cookie. The user "
    "can inspect the information to decide whether to initiate or continue a session with this "
    "cookie.\n"
  "\n"
  ":type  domain:  string\n"
  ":param domain:  Optional. The Domain attribute specifies the domain for which the cookie is "
    "valid. An explicitly specified domain must always start with a dot.\n"
  "\n"
  ":type  path:    string\n"
  ":param path:    Optional. The Path attribute specifies the subset of URLs to which this cookie "
    "applies.\n"
  "\n"
  ":type  secure:  bool\n"
  ":param secure:  Optional. The Secure attribute directs the user agent to use only (unspecified) "
    "secure means to contact the origin server whenever it sends back this cookie.\n"
    "\n"
    "The user agent (possibly under the user's control) may determine what level of security it "
    "considers appropriate for *secure* cookies. The Secure attribute should be considered security "
    "advice from the server to the user agent, indicating that it is in the session's interest to "
    "protect the cookie contents.\n"
  "\n"
  ":type  version: int\n"
  ":param version: Optional. The Version attribute, a decimal integer, identifies to which version "
    "of the state management specification the cookie conforms. For the "
    "`RFC 2109 <http://www.faqs.org/rfcs/rfc2109.html>`__ specification, Version=1 applies. If not "
    "specified, this will be set to ``1``.\n"
  "\n"
  ":type  max_age: int\n"
  ":param max_age: The value of the Max-Age attribute is delta-seconds, the lifetime of the cookie "
    "in seconds, a decimal non-negative integer. To handle cached cookies correctly, a client "
    "**should** calculate the age of the cookie according to the age calculation rules in the "
    "`HTTP/1.1 specification <http://www.faqs.org/rfcs/rfc2616.html>`__. When the age is greater "
    "than delta-seconds seconds, the client **should** discard the cookie. A value of zero means "
    "the cookie **should** be discarded immediately (not when the browsers closes, but really "
    "immediately)\n"
  "\n"
  ":type  http_only: bool\n"
  ":param http_only: When True the cookie will be made accessible only through the HTTP protocol. "
    "This means that the cookie won't be accessible by scripting languages, such as JavaScript. "
    "This setting can effectly help to reduce identity theft through "
    "`XSS attacks <http://en.wikipedia.org/wiki/Cross-site_scripting>`__ (although it is not "
    "supported by all browsers).\n"
  "\n"
  ":rtype:         None");
PyObject *smisk_Response_set_cookie(smisk_Response* self, PyObject *args, PyObject *kwargs) {
  log_trace("ENTER");
  static char *kwlist[] = {"name", "value", /* required */
                           "comment", "domain", "path",
                           "secure", "version", "max_age", "http_only", NULL};
  char *name = NULL,
       *value = NULL,
       *comment = NULL,
       *domain = NULL,
       *path = NULL;
  
  int  secure = 0,
       version = 1,
       max_age = -1,
       http_only = 0;
  
  PyObject *s;
  
  if (self->has_begun == Py_True)
    return PyErr_Format(PyExc_EnvironmentError, "Cookies can not be set when output has already begun.");
  
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss|zzziiii", kwlist,
      &name, &value, &comment, &domain, &path, &secure, &version, &max_age, &http_only)) {
    return NULL;
  }
  
  // Mandatory fields
  
  name = smisk_url_encode(name, 1);
  value = smisk_url_encode(value, 1);
  s = PyString_FromFormat("Set-Cookie: %s=%s;Version=%d", name, value, version);
  free(name); // smisk_url_encode
  free(value); // smisk_url_encode
  
  
  // Optional fields
  
  if (comment) {
    comment = smisk_url_encode(comment, 1);
    PyString_ConcatAndDel(&s, PyString_FromFormat(";Comment=%s", comment));
    free(comment);
  }
  
  if (domain) {
    domain = smisk_url_encode(domain, 1);
    PyString_ConcatAndDel(&s, PyString_FromFormat(";Domain=%s", domain));
    free(domain);
  }
  
  if (path) {
    path = smisk_url_encode(path, 1);
    PyString_ConcatAndDel(&s, PyString_FromFormat(";Path=%s", path));
    free(path);
  }
  
  if (max_age > -1) {
    PyString_ConcatAndDel(&s, PyString_FromFormat(";Max-Age=%d", max_age));
    // Add Expires for compatibility reasons
    // ;Expires=Wdy, DD-Mon-YY HH:MM:SS GMT
    // XXX check for NULL returns
    PyObject *expires = PyString_FromStringAndSize(NULL, 36);
    time_t t = time(NULL) + max_age;
    strftime(PyString_AS_STRING(expires), 36, ";Expires=%a, %d-%b-%g %H:%M:%S GMT", gmtime(&t));
    PyString_ConcatAndDel(&s, expires);
  }
  else {
    PyString_ConcatAndDel(&s, PyString_FromString(";Discard"));
  }
  
  if (secure)
    PyString_ConcatAndDel(&s, PyString_FromString(";Secure"));
    
  // More info: http://msdn2.microsoft.com/en-us/library/ms533046(VS.85).aspx
  if (http_only)
    PyString_ConcatAndDel(&s, PyString_FromString(";HttpOnly"));
  
  // Make sure self->headers is initialized
  ENSURE_BY_GETTER(self->headers, smisk_Response_get_headers(self), return NULL; );
  
  // Append the set-cookie header
  if (PyList_Append(self->headers, s) != 0)
    return NULL;
  
  Py_DECREF(s); // the list is the new owner
  
  Py_RETURN_NONE;
}


#pragma mark -
#pragma mark Get- and Setters


PyObject *smisk_Response_get_headers(smisk_Response* self) {
  log_trace("ENTER");
  
  if ( (self->headers == NULL) && ((self->headers = PyList_New(0)) == NULL) )
    return NULL;
  
  Py_INCREF(self->headers); // callers reference
  return self->headers;
}


static int smisk_Response_set_headers(smisk_Response* self, PyObject *headers) {
  log_trace("ENTER");
  REPLACE_OBJ(self->headers, headers, PyObject);
  return self->headers ? 0 : -1;
}


#pragma mark -
#pragma mark Type construction

PyDoc_STRVAR(smisk_Response_DOC,
  "A HTTP response\n"
  "\n"
  "Documentation for `__call__()`:\n"
  "\n"
  "Respond with a series of strings.\n"
  "\n"
  "This is equivalent of calling `writelines((arg1, arg2 ...))`, thus if `begin()` has not yet been called, it will be. Calling without any arguments has no effect. Note that the arguments must be strings, as this method actually uses writelines."
  );

// Methods
static PyMethodDef smisk_Response_methods[] = {
  {"send_file",   (PyCFunction)smisk_Response_send_file,    METH_O,       smisk_Response_send_file_DOC},
  {"begin",       (PyCFunction)smisk_Response_begin,        METH_NOARGS,  smisk_Response_begin_DOC},
  {"write",       (PyCFunction)smisk_Response_write,        METH_O,       smisk_Response_write_DOC},
  {"writelines",  (PyCFunction)smisk_Response_writelines,   METH_O,       smisk_Response_writelines_DOC},
  {"set_cookie",  (PyCFunction)smisk_Response_set_cookie,   METH_VARARGS|METH_KEYWORDS,
                  smisk_Response_set_cookie_DOC},
  {"find_header", (PyCFunction)smisk_Response_find_header,  METH_O,       smisk_Response_find_header_DOC},
  {NULL, NULL, 0, NULL}
};

// Properties
static PyGetSetDef smisk_Response_getset[] = {
  {"headers", (getter)smisk_Response_get_headers, (setter)smisk_Response_set_headers,
    ":type: list", NULL},
  {NULL, NULL, NULL, NULL, NULL}
};

// Members
static struct PyMemberDef smisk_Response_members[] = {
  {"out",       T_OBJECT_EX, offsetof(smisk_Response, out), RO,
    ":type: `Stream`"},
  
  {"has_begun", T_OBJECT_EX, offsetof(smisk_Response, has_begun), RO,
    "Check if output (http headers & possible body content) has been sent to the client.\n"
    "\n"
    "True if `begin()` has been called and output has started, otherwise False.\n"
    "\n"
    ":type:   bool"},
  
  {NULL, 0, 0, 0, NULL}
};

// Type definition
PyTypeObject smisk_ResponseType = {
  PyObject_HEAD_INIT(&PyType_Type)
  0,                         /*ob_size*/
  "smisk.core.Response",             /*tp_name*/
  sizeof(smisk_Response),       /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  (destructor)smisk_Response_dealloc,        /* tp_dealloc */
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                         /*tp_compare*/
  0,                         /*tp_repr*/
  0,                         /*tp_as_number*/
  0,                         /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  0,                         /*tp_hash */
  (ternaryfunc)smisk_Response___call__,                         /*tp_call*/
  0,                         /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /*tp_flags*/
  smisk_Response_DOC,          /*tp_doc*/
  0,                         /* tp_traverse */
  0,                         /* tp_clear */
  0,                         /* tp_richcompare */
  0,                         /* tp_weaklistoffset */
  0,                         /* tp_iter */
  0,                         /* tp_iternext */
  smisk_Response_methods,      /* tp_methods */
  smisk_Response_members,      /* tp_members */
  smisk_Response_getset,       /* tp_getset */
  0,                           /* tp_base */
  0,                           /* tp_dict */
  0,                           /* tp_descr_get */
  0,                           /* tp_descr_set */
  0,                           /* tp_dictoffset */
  (initproc)smisk_Response_init, /* tp_init */
  0,                           /* tp_alloc */
  smisk_Response_new,           /* tp_new */
  0                            /* tp_free */
};

int smisk_Response_register_types(PyObject *module) {
  log_trace("ENTER");
  if (PyType_Ready(&smisk_ResponseType) == 0)
    return PyModule_AddObject(module, "Response", (PyObject *)&smisk_ResponseType);
  return -1;
}
