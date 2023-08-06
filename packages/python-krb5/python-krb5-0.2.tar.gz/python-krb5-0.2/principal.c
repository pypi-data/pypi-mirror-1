/* 
 * principal.c - source for the Principal object
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
#include <string.h>
#include <time.h>
#include "Python.h"
#include "structmember.h"
#include "python-krb5.h"
#include "error.h"
#include "credential.h"
#include "principal.h"

/**
 * Creates a new Principal object.
 * @return the object or NULL.
 */
static PyObject *Principal_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	Principal *self;

	self = (Principal *)type->tp_alloc(type, 0);
	if (self != NULL) {
		self->ccache = NULL;
		self->principal = NULL;
		return (PyObject *)self;
	}
	else {
		Py_DECREF(self);
		return NULL;
	}
}

/**
 * Creates a new Principal object.
 * @param name the user's name in username@realm format.
 * @param password the user's password.
 * @return 0 if object is created, -1 otherwise.
 */
static int Principal_init(Principal *self, PyObject *args, PyObject *kwds)
{
    const char *                name = NULL;
	const char *                password = NULL;
    krb5_creds 			        credentials;
	krb5_get_init_creds_opt *	options = NULL;
	krb5_error_code 		    retval = 0;
    krb5_deltat                 lifetime = 0;
    krb5_deltat                 rlife = 0;

	static char *kwlist[] = {"name", "password", NULL};
	(void) memset((char *) &credentials, 0, sizeof(credentials));

    /* process arguments */	
	if(!PyArg_ParseTupleAndKeywords(args, kwds, "ss:Principal", kwlist, &name, &password))
			return -1;
			
	/* parse the username */
    retval = krb5_parse_name(module_context, name, &self->principal);
	if (retval) {
		if (retval == ENOMEM) {
			PyErr_NoMemory();
		}
		else {
			python_krb5_error(retval);
		}

        return -1;
	}

	/* initialize option structure */
    krb5_get_init_creds_opt_alloc(module_context, &options);
	krb5_get_init_creds_opt_init(options);

    krb5_string_to_deltat("24h", &lifetime);
	krb5_get_init_creds_opt_set_tkt_life(options, lifetime);
	
    krb5_string_to_deltat("48h", &rlife);
    krb5_get_init_creds_opt_set_renew_life(options, rlife);

	krb5_get_init_creds_opt_set_forwardable(options, 1);
	krb5_get_init_creds_opt_set_proxiable(options, 1);
	krb5_get_init_creds_opt_set_address_list(options, NULL);

	/* get a TGT from the KDC */
    retval = krb5_get_init_creds_password(module_context, 
                                               &credentials, 
                                               self->principal, 
				                               (char *) password, 
                                               0, 
                                               0, 
                                               0, 
                                               0, 
                                               options);
	if (retval) {
		python_krb5_error(retval);
		goto error1;
	}

    /* get the default credentials cache */
    retval = krb5_cc_default(module_context, &self->ccache);
	if(retval) {
        python_krb5_error(retval);
        goto error2;
    }

	/* initialize the new ccache */
    retval = krb5_cc_initialize(module_context, self->ccache, self->principal);
	if (retval) {
		python_krb5_error(retval);
		goto error3;
	}

	/* store the credentials in the ccache */
    retval = krb5_cc_store_cred(module_context, self->ccache, &credentials);
	if (retval) {
		python_krb5_error(retval);
		goto error3;
	}

    krb5_get_init_creds_opt_free(module_context, options);
   	krb5_free_cred_contents(module_context, &credentials);
    return 0;

    /* ERROR HANDLING */
error3:
    krb5_cc_close(module_context, self->ccache);
error2:
    krb5_get_init_creds_opt_free(module_context, options);
   	krb5_free_cred_contents(module_context, &credentials);
error1:
    krb5_free_principal(module_context, self->principal);

    return -1;	
}

/**
 * Deallocates a Principal object.
 */
static void Principal_dealloc(Principal *self)
{
	if(self->ccache != NULL)
		krb5_cc_close(module_context, self->ccache);
	if(self->principal != NULL)
		krb5_free_principal(module_context, self->principal);
	self->ob_type->tp_free((PyObject *)self);
}

/**
 * Returns a new reference to the full name of the principal.
 */
static PyObject *Principal_get_name(Principal *self, void *closure)
{
	char *name;
	PyObject *py_name;
	krb5_error_code retval;

	/* get the principal name string */	
	retval = krb5_unparse_name(module_context, self->principal, &name);
	if(retval)
	{
		python_krb5_error(retval);
		return NULL;
	}
	
	/* create the string object */	
	py_name = PyString_FromString(name);
	krb5_free_unparsed_name(module_context, name);
	if (py_name == NULL) {
		return PyErr_NoMemory();
	}

	/* return the name string */
	return py_name;
}

/**
 * Returns the name of this Principal's credentials cache.
 */
static PyObject *Principal_get_ccache_name(Principal *self) {
	const char *type;
	const char *name;
	PyObject *ccache_name;

	type = krb5_cc_get_type(module_context, self->ccache);
	name = krb5_cc_get_name(module_context, self->ccache);
	ccache_name = PyString_FromFormat("%s:%s", type, name);
	return ccache_name;
}

/**
 * Renew the Principal's TGT.
 *
 * Returns: True if the ticket is renewed.  If the ticket can't be renewed, an
 *          exception is set and the function returns NULL.
 */
static PyObject *Principal_renew(Principal *self) {
    int buf_len; 
    krb5_data *realm;
    char *service_name;
    krb5_creds credentials;
    krb5_error_code retval;

    memset(&credentials, 0, sizeof(credentials));

    /* get the realm */
    realm = krb5_princ_realm(module_context, self->principal);

    /* build the service name string */
    buf_len = KRB5_TGS_NAME_SIZE + realm->length + 2;
    service_name = (char *) malloc(buf_len);
    if (service_name == NULL) {
        return PyErr_NoMemory();
    }
    snprintf(service_name, buf_len, "%s/%s", KRB5_TGS_NAME, realm->data);

    /* renew the TGT */
	retval = krb5_get_renewed_creds(module_context, &credentials, 
                                    self->principal, self->ccache, 
                                    service_name);
    free(service_name);
    if(retval) {
        goto error;
    }

    /* initialize the credentials cache */
    retval = krb5_cc_initialize(module_context, self->ccache, self->principal);
    if (retval) {
	    goto error;
    }

    /* store the new TGT */
    retval = krb5_cc_store_cred(module_context, self->ccache, &credentials);
    if (retval) {
	    goto error;
    }

    /*krb5_free_data(module_context, realm);*/
    krb5_free_cred_contents(module_context, &credentials);
    Py_RETURN_TRUE;

error:
    krb5_free_cred_contents(module_context, &credentials);
    python_krb5_error(retval);
    
    return NULL;
}


/**
 * Returns a new reference to a list of all credentials in the
 * credentials cache.
 */
static PyObject *Principal_get_credentials(Principal *self) {
	PyObject *cred_list;
	Credential *cred;
	krb5_cc_cursor cur;
	krb5_creds credentials;
	krb5_error_code retval;

	/* create a credential cache cursor */
	retval = krb5_cc_start_seq_get(module_context, self->ccache, &cur);
	if(retval) {
		return python_krb5_error(retval);
	}

	/* create a new python list with no members */
	cred_list = PyList_New(0);
	if (cred_list == NULL) {
		PyErr_NoMemory();
		goto error1;
	}

	/* add each credential in the cache to the list */
	while(krb5_cc_next_cred(module_context, self->ccache, &cur, &credentials) != KRB5_CC_END) {
		/* create a new Credential object */
		cred = PyObject_New(Credential, &CredentialType);
		if (cred == NULL) {
			PyErr_NoMemory();
			goto error2;
		}
		
		/* copy the krb5_creds data for the Credential object */
		retval = krb5_copy_creds(module_context, (krb5_creds *)&credentials, &cred->cred);
		if (retval) {
			python_krb5_error(retval);
			goto error3;
		}

		/* Add the Credential into the list */
		if (PyList_Append(cred_list, (PyObject *) cred) == -1) goto error3;
	}

	return cred_list;

	/* ERROR HANDLING */
error3:
	Py_DECREF(cred);
error2:
	Py_DECREF(cred_list);
error1:
	krb5_cc_end_seq_get(module_context, self->ccache, &cur);
	return NULL;
}

/**
 * Get a new service ticket for the Principal.
 *
 * This function takes two arguments:
 * host - A Python string with the hostname.
 * service - A Python string with the service name.
 *
 * Returns: True if ticket is successfully created.  If there is an error,
 *          an exception will be set and the function will return NULL.
 *
 * FIXME: should this return the credential object??
 */
static PyObject *Principal_get_service_ticket(Principal *self, PyObject *args) {
	const char *hostname;
	const char *service;
	krb5_error_code retval;
	krb5_principal	server;
	krb5_creds	increds;
	krb5_creds	*outcreds;
	krb5_creds	**tgtcreds;
		
	/* parse args from python */
	if(!PyArg_ParseTuple(args, "ss:get_service_ticket", &hostname, &service)) {
		PyErr_SetString(PyExc_TypeError, "Invalid arguments.");
		return NULL;
	}

	/* parse server principal name */
	retval = krb5_sname_to_principal(
			module_context,
			hostname,
			service,
			KRB5_NT_SRV_HST,
			&server
			);
	if(retval) {
		return python_krb5_error(retval);
	}

	/* set up options for ticket */
	/* FIXME: make this configurable! */
	memset(&increds, 0, sizeof(increds));
	increds.client = self->principal;
	increds.times.endtime = 0;
	increds.server = server;

	/* request the ticket from the KDC */
	retval = krb5_get_cred_from_kdc(
			module_context,
			self->ccache,
			&increds,
			&outcreds,
			&tgtcreds
			);
	if(retval) {
		python_krb5_error(retval);
		goto error1;
	}

	/* store the credential in the cache */
	retval = krb5_cc_store_cred(module_context, self->ccache, outcreds);
	if(retval) {
		python_krb5_error(retval);
		goto error1;
	}

	/* clean up */
	krb5_free_creds(module_context, outcreds);
	krb5_free_principal(module_context, server);

	/* ticket successfully created return true */
	Py_RETURN_TRUE;

	/* ERROR HANDLING */
error1:
	krb5_free_principal(module_context, server);
	return NULL;
}

/**
 * Change this Principal's password.
 *
 * This function takes two arguments:
 * old_pw: the Principal's current password
 * new_pw: the new password
 *
 * Returns: True if the password is changed successfully, if there is an error
 *          an exception will be set and the function will return NULL.
 */
static PyObject *Principal_change_password(Principal *self, PyObject *args) {
	char *old_pw, *new_pw;
	krb5_error_code retval;
	krb5_get_init_creds_opt opts;
	krb5_creds creds;
	int result_code;
	
	/* parse args from python */
	if(!PyArg_ParseTuple(args, "ss:change_password", &old_pw, &new_pw)) {
		PyErr_SetString(PyExc_TypeError, "Invalid arguments.");
		return NULL;
	}

	/* set cred options */
	krb5_get_init_creds_opt_init(&opts);
	krb5_get_init_creds_opt_set_tkt_life(&opts, 5*60);
	krb5_get_init_creds_opt_set_renew_life(&opts, 0);
	krb5_get_init_creds_opt_set_forwardable(&opts, 0);
	krb5_get_init_creds_opt_set_proxiable(&opts, 0);

	/* get the kadmin/changepw ticket */
	if ((retval = krb5_get_init_creds_password(module_context, &creds, self->principal, old_pw,
					NULL, NULL, 0, "kadmin/changepw", &opts))) {
		if (retval == KRB5KRB_AP_ERR_BAD_INTEGRITY) {
			PyErr_SetString(PyExc_AttributeError, "Password incorrect while getting changepw ticket");
			return NULL;
		}
		else {
			PyErr_SetString(PyExc_RuntimeError, "Error getting changepw ticket.");
			return NULL;
		}
	}

	/* change the password */
	if ((retval = krb5_change_password(module_context, &creds, new_pw, &result_code, NULL, NULL))) {
		PyErr_SetString(PyExc_RuntimeError, "Error changing password.");
		return NULL;
	}

	Py_RETURN_TRUE;	
}

static PyMethodDef Principal_methods[] = {
	{"get_credentials",	(PyCFunction)Principal_get_credentials,		METH_NOARGS,
	 "Get a list of the credentials for this Principal."},
	{"get_service_ticket",	(PyCFunction)Principal_get_service_ticket,	METH_VARARGS,
	 "Get a new service ticket."},
	{"get_ccache_name", 	(PyCFunction)Principal_get_ccache_name,		METH_NOARGS,
	 "Get the name of the credentials cache for this Principal."},
	{"change_password",	(PyCFunction)Principal_change_password,		METH_VARARGS,
	 "Change the Principal's password."},
    {"renew", (PyCFunction)Principal_renew, METH_VARARGS,
     "Renew the Principal's TGT."},
	{NULL} /* Sentinel */
};

static PyGetSetDef Principal_getsets[] = {
	{"name",	(getter)Principal_get_name,	NULL,
		"The full name of the Principal (including realm).", NULL},
	{NULL} /* Sentinel */
};

static PyMemberDef Principal_members[] = {
	{NULL} /* Sentinel */
};

PyTypeObject PrincipalType = {
	PyObject_HEAD_INIT(NULL)
	0,						/* ob_size 			*/
	"krb5.Principal",				/* tp_name 			*/
	sizeof(Principal),				/* tp_basicsize			*/
	0,						/* tp_itemsize 			*/
	(destructor)Principal_dealloc,			/* tp_dealloc 			*/
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
	0,						/* tp_str			*/
	0,						/* tp_getattro			*/
	0,						/* tp_setattro			*/
	0,						/* tp_as_buffer			*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/* tp_flags			*/
	"Kerberos Principal object.",			/* __doc__			*/
	0,						/* tp_traverse 			*/
	0,						/* tp_clear 			*/
	0,						/* tp_richcompare 		*/
	0,						/* tp_weaklistoffset 		*/
	0,						/* tp_iter 			*/
	0,						/* tp_iternext 			*/
	Principal_methods,				/* tp_methods 			*/
	Principal_members,				/* tp_members 			*/
	Principal_getsets,				/* tp_getset 			*/
	0,						/* tp_base 			*/
	0,						/* tp_dict 			*/
	0,						/* tp_descr_get 		*/
	0,						/* tp_descr_set 		*/
	0,						/* tp_dictoffset 		*/
	(initproc)Principal_init,			/* tp_init 			*/
	0,						/* tp_alloc 			*/
	Principal_new,					/* tp_new 			*/
};
