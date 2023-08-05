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
#include "ldtp-utils.h"
#include "ldtp-error.h"
#include "ldtp-logger.h"
#include "ldtp-command.h"
#include "ldtp-gui-comp.h"

static LDTPErrorCode
is_menu_item_enabled (Accessible *object, FILE *log_fp)
{
	if (object_state_contains (object, MENU_ITEM, log_fp) != 0) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_MENU_ITEM_STATE_DISABLED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
select_menu_item (Accessible *object, FILE *log_fp)
{
	long i;
	long action_count;
	char *name = NULL;
	SPIBoolean flag = FALSE;
	AccessibleAction *action;

	if (wait_till_object_state_contains (object, MENU_ITEM, log_fp) != 0) {
		LDTPErrorCode error;
		error = LDTP_ERROR_INVALID_OBJECT_STATE;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	action = Accessible_getAction (object);
	if (!action) {
		LDTPErrorCode error;
		name = Accessible_getName (object);
		g_print ("Unable to get Action handle: %s\n", name);
		SPI_freeString (name);
		error = LDTP_ERROR_SELECT_MENU_ITEM_FAILED;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	/*
	  Get total action item on given object
	*/
	action_count = AccessibleAction_getNActions (action);
	g_print ("Total action count: %ld\n", action_count);

	for (i = 0; i < action_count; i++) {
		char *name, *desc;
		name = AccessibleAction_getName (action, i);
		desc = AccessibleAction_getDescription (action, i);
		g_print ("Name: %s, Description: %s\n", name, desc);
		SPI_freeString(name);
		SPI_freeString(desc);
	}
	ldtp_nsleep (0, 15000);
	flag = AccessibleAction_doAction (action, 0);
	Accessible_unref (action);
	if (flag)
		return  (LDTP_ERROR_SUCCESS);
	else {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_SELECT_MENU_ITEM_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

/*
  FIXME: Thanika - Do we need this function apart from printing ?
  If not we can remove ?
*/
static LDTPErrorCode
list_child_menu_items (Accessible *object, FILE *log_fp)
{
	long i;
	gboolean flag = FALSE;
	long child_count;
	
	child_count = Accessible_getChildCount (object);
	g_print ("Child count: %ld\n", child_count);
	g_print ("Menu Items\n");
	if (child_count > 0) {
		char *name = NULL;
		Accessible *child;

		for (i = 0; i < child_count; i++) {
			child = Accessible_getChildAtIndex (object, i);
			if (child) {
				name = Accessible_getName (child);
				g_print ("Child name: %s\n", name);
				log_msg (LDTP_LOG_INFO, name, log_fp);
				//if(strcasecmp(name, item_name) == 0)
				//{
				//flag = 1;
				//break;
				//}
				SPI_freeString(name);
				Accessible_unref (child);
			} // if
		} // for
	} // if
	if (flag == TRUE) {
		// Accessible *selection;
		// selection = Accessible_getSelection(object);
		// AccessibleSelection_selectChild(selection, i);
		return  (LDTP_ERROR_SUCCESS);
	}
	else {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_UNABLE_TO_LIST_MENU_ITEMS);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

LDTPErrorCode
menu_item_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	AccessibleRole class_id;

	switch (command) {
	case LDTP_CMD_SELECTMENUITEM:
		error = select_menu_item (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_ISMENUITEMENABLED:
		error = is_menu_item_enabled (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYMENUCHECK:
	case LDTP_CMD_VERIFYMENUUNCHECK:
		class_id = Accessible_getRole (cctxt->gui_handle->handle);
		if (class_id == SPI_ROLE_CHECK_MENU_ITEM)
			error = check_menu_item_main (cctxt, command);
		else if (class_id == SPI_ROLE_RADIO_MENU_ITEM)
			error = radio_menu_item_main (cctxt, command);
		else
			error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
		break;
	case LDTP_CMD_LISTSUBMENUS: {
		char *name, *role;
		name = Accessible_getName(cctxt->gui_handle->handle);
		role = Accessible_getRoleName(cctxt->gui_handle->handle);
		g_print ("role = %s name = %s\n", role, name);
		SPI_freeString (name);
		SPI_freeString (role);
		error = list_child_menu_items (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	}
	default:
		class_id = Accessible_getRole (cctxt->gui_handle->handle);
		if (class_id == SPI_ROLE_RADIO_MENU_ITEM)
			error = radio_menu_item_main (cctxt, command);
		else if (class_id == SPI_ROLE_CHECK_MENU_ITEM)
			error = check_menu_item_main (cctxt, command);
		else
			return  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
	}
	return error;
}
