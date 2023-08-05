/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Nagappan A <nagappan@gmail.com>
 *    S Thanikachalam <sthanikachalam@novell.com>
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

#include "ldtp.h"
#include "ldtp-gui.h"
#include "ldtp-utils.h"
#include "ldtp-error.h"
#include "ldtp-logger.h"
#include "ldtp-appmap.h"
#include "ldtp-command.h"
#include "ldtp-gui-comp.h"

extern gboolean ldtp_debug;
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

static char*
read_delimiter (int fd, char delimit)
{
	int len = 128;
	int size = 0;
	char ch;
	char *data = NULL;

	while (read (fd, &ch, 1) > 0) {
		if (!data)
			data = (char *) malloc (sizeof (char)*len);
		if (size%len == 0)
			data = (char *) realloc (data, sizeof (char)*len+size+1);
		data[size++] = ch;
		if (data[0] == '\n' || ch == delimit || (size && data[size - 1] == ']')) {
			if (data[0] != '\n' && read (fd, &ch, 1) > 0) {
				/*
				 * Don't do any operation
				 */
			}
			if (size%len == 0)
				data = (char *) realloc (data, sizeof (char)+size+1);
			data[size] = '\0';
			return data;
		}
	}
	return NULL;
}

static void
add_child_attributes (char *cur_entry, GHashTable *cur_context_table)
{
	char *token = NULL;
	int offset;
	char *component = NULL;
	    
	token = strtok (strdup (cur_entry), "=");
	if (token)
		component = strdup (token);
	    
	offset = strlen (component) + 1;
	if (cur_entry[offset] == '{') {
		char *end = strstr (cur_entry, "}");
		if (end) {
			char *key, *value;
			char *all_attributes;
			GHashTable *hash_attributes;
			int len = (end - cur_entry) - (offset+1);
	 
			all_attributes = (char *) malloc (sizeof (char) * len + 1);
			strncpy (all_attributes, (cur_entry + offset + 1), len);
			all_attributes[len] = '\0';

			/*
			  Create new attribute hash table
			*/
			hash_attributes = g_hash_table_new (&g_str_hash, &g_str_equal);
			key = strtok (strdup (all_attributes), "=");
			while (key) {
				char *hash_key;
				char *hash_value;
				hash_key = g_strdup (key);
				value = strtok (NULL, ",");
				hash_value = g_strdup (value);
				if (hash_key && hash_value)
					g_print ("%s: %s\n", hash_key, hash_value);
				if (hash_attributes && hash_key && hash_value)
					g_hash_table_insert (hash_attributes, hash_key, hash_value);
				key = strtok (NULL, "=");
			}
			if (component && cur_context_table && hash_attributes)
				g_hash_table_insert (cur_context_table, component, hash_attributes);
		}
	}
}

void
print_attributes (char *key, char *value, char *userdata)
{
	if (key && value)
		g_print ("\t|-------%s = %s\n", key, value);
}

void
print_component (char *key, GHashTable *component, char *userdata)
{
	if (key)
		g_print ("|-------%s\n", key);
	g_hash_table_foreach (component, (GHFunc)&print_attributes, userdata);
}

void
print_context (char *key, GHashTable *context, char *userdata)
{
	if (key)
		g_print (":%s:\n", key);
	g_hash_table_foreach (context, (GHFunc)&print_component, userdata);
}

/*
  Initialize application map
*/
GHashTable*
appmap_init (char *gui_map_filename, FILE *log_fp)
{
	int fd;
	//int quit_flag = 0;
	FILE *fp;
	char *cur_entry = NULL;
	GHashTable *appmap;
	GHashTable *cur_context_table = NULL;

	appmap = g_hash_table_new (&g_str_hash, &g_str_equal);
    
	fp = fopen (gui_map_filename, "r");
	if (fp == NULL) {
		g_print ("Unable to open appmap %s file\n", gui_map_filename);
		log_msg (LDTP_LOG_CAUSE, "Unable to open appmap file", log_fp);
		return NULL;
	}
	fd = fileno (fp);

	cur_entry = read_delimiter (fd, '}');
	while (1) {
		int cur_entry_len;
		char *context = NULL;
		if (!cur_entry)
			break;
		cur_entry_len = strlen (cur_entry);
		if (cur_entry [0] == '[' && cur_entry [cur_entry_len - 1] == ']') {
			cur_context_table = g_hash_table_new (&g_str_hash, &g_str_equal);
			context = (char *) g_new0 (char, sizeof (char) * (cur_entry_len - 1));

			/* Copy everything except the leading '[' and trailing ']' */
			memcpy (context, cur_entry+1, cur_entry_len-2);
			if (appmap && context && cur_context_table) 
				g_hash_table_insert (appmap, context, cur_context_table);
		}
		else if (cur_entry[0] == '\n') {
			cur_entry = read_delimiter (fd, '}');
			continue;
		}
		else
			add_child_attributes (cur_entry, cur_context_table);
		cur_entry = read_delimiter (fd, '}');
	}
	if (ldtp_debug)
		g_hash_table_foreach (appmap, (GHFunc)&print_context, NULL);
	return appmap;
}

void
key_destroy_func (gpointer data)
{
	if (data)
		g_free (data);
}

void
value_destroy_func (gpointer data)
{
	if (data)
		g_free (data);
}

static gboolean
is_remaped (gpointer key, gpointer value, gpointer user_data)
{
	if (key == NULL || value == NULL)
		return FALSE;
	g_print ("%s - %s ******* DEBUG\n", (char *) key, (char *) value);
	if (g_utf8_collate (key, "remap") == 0)
		return TRUE;
	return FALSE;
}

gboolean
remove_remapped_entry (gpointer key, gpointer value, gpointer user_data)
{
	if (key == NULL || value == NULL)
		return FALSE;
	g_hash_table_foreach_remove (value, is_remaped, key);
	return FALSE;
}

gboolean
remove_context_entries (gpointer key, gpointer value, gpointer context)
{
	GHashTable *component = NULL;

	if (context == NULL || key == NULL)
		return TRUE;
	component = g_hash_table_lookup (context, (char *)key);
	if (component) {
		g_hash_table_destroy (component);
		component = NULL;
	}
	return TRUE;
}

static gboolean
remove_appmap_entries (gpointer key, gpointer value, gpointer user_data)
{
	GHashTable *context = NULL;
	GHashTable *appmap = user_data;

	if (!appmap || !key)
		return TRUE;
	context = g_hash_table_lookup (appmap, (char *)key);
	if (context) {
		g_hash_table_foreach_remove (context, (GHRFunc)&remove_context_entries, context);
		g_hash_table_destroy (context);
		context = NULL;
	}
	return TRUE;
}

/*
  Free application map resource
*/
void
ldtp_appmap_free (GHashTable *appmap)
{
	if (!appmap)
		return;

	pthread_mutex_lock (&mutex);
	g_hash_table_foreach_remove (appmap, (GHRFunc)&remove_appmap_entries, appmap);
	g_hash_table_destroy (appmap);
	pthread_mutex_unlock (&mutex);
	appmap = NULL;
}

static gboolean
search_key_glob_based (gpointer key, gpointer value, gpointer user_data)
{
	char *tmp;
	OBJInfo *obj;
	if (!key && !user_data) {
		return FALSE;
	}
	/*
	  FIXME: Use get_object_info function to get the the type of object
	  if type and key matches then return true
	*/
	obj = (OBJInfo *) user_data;
	if (ldtp_debug && obj->key && key) {
		g_print ("glob- key: %d - %d - %d - %s %s %ld %ld\n",
			 obj->obj_is_window,
			 g_pattern_match_simple ("frm*", obj->key),
			 g_pattern_match_simple ("dlg*", obj->key),
			 obj->key, (char *) key, g_utf8_strlen (key, -1),
			 g_utf8_strlen (obj->key, -1));
	}
	if (obj->obj_is_window) {
		if (obj->key && g_utf8_collate (key, obj->key) == 0)
			return TRUE;
		if (obj->pattern) {
			if (g_pattern_match_string (obj->pattern, key))
				return TRUE;
		}
		tmp = g_strdup_printf ("frm%s", (gchar *)key);
		if (tmp && g_pattern_match_simple (tmp, key)) {
			g_free (tmp);
			return TRUE;
		}
		g_free (tmp);
		tmp = g_strdup_printf ("dlg%s", obj->key);
		if (tmp && g_pattern_match_simple (tmp, key)) {
			g_free (tmp);
			return TRUE;
		}
		g_free (tmp);
		tmp = g_strdup_printf ("frm%s*", obj->key);
		if (tmp && g_pattern_match_simple (tmp, key)) {
			g_free (tmp);
			return TRUE;
		}
		g_free (tmp);
		tmp = g_strdup_printf ("dlg%s*", obj->key);
		if (tmp && g_pattern_match_simple (tmp, key)) {
			g_free (tmp);
			return TRUE;
		}
		g_free (tmp);
		return FALSE;
	}
	if (obj->pattern && !obj->obj_is_window) {
		return g_pattern_match_string (obj->pattern, key);
	}
	return FALSE;
}

static gboolean
search_label_based (gpointer key, gpointer value, gpointer user_data)
{
	OBJInfo *obj;
	gchar *tmp   = NULL;
	gchar *class = NULL;
	gchar *label = NULL;
	gchar *label_by = NULL;
	gchar *tmp_data = NULL;
	gboolean flag = FALSE;
	GPatternSpec *pattern = NULL;

	if (!value && !user_data) {
		return FALSE;
	}
	obj = (OBJInfo *) user_data;
	g_hash_table_lookup_extended (value, "class", NULL, (gpointer) &class);
	g_hash_table_lookup_extended (value, "label", NULL, (gpointer) &label);

	tmp_data = obj->key;
	if (class)
		pattern = g_pattern_spec_new (class);
	if (pattern && (g_pattern_match_string (pattern, "frame") ||
	    g_pattern_match_string (pattern, "dialog") ||
	    g_pattern_match_string (pattern, "alert") ||
	    g_pattern_match_string (pattern, "file_chooser") ||
	    g_pattern_match_string (pattern, "font_chooser"))) {
		flag = TRUE;
	}
	if (pattern)
		g_pattern_spec_free (pattern);
	/*
	  FIXME: Use get_object_info function to get the the type of object
	  if type and key matches then return true
	*/
	if (label && tmp_data) {
		if ((gchar *)key && label && tmp_data)
			g_print ("Label: %s - %s - %s\n", (gchar *)key, (char *)tmp_data, label);
		if (!obj->obj_is_window || flag)
			if (g_utf8_collate (label, tmp_data) == 0)
				return TRUE;
		// Search for mnemonics, if available then remove just _
		if (g_utf8_strchr (label, -1, '_') == NULL)
			return FALSE;
		tmp = escape_character (label, '_');
		if (tmp && tmp_data)
			if (g_utf8_collate (tmp, tmp_data) == 0) {
				g_free (tmp);
				return TRUE;
			}
		g_free (tmp);
		return FALSE;
	}
	g_hash_table_lookup_extended (value, "label_by", NULL, (gpointer) &label_by);
	if (label_by && tmp_data) {
		if ((gchar *)key && label_by && tmp_data)
			g_print ("LabelBy: %s - %s - %s\n", (char *)key, (char *)tmp_data, label_by);
		if (!obj->obj_is_window || flag)
			if (g_utf8_collate (label_by, tmp_data) == 0)
				return TRUE;
		// Search for mnemonics, if available then remove just _
		if (g_utf8_strchr (label_by, -1, '_') == NULL)
			return FALSE;
		tmp = escape_character (label, '_');
		if (tmp && tmp_data)
			if (g_utf8_collate (tmp, tmp_data) == 0) {
				g_free (tmp);
				return TRUE;
			}
		g_free (tmp);
		return FALSE;
	}
	return FALSE;
}

static gboolean
search_label_glob_based (gpointer key, gpointer value, gpointer user_data)
{
	OBJInfo *obj;
	char *class = NULL;
	char *tmp_label = NULL;
	char *tmp_label_by = NULL;
	GPatternSpec *pattern = NULL;
	gboolean flag = FALSE;

	if (!value && !user_data)
		return FALSE;
	/*
	  FIXME: Remove under score from label or label_by and do a pattern match too
	*/

	obj = (OBJInfo *) user_data;
	if (g_hash_table_lookup_extended (value, "class", NULL, (gpointer) &class))
		pattern = g_pattern_spec_new (class);
	if (pattern && (g_pattern_match_string (pattern, "frame") ||
	    g_pattern_match_string (pattern, "dialog") ||
	    g_pattern_match_string (pattern, "alert") ||
	    g_pattern_match_string (pattern, "file_chooser") ||
	    g_pattern_match_string (pattern, "font_chooser"))) {
		flag = TRUE;
	}
	if (pattern)
		g_pattern_spec_free (pattern);
	if (g_hash_table_lookup_extended (value, "label", NULL, (gpointer) &tmp_label)) {
		if (key && value)
			g_print ("Label glob: %s - %s\n", (char *)key, (char *)value);
		if (obj->pattern && (!obj->obj_is_window || flag == TRUE))
			return g_pattern_match_string (obj->pattern, tmp_label);
	}

	if (g_hash_table_lookup_extended (value, "label_by", NULL, (gpointer) &tmp_label_by)) {
		g_print ("Label_By glob: %s\n", tmp_label_by);
		if (obj->pattern && (!obj->obj_is_window || flag))
			return g_pattern_match_string (obj->pattern, tmp_label_by);
	}
	return FALSE;
}

/*
static gboolean 
search_label_name (gpointer key, gpointer value, gpointer user_data)
{
	char *child_index = NULL;
	UnknLabelProperty *tmp_data = (UnknLabelProperty *) user_data;
	if (!value && !tmp_data && !key) {
		return FALSE;
	}
	if (g_hash_table_lookup_extended (value, "child_index", NULL, (gpointer) &child_index)) {
		if ((char *)key && tmp_data->str_child_index && tmp_data->parent_name)
			g_print ("Key - Child index - Parent: %s - %s - %s\n",
				 (char *)key, tmp_data->str_child_index,
				 tmp_data->parent_name);
		if (child_index && tmp_data->str_child_index &&
		    g_utf8_collate (child_index, tmp_data->str_child_index) == 0) {
			char *parent_name = NULL;
			g_hash_table_lookup_extended (value, "parent", NULL, (gpointer) &parent_name);
			g_print ("Key - Parent: %s - %s\n",
				 (char *)key,
				 parent_name);
			if (parent_name && tmp_data->parent_name &&
			    g_utf8_collate (parent_name, tmp_data->parent_name) == 0) {
				tmp_data->obj_name = (char *) key;
				return TRUE;
			}
		}
 	}
	return FALSE;
}
*/

static gboolean
search_obj_after_stripping_space (gpointer key, gpointer value, gpointer user_data)
{
	char *tmp;
	if (!key && !user_data)
		return FALSE;
	if (g_utf8_strchr (user_data, -1, ' ') == NULL)
		return FALSE;
	tmp = escape_character (user_data, ' ');
	if (!tmp)
		return FALSE;
	g_print ("DEBUG: %s - %s - %s\n", tmp, (char *)user_data, (char *)key);
	if (g_utf8_collate (key, tmp) == 0 || g_utf8_collate (key, user_data) == 0) {
		g_free (tmp);
		return TRUE;
	}
	else {
		char *glob_str = NULL;
		/*
		  FIXME: Use get_object_info function to get the the type of object
		  and based on that use the convention, instead of directly using *
		*/
		glob_str = g_strdup_printf ("*%s", tmp);
		g_print ("Glob str: %s - %s - %s\n", glob_str, (char *)key, tmp);
		if (g_pattern_match_simple (glob_str, key) ||
		    g_pattern_match_simple (key, tmp)) {
			g_print ("search_obj_after_stripping_space - matched\n");
			g_free (tmp);
			g_free (glob_str);
			return TRUE;
		}
		g_free (glob_str);
		g_free (tmp);
	}
	return FALSE;
}

/*
  Get window definition
*/
GHashTable*
get_object_def (GHashTable *ht, char *context, FILE *log_fp, gboolean obj_is_window)
{
	GHashTable *ht_context = NULL;
	LDTPErrorCode err;
	char *msg = NULL;

	if (ht == NULL) {
		err =  (LDTP_ERROR_APPMAP_NOT_INITIALIZED);
		g_print ("%s - %d - %s\n", __FILE__, __LINE__, ldtp_error_get_message (err));
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (err), log_fp);
		return NULL;
	}
	if (context == NULL) {
		err =  (LDTP_ERROR_ARGUMENT_NULL);
		g_print ("%s\n", ldtp_error_get_message (err));
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (err), log_fp);
		return NULL;
	}
	/*
	  Search given context in hash table
	*/
	g_hash_table_lookup_extended (ht, (gconstpointer) context, NULL, (gpointer) ht_context);
	if (ht_context)
		return ht_context;
	if (!ht_context) {
		OBJInfo obj;
		GPatternSpec *pattern = NULL;
		/*
		  Search key based on glob expression
		*/
		g_print ("Search key based on glob expression: %s - %d\n", context, obj_is_window);
		if (context)
			pattern = g_pattern_spec_new ((const gchar *)context);

		obj.obj_is_window = obj_is_window;
		obj.pattern = pattern;
		obj.key = context;
		ht_context = g_hash_table_find (ht, search_key_glob_based, &obj);
		if (pattern)
			g_pattern_spec_free (pattern);
	}
	if (!ht_context) {
		/*
		  Search label based
		*/
		OBJInfo obj;

		g_print ("Search label based: %s - %d\n", context, obj_is_window);

		obj.obj_is_window = obj_is_window;
		obj.pattern = NULL;
		obj.key = context;
		ht_context = g_hash_table_find (ht, search_label_based, &obj);
	}
	if (!ht_context) {
		/*
		  Search label based on glob expression
		*/
		OBJInfo obj;
		GPatternSpec *pattern = NULL;

		g_print ("Search label based on glob expression: %s\n", context);
		if (context)
			pattern = g_pattern_spec_new (context);

		obj.obj_is_window = obj_is_window;
		obj.pattern = pattern;
		obj.key = context;
		ht_context = g_hash_table_find (ht, search_label_glob_based, &obj);
		if (pattern)
			g_pattern_spec_free (pattern);
	}
	if (!ht_context) {
		/*
		  Search key after stripping space
		*/
		g_print ("Search key after stripping space: %s\n", context);
		ht_context = g_hash_table_find (ht, search_obj_after_stripping_space, context);
	}
	if (!ht_context) {
		msg = g_strdup_printf ("Object definition %s not found in appmap", context);
		g_print ("%s\n", msg);
		log_msg (LDTP_LOG_DEBUG, msg, log_fp);
		g_free (msg);
	}
	return ht_context;
}

char*
get_property (GHashTable *ht, char *property, FILE *log_fp)
{
	char *value = NULL;
	char *msg = NULL;
	LDTPErrorCode err;
	gboolean flag;

	if (ht == NULL) {
		err =  (LDTP_ERROR_APPMAP_NOT_INITIALIZED);
		g_print ("%s - %d - %s\n", __FILE__, __LINE__, ldtp_error_get_message (err));
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (err), log_fp);
		return NULL;
	}
	if (property == NULL) {
		err =  (LDTP_ERROR_ARGUMENT_NULL);
		g_print ("%s\n", ldtp_error_get_message (err));
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (err), log_fp);
		return NULL;
	}
	flag = g_hash_table_lookup_extended (ht, property, NULL, (gpointer) &value);

	if (!flag || !value) {
		msg = g_strdup_printf ("Property %s not found in appmap", property);
		g_print ("%s\n", msg);
		log_msg (LDTP_LOG_DEBUG, msg, log_fp);
		g_free (msg);
	}
	else
		g_print ("Property: %s - Value: %s\n", property, value);
	return value;
}

gboolean
search_title_based (gpointer key, gpointer value, gpointer user_data)
{
	char *tmp_key = NULL;
	if (!key && !user_data)
		return FALSE;
	if (g_utf8_collate (key, user_data) == 0)
		return TRUE;
	if (g_pattern_match_simple (key, user_data))
		return TRUE;
	tmp_key = g_strdup_printf ("*%s", (char *)key);
	if (tmp_key && g_pattern_match_simple (tmp_key, user_data)) {
		g_free (tmp_key);
		return TRUE;
	}
	if (tmp_key)
		g_free (tmp_key);
	return FALSE;
}
