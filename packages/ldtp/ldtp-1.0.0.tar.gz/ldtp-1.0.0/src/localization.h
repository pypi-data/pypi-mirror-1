/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://www.gnomebangalore.org/ldtp
 *
 * Author:
 *    Nagappan A <nagappan@gmail.com>
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

#ifndef __LOCALIZATION_H__
#define __LOCALIZATION_H__

#include "ldtp.h"
#define GETTEXT_PACKAGE "gtk20"
#ifdef ENABLE_LOCALIZATION
#include <gettext-po.h>
#endif
#include <glib/gi18n.h>

typedef struct {
	GHashTable *table;
	struct LdtpHashTable *next;
}LdtpHashTable;

#endif

gboolean init_catalog (gchar *, FILE *);
gchar *ldtp_compare_with_locale (gchar *, gchar *);
gchar *reverse_lookup (gchar *);
