/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project - http://ldtp.freedesktop.org
 *
 * Author:
 *    S. Aishwariya <aishwariyabhavan@yahoo.com>
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
get_check_menu_state (Accessible *object)
{
	SPIBoolean checked;
	AccessibleStateSet *state;
	
	state = Accessible_getStateSet (object);
	checked = AccessibleStateSet_contains (state, SPI_STATE_CHECKED);

	/*
	  Check, if Check Menu Item state is already checked
	*/
	if (checked)
		return TRUE; // Checked state
	else
		return FALSE; // Unchecked state
}

static LDTPErrorCode
click (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	SPIBoolean flag = FALSE;
	AccessibleAction *action;
	
	if (wait_till_object_state_contains (object, CHECK_MENU_ITEM, log_fp) != 0) {
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
		return  (LDTP_ERROR_CLICK_FAILED);
}

static LDTPErrorCode
check_check_menu_item (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleAction *action;

	if (wait_till_object_state_contains (object, CHECK_MENU_ITEM, log_fp) != 0) {
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	/*
	  If state is already 'selected' then 'unselect' 
	*/
	if (get_check_menu_state (object) == FALSE) {
		/* unchecked */
		SPIBoolean flag = FALSE;
		action = Accessible_getAction (object);
		flag = AccessibleAction_doAction (action, 0); //check
		Accessible_unref (action);
		if (flag)
			return  (LDTP_ERROR_SUCCESS);
		else {
			error =  (LDTP_ERROR_CHECK_ACTION_FAILED);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
	}
	else
		log_msg (LDTP_LOG_WARNING, "Check Menu Item is already checked", log_fp);
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
uncheck_check_menu_item (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleAction *action;

	if (wait_till_object_state_contains (object, CHECK_MENU_ITEM, log_fp) != 0) {
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	if (get_check_menu_state (object) == TRUE) {
		/* checked */
		SPIBoolean flag = FALSE;
		action = Accessible_getAction (object);
		flag = AccessibleAction_doAction (action, 0); //uncheck
		Accessible_unref (action); 
		if (flag)
			return  (LDTP_ERROR_SUCCESS);
		else {
			error =  (LDTP_ERROR_UNCHECK_ACTION_FAILED);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
	}
	else
		log_msg (LDTP_LOG_WARNING, "Check Menu Item is not checked", log_fp);
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
verify_menu_check (Accessible *object)
{
	if (get_check_menu_state (object))
		return  (LDTP_ERROR_SUCCESS);
	else
		return  (LDTP_ERROR_STATE_UNCHECKED);
}

static LDTPErrorCode
verify_menu_uncheck (Accessible *object)
{
	if (get_check_menu_state (object) == FALSE)
		return  (LDTP_ERROR_SUCCESS);
	else
		return  (LDTP_ERROR_STATE_CHECKED);
}

LDTPErrorCode
check_menu_item_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_MENUCHECK:
		error = check_check_menu_item (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_MENUUNCHECK:
		error = uncheck_check_menu_item (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_CLICK:
		error = click (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_SELECTMENUITEM:
		error = click (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYMENUCHECK:
		error = verify_menu_check (cctxt->gui_handle->handle);
		break;
	case LDTP_CMD_VERIFYMENUUNCHECK:
		error = verify_menu_uncheck (cctxt->gui_handle->handle);
		break;
	default:
		error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
		break;
	}
	return error;
}
