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

static gboolean
get_state (Accessible *object)
{
	SPIBoolean checked;
	AccessibleStateSet *state;
	
	state = Accessible_getStateSet (object);
	checked = AccessibleStateSet_contains (state, SPI_STATE_CHECKED);

	if (checked)
		return TRUE; // Checked state
	else
		return FALSE; // Unchecked state
}

static LDTPErrorCode
toggle (Accessible *object, FILE *log_fp)
{
	SPIBoolean flag = FALSE;
	AccessibleAction *action;

	if (wait_till_object_state_contains (object, TOGGLE_BUTTON, log_fp) != 0) {
		LDTPErrorCode error;

		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	action = Accessible_getAction (object);
	flag = AccessibleAction_doAction (action, 0);
	Accessible_unref (action);
	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_TOGGLE_ACTION_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
} 

static LDTPErrorCode
press (Accessible *object, FILE *log_fp)
{
	SPIBoolean flag = FALSE;
	AccessibleAction *action;

	if (wait_till_object_state_contains (object, TOGGLE_BUTTON, log_fp) != 0) {
		LDTPErrorCode error;

		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	action = Accessible_getAction (object);
	flag = AccessibleAction_doAction (action, 1);
	Accessible_unref (action);
	if (flag)
		return  (LDTP_ERROR_SUCCESS);
	else {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_TOGGLE_ACTION_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
verify_toggled (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	if (wait_till_object_state_contains (object, TOGGLE_BUTTON, log_fp) != 0) {
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	if (get_state (object) == FALSE) {
		error =  (LDTP_ERROR_TOGGLE_NOT_CHECKED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return  (LDTP_ERROR_SUCCESS);
}
        
LDTPErrorCode
toggle_button_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_CLICK:
		error = toggle (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_PRESS:
		error = press (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYTOGGLED:
		error = verify_toggled (cctxt->gui_handle->handle,
					cctxt->log_fp);
		break;
	case LDTP_CMD_KBDENTER:
		error = device_main (cctxt, command);
		break;
	default:
		error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
	}
	return error;
}
