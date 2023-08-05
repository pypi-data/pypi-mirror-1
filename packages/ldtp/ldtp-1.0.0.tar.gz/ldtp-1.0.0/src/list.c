/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Poornima Nayak <pnayak@novell.com>
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
select_item (Accessible *object, char *text_item, FILE *log_fp)
{
	long i;
	long count;
	gint collate = -1;
	LDTPErrorCode error;
	gboolean flag = FALSE;
	char *list_text = NULL;
	AccessibleText *text;
	Accessible *child_object;
	
	count = Accessible_getChildCount (object);
	g_print ("Child count: %ld\n", count);

	// In list box check if specified item exists 
	for (i = 0; i < count; i++) {
		child_object = Accessible_getChildAtIndex (object, i);
		text = Accessible_getText (child_object);
		if (text) {
			list_text = AccessibleText_getText (text, 0,
							    AccessibleText_getCharacterCount (text));
			Accessible_unref (text);
		} else {
			list_text = Accessible_getName (child_object);
		}
		if (list_text) {
			/*
			  Compare Listbox value and text value to be selected
			*/
			collate = g_utf8_collate (list_text, text_item);
			SPI_freeString (list_text);
		}
		if (collate == 0) {
			AccessibleSelection *selection = NULL;

			selection = Accessible_getSelection (object);
			if (selection) {
				if (AccessibleSelection_isChildSelected (selection, i) ||
				    AccessibleSelection_selectChild (selection, i)) {
					if (Accessible_isAction (child_object)) {
						AccessibleAction *action = Accessible_getAction (child_object);
						if (action) {
							flag = AccessibleAction_doAction (action, 0);
							Accessible_unref (action);
						}
					} else
						flag = TRUE;
				} else
					log_msg (LDTP_LOG_CAUSE, "Selection failed", log_fp);
				Accessible_unref (selection);
			}
			Accessible_unref (child_object);
			break; // Break for loop
		} // if
		Accessible_unref (child_object);
	} // for
	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);

	error = LDTP_ERROR_UNABLE_TO_SELECT_LIST_ITEM;
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
select_index (Accessible *object, long text_index, FILE *log_fp)
{
	gboolean flag = FALSE;
	LDTPErrorCode error;
	char *text, *name, *desc;
	long child_cnt, i, action_count;
	Accessible *child_object, *parent;
	AccessibleAction *action;
	AccessibleSelection *selection;
	AccessibleText *text_object;
	AccessibleEditableText *editable_text;

	child_cnt = Accessible_getChildCount (object);

	if (text_index > child_cnt) {
		error =  (LDTP_ERROR_LIST_INDEX_GREATER);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	selection = Accessible_getSelection (object);

	if (AccessibleSelection_selectChild (selection, text_index)) {	
		child_object = AccessibleSelection_getSelectedChild (selection, 0);
		Accessible_unref (selection);
		if (child_object == NULL) {
			error =  (LDTP_ERROR_UNABLE_TO_GET_SELECTED_CHILD);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
		text_object = Accessible_getText (child_object);
		text = AccessibleText_getText (text_object, 0, LONG_MAX);
		Accessible_unref (text_object);
	}
	else {
		Accessible_unref (selection);
		error =  (LDTP_ERROR_UNABLE_TO_SELECT_CHILD);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	while (child_object != NULL) {
		parent = Accessible_getParent (child_object);
		Accessible_unref (child_object);
		action = Accessible_getAction (parent);
		action_count = AccessibleAction_getNActions (action);

		if (action_count >= 0) {
			for (i = 0; i < action_count; i++) {
				name = AccessibleAction_getName (action, i);
				desc = AccessibleAction_getDescription (action, i);

				g_print ("Name: %s - Desc: %s\n", name, desc);
				SPI_freeString (desc);
				if (g_ascii_strcasecmp (name, "press") == 0) {
					SPI_freeString (name);
					break;
				}
				SPI_freeString (name);
			}
			/*
			  If 'Takeaction' found in parent of list object, get child of parent
			  which is of type 'Text', to set the Selected text value in combo box.
			  Basically combo box comprises of List box which displays list of values,
			  Text box which contains currently selected value 
			*/
			if (i < action_count) {
				Accessible *object = NULL;
				object = get_text_handle (parent);
				if (object) {
					editable_text = Accessible_getEditableText (object);
					Accessible_unref (object);
					if (editable_text) {
						AccessibleEditableText_setTextContents (editable_text, text);
						Accessible_unref (editable_text);
					}
					flag = AccessibleAction_doAction (action, 0);
				}
				Accessible_unref (action);
				Accessible_unref (parent);
				break;
			}
		} // if (action_count >= 0)
		Accessible_unref (action);
		child_object = parent;	
	} // while
	if (flag == FALSE) {
		error =  (LDTP_ERROR_UNABLE_TO_SELECT_CHILD);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	else
		return  (LDTP_ERROR_SUCCESS);
}

LDTPErrorCode
list_main (LDTPClientContext* cctxt, int command)
{
	long count = 0;
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_SELECTITEM:
	case LDTP_CMD_SELECTTEXTITEM:
		error = select_item (cctxt->gui_handle->handle,
				     cctxt->req->arg_list->data, cctxt->log_fp);
		break;
	case LDTP_CMD_SELECTINDEX:
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			count = atol (cctxt->req->arg_list->data);
		error = select_index (cctxt->gui_handle->handle,
				      count, cctxt->log_fp);
		break;
	default:
		error = ( (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED));
		break;
	}
	return error;
}
