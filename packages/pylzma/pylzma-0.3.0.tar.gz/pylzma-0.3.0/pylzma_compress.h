/*
 * Python Bindings for LZMA
 *
 * Copyright (c) 2004-2006 by Joachim Bauch, mail@joachim-bauch.de
 * 7-Zip Copyright (C) 1999-2005 Igor Pavlov
 * LZMA SDK Copyright (C) 1999-2005 Igor Pavlov
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 * 
 * $Id: pylzma_compress.h 104 2006-01-08 18:17:14Z jojo $
 *
 */

#ifndef ___PYLZMA_COMPRESS__H___
#define ___PYLZMA_COMPRESS__H___

#include <Python.h>

extern const char doc_compress[];
PyObject *pylzma_compress(PyObject *self, PyObject *args, PyObject *kwargs);

#endif
