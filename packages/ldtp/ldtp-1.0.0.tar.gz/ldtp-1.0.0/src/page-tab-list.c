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
select_tab (Accessible *object, char *tab_name, FILE *log_fp)
{
	long i;
	char *name = NULL;
	LDTPErrorCode error;
	Accessible *child = NULL;
	
	for (i = 0; i < Accessible_getChildCount (object); i++) {
		child = Accessible_getChildAtIndex (object, i);
		name = Accessible_getName (child);

		if (g_utf8_collate (name, tab_name) == 0) {
			AccessibleStateSet *state;

			SPI_freeString (name);
			state = Accessible_getStateSet  (child);
			if (AccessibleStateSet_contains (state, SPI_STATE_SELECTED) == FALSE) {
				SPIBoolean flag = FALSE;
				AccessibleSelection *selection;
				AccessibleComponent *component;

				selection = Accessible_getSelection (object);
				flag = AccessibleSelection_selectChild (selection, i);
				Accessible_unref (selection);
				if (flag) {
					component = Accessible_getComponent (child);
					AccessibleComponent_grabFocus (component);
					Accessible_unref (component);
				}
				Accessible_unref (child);
				if (flag == FALSE) {
					error =  (LDTP_ERROR_PAGE_TAB_NAME_SELECTION_FAILED);
					log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
					return error;
				}
				else {
					return  (LDTP_ERROR_SUCCESS);
				}
			}
			else {
				error =  (LDTP_ERROR_PAGE_TAB_NAME_ALREADY_IN_SELECTED_STATE);
				log_msg (LDTP_LOG_WARNING, ldtp_error_get_message (error), log_fp);
			}
			Accessible_unref (child);
			return  (LDTP_ERROR_SUCCESS);
		} // if (g_utf8_collate (name, tab_name) == 0)
		SPI_freeString (name);
		Accessible_unref (child);
	} // for
	error =  (LDTP_ERROR_PAGE_TAB_NAME_DOESNOT_EXIST);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
select_tab_index (Accessible *object, long tab_number, FILE *log_fp)
{
	long child_count;
	LDTPErrorCode error;
	
	child_count = Accessible_getChildCount (object);
	if (tab_number >= 0 && tab_number < child_count) {
		Accessible *child;
		AccessibleStateSet *state;

		child = Accessible_getChildAtIndex (object, tab_number);
		state = Accessible_getStateSet (child);
		Accessible_unref (child);

		if (AccessibleStateSet_contains (state, SPI_STATE_SELECTED) == FALSE) {
			SPIBoolean flag = FALSE;
			AccessibleSelection *selection;
			selection = Accessible_getSelection (object);
			flag = AccessibleSelection_selectChild (selection, tab_number);
			Accessible_unref (selection);
			if (flag == FALSE) {
				error =  (LDTP_ERROR_PAGE_TAB_NAME_SELECTION_FAILED);
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
				return error;
			}
		}
		else {
			error =  (LDTP_ERROR_PAGE_TAB_NAME_ALREADY_IN_SELECTED_STATE);
			log_msg (LDTP_LOG_WARNING, ldtp_error_get_message (error), log_fp);
		}
		return  (LDTP_ERROR_SUCCESS);
	}
	error =  (LDTP_ERROR_PAGE_TAB_INDEX_DOESNOT_EXIST);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

long
get_page_tab_index (Accessible *accessible)
{
	long i, num_child;
	Accessible *child;
	num_child = Accessible_getChildCount (accessible);

	for (i = 0; i < num_child; i++) {
		AccessibleStateSet *state;
		child = Accessible_getChildAtIndex (accessible, i);
		if (!child)
			continue;
		state = Accessible_getStateSet (child);
		if (AccessibleStateSet_contains (state, SPI_STATE_SELECTED)) {
			Accessible_unref (child);
			return i;
		}
		Accessible_unref (child);
	}
	return -1l;
}

LDTPErrorCode
page_tab_list_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_SELECTTAB:
		if (!cctxt->req->arg_list->data) {
			error = LDTP_ERROR_PAGE_TAB_NAME_INPUT_DOESNOT_EXIST;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
			return error;
		}
		g_print ("Tab name: %s\n", (char *)cctxt->req->arg_list->data);
		error = select_tab (cctxt->gui_handle->handle,
				    cctxt->req->arg_list->data, cctxt->log_fp);
		break;
	case LDTP_CMD_SELECTTABINDEX: {
		long tab_index;
		if (!cctxt->req->arg_list || !cctxt->req->arg_list->data) {
			error = LDTP_ERROR_PAGE_TAB_INDEX_INPUT_DOESNOT_EXIST;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
			return error;
		}
		tab_index = atol (cctxt->req->arg_list->data);

		g_print ("Tab index: %ld\n", tab_index);
		error = select_tab_index (cctxt->gui_handle->handle,
					  tab_index, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_GETTABCOUNT:
		error = panel_main (cctxt, LDTP_CMD_GETPANELCHILDCOUNT);
		break;
	default:
		error = LDTP_ERROR_COMMAND_NOT_IMPLEMENTED;
		break;
	}
	return error;
}
