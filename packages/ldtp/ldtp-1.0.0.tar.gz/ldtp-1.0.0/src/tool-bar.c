/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/* 
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Bhargavi K <kbhargavi_83@yahoo.co.in>
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
verify_visible_button_count (Accessible *object, long expected_button_count, FILE *log_fp)
{
	long i;
	char *name;
	long child_count = 0;
	long button_count = 0;
	long visible_button_count = 0;
	Accessible *child;
	AccessibleRole role;
	AccessibleStateSet *state;

	child_count = Accessible_getChildCount (object);
	g_print ("Child count: %ld\n", child_count);
	for (i = 0 ; i < child_count ; i++) {
		child = Accessible_getChildAtIndex (object, i);
		name = Accessible_getName (child);
		g_print ("Name: %s\n", name);
		SPI_freeString (name);
		do {
			button_count = Accessible_getChildCount (child);
			if (button_count > 0) {
				Accessible *tmp_child;
				tmp_child = child;
				child = Accessible_getChildAtIndex (child, 0);
				Accessible_unref (tmp_child);
			}
		} while (button_count > 0);

		state = Accessible_getStateSet (child);
		role =  Accessible_getRole (child);
		Accessible_unref (child);

		if (AccessibleStateSet_contains (state, SPI_STATE_VISIBLE) &&
		    role == SPI_ROLE_PUSH_BUTTON)
			visible_button_count++;
		AccessibleStateSet_unref (state);
	}
	visible_button_count > 0 ? visible_button_count++ : visible_button_count;
	g_print ("Expected: %ld - Actual: %ld\n", expected_button_count, visible_button_count);
	if (visible_button_count != expected_button_count) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_TOOLBAR_VISIBLE_BUTTON_COUNT_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return  (LDTP_ERROR_SUCCESS);
}	

static LDTPErrorCode
verify_button_count (Accessible *object, long expected_button_count, FILE *log_fp)
{
	LDTPErrorCode error;
	long i;
	long child_count;
	long button_count = 0;
	long actual_button_count = 0;
	char *name;
	Accessible *child;
	
	child_count = Accessible_getChildCount (object);
	for (i = 0; i < child_count; i++) {
		child = Accessible_getChildAtIndex (object, i);
		name = Accessible_getName (child);
		g_print ("Name: %s\n", name);
		SPI_freeString (name);
		do {
			button_count = Accessible_getChildCount (child);
			if (button_count > 0) {
				Accessible *tmp_child;
				tmp_child = child;
				child = Accessible_getChildAtIndex (child, 0);
				Accessible_unref (tmp_child);
			}
		} while (button_count > 0);

		if (Accessible_getRole (child) == SPI_ROLE_PUSH_BUTTON)
			actual_button_count++;
		Accessible_unref (child);
	}
	g_print ("Child: %ld - Expected: %ld - Actual - %ld\n", child_count, expected_button_count, actual_button_count);
	if (actual_button_count != expected_button_count) {
		error =  (LDTP_ERROR_TOOLBAR_BUTTON_COUNT_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return  (LDTP_ERROR_SUCCESS);
}	

LDTPErrorCode
tool_bar_main (LDTPClientContext* cctxt, int command)
{
	long count = 0;
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_VERIFYBUTTONCOUNT:
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			count = atol (cctxt->req->arg_list->data);
		error = verify_button_count (cctxt->gui_handle->handle,
					     count,
					     cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYVISIBLEBUTTONCOUNT:
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			count = atol (cctxt->req->arg_list->data);
		error = verify_visible_button_count (cctxt->gui_handle->handle,
						     count,
						     cctxt->log_fp);
		break;
	default:
		error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
		break;
	}
	return error;
}
