/* 
 * python-krb5.c - source file for module functions
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
#include "error.h"
#include "principal.h"
#include "credential.h"

/* defines for module variables */
krb5_context module_context = NULL;

/**
 * Create a Principal object for the currently logged in user.
 */
static PyObject *get_login_principal(PyObject *self)
{
	Principal *princ;
	krb5_error_code retval;

	princ = PyObject_New(Principal, &PrincipalType);
	if(princ != NULL) {
		/* get credentials cache */
		retval = krb5_cc_default(module_context, &princ->ccache);
		if(retval) {
			return python_krb5_error(retval);
		}

		retval = krb5_cc_get_principal(module_context, princ->ccache, &princ->principal);
		if(retval) {
			return python_krb5_error(retval);
		}

		return (PyObject *) princ;
	}
	else {
		return PyErr_NoMemory();
	}
}

/**
 * Get the default realm for this host.
 */
static PyObject *get_default_realm(PyObject *self)
{
	char *realm = NULL;
    PyObject *pyrealm = NULL;
	krb5_error_code retval;

	retval = krb5_get_default_realm(module_context, &realm);
	if (retval)
		return python_krb5_error(retval);

	pyrealm = PyString_FromString(realm);
	free(realm);

    return pyrealm;
}

/**
 * Get the name of the default credentials cache.
 */
static PyObject *get_ccache_default_name(PyObject *self)
{
    char *name = NULL;

    /* FIXME : this is a memory leak!! */
    name = krb5_cc_default_name(module_context);
    return PyString_FromString(name);
}

/**
 * Module deallocation function.
 */
void cleanup(void)
{
	if(module_context != NULL) {
		krb5_free_context(module_context);
		module_context = NULL;
	}
}

static PyMethodDef krb5_methods[] = {
	{"get_login_principal",		(PyCFunction) get_login_principal,	METH_NOARGS,
	 "Get a Principal object for the currently logged in Principal."}, 
	{"get_default_realm",		(PyCFunction) get_default_realm,	METH_NOARGS,
	 "Get the default Kerberos realm."},
    {"get_ccache_default_name", (PyCFunction) get_ccache_default_name, METH_NOARGS,
     "Get the default ccache name."},
	{ NULL }
};


#ifndef PyMODINIT_FUNC
#ifdef WIN32
#define PyMODINIT_FUNC void __declspec(dllexport)
#else
#define PyMODINIT_FUNC
#endif /* WIN32 */
#endif /* PyMODINTIT_FUNC */
/**
 * python-krb5 initialization function.
 */
PyMODINIT_FUNC initkrb5(void)
{
	PyObject *module;
	krb5_error_code rc;
   
	if(PyType_Ready(&PrincipalType) < 0)
		return;
	if(PyType_Ready(&CredentialType) < 0)
		return;

	module = Py_InitModule("krb5", krb5_methods);

	if(module == NULL)
		return;
		
	/* define Krb5Error exception */
	//Krb5Error = PyErr_NewException("krb5.Krb5Error", NULL, NULL);
	//Py_INCREF(Krb5Error);
	//PyModule_AddObject(module, "error", Krb5Error);

	/* initialize kerberos */
	rc = krb5_init_context(&module_context);
	if(rc) {
		return;
	}

	/* Add the Principal object */
	Py_INCREF(&PrincipalType);
	PyModule_AddObject(module, "Principal", (PyObject *)&PrincipalType);

	/* Add the Credential object */
	Py_INCREF(&CredentialType);
	PyModule_AddObject(module, "Credential", (PyObject *)&CredentialType);

	/* define module cleanup function */
	Py_AtExit(cleanup);
}
