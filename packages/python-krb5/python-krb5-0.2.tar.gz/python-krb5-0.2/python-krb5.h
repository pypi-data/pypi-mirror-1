/* 
 * python-krb5.h - common module header file
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

#ifndef PYTHON_KRB5_H
#define PYTHON_KRB5_H

#include <krb5.h>
#include "Python.h"

/* module kerberos context */
extern krb5_context module_context;

/* hack for python 2.3 compat */
#if (PY_MAJOR_VERSION == 2 && PY_MINOR_VERSION == 3)
#define Py_RETURN_FALSE Py_INCREF(Py_False); return Py_False
#define Py_RETURN_TRUE Py_INCREF(Py_True); return Py_True
#endif

#endif /* PYTHON_KRB5_H */
