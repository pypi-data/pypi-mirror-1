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

#include "ldtp.h"
#include "ldtp-gui.h"
#include "remap.h"
#include "ldtp-utils.h"
#include "ldtp-error.h"
#include "ldtp-logger.h"
#include "ldtp-command.h"
#include "ldtp-gui-comp.h"
#include "localization.h"

gboolean catalogs_initialised = FALSE;

LdtpHashTable *english_catalog;
LdtpHashTable *locale_catalog;

#ifdef ENABLE_LOCALIZATION

static gboolean
init_hash_tables (void)
{
	english_catalog = (LdtpHashTable *)g_malloc (sizeof(LdtpHashTable));
	if (english_catalog) {
		english_catalog->table = g_hash_table_new (&g_str_hash, &g_str_equal);
		english_catalog->next = NULL;
	}
	else
		return FALSE;
  
	locale_catalog = (LdtpHashTable *)g_malloc (sizeof(LdtpHashTable));
	if (locale_catalog) {
		locale_catalog->table = g_hash_table_new (&g_str_hash, &g_str_equal);
		locale_catalog->next = NULL;
	}
	else
		return FALSE;
  
	return TRUE;
}

static LdtpHashTable*
ldtp_add_to_hash_list (LdtpHashTable *ldtphash)
{
	LdtpHashTable *node,*temp;

	for (node=ldtphash; node->next; node=(LdtpHashTable*)node->next);	
  
	node->next = (struct LdtpHashTable*)g_malloc (sizeof (LdtpHashTable));
	if (!node->next)
		return NULL;
  
	temp = (LdtpHashTable*) node->next;
	temp->table = g_hash_table_new (&g_str_hash, &g_str_equal);
	temp->next = NULL;
	return temp;
}

static void
ldtp_insert_keyval (LdtpHashTable *ldtphash, gchar* key, gchar* val)
{
	int found = 0;
	LdtpHashTable *insertpoint;
	/* Insert the key-value in the first hash table
	   which does not have this pair
	*/
	insertpoint = ldtphash;
	for (;insertpoint; insertpoint = (LdtpHashTable*)insertpoint->next) {
		if (!g_hash_table_lookup (insertpoint->table, key)) {
			found = 1;
			break;
		}
	}
	/* Now either we found an insert point OR we reached
	   end of linked list, in which case we allocate one
	   more structure and add this key-value pair to the
	   newly allocated hash table
	*/
	if(!found)
		insertpoint = ldtp_add_to_hash_list (ldtphash);
  
	g_hash_table_insert (insertpoint->table, (gpointer)key, (gpointer)val);
}

static gint
ldtp_hash_key_instance (LdtpHashTable *ldtphash, gchar *key)
{
	gint count = 0;
	LdtpHashTable *temp = ldtphash;

	for ( ;temp; temp=(LdtpHashTable*) temp->next) {
		if (g_hash_table_lookup (temp->table,key))
			count++;
	}
	return count;
}

static gchar*
ldtp_hash_return_value (LdtpHashTable *ldtphash, gchar *key, gint instance)
{
	gint count = 0;
	LdtpHashTable *temp = ldtphash;
	gchar *value;
  
	for (; count < instance; count++)
		temp = (LdtpHashTable*) temp->next;
  
	value = g_hash_table_lookup (temp->table, key);
	return value;
}

gboolean
init_catalog (gchar *filename, FILE *fp)
{
	po_file_t pofile = NULL;

	po_error_handler_t error_handle;
	const char * const *domains;
	const char * const *domainp;
	const char *msgstr = NULL;
	const char *msgid = NULL;
	char msg[256];
  
	memset (msg, 0x00, 256);
	error_handle = (po_error_handler_t) malloc (sizeof (po_error_handler_t));
	pofile = po_file_read (filename, error_handle);
	if (pofile != NULL) {
		domains = po_file_domains (pofile);
		if (!catalogs_initialised) {
			g_print ("Initilising message catalog.....\n");
			catalogs_initialised = init_hash_tables ();
			if (!catalogs_initialised) {
				strcpy (msg, "Unable to inilialise message catalogs");
				g_print ("%s\n", msg);
				log_msg (LDTP_LOG_CAUSE, msg, fp);
				return FALSE;
			}
		}
		for (domainp = domains; *domainp; domainp++) {
			const char *domain = *domainp;
			po_message_t message;
			po_message_iterator_t iterator = po_message_iterator (pofile,
									      domain);
			message = po_next_message (iterator);
			for (;message;) {
				gchar *key;
				gchar *value;
				/* FIXME:
				 * Currently we are not handling
				 * plural messages
				 */
				msgstr = po_message_msgstr (message);
				msgid = po_message_msgid (message);
				if (msgstr && msgid) {
					if (g_utf8_collate (msgstr, "") != 0) {
						key = g_utf8_collate_key (msgstr, -1);
						value = g_strdup (msgid);
						ldtp_insert_keyval (locale_catalog, key, value);
						//g_free (key);
					}
					if (g_utf8_collate (msgid, "") != 0) {
						key = g_utf8_collate_key (msgid, -1);
						value = g_strdup (msgstr);
						ldtp_insert_keyval (english_catalog, key, value);
						//g_free (key);
					}
				}
				message = po_next_message (iterator);
			}
			po_message_iterator_free (iterator);
		}
		po_file_free (pofile);
		return TRUE;
	} else {
		g_sprintf (msg, "Unable to find %s for initialising catalogs", filename);
		g_print ("%s\n", msg);
		log_msg (LDTP_LOG_CAUSE, msg, fp);
		return FALSE;
	}
}

gchar*
ldtp_compare_with_locale (gchar *eng_msg, gchar *locale_msg)
{
	gint i;
	gchar *key;
	gint len = -1;
	gint collate  = -1;
	gint instance = 0;
	gboolean flag = FALSE;
	gchar *tmp_msg     = NULL;
	gchar *under_score = NULL;
	gchar *utf8_string = NULL;

	tmp_msg = g_strdup (eng_msg);
	if (catalogs_initialised && tmp_msg && locale_msg) {
		key = g_utf8_collate_key (tmp_msg, -1);
		instance = ldtp_hash_key_instance (english_catalog, key);
		for (i = 0; i < instance; i++) {
			utf8_string = ldtp_hash_return_value (english_catalog, key, i);
			if (utf8_string && (under_score = g_utf8_strchr (utf8_string,
									 len, '_')) != NULL) {
				gchar *str = NULL;
				str = escape_character (utf8_string, '_');
				g_print ("Before: %s - After: %s\n", utf8_string, str);
				collate = g_utf8_collate (locale_msg, str);
				flag = g_pattern_match_simple (str, locale_msg);
				g_free (str);
			}
			else
				if (utf8_string) {
					collate = g_utf8_collate (locale_msg, utf8_string);
					flag = g_pattern_match_simple (utf8_string, locale_msg);
				}
			if (!collate)
				break;
		}
		if (collate) {
			utf8_string = g_strdup (tmp_msg);
			if (utf8_string) {
				if ((under_score = g_utf8_strchr (utf8_string,
								  len, '_')) != NULL) {
					gchar *str = NULL;
					str = escape_character (utf8_string, '_');
					g_print ("Before: %s - After: %s\n", utf8_string, str);
					collate = g_utf8_collate (locale_msg, str);
					flag = g_pattern_match_simple (str, locale_msg);
					g_free (str);
				}
				else {
					collate = g_utf8_collate (locale_msg, utf8_string);
					flag = g_pattern_match_simple (utf8_string, locale_msg);
				}
			}
		}
		g_free (key);
	}
	else {
		utf8_string = g_strdup (_(tmp_msg));
		if ((under_score = g_utf8_strchr (utf8_string, len, '_')) != NULL) {
			gchar *str = NULL;
			str = escape_character (utf8_string, '_');
			g_print ("Before: %s - After: %s\n", utf8_string, str);
			collate = g_utf8_collate (locale_msg, str);
			flag = g_pattern_match_simple (str, locale_msg);
			g_free (str);
		}
		else {
			collate = g_utf8_collate (locale_msg, utf8_string);
			flag = g_pattern_match_simple (utf8_string, locale_msg);
			g_print ("Locale MSG: %s - UTF8 - %s\n", locale_msg, utf8_string);
		}
	}
	g_free (tmp_msg);
	if (!collate || flag)
		return utf8_string;
	else {
		g_free (utf8_string);
		return NULL;
	}
}

gchar*
reverse_lookup (gchar *spec_msgstr)
{
	gchar *key;
	gchar *value = NULL;
	LdtpHashTable *temp = locale_catalog;
  
	if (catalogs_initialised && spec_msgstr) {
		key = g_utf8_collate_key (spec_msgstr, -1);
      
		for ( ;temp; temp = (LdtpHashTable*) temp->next) {
			value = g_hash_table_lookup (temp->table, key);
			if (value)
				break;
		}
		return g_strdup (value);
	}
	return g_strdup (spec_msgstr);
}

#endif
