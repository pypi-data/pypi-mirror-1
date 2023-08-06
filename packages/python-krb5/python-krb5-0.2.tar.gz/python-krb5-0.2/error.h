/* 
 * error.h - header file for python-krb5 error handling routines
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

#ifndef ERROR_H
#define ERROR_H

#include <krb5.h>
#include "Python.h"

#define ERRORCHECK_KRB5_CALL(x) if (x) return python_krb5_error(x)
#define ERRORCHECK_NEW_PYOBJECT(x) if (x == NULL) return PyErr_NoMemory()

extern PyObject *python_krb5_error (krb5_error_code ec);

#endif /* ERROR_H */
