/* 
 * credential.c - source for the Credential object
 *
 * Copyright 2009 - Benjamin Montgomery (bmontgom@montynet.org)
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

#include <krb5.h>
#include "Python.h"
#include "structmember.h"
#include "python-krb5.h"
#include "error.h"
#include "principal.h"
#include "credential.h"

/**
 * Function to get values from the krb_creds struct.
 */
static PyObject *Credential_get(Credential *self, void *closure)
{
	char *temp;
	char *op = (char *)closure;
	PyObject *attr;
	PyObject *datetime_mod = NULL;
	PyObject *datetime_class = NULL;
	krb5_error_code retval;

	/* check if Credential has been initialized */
	if (self->cred == NULL) {
		PyErr_SetString(PyExc_RuntimeError, "Credential not initialized");
		return NULL;
	}
	
	/* get the client name */
	if (strcmp(op, "client") == 0) {
		if ((retval = krb5_unparse_name(module_context, self->cred->client, &temp))) {
			return python_krb5_error(retval);
		}
		attr = PyString_FromString(temp);
		krb5_free_unparsed_name(module_context, temp);
		return attr;
	}

	/* get the server name */
	if (strcmp(op, "server") == 0) {
		if ((retval = krb5_unparse_name(module_context, self->cred->server, &temp))) {
			return python_krb5_error(retval);
		}
		attr = PyString_FromString(temp);
		krb5_free_unparsed_name(module_context, temp);
		return attr;
	}

	/* load the datetime module since the remaining attributes require it */
	if ((datetime_mod = PyImport_ImportModule("datetime")) == NULL) {
		return NULL;
	}
	
	if ((datetime_class = PyObject_GetAttrString(datetime_mod, "datetime")) == NULL ) {
		return NULL;
	}
	
	/* get the ticket's start time */
	if (strcmp(op, "starttime") == 0) {
		if (!self->cred->times.starttime) {
			self->cred->times.starttime = self->cred->times.authtime;
		}
		attr = PyObject_CallMethod(datetime_class, "fromtimestamp", "i", self->cred->times.starttime);
		Py_DECREF(datetime_mod);
		Py_DECREF(datetime_class);
		if (attr == NULL) {
			return NULL;
		}
		else {
			return attr;
		}
	}

	/* get the ticket's end time */
	if (strcmp(op, "endtime") == 0) {
		attr = PyObject_CallMethod(datetime_class, "fromtimestamp", "i", self->cred->times.endtime);
		Py_DECREF(datetime_mod);
		Py_DECREF(datetime_class);
		if (attr == NULL) {
			return NULL;
		}
		else {
			return attr;
		}

	}

	/* get the ticket's renewal time */
	if (strcmp (op, "renewtime") == 0) {
		attr = PyObject_CallMethod(datetime_class, "fromtimestamp", "i", self->cred->times.renew_till);
		Py_DECREF(datetime_mod);
		Py_DECREF(datetime_class);
		if (attr == NULL) {
			return NULL;
		}
		else {
			return attr;
		}
	}

	/* if execution gets here, this is an error */
	PyErr_SetString(PyExc_RuntimeError, "request for unknown Credential attribute");
	return NULL;
}

/**
 * Get the encryption type of the ticket in this credential.
 *
 * Returns a python string of the type of ticket.
 */
static PyObject *Credential_get_enctype(Credential *self, PyObject *args /* = NULL */) {
	switch (self->cred->keyblock.enctype) {
	case ENCTYPE_NULL:
		return PyString_FromString("NULL");
	case ENCTYPE_DES_CBC_CRC:
        	return PyString_FromString("DES-CBC-CRC");
    case ENCTYPE_DES_CBC_MD4:
		return PyString_FromString("DES-CBC-MD4");
    case ENCTYPE_DES_CBC_MD5:
		return PyString_FromString("DES-CBC-MD5");
    case ENCTYPE_DES_CBC_RAW:
		return PyString_FromString("DES-CBC-RAW");
    case ENCTYPE_DES3_CBC_SHA:
		return PyString_FromString("DES3-CBC-SHA");
    case ENCTYPE_DES3_CBC_RAW:
		return PyString_FromString("DES3-CBC-RAW");
    case ENCTYPE_DES_HMAC_SHA1:
		return PyString_FromString("DES-HMAC-SHA1");
    case ENCTYPE_DES3_CBC_SHA1:
		return PyString_FromString("DES3-CBC-SHA1");
    case ENCTYPE_AES128_CTS_HMAC_SHA1_96:
		return PyString_FromString("AES128_CTS-HMAC-SHA1_96");
    case ENCTYPE_AES256_CTS_HMAC_SHA1_96:
		return PyString_FromString("AES256_CTS-HMAC-SHA1_96");
    case ENCTYPE_ARCFOUR_HMAC:
		return PyString_FromString("RC4-HMAC-NT");
    case ENCTYPE_ARCFOUR_HMAC_EXP:
		return PyString_FromString("RC4-HMAC-NT-EXP");
    case ENCTYPE_UNKNOWN:
		return PyString_FromString("UNKNOWN");
#ifdef ENCTYPE_LOCAL_DES3_HMAC_SHA1
    case ENCTYPE_LOCAL_DES3_HMAC_SHA1:
		return PyString_FromString("LOCAL-DES3-HMAC-SHA1");
#endif
#ifdef ENCTYPE_LOCAL_RC4_MD4
    case ENCTYPE_LOCAL_RC4_MD4:
		return PyString_FromString("LOCAL-RC4-MD4");
#endif
    default:
		return PyString_FromFormat("#%d", self->cred->keyblock.enctype);
    }
}

static PyObject *Credential_is_forwardable(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_FORWARDABLE) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_forwarded(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_FORWARDED) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_proxiable(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_PROXIABLE) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_proxy(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_PROXY) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_postdateable(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_MAY_POSTDATE) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_postdated(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_POSTDATED) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_invalid(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_INVALID) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_renewable(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_RENEWABLE) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_initial(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_INITIAL) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_hwauth(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_HW_AUTH) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_preauth(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_PRE_AUTH) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_transit_policy_checked(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_TRANSIT_POLICY_CHECKED) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_ok_as_delegate(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_OK_AS_DELEGATE) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_is_anonymous(Credential *self, PyObject *args /* = NULL */) {
	if (self->cred->ticket_flags & TKT_FLG_ANONYMOUS) {
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

static PyObject *Credential_str(Credential *self) {
	char *temp;
	PyObject *attr;
	krb5_error_code retval;
		
	if ((retval = krb5_unparse_name(module_context, self->cred->server, &temp))) {
		return python_krb5_error(retval);
	}
	attr = PyString_FromString(temp);
	krb5_free_unparsed_name(module_context, temp);
	return attr;
}

/**
 * Deallocates a Credential object.
 */
static void Credential_dealloc(Credential *self)
{
	/* free the credential structure */
	krb5_free_creds(module_context, self->cred);

	self->ob_type->tp_free((PyObject *)self);
}

static PyMethodDef Credential_methods[] = {
	{"is_forwardable",	(PyCFunction)Credential_is_forwardable,		METH_NOARGS,
	 "Returns True if the ticket is forwardable, False otherwise."},
	{"is_forwarded",	(PyCFunction)Credential_is_forwarded,		METH_NOARGS,
	 "Returns True if the ticket has been forwarded, False otherwise."},
	{"is_proxiable",	(PyCFunction)Credential_is_proxiable,		METH_NOARGS,
	 "Returns True if the ticket is proxiable, False otherwise."},
	{"is_proxy",		(PyCFunction)Credential_is_proxy,		METH_NOARGS,
	 "Returns True if the ticket has been proxied, False otherwise."},
	{"is_postdateable",	(PyCFunction)Credential_is_postdateable,	METH_NOARGS,
	 "Returns True if the ticket can be postdated, False otherwise."},
	{"is_postdated",	(PyCFunction)Credential_is_postdated,		METH_NOARGS,
	 "Returns True if the ticket has been postdated, False otherwise."},
	{"is_invalid",		(PyCFunction)Credential_is_invalid,		METH_NOARGS,
	 "Returns True if the ticket is invalid, False otherwise."},
	{"is_renewable",	(PyCFunction)Credential_is_renewable,		METH_NOARGS,
	 "Returns True if the ticket is renewable, False otherwise."},
	{"is_initial",		(PyCFunction)Credential_is_initial,		METH_NOARGS,
	 "Returns True if the ticket is initial, False otherwise."},
	{"is_hwauth",		(PyCFunction)Credential_is_hwauth,		METH_NOARGS,
	 "Returns True if the ticket is for HW auth, False otherwise."},
	{"is_preauth",		(PyCFunction)Credential_is_preauth,		METH_NOARGS,
	 "Returns True if the ticket is preauthenticated, False otherwise."},
	{"is_transit_policy_checked", (PyCFunction)Credential_is_transit_policy_checked, METH_NOARGS,
	 "Returns True if the transit policy has been checked, False otherwise."},
	{"is_ok_as_delegate",	(PyCFunction)Credential_is_ok_as_delegate, 	METH_NOARGS,
	 "Returns True if the ticket is ok as a delegate, False otherwise."},
	{"is_anonymous",	(PyCFunction)Credential_is_anonymous,		METH_NOARGS,
	 "Returns True if the ticket is anonymous, False otherwise."},
	{NULL} /* Sentinel */
};

static PyGetSetDef Credential_getsets[] = {
	{"client", (getter)Credential_get, NULL,
		"client's principal identifier", "client"},
	{"server", (getter)Credential_get, NULL,
		"server's principal identifier", "server"},
	{"starttime", (getter)Credential_get, NULL,
		"the ticket's start time", "starttime"},
	{"endtime", (getter)Credential_get, NULL,
		"the ticket's end time", "endtime"},
	{"renewtime", (getter)Credential_get, NULL,
		"the ticket's renew time", "renewtime"},
	{"enctype", (getter)Credential_get_enctype, NULL,
		"the ticket's encryption type", NULL},
	{NULL} /* Sentinel */
};

static PyMemberDef Credential_members[] = {
	{NULL} /* Sentinel */
};

PyTypeObject CredentialType = {
	PyObject_HEAD_INIT(NULL)
	0,						/* ob_size 			*/
	"krb5.Credential",				/* tp_name 			*/
	sizeof(Credential),				/* tp_basicsize			*/
	0,						/* tp_itemsize 			*/
	(destructor)Credential_dealloc,			/* tp_dealloc 			*/
	0,						/* tp_print 			*/
	0,						/* tp_getattr			*/
	0,						/* tp_setattr			*/
	0,						/* tp_compare			*/
	0,						/* tp_repr			*/
	0,						/* tp_as_number			*/
	0,						/* tp_as_sequence		*/
	0,						/* tp_as_mapping		*/
	0,						/* tp_hash			*/
	0,						/* tp_call			*/
	Credential_str,					/* tp_str			*/
	0,						/* tp_getattro			*/
	0,						/* tp_setattro			*/
	0,						/* tp_as_buffer			*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/* tp_flags			*/
	"Kerberos Credential object.",			/* __doc__			*/
	0,						/* tp_traverse 			*/
	0,						/* tp_clear 			*/
	0,						/* tp_richcompare 		*/
	0,						/* tp_weaklistoffset 		*/
	0,						/* tp_iter 			*/
	0,						/* tp_iternext 			*/
	Credential_methods,				/* tp_methods 			*/
	Credential_members,				/* tp_members 			*/
	Credential_getsets,				/* tp_getset 			*/
};
