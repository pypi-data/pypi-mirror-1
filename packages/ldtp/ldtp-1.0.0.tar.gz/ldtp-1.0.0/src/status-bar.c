/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    S. Aishwariya <poorvaishoo@yahoo.com>
 *    K. Sree Kamakshi <poorvaishoo@yahoo.com>
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

static gboolean
is_object_status_bar (Accessible *object, FILE *log_fp)
{
	if (wait_till_object_state_contains (object, STATUS_BAR, log_fp) != 0) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return FALSE;
	}
	return TRUE;
}

static gboolean
is_status_bar_state_visible (Accessible *object)
{
	AccessibleStateSet *state;
	state = Accessible_getStateSet (object);

	/*
	  Check if the status bar is visible or not 
	*/

	if (AccessibleStateSet_contains (state, SPI_STATE_VISIBLE))
		return TRUE; //Visible State
	else
		return FALSE;  //Invisible State
}

static LDTPErrorCode
get_statusbar_text (Accessible *object, GSList **l, FILE *log_fp)
{
	char *statusbar_text;
	AccessibleText *text;

	/*
	  Gets the object 'textbox' for the AccessibleObject Status bar
	*/
	text = Accessible_getText (object);

	/*
	  Gets the label(text displayed) of the status bar
	*/
	statusbar_text = AccessibleText_getText (text, 0, AccessibleText_getCharacterCount (text));
  
	if (statusbar_text == NULL) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_STATUSBAR_GETTEXT_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		Accessible_unref (text);
		return error;
	}
	*l = g_slist_prepend (*l, g_strdup (statusbar_text));
	SPI_freeString (statusbar_text);
	Accessible_unref (text);
	return  (LDTP_ERROR_SUCCESS);
}

LDTPErrorCode
status_bar_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_VERIFYSTATUSBAR:
		if (is_object_status_bar (cctxt->gui_handle->handle, cctxt->log_fp))
			error =  (LDTP_ERROR_SUCCESS);
		else
			error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		break;
	case LDTP_CMD_VERIFYSTATUSBARVISIBLE:
		if (is_status_bar_state_visible (cctxt->gui_handle->handle))
			error =  (LDTP_ERROR_SUCCESS);
		else
			error =  (LDTP_ERROR_STATUSBAR_NOT_VISIBLE);
		break;
	case LDTP_CMD_GETSTATUSBARTEXT:
		error = get_statusbar_text (cctxt->gui_handle->handle, &cctxt->req->arg_list,
					    cctxt->log_fp);
		if (error == LDTP_ERROR_SUCCESS) {
			cctxt->resp->data = cctxt->req->arg_list->data;
			cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
			cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, cctxt->req->arg_list->data);
		}
		break;
	default:
		error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
	}
	return error;
}
