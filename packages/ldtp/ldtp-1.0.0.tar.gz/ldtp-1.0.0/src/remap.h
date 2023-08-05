/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Premkumar J <jpremkumar@novell.com>
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

#ifndef __REMAP_H__
#define __REMAP_H__

gchar *strip_delim (const gchar *text, gchar ch);
GHashTable *do_remap (Accessible *accessible, char *name, GHashTable *context,
		      GHashTable *context_attributes, gboolean locale_flag,
		      gboolean overloadedWindowName, gboolean remap_context); 
char *get_window_name_in_appmap_format (char *window_name, AccessibleRole role);

#endif
