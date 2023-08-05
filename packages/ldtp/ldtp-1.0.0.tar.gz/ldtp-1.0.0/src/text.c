/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Nagappan A <nagappan@gmail.com>
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
#include "ldtp-error.h"
#include "ldtp-logger.h"
#include "ldtp-command.h"
#include "ldtp-gui-comp.h"

static LDTPErrorCode
is_text_state_enabled (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleStateSet *state;
	state = Accessible_getStateSet (object);

	if (AccessibleStateSet_contains (state, SPI_STATE_EDITABLE))
		error =  (LDTP_ERROR_SUCCESS);
	else
		error = (LDTP_ERROR_TEXT_STATE_NOT_ENABLED);
	log_msg (LDTP_LOG_INFO, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
set_text_value (Accessible *object, char *text, FILE *log_fp)
{
	LDTPErrorCode error;

	if (Accessible_isEditableText (object)) {
		SPIBoolean flag = FALSE;
		if (Accessible_isComponent (object)) {
			AccessibleComponent *accessible_component;
			accessible_component = Accessible_getComponent (object);
			flag = AccessibleComponent_grabFocus (accessible_component);
			Accessible_unref (accessible_component);
		}
		AccessibleEditableText *editableText = Accessible_getEditableText (object);
		flag = AccessibleEditableText_setTextContents (editableText, text);
		Accessible_unref (editableText);
		if (flag == FALSE) {
			g_print ("%s - %d\n", __FILE__, __LINE__);
			error =  (LDTP_ERROR_UNABLE_TO_SET_TEXT);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
		return  (LDTP_ERROR_SUCCESS);
	}
	g_print ("%s - %d\n", __FILE__, __LINE__);
	error =  (LDTP_ERROR_UNABLE_TO_SET_TEXT);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
cut_text (Accessible *object, int startpos, int endpos, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleEditableText *editableText;

	if (Accessible_isEditableText (object)) {
		AccessibleText *text = NULL;
		editableText = Accessible_getEditableText (object);
		if (editableText) {
			SPIBoolean flag = FALSE;
			if (!endpos) {
				text = Accessible_getText (object);
				if (text) {
					endpos = AccessibleText_getCharacterCount (text);
					Accessible_unref (text);
				}
				else {
					Accessible_unref (editableText);
					return  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
				}					
			}
			flag = AccessibleEditableText_cutText (editableText, startpos, endpos);
			Accessible_unref (editableText);
			if (flag)
				return  (LDTP_ERROR_SUCCESS);
			else {
				error =  (LDTP_ERROR_UNABLE_TO_CUT_TEXT);
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
				return error;
			}
		}
	}
	error =  (LDTP_ERROR_UNABLE_TO_CUT_TEXT);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
} 

static LDTPErrorCode
activate_text (Accessible *object, FILE *log_fp)
{
	long i;
	long action_count;
	char *name = NULL;
	LDTPErrorCode error;
	SPIBoolean result = FALSE;
	AccessibleAction *action;

	name = Accessible_getName (object);
	g_print ("Text name: %s\n", name);
	SPI_freeString (name);

	/*
	  Get action handle of the given object
	*/
	action = Accessible_getAction (object);
	action_count = AccessibleAction_getNActions (action);
	g_print ("action count: %ld\n", action_count);
	for (i = 0; i < action_count; i++) {
		char *name, *desc;
		name = AccessibleAction_getName (action, i);
		desc = AccessibleAction_getDescription (action, i);
		g_print ("Name: %s\tDesc: %s\n", name, desc);
		if (g_ascii_strcasecmp (name, "activate") == 0) {
			SPI_freeString (name);
			SPI_freeString (desc);
			/*
			  To execute activate action
			*/
			result = AccessibleAction_doAction (action, i);
			Accessible_unref (action);
			break;
		}
		SPI_freeString (name);
		SPI_freeString (desc);
	}

	if (result)
		g_print ("Activate: success\n");
	else {
		error =  (LDTP_ERROR_UNABLE_TO_ACTIVATE_TEXT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
paste_text (Accessible *object, long pos, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleEditableText *editableText;

	if (Accessible_isEditableText (object)) {
		SPIBoolean flag = FALSE;
		editableText = Accessible_getEditableText (object);
		flag = AccessibleEditableText_pasteText (editableText, pos);
		Accessible_unref (editableText);
		if (flag)
			return  (LDTP_ERROR_SUCCESS);
		else {
			error =  (LDTP_ERROR_UNABLE_TO_PASTE_TEXT);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
	}
	error =  (LDTP_ERROR_UNABLE_TO_PASTE_TEXT);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
delete_text (Accessible *object, long startpos, long endpos, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleEditableText *editableText;

	if (Accessible_isEditableText (object)) {
		AccessibleText *text = NULL;
		editableText = Accessible_getEditableText (object);
		if (editableText) {
			SPIBoolean flag = FALSE;
			if (!endpos) {
				text = Accessible_getText (object);
				if (text) {
					endpos = AccessibleText_getCharacterCount (text);
					Accessible_unref (text);
				}
				else {
					Accessible_unref (editableText);
					return  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
				}
			}
			flag = AccessibleEditableText_deleteText (editableText, startpos, endpos);
			Accessible_unref (editableText);
			if (flag)
				return  (LDTP_ERROR_SUCCESS);
			else {
				error =  (LDTP_ERROR_UNABLE_TO_DELETE_TEXT);
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
				return error;
			}
		}
	}
	error =  (LDTP_ERROR_UNABLE_TO_DELETE_TEXT);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
select_text_by_index_and_region (Accessible *object, long startpos,
				 long endpos, long selection_num,
				 FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleEditableText *editableText;

	if (Accessible_isEditableText (object)) {
		AccessibleText *text = NULL;
		editableText = Accessible_getEditableText (object);
		if (editableText) {
			SPIBoolean flag = FALSE;
			if (!endpos) {
				text = Accessible_getText (object);
				if (text) {
					endpos = AccessibleText_getCharacterCount (text);
					Accessible_unref (text);
				}
				else {
					Accessible_unref (editableText);
					return  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
				}
			}
			flag = AccessibleText_setSelection (editableText, selection_num, startpos, endpos);
			Accessible_unref (editableText);
			if (flag)
				return  (LDTP_ERROR_SUCCESS);
			else {
				error =  (LDTP_ERROR_UNABLE_TO_SELECT_TEXT);
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
				return error;
			}
		}
	}
	error =  (LDTP_ERROR_UNABLE_TO_SELECT_TEXT);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
select_text_by_name (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	SPIBoolean flag = FALSE;
	AccessibleText *text;

	text = Accessible_getText (object);
	if (!text) {
		error =  (LDTP_ERROR_UNABLE_TO_SELECT_TEXT);
		return error;
	}
	flag = AccessibleText_addSelection (text, 0,
					    AccessibleText_getCharacterCount (text));
	if (flag)
		error =  (LDTP_ERROR_SUCCESS);
	else {
		error = (LDTP_ERROR_UNABLE_TO_SELECT_TEXT_ITEM);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	}
	Accessible_unref (text);
	return error;
}

static char*
get_text_value (Accessible *object)
{
	char *text = NULL;

	AccessibleText *accessibleText;
	g_print ("GETTEXTVALUE\n");
	accessibleText = Accessible_getText (object);
	if (accessibleText) {
		char *tmp = NULL;
		tmp = AccessibleText_getText (accessibleText, 0, LONG_MAX);
		g_print ("Text: %s\n", tmp);
		text = strdup (tmp);
		SPI_freeString (tmp);
		Accessible_unref (accessibleText);
	}
	return text;
}

static LDTPErrorCode
append_text (Accessible *object, char *text, FILE *log_fp)
{
	char *tmp = NULL;
	LDTPErrorCode error;
	char *available_text = NULL;
	if (text == NULL) {
		error =  (LDTP_ERROR_ARGUMENT_NULL);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	available_text = get_text_value (object);
	if (!available_text) {
		error =  (LDTP_ERROR_UNABLE_TO_APPEND_TEXT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	tmp = g_strdup_printf ("%s%s", available_text, text);
	free (available_text);
	error = set_text_value (object, tmp, log_fp);
	free (tmp);
	if (error == LDTP_ERROR_SUCCESS)
		return error;
	error =  (LDTP_ERROR_UNABLE_TO_APPEND_TEXT);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
verify_set_text_value (Accessible *object, char *verify_text, FILE *log_fp)
{
	char *text = NULL;
	AccessibleText *text_object = NULL;
	LDTPErrorCode error;
	
	text_object = Accessible_getText (object);
	if (text_object) {
		text = AccessibleText_getText (text_object, 0, AccessibleText_getCharacterCount (text_object));
		Accessible_unref (text_object);
		g_print ("Text: %s\n", text);
	}
	else {
		error =  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	if (verify_text == NULL || text == NULL ||
	    g_utf8_collate (verify_text, text) != 0) {
		LDTPErrorCode error;
		SPI_freeString (text);
		error =  (LDTP_ERROR_VERIFY_SET_TEXT_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	else
		SPI_freeString (text);
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
verify_partial_match (Accessible *object, char *textvalue, FILE *log_fp)
{
	char *tmp = NULL,*sub = NULL;
	LDTPErrorCode error;
	AccessibleText *accessibleText;
	int i, j, k;
	
	sub = textvalue;
	accessibleText = Accessible_getText (object);
	if (accessibleText == NULL) {
		error =  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	
	tmp = AccessibleText_getText (accessibleText, 0, -1);
	Accessible_unref (accessibleText);
	
	for (i = 0 ; tmp[i] != '\0' ; i++) {
		for(j = i, k=0; sub && sub[k] != '\0' && tmp[j] == sub[k] ; j++ , k++) 
			; /* Do nothing */
		if( k > 0 && sub[k] == '\0')
			return  (LDTP_ERROR_SUCCESS);
	}
	error =  (LDTP_ERROR_VERIFY_PARTIAL_MATCH_FAILED);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
get_text (Accessible *object, GSList **l)
{
	char *tmp = NULL;
	long startpos = 0;
	long endpos = 0;
	GSList *tmp_list = *l;
	AccessibleText *accessibleText;
	LDTPErrorCode error;
	
	accessibleText = Accessible_getText (object);
	if (accessibleText == NULL) {
		error =  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
		return error;
	}

	if (tmp_list && tmp_list->data) {
		startpos = atol (tmp_list->data);
		tmp_list = tmp_list->next;
	}
	if (tmp_list && tmp_list->data && atol (tmp_list->data) > 0)
		endpos = atol (tmp_list->data);
	else
		endpos = AccessibleText_getCharacterCount (accessibleText);
	g_print ("Start: %ld, End: %ld\n", startpos, endpos);
	tmp = AccessibleText_getText (accessibleText, startpos, endpos);

	Accessible_unref (accessibleText);
	if (tmp) {
		*l = g_slist_prepend (*l, g_strdup (tmp));
		g_print ("GetTextValue: %s\n", tmp);
		SPI_freeString (tmp);
		return  (LDTP_ERROR_SUCCESS);
	}
	else
		return  (LDTP_ERROR_GETTEXTVALUE_FAILED);
}

static long
get_character_count (Accessible *object)
{
	AccessibleText *accessibleText;
	long len;
	accessibleText = Accessible_getText (object);
	if (accessibleText == NULL)
		return (long) -1;

	len =  AccessibleText_getCharacterCount (accessibleText);
	Accessible_unref (accessibleText);
	return len;
}

static long
get_cursor_position (Accessible *object)
{
	AccessibleText *accessibleText;
	long pos;
	accessibleText = Accessible_getText (object);//cctxt->gui_handle->handle);

	if (accessibleText == NULL)
		return (long) -1;
	
	pos = AccessibleText_getCaretOffset (accessibleText);
	g_print ("Setting Caret position to %ld\n",pos);
	Accessible_unref (accessibleText);
	return pos;
}

static LDTPErrorCode
set_cursor_position (LDTPClientContext *cctxt)
{
	AccessibleText *accessibleText;
	LDTPErrorCode error;
	SPIBoolean flag;
	long offset;
	long count;
	FILE *log_fp = cctxt->log_fp;

	if (!cctxt->req->arg_list || !cctxt->req->arg_list->data) {
		error =  (LDTP_ERROR_ARGUMENT_NULL);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	offset = atol (cctxt->req->arg_list->data);
	count = get_character_count (cctxt->gui_handle->handle);
	if (count < offset) {
		error =  (LDTP_ERROR_OFFSET_OUT_OF_BOUND);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	accessibleText = Accessible_getText (cctxt->gui_handle->handle);
	if (accessibleText == NULL) {
		error =  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	
	flag = AccessibleText_setCaretOffset (accessibleText, offset);
	if (flag == FALSE) {
		error =  (LDTP_ERROR_UNABLE_TO_SET_CARET);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	Accessible_unref (accessibleText);

	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
copy_text (Accessible *object, int startpos, int endpos, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleText *editableText;

	if (Accessible_isEditableText (object)) {
		AccessibleText *text = NULL;
		editableText = Accessible_getEditableText (object);
		if (editableText) {
			SPIBoolean flag = FALSE;
			if (!endpos) {
				text = Accessible_getText (object);
				if (text) {
					endpos = AccessibleText_getCharacterCount (text);
					Accessible_unref (text);
				}
				else {
					Accessible_unref (editableText);
					return  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
				}					
			}
			flag = AccessibleEditableText_copyText (editableText, startpos, endpos);
			Accessible_unref (editableText);
			if (flag)
				return  (LDTP_ERROR_SUCCESS);
			else {
				error =  (LDTP_ERROR_UNABLE_TO_COPY_TEXT);
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
				return error;
			}
		}
	}
	error =  (LDTP_ERROR_UNABLE_TO_COPY_TEXT);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
insert_text (Accessible *object, char *text, int pos, FILE *log_fp)
{
	long len = 0;
	LDTPErrorCode error;
	AccessibleEditableText *editableText;
	long present_length = 0;
	
	if (text == NULL) {
		error =  (LDTP_ERROR_TEXT_TO_INSERT_IS_EMPTY);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	present_length = get_character_count (object);
	if (pos>present_length)
		log_msg (LDTP_LOG_WARNING, "Inserting text in earlier position due to inadequate text present", log_fp);
	len = strlen (text);

	g_print ("Length of text = %ld\n", len +1);
	if (Accessible_isEditableText (object)) {
		SPIBoolean flag = FALSE;
		editableText = Accessible_getEditableText (object);
		flag = AccessibleEditableText_insertText (editableText, pos, text, len);
		Accessible_unref (editableText);
		if (flag == TRUE)
			return  (LDTP_ERROR_SUCCESS);
	}
	error =  (LDTP_ERROR_UNABLE_TO_INSERT_TEXT);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
get_text_property (Accessible *object, GSList **l, FILE *log_fp)
{
	long start_pos = 0;
	long end_pos = 0;
	long int diff, zero = 0;
	GSList *tmp = *l;
	char *text_prop = NULL;
	AccessibleText *accessibleText;
	LDTPErrorCode error;
	
	accessibleText = Accessible_getText (object);
	if (accessibleText == NULL) {
		error =  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	if (tmp && tmp->data) {
		start_pos = atol (tmp->data);
		tmp = tmp->next;
		if (tmp && tmp->data && (atol (tmp->data) > 0))
			end_pos = atol (tmp->data);
		else
			end_pos = AccessibleText_getCharacterCount (accessibleText);
	}

	diff = end_pos - start_pos;
	text_prop = AccessibleText_getAttributes (accessibleText, start_pos, &zero, &diff);
	/* AccessibleText_getAttributes doesn't seem to be taking the
	end position i.e. the diff value into account. It only checks
	from the start position */

	if (text_prop) {
		/* 
		   We don't have to free params[0] as they are just pointers
		   to actual parameters in LDTPRequest structure.
		*/
		*l = g_slist_prepend (*l, g_strdup (text_prop));
		SPI_freeString (text_prop);
		Accessible_unref (accessibleText);
		return  (LDTP_ERROR_SUCCESS);
	}
	else {
		LDTPErrorCode error;
		/* 
		   We don't have to free params[0] as they are just pointers
		   to actual parameters in LDTPRequest structure.
		*/
		Accessible_unref (accessibleText);
		error =  (LDTP_ERROR_UNABLE_TO_GET_TEXT_PROPERTY);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
compare_text_property (Accessible *object, GSList *l, FILE *log_fp)
{
	char *key;
	char *value;
	long start_pos = 0;
	long end_pos = 0;
	GSList *tmp = l;
	LDTPErrorCode error;
	char *text_prop = NULL;
	char *specimen_prop = NULL;
	int total = 0;
	gboolean flag = FALSE;
	GHashTable *property_table;
	AccessibleText *accessibleText;

	accessibleText = Accessible_getText (object);
	if (accessibleText == NULL) {
		error =  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	
	if (tmp && tmp->data) {
		start_pos = atol (tmp->data);
		tmp = tmp->next;
		if (tmp && tmp->data && (atol (tmp->data) > 0))
			end_pos = atol (tmp->data);
		else
			end_pos = AccessibleText_getCharacterCount (accessibleText);
	}
	tmp = tmp->next;
	specimen_prop = g_strdup (tmp->data);
	text_prop = AccessibleText_getAttributes (accessibleText, 0, &start_pos, &end_pos);

	if (text_prop) {
		property_table = g_hash_table_new (&g_str_hash, &g_str_equal);
		key = strtok (g_strdup (specimen_prop), ":");
		while (key) {
			key = g_strdup (g_strstrip (key));
			value = strtok (NULL, ";");
			if (value)
				value = g_strdup (g_strstrip (value));
			g_hash_table_insert (property_table, g_strdup (key), g_strdup (value));
			total++;
			g_free (value);
			g_free (key);
			key = strtok (NULL, ":");
		}
		g_print ("Obtained text property: %s\n", text_prop);
		key = strtok (strdup (text_prop), ":");
		while (key) {
			char *hash_value;
			key = g_strdup (g_strstrip (key));
			value = strtok (NULL, ";");
			if (value)
				value = g_strdup (g_strstrip (value));
			hash_value = g_hash_table_lookup (property_table, key);
			if (hash_value) {
				if (g_utf8_collate (value, hash_value) == 0)
					total--;
				else {
					g_free (value);
					flag = TRUE;
					break;
				}
			}
			else {
				g_free (value);
				flag = TRUE;
				break;
			}
			g_free (value);
			key = strtok (NULL, ":");
		}
		g_hash_table_destroy (property_table);
		SPI_freeString (text_prop);
		g_free (specimen_prop);
		Accessible_unref (accessibleText);

		if (total == 0 && flag == FALSE)
			return  (LDTP_ERROR_SUCCESS);
		error =  (LDTP_ERROR_ONE_OR_MORE_PROPERTIES_DOES_NOT_MATCH);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	g_free (specimen_prop);
	Accessible_unref (accessibleText);
	error =  (LDTP_ERROR_UNABLE_TO_GET_TEXT_PROPERTY);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
contains_text_property (Accessible *object, GSList *l, FILE *log_fp)
{
	char *key = NULL;
	char *value = NULL;
	long start_pos = 0;
	long end_pos = 0;
	LDTPErrorCode error;
	char *text_prop = NULL;
	char *property = NULL;
	char *prop_key = NULL;
	char *prop_value = NULL;
	GHashTable *property_table;
	AccessibleText *accessibleText;

	accessibleText = Accessible_getText (object);
	if (accessibleText == NULL) {
		error =  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	
	if (l && l->data) {
		start_pos = atol (l->data);
		l = l->next;
		if (l && l->data && (atol (l->data) > 0))
			end_pos = atol (l->data);
		else
			end_pos = AccessibleText_getCharacterCount (accessibleText);
	}
	l = l->next;
	if (l && l->data)
		property = strdup (l->data);
	text_prop = AccessibleText_getAttributes (accessibleText, 0, &start_pos, &end_pos);

	if (text_prop) {
		property_table = g_hash_table_new (&g_str_hash, &g_str_equal);
		g_print ("Obtained text property: %s\n", text_prop);
		key = strtok (strdup (text_prop), ":");
		while (key) {
			key = g_strdup (g_strstrip (key));
			value = strtok (NULL, ";");
			if (value)
				value = g_strdup (g_strstrip (value));
			g_hash_table_insert (property_table, g_strdup (key), g_strdup (value));
			g_free (value);
			g_free (key);
			key = strtok (NULL, ":");
		}
		prop_key = strtok (strdup (property), ":");
		prop_value = strtok (NULL, ";");
		if (prop_key && prop_value) {
			value = g_hash_table_lookup (property_table, prop_key);
			if (value) {
				if (g_utf8_collate (value, prop_value) == 0) {
					g_free (property);
					g_free (prop_key);
					Accessible_unref (accessibleText);
					g_hash_table_destroy (property_table);
					SPI_freeString (text_prop);
					log_msg (LDTP_LOG_INFO, "Property matches", log_fp);
					return  (LDTP_ERROR_SUCCESS);
				}
				else {
					g_free (property);
					g_free (prop_key);
					Accessible_unref (accessibleText);
					g_hash_table_destroy (property_table);
					SPI_freeString (text_prop);
					error =  (LDTP_ERROR_TEXT_OBJECT_VALUE_CONTAINS_DIFF_PROEPRTY);
					log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
					return error;
				}
			}
			else {
				g_free (property);
				g_free (prop_key);
				Accessible_unref (accessibleText);
				SPI_freeString (text_prop);
				error =  (LDTP_ERROR_TEXT_OBJECT_DOES_NOT_CONTAIN_PROEPRTY);
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
				return error;
			}
		}
		else {
			g_free (property);
			Accessible_unref (accessibleText);
			SPI_freeString (text_prop);
			error =  (LDTP_ERROR_TEXT_PROEPRTY_VALUE_PAIR_IS_INVALID);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
	}
	else {
		g_free (property);
		Accessible_unref (accessibleText);
		error =  (LDTP_ERROR_UNABLE_TO_GET_TEXT_PROPERTY);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
right_click (Accessible *object)
{
	gboolean flag = FALSE;
	long x, y, height, width;
	if (Accessible_isComponent (object)) {
		AccessibleComponent *accessible_component;
		accessible_component = Accessible_getComponent (object);
		AccessibleComponent_getExtents (accessible_component,
						&x, &y, &height, &width,
						SPI_COORD_TYPE_WINDOW);
		g_print ("X = %ld, Y = %ld, Width = %ld, Height = %ld\n",
			 x, y, width, height);
		g_print ("X = %ld, Y = %ld, Width / 2 = %ld, Height / 2 = %ld\n",
			 x, y, width / 2, height / 2);
		flag = AccessibleComponent_grabFocus (accessible_component);
		Accessible_unref (accessible_component);
	}
	if (flag && SPI_generateMouseEvent (x + width / 2, y + height / 2, "b3c"))
		return  (LDTP_ERROR_SUCCESS);
	else
		return  (LDTP_ERROR_RIGHT_CLICK_FAILED);
}

LDTPErrorCode
text_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_SETTEXTVALUE:
		if (cctxt->req->arg_list == NULL || cctxt->req->arg_list->data == NULL)
			error = set_text_value (cctxt->gui_handle->handle,
						"", cctxt->log_fp);
		else
			error = set_text_value (cctxt->gui_handle->handle,
						cctxt->req->arg_list->data,
						cctxt->log_fp);
		break;
	case LDTP_CMD_CUTTEXT: {
		long startpos = 0;
		long endpos = 0;
		GSList *l = cctxt->req->arg_list;
		if (l && l->data) {
			startpos = atol (l->data);
			l = l->next;
			if (l && l->data)
				endpos = atol (l->data);
		}
		/*TODO: Check if the given positions are within the character length*/
		error = cut_text (cctxt->gui_handle->handle, startpos, endpos, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_PASTETEXT: {
		long pos = 0;
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			pos = atol (cctxt->req->arg_list->data);
		error = paste_text (cctxt->gui_handle->handle, pos, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_ACTIVATETEXT:
		error = activate_text (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_DELETETEXT: {
		long startpos = 0;
		long endpos = 0;
		GSList *l = cctxt->req->arg_list;
		if (l && l->data) {
			startpos = atol (l->data);
			l = l->next;
			if (l && l->data)
				endpos = atol (l->data);
		}
		/*TODO: check if the given positions are within the available text length*/
		error = delete_text (cctxt->gui_handle->handle, startpos, endpos, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_SELECTTEXTBYINDEXANDREGION: {
		/*
		  Select text based on index and optional region text
		*/
		long startpos = 0;
		long endpos = 0;
		long selection_num = 0;
		GSList *l = cctxt->req->arg_list;
		if (l && l->data) {
			startpos = atol (l->data);
			l = l->next;
			if (l && l->data) {
				endpos = atol (l->data);
				l = l->next;
				if (l && l->data)
					selection_num = atol (l->data);
			}
		}
		/*TODO: check if the given positions are within the available text length*/
		error = select_text_by_index_and_region (cctxt->gui_handle->handle,
							 selection_num, startpos,
							 endpos, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_SELECTTEXTBYNAME: {
		error = select_text_by_name (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_APPENDTEXT:
		if (cctxt->req->arg_list == NULL || cctxt->req->arg_list->data == NULL)
			error = append_text (cctxt->gui_handle->handle,
					     "", cctxt->log_fp);
		else
			error = append_text (cctxt->gui_handle->handle,
					     cctxt->req->arg_list->data, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYPARTIALMATCH:
		if (cctxt->req->arg_list == NULL || cctxt->req->arg_list->data == NULL)
			error = verify_partial_match (cctxt->gui_handle->handle,
						      "", cctxt->log_fp);
		else
			error = verify_partial_match (cctxt->gui_handle->handle,
						      cctxt->req->arg_list->data,
						      cctxt->log_fp);
		break;	
	case LDTP_CMD_GETTEXTVALUE:
		error = get_text (cctxt->gui_handle->handle, &cctxt->req->arg_list);
		if (error == LDTP_ERROR_SUCCESS) {
			if (cctxt->req->arg_list && cctxt->req->arg_list->data) {
				cctxt->resp->data = cctxt->req->arg_list->data;
				cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
				cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, cctxt->req->arg_list->data);
			} else {
				error =  (LDTP_ERROR_GETTEXTVALUE_FAILED);
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
				return error;
			}
		}
		break;
	case LDTP_CMD_VERIFYSETTEXT:
		if (cctxt->req->arg_list == NULL || cctxt->req->arg_list->data == NULL)
			error = verify_set_text_value (cctxt->gui_handle->handle,
						       "", cctxt->log_fp);
		else
			error = verify_set_text_value (cctxt->gui_handle->handle,
						       cctxt->req->arg_list->data,
						       cctxt->log_fp);
		break;
	case LDTP_CMD_GRABFOCUS:
		error = grab_focus (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_GETCHARCOUNT:
		cctxt->resp->data = g_strdup_printf ("%ld", get_character_count (cctxt->gui_handle->handle));
		cctxt->resp->data_len = strlen (cctxt->resp->data);
		error =  (LDTP_ERROR_SUCCESS);
		break;
	case LDTP_CMD_COPYTEXT: {
		long startpos = 0;
		long endpos = 0;
		GSList *l = cctxt->req->arg_list;
		if (l && l->data) {
			startpos = atol (l->data);
			l = l->next;
			if (l && l->data)
				endpos = atol (l->data);
		}
		/*TODO: check if the given positions are within the available text length*/
		error = copy_text (cctxt->gui_handle->handle, startpos, endpos,
				   cctxt->log_fp);
		break;
	}
	case LDTP_CMD_INSERTTEXT: {
		long pos = 0;
		char *text = NULL;
		GSList *l = cctxt->req->arg_list;
		if (l && l->data) {
			pos = atol(l->data);
			l = l->next;
			if (l && l->data) {
				text = l->data;
			}
		}
		
		if (text == NULL)
			error = insert_text (cctxt->gui_handle->handle, "",
					     pos, cctxt->log_fp);
		else
			error = insert_text (cctxt->gui_handle->handle, text,
					     pos, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_GETTEXTPROPERTY:
		error = get_text_property (cctxt->gui_handle->handle,
					   &cctxt->req->arg_list, cctxt->log_fp);
		if (error == LDTP_ERROR_SUCCESS) {
			cctxt->resp->data = cctxt->req->arg_list->data;
			cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
			cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, cctxt->req->arg_list->data);
		}
		break;
	case LDTP_CMD_COMPARETEXTPROPERTY:
		error = compare_text_property (cctxt->gui_handle->handle,
					       cctxt->req->arg_list, cctxt->log_fp);
		break;
	case LDTP_CMD_CONTAINSTEXTPROPERTY:
		error = contains_text_property (cctxt->gui_handle->handle,
						cctxt->req->arg_list, cctxt->log_fp);
		break;
	case LDTP_CMD_ISTEXTSTATEENABLED:
		error = is_text_state_enabled (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_RIGHTCLICK:
		error = right_click (cctxt->gui_handle->handle);
		break;
        case LDTP_CMD_MOUSELEFTCLICK:
        case LDTP_CMD_MOUSERIGHTCLICK: {
		error = is_text_state_enabled (cctxt->gui_handle->handle, cctxt->log_fp);
                if (error != LDTP_ERROR_SUCCESS)
                        error = device_main (cctxt, command);
                break;
        }
        case LDTP_CMD_MOUSEMOVE:
                error = device_main (cctxt, command);
                break;
	case LDTP_CMD_KBDENTER:
		error = device_main (cctxt, command);
		break;
	case LDTP_CMD_SETCURSOR:
		error = set_cursor_position (cctxt);
		break;
	case LDTP_CMD_GETCURSOR: {
		glong position;
		position = get_cursor_position (cctxt->gui_handle->handle);
		if (position == -1)
			error =  (LDTP_ERROR_TEXT_NOT_ACCESSIBLE);
		else {
			cctxt->resp->data = g_strdup_printf ("%ld", position);
			cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
			error =  (LDTP_ERROR_SUCCESS);
		}
		break;
	}
	default:
		error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
	}
	return error;
}
