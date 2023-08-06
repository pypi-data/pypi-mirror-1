/***********************************************************
Copyright 1991-1995 by Stichting Mathematisch Centrum, Amsterdam,
The Netherlands.

                        All Rights Reserved

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation, and that the names of Stichting Mathematisch
Centrum or CWI or Corporation for National Research Initiatives or
CNRI not be used in advertising or publicity pertaining to
distribution of the software without specific, written prior
permission.

While CWI is the initial source for this software, a modified version
is made available by the Corporation for National Research Initiatives
(CNRI) at the Internet address ftp://ftp.python.org.

STICHTING MATHEMATISCH CENTRUM AND CNRI DISCLAIM ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL STICHTING MATHEMATISCH
CENTRUM OR CNRI BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL
DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.

******************************************************************/
/*
 * Python MQ Extension. Low level mqi wrappers. These present a
 * low-level interface to the MQI 'C' library. 
 *
 * Author: L. Smithson (lsmithson@open-networks.co.uk)
 * Author: Dariusz Suchojad (dsuch at gefira.pl)
 *
 * DISCLAIMER
 * You are free to use this code in any way you like, subject to the
 * Python & IBM disclaimers & copyrights. I make no representations
 * about the suitability of this software for any purpose. It is
 * provided "AS-IS" without warranty of any kind, either express or
 * implied. So there.
 *
 *
 */
 
static char __version__[] = "1.0.1";

static char pymqe_doc[] = " \
pymqe - A Python MQ Extension.  This presents a low-level Python \
interface to the MQI 'C' library. Its usage and conventions are more \
or less the same as the MQI 'C' language API. \
 \
MQI Connection & Object handles are passed around as Python \
longs. Structure parameters (such as MQGMO) are passed as Python \
string buffers. These buffers should be aligned & byte-ordered the \
same way the native 'C' compiler does. (Hint: use the Python struct.py \
package. See pymqi.py for an example). IN/OUT parameters are not\
updated in place, but returned as parameters in a tuple.\
\
All calls return the MQI completion code & reason as the last two\
elements of a tuple.\
\
The MQ verbs implemented here are:\
  MQCONN, MQCONNX, MQDISC, MQOPEN, MQCLOSE, MQPUT, MQPUT1, MQGET,\
  MQCMIT, MQBACK, MQBEGIN, MQINQ, MQSET\
\
The PCF MQAI call mqExecute is also implemented.\
\
The supported command levels (from 5.0 onwards) for the version of MQI \
linked with this module are available in the tuple pymqe.__mqlevels__. \
For a client build, pymqe.__mqbuild__ is set to the string 'client', otherwise \
it is set to 'server'.\
";


#include <cmqc.h>
#include <cmqxc.h>

/* 
 * 64bit suppport courtesy of Brent S. Elmer, Ph.D. (mailto:webe3vt@aim.com)
 * 
 * On 64 bit machines when MQ is compiled 64bit, MQLONG is an int defined
 * in /opt/mqm/inc/cmqc.h or wherever your MQ installs to.
 *
 * On 32 bit machines, MQLONG is a long and many other MQ data types are
 * set to MQLONG.
 */


/*
 * Setup features. MQ Version string is added to the pymqe dict so
 * that pymqi can find out what its been linked with.
 */
#ifdef MQCMDL_LEVEL_530
#define PYMQI_FEATURE_MQAI
#define PYMQI_FEATURE_SSL
#endif



#ifdef PYMQI_FEATURE_MQAI
#include <cmqcfc.h>
#include <cmqbc.h>
#endif

#include "Python.h"
static PyObject *ErrorObj;

/*
 * MQI Structure sizes for the current supported MQ version are
 * defined here for convenience. This allows older versions of pymqi
 * to work with newer versions of MQI.
 *
 * Current supported MQ Versions are 5.2. Known to work with 5.3
 */

#define PYMQI_MQCD_SIZEOF MQCD_CURRENT_LENGTH
#define PYMQI_MQOD_SIZEOF MQOD_CURRENT_LENGTH
#define PYMQI_MQMD_SIZEOF sizeof(MQMD)
#define PYMQI_MQPMO_SIZEOF MQPMO_CURRENT_LENGTH
#define PYMQI_MQGMO_SIZEOF sizeof(MQGMO)
#ifdef PYMQI_FEATURE_SSL
#define PYMQI_MQSCO_SIZEOF sizeof(MQSCO)
#endif

/* ----------------------------------------------------- */


static int checkArgSize(size_t given, size_t expected, const char *name) {
  if (given != expected) {
    PyErr_Format(ErrorObj, "%s wrong size. Given: %lu, expected %lu", name, (unsigned long)given, (unsigned long)expected);
    return 1;
  }
  return 0;
}

static char pymqe_MQCONN__doc__[] =
"MQCONN(mgrName) \
 \
Calls the MQI MQCONN(mgrName) function to connect the Queue Manager \
specified by the string mgrName. The tuple (handle, comp, reason) is \
returned. Handle should be passed to subsequent calls to MQOPEN, etc.\
";

static PyObject * pymqe_MQCONN(PyObject *self, PyObject *args) {
  char *name;
  MQHCONN handle;
  MQLONG compCode, compReason;
  
  if (!PyArg_ParseTuple(args, "s", &name)) {
    return NULL;
  }
  Py_BEGIN_ALLOW_THREADS
  MQCONN(name, &handle, &compCode, &compReason);
  Py_END_ALLOW_THREADS
  return Py_BuildValue("(lll)", (long) handle, (long) compCode, (long) compReason);
}

/*
 * MQCONNX code courtesy of John OSullivan (mailto:jos@onebox.com)
 * SSL additions couresy of Brian Vicente (mailto:sailbv@netscape.net)
 * Connect options suggested by Jaco Smuts (mailto:JSmuts@clover.co.za)
 */

static char pymqe_MQCONNX__doc__[] =
"MQCONNX(mgrName, options, mqcd, mqsco) \
 \
Calls the MQI MQCONNX(mgrName, options, mqcno) function to connect the Queue \
Manager specified by the string mgrName using options with the channel descriptor \
mqcd. The optional mqsco specifies SSL information. \
The tuple (handle, comp, reason) is returned. Handle should be \
passed to subsequent calls to MQOPEN, etc.\
 \
NOTE: The argument mqcd refers to the MQI MQCD structure, not MQCNO. \
";

static PyObject * pymqe_MQCONNX(PyObject *self, PyObject *args) {
  char*	name = 0;
  MQHCONN handle;
  MQLONG compCode, compReason;
  char*	mqcdBuf = 0;
  int mqcdBufLen = 0;
  MQCNO connectOpts = {MQCNO_DEFAULT};
  
  /*  Note: MQLONG is an int on 64 bit platforms and MQHCONN is an MQLONG
   */
  
  long lOptions = MQCNO_NONE;
  
#ifdef PYMQI_FEATURE_SSL
  char *mqscoBuf = 0;
  int mqscoBufLen = 0;

  if (!PyArg_ParseTuple(args, "sls#|s#", &name, &lOptions, &mqcdBuf, &mqcdBufLen, &mqscoBuf, &mqscoBufLen)) {
    return 0;
  }
  if (mqscoBuf && checkArgSize(mqscoBufLen, PYMQI_MQSCO_SIZEOF, "MQSCO")) {
    return NULL;
  }
#else
  if (!PyArg_ParseTuple(args, "sls#", &name, &lOptions, &mqcdBuf, &mqcdBufLen)) {
    return 0;
  }
#endif  

  if (checkArgSize(mqcdBufLen, PYMQI_MQCD_SIZEOF, "MQCD")) {
    return NULL;
  }
      
  /*
   * Setup client connection fields appropriate to the version of MQ
   * we've been built with.
   */
#ifdef PYMQI_FEATURE_SSL
  connectOpts.Version = MQCNO_VERSION_4;
  connectOpts.SSLConfigPtr =  (MQSCO*)mqscoBuf;
#else  
  connectOpts.Version = MQCNO_VERSION_2;
#endif 

  connectOpts.ClientConnPtr = (MQCD*)mqcdBuf;
  connectOpts.Options = (MQLONG) lOptions;
  
  Py_BEGIN_ALLOW_THREADS
  MQCONNX(name, &connectOpts, &handle, &compCode, &compReason);
  Py_END_ALLOW_THREADS
  return Py_BuildValue("(lll)", (long) handle, (long) compCode, (long) compReason);
}



static char pymqe_MQDISC__doc__[] =
"MQDISC(handle) \
 \
Calls the MQI MQDISC(handle) function to disconnect the Queue \
Manager. The tuple (comp, reason) is returned. \
";

static PyObject * pymqe_MQDISC(PyObject *self, PyObject *args) {
  MQHCONN handle;
  MQLONG compCode, compReason;
  
  /*  Note: MQLONG is an int on 64 bit platforms and MQHCONN is an MQLONG
   */
  
  long lHandle;
  
  if (!PyArg_ParseTuple(args, "l", &lHandle)) {
    return NULL;
  }
  handle = (MQHCONN) lHandle;
  
  Py_BEGIN_ALLOW_THREADS
  MQDISC(&handle, &compCode, &compReason);
  Py_END_ALLOW_THREADS
  return Py_BuildValue("(ll)", (long) compCode, (long) compReason);
}


static char pymqe_MQOPEN__doc__[] =
"MQOPEN(qMgr, qDesc, options) \
\
Calls the MQI MQOPEN(qMgr, qDesc, options) function to open the queue \
specified by the MQOD structure in the string buffer qDesc. QMgr is \
the Queue Manager handled returned by an earlier call to \
MQCONN. Options are the options for opening the Queue. \
 \
The tuple (qHandle, qDesc, comp, reason) is returned, where qHandle is \
the Queue Handle for the open queue and qDesc is the (possibly) \
updated copy of the Queue MQOD structure. \
 \
If qDesc is not the size expected for an MQOD structure, an exception \
is raised. \
" ;

static PyObject *pymqe_MQOPEN(PyObject *self, PyObject *args) {
  
  MQOD *qDescP;
  char *qDescBuffer;
  int qDescBufferLength;
  MQHOBJ qHandle;
  MQLONG compCode, compReason;

  long lOptions, lQmgrHandle;

  if (!PyArg_ParseTuple(args, "ls#l", &lQmgrHandle, &qDescBuffer,
			&qDescBufferLength, &lOptions)) {
    return NULL;
  }
  
  qDescP = (MQOD *)qDescBuffer;
  if (checkArgSize(qDescBufferLength, PYMQI_MQOD_SIZEOF, "MQOD")) {
    return NULL;
  }
  
  Py_BEGIN_ALLOW_THREADS
    MQOPEN((MQHCONN)lQmgrHandle, qDescP, (MQLONG) lOptions, &qHandle, &compCode, &compReason);
  Py_END_ALLOW_THREADS
  return Py_BuildValue("(ls#ll)", (long) qHandle, qDescP,
                       PYMQI_MQOD_SIZEOF, (long) compCode, (long) compReason);
}



static char pymqe_MQCLOSE__doc__[] =
"MQCLOSE(qMgr, qHandle, options) \
 \
Calls the MQI MQCLOSE(qMgr, qHandle, options) function to close the \
queue referenced by qMgr & qHandle. The tuple (comp, reason), is \
returned. \
";

static PyObject * pymqe_MQCLOSE(PyObject *self, PyObject *args) {
  MQHOBJ qHandle;
  MQLONG compCode, compReason;
  
  /* Note: MQLONG is an int on 64 bit platforms and MQHCONN and MQHOBJ are MQLONG
   */

  long lOptions, lQmgrHandle, lqHandle;
  
  if (!PyArg_ParseTuple(args, "lll", &lQmgrHandle, &lqHandle, &lOptions)) {
    return NULL;
  }
  qHandle = (MQHOBJ) lqHandle;

  Py_BEGIN_ALLOW_THREADS
  MQCLOSE((MQHCONN) lQmgrHandle, &qHandle, (MQLONG) lOptions, &compCode, &compReason);
  Py_END_ALLOW_THREADS
  return Py_BuildValue("(ll)", (long) compCode, (long) compReason);
}


/*
 * Internal function that calls either PUT or PUT1 according to the
 * put1Flag arg
 */
static PyObject *mqputN(int put1Flag, PyObject *self, PyObject *args) {
  MQLONG compCode, compReason;
  char *mDescBuffer;
  int mDescBufferLength;
  MQMD *mDescP;
  char *putOptsBuffer;
  int putOptsBufferLength;
  MQPMO *pmoP;
  char *msgBuffer;
  int msgBufferLength;
  char *qDescBuffer;
  int qDescBufferLength;
  MQOD *qDescP = NULL;

  long lQmgrHandle, lqHandle;

  if (!put1Flag) {
    /* PUT call, expects qHandle for an open q */
    if (!PyArg_ParseTuple(args, "lls#s#s#", &lQmgrHandle, &lqHandle,
			  &mDescBuffer, &mDescBufferLength,
			  &putOptsBuffer, &putOptsBufferLength,
			  &msgBuffer, &msgBufferLength)) {
      return NULL;
    }
  } else {
    /* PUT1 call, expects od for a queue to be opened */
    if (!PyArg_ParseTuple(args, "ls#s#s#s#", &lQmgrHandle,
			  &qDescBuffer, &qDescBufferLength,
			  &mDescBuffer, &mDescBufferLength,
			  &putOptsBuffer, &putOptsBufferLength,
			  &msgBuffer, &msgBufferLength)) {
      return NULL;

    }
    if (checkArgSize(qDescBufferLength, PYMQI_MQOD_SIZEOF, "MQOD")) {
      return NULL;
    }
    qDescP = (MQOD *)qDescBuffer;
  }
  
  if (checkArgSize(mDescBufferLength, PYMQI_MQMD_SIZEOF, "MQMD")) {
    return NULL;
  }
  mDescP = (MQMD *)mDescBuffer;

  if (checkArgSize(putOptsBufferLength, PYMQI_MQPMO_SIZEOF, "MQPMO")) {
    return NULL;
  }
  pmoP = (MQPMO *)putOptsBuffer;
  if (!put1Flag) {
    Py_BEGIN_ALLOW_THREADS
    MQPUT((MQHCONN) lQmgrHandle, (MQHOBJ) lqHandle, mDescP, pmoP, (MQLONG) msgBufferLength, msgBuffer,
	  &compCode, &compReason);
    Py_END_ALLOW_THREADS
  } else {
    Py_BEGIN_ALLOW_THREADS
    MQPUT1((MQHCONN) lQmgrHandle, qDescP, mDescP, pmoP, (MQLONG) msgBufferLength, msgBuffer,
	   &compCode, &compReason);
    Py_END_ALLOW_THREADS
  }
  return Py_BuildValue("(s#s#ll)", mDescP, PYMQI_MQMD_SIZEOF,
		       pmoP, PYMQI_MQPMO_SIZEOF, (long) compCode, (long) compReason);
}


static char pymqe_MQPUT__doc__[] = 
"MQPUT(qMgr, qHandle, mDesc, options, msg) \
 \
Calls the MQI MQPUT(qMgr, qHandle, mDesc, putOpts, msg) function to \
put msg on the queue referenced by qMgr & qHandle. The message msg may \
contain embedded nulls. mDesc & putOpts are string buffers containing \
a MQMD Message Descriptor structure and a MQPMO Put Message Option \
structure. \
 \
The tuple (mDesc, putOpts, comp, reason) is returned, where mDesc & \
putOpts are the (possibly) updated copies of the MQMD & MQPMO \
structures. \
 \
If either mDesc or putOpts are the wrong size, an exception is raised. \
";

static PyObject *pymqe_MQPUT(PyObject *self, PyObject *args) {
  return mqputN(0, self, args);
}


static char pymqe_MQPUT1__doc__[] = 
"MQPUT1(qMgr, qDesc, mDesc, options, msg) \
 \
Calls the MQI MQPUT1(qMgr, qDesc, mDesc, putOpts, msg) function to put \
the message msg on the queue referenced by qMgr & qDesc. The message \
msg may contain embedded nulls. mDesc & putOpts are string buffers \
containing a MQMD Message Descriptor structure and a MQPMO Put Message \
Option structure. \
 \
The tuple (mDesc, putOpts, comp, reason) is returned, where mDesc & \
putOpts are the (possibly) updated copies of the MQMD & MQPMO \
structures. \
 \
MQPUT1 is the optimal way to put a single message on a queue. It is \
equivalent to calling MQOPEN, MQPUT and MQCLOSE. \
 \
If any of qDesc, mDesc or putOpts are the wrong size, an exception is \
raised. \
";

static PyObject *pymqe_MQPUT1(PyObject *self, PyObject *args) {
  return mqputN(1, self, args);
}


static char pymqe_MQGET__doc__[] = 
"MQGET(qMgr, qHandle, mDesc, getOpts, maxlen) \
 \
Calls the MQI MQGET(qMgr, qHandle, mDesc, getOpts, maxlen) function to \
get a message from the queue referred to by qMgr & qHandle.  mDesc & \
getOpts are string buffers containing a MQMD Message Descriptor and a \
MQGMO Get Message Options structure. maxlen specified the maximum \
length of messsage to read from the queue. If the message length \
exceeds maxlen, the the behaviour is as defined by MQI. \
 \
The tuple (msg, mDesc, getOpts, actualLen, comp, reason) is returned, \
where msg is a string containing the message read from the queue and \
mDesc & getOpts are copies of the (possibly) updated MQMD & MQGMO \
structures. actualLen is the actual length of the message in the \
Queue. If this is bigger than maxlen, then as much data as possible is \
copied into the return buffer. In this case, the message may or may \
not be removed from the queue, depending on the MQGMO options. See the \
MQI APG/APR for more details. \
 \
If mDesc or getOpts are the wrong size, an exception is raised. \
";

static PyObject *pymqe_MQGET(PyObject *self, PyObject *args) {
  MQLONG compCode, compReason;
  char *mDescBuffer;
  int mDescBufferLength;
  MQMD *mDescP;
  char *getOptsBuffer;
  int getOptsBufferLength;
  MQGMO *gmoP;
  long maxLength, returnLength;
  MQLONG actualLength;
  char *msgBuffer;
  PyObject *rv;

  long lQmgrHandle, lqHandle;

  if (!PyArg_ParseTuple(args, "lls#s#l", &lQmgrHandle, &lqHandle,
			&mDescBuffer, &mDescBufferLength,
			&getOptsBuffer, &getOptsBufferLength, &maxLength)) {
    return NULL;
  }
  if (checkArgSize(mDescBufferLength, PYMQI_MQMD_SIZEOF, "MQMD")) {
    return NULL;
  }

  mDescP = (MQMD *)mDescBuffer;

  if (checkArgSize(getOptsBufferLength, PYMQI_MQGMO_SIZEOF, "MQGMO")) {
    return NULL;
  }
  gmoP = (MQGMO *)getOptsBuffer;

  /* Allocate temp. storage for message */
  if (!(msgBuffer = malloc(maxLength))) {
    PyErr_SetString(ErrorObj, "No memory for message");
    return NULL;
  }
  actualLength = 0;
  Py_BEGIN_ALLOW_THREADS
  MQGET((MQHCONN) lQmgrHandle, (MQHOBJ) lqHandle, mDescP, gmoP, (MQLONG) maxLength, msgBuffer, &actualLength,
	&compCode, &compReason);
  Py_END_ALLOW_THREADS

  /*
   * Message may be too big for caller's buffer, so only copy in as
   * much data as will fit, but return the actual length of the
   * message. Thanks to Maas-Maarten Zeeman for this fix.
   */
  if(actualLength >= maxLength) {
    returnLength = maxLength;
  } else {
    returnLength = actualLength;
  }
  
  rv = Py_BuildValue("(s#s#s#lll)", msgBuffer, (int) returnLength,
		     mDescP, PYMQI_MQMD_SIZEOF, gmoP, PYMQI_MQGMO_SIZEOF,
		     (long) actualLength, (long) compCode, (long) compReason);
  free(msgBuffer);
  return rv;
}


static char pymqe_MQBEGIN__doc__[] =
"MQBEGIN(handle)  \
\
Calls the MQI MQBEGIN(handle) function to begin a new global \
transaction. This is used in conjunction with MQ coodinated \
Distributed Transactions and XA resources. \
 \
The tuple (comp, reason) is returned.\
";

static PyObject * pymqe_MQBEGIN(PyObject *self, PyObject *args) {
  MQLONG compCode, compReason;
  MQBO beginOpts = {MQBO_DEFAULT};

  long lHandle;

  if (!PyArg_ParseTuple(args, "l", &lHandle)) {
    return NULL;
  }
  Py_BEGIN_ALLOW_THREADS
  MQBEGIN((MQHCONN) lHandle, &beginOpts, &compCode, &compReason);
  Py_END_ALLOW_THREADS
  return Py_BuildValue("(ll)", (long) compCode, (long) compReason);
}


static char pymqe_MQCMIT__doc__[] =
"MQCMIT(handle) \
 \
Calls the MQI MQCMIT(handle) function to commit any pending gets or \
puts in the current unit of work. The tuple (comp, reason) is \
returned. \
";

static PyObject * pymqe_MQCMIT(PyObject *self, PyObject *args) {
  MQLONG compCode, compReason;
  
  long lHandle;
  
  if (!PyArg_ParseTuple(args, "l", &lHandle)) {
    return NULL;
  }
  Py_BEGIN_ALLOW_THREADS
  MQCMIT((MQHCONN) lHandle, &compCode, &compReason);
  Py_END_ALLOW_THREADS
  return Py_BuildValue("(ll)", (long) compCode, (long) compReason);
}

static char pymqe_MQBACK__doc__[] =
"MQBACK(handle) \
 \
Calls the MQI MQBACK(handle) function to backout any pending gets or \
puts in the current unit of work. The tuple (comp, reason) is \
returned. \
";

static PyObject * pymqe_MQBACK(PyObject *self, PyObject *args) {
  MQLONG compCode, compReason;
  
  long lHandle;
  
  if (!PyArg_ParseTuple(args, "l", &lHandle)) {
    return NULL;
  }
  Py_BEGIN_ALLOW_THREADS
  MQBACK((MQHCONN) lHandle, &compCode, &compReason);
  Py_END_ALLOW_THREADS
  return Py_BuildValue("(ll)", (long) compCode, (long) compReason);
}


/*
 * MQINQ Interface. Only supports Inquire of single attribute.
 */
static char pymqe_MQINQ__doc__[] =
"MQINQ(qMgr, handle, selector) \
\
Calls MQINQ with a single attribute. Returns the value of that \
attribute. \
";

/*
 * This figure plucked out of thin air + 1 added for null. Doesn't
 * look like there's anything bigger than this in cmqc.h. I'm sure
 * someone will tell me if I'm wrong.
 */
#define MAX_CHARATTR_LENGTH 129

static PyObject *pymqe_MQINQ(PyObject *self, PyObject *args) {
  MQLONG compCode, compReason;
  MQLONG selectorCount = 1;
  MQLONG selectors[1];
  MQLONG intAttrCount = 0;
  MQLONG intAttrs[1];
  MQLONG charAttrCount = 0;
  MQCHAR charAttrs[MAX_CHARATTR_LENGTH];
  PyObject *retVal = NULL;
  
  long lQmgrHandle, lObjHandle, lSelectors[1];

  if (!PyArg_ParseTuple(args, "lll", &lQmgrHandle, &lObjHandle, lSelectors)) {
    return NULL;
  }
  selectors[0] = (MQLONG) lSelectors[0];
  
  if ((selectors[0] >= MQIA_FIRST) && (selectors[0] <= MQIA_LAST)) {
    intAttrCount = 1;
  } else {
    charAttrCount = sizeof(charAttrs) -1;
    memset(charAttrs, 0, sizeof(charAttrs));
  }
  
  Py_BEGIN_ALLOW_THREADS
  MQINQ((MQHCONN) lQmgrHandle, (MQHOBJ) lObjHandle, selectorCount, selectors,
        intAttrCount, intAttrs, charAttrCount, charAttrs, &compCode, &compReason);
  Py_END_ALLOW_THREADS

  if (intAttrCount) {
    retVal = Py_BuildValue("(lll)", (long) intAttrs[0], (long) compCode, (long) compReason);
  } else {
    retVal = Py_BuildValue("(sll)", charAttrs, (long) compCode, (long) compReason);
  }
  return retVal;
}

/*
 * MQSET Interface. Only supports Set of single attribute.
 */
static char pymqe_MQSET__doc__[] =
"MQSET(qMgr, handle, selector, val) \
 \
Calls MQSET with a single selector and attribute. \
";

static PyObject *pymqe_MQSET(PyObject *self, PyObject *args) {
  MQLONG compCode, compReason;
  MQLONG selectorCount = 1;
  MQLONG selectors[1];
  MQLONG intAttrCount = 0;
  MQLONG intAttrs[1];
  MQLONG charAttrCount = 0;
  MQCHAR charAttrs[MAX_CHARATTR_LENGTH];
  PyObject *attrArg = NULL;
  
  long lQmgrHandle, lObjHandle, lSelectors[1];

  if (!PyArg_ParseTuple(args, "lllO", &lQmgrHandle, &lObjHandle, lSelectors, &attrArg)) {
    return NULL;
  }
  selectors[0] = (MQLONG) lSelectors[0];

  if ((selectors[0] >= MQIA_FIRST) && (selectors[0] <= MQIA_LAST)) {
    if (!PyLong_Check(attrArg)) {
      PyErr_SetString(ErrorObj, "Arg is not a long integer");
      return NULL;
    }
    intAttrs[0] = PyLong_AsLong(attrArg);
    intAttrCount = 1;
  } else {
    if (!PyString_Check(attrArg)) {
      PyErr_SetString(ErrorObj, "Arg is not a string");
      return NULL;
    }
    strncpy(charAttrs, PyString_AsString(attrArg), MAX_CHARATTR_LENGTH);
    charAttrCount = strlen(charAttrs);
  }
  
  Py_BEGIN_ALLOW_THREADS
  MQSET((MQHCONN) lQmgrHandle, (MQHOBJ) lObjHandle, selectorCount, selectors,
        intAttrCount, intAttrs, charAttrCount, charAttrs, &compCode, &compReason);
  Py_END_ALLOW_THREADS
  return Py_BuildValue("(ll)", (long) compCode, (long) compReason);
}


#ifdef PYMQI_FEATURE_MQAI


static void cleanupBags(MQHBAG adminBag, MQHBAG responseBag) {
  MQLONG compCode, compReason;
  if (adminBag != MQHB_UNUSABLE_HBAG) {
    mqDeleteBag(&adminBag, &compCode, &compReason);
  }
  if (responseBag != MQHB_UNUSABLE_HBAG) {
    mqDeleteBag(&responseBag, &compCode, &compReason);
  }
}

static char pymqe_mqaiExecute__doc__[] =
"mqaiExecute(qMgr, cmd, args)\
\
Execute the PCF command 'cmd' on Queue Manager 'qMgr', with the \
optional dictionary 'args'.  The command is a MQCMD_* code from \
cmqcfc.h. The argument dictionary keys are the MQ[C|I]AC* codes from \
cmqcfc.h. The dictionary values are either int or string, as \
appropriate for the command. \
 \
The tuple (resultList, compCode, compReason) is returned. The \
resultsList is a list of zero or more dictionaries for each of the \
matching results. \
";

static PyObject *pymqe_mqaiExecute(PyObject *self, PyObject *args) {
    PyObject* argDict = 0;
    MQLONG compCode, compReason;
    PyObject *argKeys;
    MQHBAG adminBag = MQHB_UNUSABLE_HBAG;  
    MQHBAG responseBag = MQHB_UNUSABLE_HBAG;
    MQHBAG resultBag;
    PyObject *resultsList;

    long lQmgrHandle, lCmdCode;
  
    if(!PyArg_ParseTuple(args, "ll|O", &lQmgrHandle, &lCmdCode, &argDict)) {
        return NULL;
    }
    
    if(argDict && !PyDict_Check(argDict)) {
        PyErr_SetString(ErrorObj, "args is not a dictionary");
        return NULL;
    }

    resultsList = PyList_New(0);  /* Owned ref */
    if(!resultsList) {
        PyErr_SetString(ErrorObj, "Can't create results list");
        return NULL;
    }
  
    do {

        /*
         * Create request + response bags
         */
        mqCreateBag(MQCBO_ADMIN_BAG, &adminBag, &compCode, &compReason);
        if(compCode != MQCC_OK) {
            break;
        }
        
        mqCreateBag(MQCBO_ADMIN_BAG, &responseBag, &compCode, &compReason);
        if (compCode != MQCC_OK) {
            break;
        }
        
        /*
         * For each arg key/value pair, create the appopriate type and add
         * it to the bag.
         */
        argKeys = PyDict_Keys(argDict);
        if(argDict && (argKeys)) {
            
            MQLONG paramType = 0;
            MQLONG intArg = 0;
            MQCHAR *strArg = "";
            
            int nKeys = PyList_Size(argKeys); /* Owned ref */ 
            int i;
        
            for(i = 0; i < nKeys; i++) {
                PyObject *key = PyList_GetItem(argKeys, i);      /* Borrowed ref */
                PyObject *value = PyDict_GetItem(argDict, key);  /* Borrowed ref */
        
                /*
                 * The key ought to be a int or long. Blow up if it isn't
                 */
                if(!PyLong_Check(key) && !PyInt_Check(key)) {
                    PyObject *keyStr = PyObject_Str(key);  /* Owned ref */
                    PyErr_Format(ErrorObj, "Argument: %s is not integer", PyString_AsString(keyStr));
                    Py_XDECREF(keyStr);
                    Py_DECREF(resultsList);
                    cleanupBags(adminBag, responseBag);
                    return NULL;
                }
                else {
                    paramType = PyLong_Check(key) ? PyLong_AsLong(key) : PyInt_AsLong(key);
                }
            
                /*
                 * Now get the value. It must be either a int/long or a string.
                 */
                 if (PyLong_Check(value)) {
                     intArg = PyLong_AsLong(value);
                     mqAddInteger(adminBag, paramType, intArg, &compCode, &compReason);
                 } else if (PyInt_Check(value)) {
                     intArg = PyInt_AsLong(value);
                     mqAddInteger(adminBag, paramType, intArg, &compCode, &compReason);
                 }
                 else if (PyString_Check(value)) {
                     strArg = PyString_AsString(value);
                     mqAddString(adminBag, paramType, MQBL_NULL_TERMINATED, strArg, &compCode, &compReason); 
                } else {
                    PyObject *keyStr = PyObject_Str(key);    /* Owned ref */
                    PyObject *valStr = PyObject_Str(value);  /* Owned ref */
                    PyErr_Format(ErrorObj, "Value %s for key %s is neither a long or string",
                                 PyString_AsString(valStr), PyString_AsString(keyStr));
                    Py_XDECREF(keyStr);
                    Py_XDECREF(valStr);
                    Py_DECREF(resultsList);
                    cleanupBags(adminBag, responseBag);
                    return NULL;
               }
               if(compCode != MQCC_OK) {
                   break;
               }
            }
        }
        Py_XDECREF(argKeys);

        /*
         * Everything bagged up -- Now execute the command
         */
        Py_BEGIN_ALLOW_THREADS
            mqExecute((MQHCONN) lQmgrHandle, (MQLONG) lCmdCode, MQHB_NONE, adminBag, responseBag,
                      MQHO_NONE, MQHO_NONE, &compCode, &compReason);
        Py_END_ALLOW_THREADS
        
        if(compCode != MQCC_OK) {
            /*
             * If the command execution failed at the Queue Manager, get
             * the code & reason out and return them as an error.
             */
            if(compReason == MQRCCF_COMMAND_FAILED) {
                mqInquireBag(responseBag, MQHA_BAG_HANDLE, 0, &resultBag, &compCode, &compReason);
                if(compCode == MQCC_OK) {
                    MQLONG mgrCompCode, mgrReasonCode;
                    mqInquireInteger(resultBag, MQIASY_COMP_CODE, MQIND_NONE, &mgrCompCode, &compCode, &compReason);
                    mqInquireInteger(resultBag, MQIASY_REASON, MQIND_NONE, &mgrReasonCode, &compCode, &compReason);
                    if (compCode == MQCC_OK) {
                        compCode = mgrCompCode;
                        compReason = mgrReasonCode;
                    }
                }
            }
        break;
        }
        
        else {
            /*
             * Command executed OK. Get each user bag (if any) from the
             * response, then get its contents. There is a bag for each
             * matching result. Each bag gets a new dictionary, which is
             * appended to the results list.
             */
             MQLONG numberOfBags;
             mqCountItems(responseBag, MQHA_BAG_HANDLE, &numberOfBags, &compCode, &compReason);
             
             if(compCode != MQCC_OK) {
                 break;
             }
             
             else {
                int i;
                for (i = 0; i < numberOfBags; i++) {
                    MQHBAG attrsBag;
                    mqInquireBag(responseBag, MQHA_BAG_HANDLE, i, &attrsBag, &compCode, &compReason);
                    
                    if (compCode != MQCC_OK) {
                        break;
                    }
                    
                    else {
                        /*
                         * Query each item in the bag to find its type. We're
                         * not interested in PCF System/bag stuff, we only want
                         * the user stuff.
                         */
                        MQLONG numberOfItems;
                        mqCountItems(attrsBag, MQSEL_ALL_USER_SELECTORS, &numberOfItems, &compCode, &compReason);
                        
                        if(compCode != MQCC_OK) {
                            break;
                        } 
                        
                        else {
                            
                            int j;
                            MQLONG itemType;
                            MQLONG selector;
                            PyObject *resultsDict = PyDict_New();  /* Owned ref - returned to interp */
                  
                            if(!resultsDict) {
                                PyErr_SetString(ErrorObj, "Can't make results dict");
                                cleanupBags(adminBag, responseBag);
                                Py_DECREF(resultsList);
                                return NULL;
                            }
                    
                            for(j = 0; j < numberOfItems; j++) {
                                /*
                                 * Dratted IBM docs have the selector & itemType params swapped!
                                 */
                                mqInquireItemInfo(attrsBag, MQSEL_ANY_USER_SELECTOR, j, &selector, &itemType, &compCode, &compReason);
                                if(compCode != MQCC_OK) {
                                    break;
                                }
                                else {
                                    /*
                                     * The selector is the key, value depends on the
                                     * type from the bag.
                                     * Key and Value objects return ownded refs, but
                                     * these are 'stolen' when added to the dict.
                                     */
                                    PyObject *key = PyLong_FromLong(selector);  /* Owned ref */
                                    
                                    if(!key) {
                                        PyErr_SetString(ErrorObj, "Can't make results dict key");
                                        cleanupBags(adminBag, responseBag);
                                        Py_DECREF(resultsList);
                                        Py_XDECREF(resultsDict);
                                        return NULL;
                                    }
                                    
                                    if(itemType == MQIT_INTEGER) {
                                        MQLONG itemIntVal;
                                        mqInquireInteger(attrsBag, MQSEL_ANY_USER_SELECTOR, j, &itemIntVal, &compCode, &compReason);
                                        
                                        PyObject *pyItemIntVal = PyLong_FromLong(itemIntVal);
                                        PyDict_SetItem(resultsDict, key, pyItemIntVal);
                                        
                                        Py_XDECREF(pyItemIntVal);
                                        Py_XDECREF(key);
                                    }
                                    
                                    else if(itemType == MQIT_STRING) {
                                        
                                        MQCHAR *itemStrVal;
                                        MQLONG strLength;
                                        /*
                                         * Two calls are needed - one to get the string
                                         * length, and one to get the string itself.
                                         */
                                         
                                        /* 1st call */ 
                                        mqInquireString(attrsBag, MQSEL_ANY_USER_SELECTOR, j, 0, 0, &strLength, 0, &compCode, &compReason);
                                        
                                        if(compCode != MQCC_OK && compReason != MQRC_STRING_TRUNCATED) {
                                            break;
                                        }
                                        
                                        strLength++;   /* + one for the Null */
                                        
                                        if(!(itemStrVal = malloc(strLength))) {
                                            PyErr_SetString(ErrorObj, "Out of memory");
                                            cleanupBags(adminBag, responseBag);
                                            Py_DECREF(resultsList);
                                            Py_XDECREF(resultsDict);
                                            Py_XDECREF(key);
                                            return NULL;
                                        }
                                        
                                        /* 2nd call */
                                        mqInquireString(attrsBag, MQSEL_ANY_USER_SELECTOR, j, strLength, itemStrVal,
                                                        &strLength, 0, &compCode, &compReason);
                                        
                                        if(compCode != MQCC_OK) {
                                            break;
                                        }
                                        
                                        itemStrVal[strLength] = 0;
                                        
                                        PyObject *pyItemStrVal = PyString_FromString(itemStrVal);
                                        PyDict_SetItem(resultsDict, key, pyItemStrVal);
                                        
                                        free(itemStrVal);
                                        Py_XDECREF(key);
                                        Py_XDECREF(pyItemStrVal);
                                        
                                    }
                                    else {
                                        /*
                                         * Must be a bag. What to do? Maybe recurse into it?
                                         */
                                        PyErr_SetString(ErrorObj, "Bag in a Bag. Send clue to les@open-networks.co.uk");
                                        cleanupBags(adminBag, responseBag);
                                        Py_XDECREF(key);
                                        Py_DECREF(resultsList);
                                        return NULL;
                                    }
                                }
                            }
                            
                        /*
                         * Append the results to the returned list
                         */
                        PyList_Append(resultsList, resultsDict);
                        Py_XDECREF(resultsDict);
                        }
                    }
                }
            }
        }
        break;
    
    } while (1);
    cleanupBags(adminBag, responseBag);
    
    PyObject *returnValue = Py_BuildValue("(Oll)", resultsList, (long) compCode, (long) compReason);
    Py_XDECREF(resultsList);
    
    return returnValue;
}



#endif


/* List of methods defined in the module */

static struct PyMethodDef pymqe_methods[] = {
  {"MQCONN", (PyCFunction)pymqe_MQCONN,	METH_VARARGS, pymqe_MQCONN__doc__},
  {"MQCONNX", (PyCFunction)pymqe_MQCONNX, METH_VARARGS, pymqe_MQCONNX__doc__},
  {"MQDISC", (PyCFunction)pymqe_MQDISC,	METH_VARARGS, pymqe_MQDISC__doc__},
  {"MQOPEN", (PyCFunction)pymqe_MQOPEN,	METH_VARARGS, pymqe_MQOPEN__doc__},
  {"MQCLOSE", (PyCFunction)pymqe_MQCLOSE, METH_VARARGS, pymqe_MQCLOSE__doc__},
  {"MQPUT", (PyCFunction)pymqe_MQPUT, METH_VARARGS, pymqe_MQPUT__doc__},
  {"MQPUT1", (PyCFunction)pymqe_MQPUT1, METH_VARARGS, pymqe_MQPUT1__doc__},
  {"MQGET", (PyCFunction)pymqe_MQGET, METH_VARARGS, pymqe_MQGET__doc__},
  {"MQBEGIN", (PyCFunction)pymqe_MQBEGIN, METH_VARARGS, pymqe_MQBEGIN__doc__},
  {"MQCMIT", (PyCFunction)pymqe_MQCMIT, METH_VARARGS, pymqe_MQCMIT__doc__},
  {"MQBACK", (PyCFunction)pymqe_MQBACK, METH_VARARGS, pymqe_MQBACK__doc__},
  {"MQINQ", (PyCFunction)pymqe_MQINQ, METH_VARARGS, pymqe_MQINQ__doc__},
  {"MQSET", (PyCFunction)pymqe_MQSET, METH_VARARGS, pymqe_MQSET__doc__},
#ifdef  PYMQI_FEATURE_MQAI
  {"mqaiExecute", (PyCFunction)pymqe_mqaiExecute, METH_VARARGS, pymqe_mqaiExecute__doc__},
#endif
  {NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};


/* Initialization function for the module (*must* be called initpymqe) */

static char pymqe_module_documentation[] = 
""
;

#ifdef WIN32
__declspec(dllexport)
#endif
     void initpymqe(void) {
  PyObject *m, *d;
	
  /* Create the module and add the functions */
  m = Py_InitModule4("pymqe", pymqe_methods,
		     pymqe_module_documentation,
		     (PyObject*)NULL,PYTHON_API_VERSION);

  /* Add some symbolic constants to the module */
  d = PyModule_GetDict(m);
  ErrorObj = PyErr_NewException("pymqe.error", NULL, NULL);
  PyDict_SetItemString(d, "pymqe.error", ErrorObj);

  PyDict_SetItemString(d, "__doc__", PyString_FromString(pymqe_doc)); 
  PyDict_SetItemString(d,"__version__", PyString_FromString(__version__));

  /*
   * Build the tuple of supported command levels, but only for versions
   *  5.* onwards
   */
  {
    PyObject *versions = PyList_New(0);
#ifdef MQCMDL_LEVEL_500
      PyList_Append(versions, PyString_FromString("5.0"));
#endif      
#ifdef MQCMDL_LEVEL_510
      PyList_Append(versions, PyString_FromString("5.1"));
#endif      
#ifdef MQCMDL_LEVEL_520
      PyList_Append(versions, PyString_FromString("5.2"));
#endif      
#ifdef MQCMDL_LEVEL_530
      PyList_Append(versions, PyString_FromString("5.3"));
#endif
#ifdef MQCMDL_LEVEL_600
      PyList_Append(versions, PyString_FromString("6.0"));
#endif
#ifdef MQCMDL_LEVEL_700
      PyList_Append(versions, PyString_FromString("7.0"));
#endif
      PyDict_SetItemString(d,"__mqlevels__", PyList_AsTuple(versions));
      Py_XDECREF(versions);
  }

  /*
   * Set the client/server build flag
   */
#if PYQMI_SERVERBUILD == 1 
  PyDict_SetItemString(d,"__mqbuild__", PyString_FromString("server"));
#else
  PyDict_SetItemString(d,"__mqbuild__", PyString_FromString("client"));
#endif
  
  /* Check for errors */
  if (PyErr_Occurred())
    Py_FatalError("can't initialize module pymqe");
}

