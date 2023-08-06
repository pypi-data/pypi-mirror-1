/* 
 * principal.h - header file for the Principal object
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

#ifndef PRINCIPAL_H
#define PRINCIPAL_H

#include "Python.h"

typedef struct {
	PyObject_HEAD
	krb5_principal principal;	/* Kerberos Principal struct */
	krb5_ccache ccache;		/* credentials cache */
} Principal;

extern PyTypeObject PrincipalType;

#endif /* PRINCIPAL_H */
