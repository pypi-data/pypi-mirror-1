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
select_item (Accessible *object, char *item_name, FILE *log_fp)
{
	long i;
	gboolean flag = FALSE;
	LDTPErrorCode error;
	long child_count;

	child_count = Accessible_getChildCount (object);

	if (child_count > 0) {
		char *name = NULL;
		Accessible *child;

		for (i = 0; i < child_count; i++) {
			child = Accessible_getChildAtIndex (object, i);
			if (child) {
				name = Accessible_getName (child);
#ifdef ENABLE_LOCALIZE
				if (g_utf8_collate (name, _(item_name)) == 0)
#else
					if (g_utf8_collate (name, item_name) == 0)
#endif
						{
							flag = TRUE;
							g_print ("Child name: %s\n", name);
							SPI_freeString (name);
							Accessible_unref (child);
							break;
						}
				SPI_freeString (name);
				Accessible_unref (child);
			}
		}
	}
	if (flag == TRUE) {
		SPIBoolean flag = FALSE;
		AccessibleSelection *selection;
		selection = Accessible_getSelection (object);
		flag = AccessibleSelection_selectChild (selection, i);
		Accessible_unref (selection);
		g_print ("Selected: %s\n", item_name);
		if (flag == TRUE)
			return  (LDTP_ERROR_SUCCESS);
	}
	error =  (LDTP_ERROR_UNABLE_TO_SELECT_LAYERED_PANE_ITEM);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static LDTPErrorCode
right_click (Accessible *object, FILE *log_fp)
{
	long action_count, i;
	SPIBoolean flag = FALSE;
	LDTPErrorCode error;
	AccessibleAction *action;
	
	action = Accessible_getAction (object);
	action_count = AccessibleAction_getNActions (action);

	for (i = 0; i < action_count; i++) {
		char *name, *desc;
		name = AccessibleAction_getName (action, i);
		desc = AccessibleAction_getDescription (action, i);
		g_print ("name = %s, desc = %s\n", name, desc);
		SPI_freeString(name);
		SPI_freeString(desc);
	}
	/*
	  FIXME: Take action based on dynamic values
	  To execute menu action
	*/
	flag = AccessibleAction_doAction (action, 1);
	Accessible_unref (action);
	if (flag)
		return  (LDTP_ERROR_SUCCESS);
	else {
		error =  (LDTP_ERROR_RIGHT_CLICK_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

LDTPErrorCode
layered_pane_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_SELECTITEM: {
		char *item_name = NULL;

		item_name = cctxt->req->arg_list->data;
		error = select_item (cctxt->gui_handle->handle, item_name, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_RIGHTCLICK:
		error = right_click (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	default:
		error = ( (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED));
		break;
	}
	return error;
}
