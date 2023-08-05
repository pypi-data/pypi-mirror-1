/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Nagappan A <nagappan@gmail.com>
 *    Poornima <pnayak@novell.com>
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

/*
  Get the check box state of the given object
*/
static gboolean
get_check_box_state (Accessible *object)
{
	AccessibleStateSet *state;
	
	state = Accessible_getStateSet (object);

	/*
	  Check, if check box state is already checked
	*/
	if (AccessibleStateSet_contains (state, SPI_STATE_CHECKED))
		return TRUE; // Checked state
	else
		return FALSE; // Unchecked state
}

static LDTPErrorCode
check_check_box (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleAction *action;

	if (wait_till_object_state_contains (object, CHECK_BOX, log_fp) != 0) {
		error = LDTP_ERROR_INVALID_OBJECT_STATE;
		goto error;
	}
	/*
	  Pre-condition
	  If state already selected then unselect ?
	*/
	if (get_check_box_state (object) == FALSE) {
		SPIBoolean flag;
		action = Accessible_getAction (object);
		flag = AccessibleAction_doAction (action, 0);
		Accessible_unref (action);
		if (flag)
			return LDTP_ERROR_SUCCESS;
		else {
			error = LDTP_ERROR_CHECK_ACTION_FAILED;
			goto error;
		}
	}
	else 
		log_msg (LDTP_LOG_WARNING, "Check box is already checked", log_fp);
	return LDTP_ERROR_SUCCESS;
 error:
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
uncheck_check_box (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleAction *action;

	if (wait_till_object_state_contains (object, CHECK_BOX, log_fp) != 0) {
		error = LDTP_ERROR_INVALID_OBJECT_STATE;
		goto error;
	}
	/*
	  Pre-condition
	  If state is checked then only uncheck it 
	*/
	if (get_check_box_state (object) == TRUE) {
		SPIBoolean flag;
		action = Accessible_getAction (object);
		flag = AccessibleAction_doAction (action, 0);
		Accessible_unref (action);
		if (flag)
			return LDTP_ERROR_SUCCESS;
		else {
			error = LDTP_ERROR_UNCHECK_ACTION_FAILED;
			goto error;
		}
	}
	else
		log_msg (LDTP_LOG_WARNING, "Check box state already unchecked", log_fp);
	return LDTP_ERROR_SUCCESS;
 error:
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
click (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	SPIBoolean flag = FALSE;
	AccessibleAction *action;
	
	if (wait_till_object_state_contains (object, CHECK_BOX, log_fp) != 0) {
		error = LDTP_ERROR_INVALID_OBJECT_STATE;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	action = Accessible_getAction (object);
	flag = AccessibleAction_doAction (action, 0);
	Accessible_unref (action);

	if (flag)
		return LDTP_ERROR_SUCCESS;
	else
		return LDTP_ERROR_CLICK_FAILED;
}
	
static LDTPErrorCode
verify_check_check_box (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	if (wait_till_object_state_contains (object, CHECK_BOX, log_fp) != 0) {
		error = LDTP_ERROR_INVALID_OBJECT_STATE;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	if (get_check_box_state (object) == FALSE)
		return LDTP_ERROR_STATE_UNCHECKED;
	else
		return LDTP_ERROR_SUCCESS;
}

static LDTPErrorCode
verify_uncheck_check_box (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	if (wait_till_object_state_contains (object, CHECK_BOX, log_fp) != 0) {
		error = LDTP_ERROR_INVALID_OBJECT_STATE;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	if (get_check_box_state (object) == TRUE)
		return LDTP_ERROR_STATE_CHECKED;
	else
		return LDTP_ERROR_SUCCESS;
}

LDTPErrorCode
check_box_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_CHECK:
		error = check_check_box (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_UNCHECK:
		error =  uncheck_check_box (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_CLICK:
		error =  click (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYCHECK:
		error =  verify_check_check_box (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYUNCHECK:
		error =  verify_uncheck_check_box (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	default:
		error =  LDTP_ERROR_COMMAND_NOT_IMPLEMENTED;
		break;
	}
	return error;
}
