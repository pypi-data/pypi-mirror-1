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
right_click (Accessible *object, FILE *log_fp)
{
	long i;
	long count;
	char *name = NULL;
	LDTPErrorCode error;
	AccessibleRole role;
	SPIBoolean flag = FALSE;
	AccessibleAction *action;

	name = Accessible_getName (object);
	g_print ("Icon name: %s\n", name);
	SPI_freeString (name);

	/*
	  Get action handle of the given object
	*/
	action = Accessible_getAction (object);
	count = AccessibleAction_getNActions (action);

	for (i = 0; i < count; i++) {
		char *name, *desc;
		name = AccessibleAction_getName (action, i);
		desc = AccessibleAction_getDescription (action, i);

		g_print ("Name: %s\tDesc: %s\n", name, desc);

		SPI_freeString (name);
		SPI_freeString (desc);
		role = Accessible_getRole (action);
		if (role == SPI_ROLE_MENU) {
			/*
			  To execute menu action
			*/
			flag = AccessibleAction_doAction (action, i);
			break;
		}
	}
	Accessible_unref (action);

	if (flag) {
		g_print ("Right click on icon: success\n");
		error =  (LDTP_ERROR_SUCCESS);
	}
	else {
		error =  (LDTP_ERROR_RIGHT_CLICK_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	}
	return error;
}

LDTPErrorCode
icon_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_RIGHTCLICK :
		error = right_click (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	default:
		error = ( (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED));
		break;
	}
	return error;
}
