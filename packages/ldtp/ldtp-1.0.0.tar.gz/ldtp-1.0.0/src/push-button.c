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

static gboolean
is_push_button_state_enabled (Accessible *object)
{
	if (!object)
		return FALSE;
	if (wait_till_object_state_contains (object, PUSH_BUTTON, NULL) == -1) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), NULL);
		return FALSE;
	}
	return TRUE;
}

static gboolean
is_object_push_button (Accessible *object, FILE *log_fp)
{
	if (object_state_contains (object, PUSH_BUTTON, log_fp) != 0) {
		log_msg (LDTP_LOG_CAUSE, "Object is not a push button", log_fp);
		return FALSE;
	}
	return TRUE;
}

static LDTPErrorCode
click (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	SPIBoolean flag = FALSE;
	AccessibleAction *action;

	if (is_push_button_state_enabled (object) == FALSE) {
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	if (Accessible_isComponent (object)) {
		SPIBoolean flag = FALSE;
		AccessibleComponent *accessible_component;
		accessible_component = Accessible_getComponent (object);
		flag = AccessibleComponent_grabFocus (accessible_component);
		Accessible_unref (accessible_component);
	}
	action = Accessible_getAction (object);
	flag = FALSE;
	if (action) {
		sleep (1);
		flag = AccessibleAction_doAction (action, 0);
		Accessible_unref (action);
	}
	if (flag == TRUE) {
		return  (LDTP_ERROR_SUCCESS);
	}
	else {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_CLICK_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

LDTPErrorCode
push_button_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_CLICK:
		error = click (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYPUSHBUTTON:
		if (is_object_push_button (cctxt->gui_handle->handle, cctxt->log_fp))
			error =  (LDTP_ERROR_SUCCESS);
		else
			error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		break;
	case LDTP_CMD_STATEENABLED:
		if (is_push_button_state_enabled (cctxt->gui_handle->handle))
			error =  (LDTP_ERROR_SUCCESS);
		else
			error =  (LDTP_ERROR_RADIO_BUTTON_STATE_NOT_ENABLED);
		break;
        case LDTP_CMD_MOUSELEFTCLICK:
        case LDTP_CMD_MOUSERIGHTCLICK:
                if (is_push_button_state_enabled (cctxt->gui_handle->handle))
                        error = device_main (cctxt, command);
                else
                        error =  (LDTP_ERROR_RADIO_BUTTON_STATE_NOT_ENABLED);
                break;
        case LDTP_CMD_MOUSEMOVE:
                error = device_main (cctxt, command);
                break;
        case LDTP_CMD_KBDENTER:
                error = device_main (cctxt, command);
                break;
	default:
		error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
		break;
	}
	return error;
}
