/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Khasim Shaheed <khasim.shaheed@gmail.com>
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

/*
  Get the state of given object
*/
static gboolean
get_state (Accessible *object)
{
	AccessibleStateSet *state;
	SPIBoolean checked;
	
	state = Accessible_getStateSet (object);
	checked = AccessibleStateSet_contains (state, SPI_STATE_CHECKED);

	/*
	  Check, if Radio Menu Item state is already checked
	*/
	if (checked)
		return TRUE; // Checked state
	else
		return FALSE; // Unchecked state
}

static LDTPErrorCode
click (Accessible *object, FILE *log_fp)
{
	SPIBoolean flag;
	LDTPErrorCode error;
	AccessibleAction *action;
	
	if (wait_till_object_state_contains (object, RADIO_MENU_ITEM, log_fp) != 0) {
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	action = Accessible_getAction (object);
	flag = AccessibleAction_doAction (action, 0);
	Accessible_unref (action);

	if (flag)
		return  (LDTP_ERROR_SUCCESS);
	else
		{
			error =  (LDTP_ERROR_CLICK_FAILED);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
}

static LDTPErrorCode
check_radio_menu_item (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleAction *action;

	if (wait_till_object_state_contains (object, RADIO_MENU_ITEM, log_fp) != 0) {
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	/*
	  If state already selected then unselect ?
	*/
	if (get_state (object) == FALSE) {
		SPIBoolean flag;
		action = Accessible_getAction (object);
		flag = AccessibleAction_doAction (action, 0);
		Accessible_unref (action);
		if (flag == FALSE) {
			error =  (LDTP_ERROR_RADIO_MENU_ITEM_NOT_CHECKED);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
	}
	else {
		error =  (LDTP_ERROR_RADIO_MENU_ITEM_ALREADY_CHECKED);
		log_msg (LDTP_LOG_WARNING, ldtp_error_get_message (error), log_fp);
	}
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
verify_check_radio_menu_item (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	if (wait_till_object_state_contains (object, RADIO_MENU_ITEM, log_fp) != 0) {
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	/*
	  If state is not checked then check it
	*/
	if (get_state (object) == FALSE) {
		error =  (LDTP_ERROR_RADIO_MENU_ITEM_NOT_CHECKED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
verify_uncheck_radio_menu_item (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	if (wait_till_object_state_contains (object, RADIO_MENU_ITEM, log_fp) != 0) {
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	/*
	  If state is not checked then check it
	*/
	if (get_state (object) == TRUE) {
		error =  (LDTP_ERROR_RADIO_MENU_ITEM_ALREADY_CHECKED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return  (LDTP_ERROR_SUCCESS);
}

LDTPErrorCode
radio_menu_item_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_CLICK:
		error = click (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_SELECTMENUITEM:
		error = click (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_MENUCHECK:
		error = check_radio_menu_item (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYMENUCHECK:
		error = verify_check_radio_menu_item (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYMENUUNCHECK:
		error = verify_uncheck_radio_menu_item (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	default:
		error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
		break;
	}
	return error;
}
