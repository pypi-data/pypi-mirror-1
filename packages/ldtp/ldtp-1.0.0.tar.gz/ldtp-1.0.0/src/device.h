/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Prashanth Mohan <prashmohan@gmail.com>
 *
 * Copyright 2004 - 2006 Novell, Inc.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this program; if not, write to the
 * Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
 * Boston, MA 02110, USA.
 */

#ifndef _DEVICE_H
#define _DEVICE_H

#include <glib.h>

#define DOWNCHAR 12
#define UPCHAR 21
#define UNDEFINED_KEY -1
#define MAX_TOKENS 256
#define MAX_TOK_SIZE 15

struct Symbol_Key_Synth {
	gchar sym;
	gint KeyVal;
};

struct NonPrint_Key_Synth {
	gchar *sym;
	gint KeyVal;
};

struct KeyValue {
	gboolean shift;
	gboolean non_print_key;
	gint value;
};
	
#endif
