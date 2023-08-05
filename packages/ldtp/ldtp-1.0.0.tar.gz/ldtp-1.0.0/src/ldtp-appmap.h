/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Nagappan A <anagappan@gmail.com>
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

#ifndef __APPMAP_H__
#define __APPMAP_H__

struct obj_property {
	gboolean appmap_type; /* TRUE, remap generated appamp. FALSE, initappmap based appmap*/
	long child_index;
	char *str_child_index;
	char *parent_name;
	int class_type; /* SPI_ROLE_MENU_ITEM */
	char *class_name; /* menu_item */
	char *label;
	char *label_by;
	char *app_name;
};

struct unkn_label_property { /* Example: txt0, pnl2*/
	gboolean appmap_type; /* TRUE, remap generated appamp. FALSE, initappmap based appmap*/
	long child_index;
	char *str_child_index;
	char *parent_name;
	char *obj_name;
};

struct obj_info {
	char *key;
	gboolean obj_is_window;
	GPatternSpec *pattern;
};

typedef struct obj_info OBJInfo;
typedef struct obj_property OBJProperty;
typedef struct unkn_label_property UnknLabelProperty;

GHashTable *appmap_init (char *, FILE *);
void   ldtp_appmap_free (GHashTable* appmap);
char   *get_property (GHashTable *, char *, FILE *);
GHashTable *get_object_def (GHashTable *, char *, FILE *, gboolean);
void print_attributes (char *key, char *value, char *userdata);
void print_component (char *key, GHashTable *component, char *userdata);
void print_context (char *key, GHashTable *context, char *userdata);
void key_destroy_func (gpointer data);
void value_destroy_func (gpointer data);
gboolean remove_context_entries (gpointer key, gpointer value, gpointer context);
gboolean remove_remapped_entry (gpointer key, gpointer value, gpointer user_data);
gboolean search_title_based (gpointer key, gpointer value, gpointer user_data);

#endif /*__APPMAP_H__*/
