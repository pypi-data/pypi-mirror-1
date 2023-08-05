/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Aishwariya Devi S <aishwariyabhavan@yahoo.com>
 *    A Nagappan <nagappan@gmail.com>
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

extern gboolean ldtp_debug;

static LDTPErrorCode
select_event_index (Accessible *object, long event_index, FILE *log_fp)
{
	long child_count;
	LDTPErrorCode error;
	Accessible *event = NULL;

	child_count = Accessible_getChildCount (object);
	if (child_count < event_index) {
		error = LDTP_ERROR_CALENDAR_EVENT_INDEX_GREATER;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		g_print ("%s\n", ldtp_error_get_message (error));
		return error;
	}

	event = Accessible_getChildAtIndex (object, event_index);
	if (get_object_type (event) == CALENDAR_EVENT) {
		if (Accessible_isComponent (event)) {
			SPIBoolean flag = FALSE;
			AccessibleComponent *accessible_component;
			accessible_component = Accessible_getComponent (event);
			flag = AccessibleComponent_grabFocus (accessible_component);
			Accessible_unref (accessible_component);
			Accessible_unref (event);
			if (!flag)
				error = LDTP_ERROR_UNABLE_TO_SELECT_CALENDAR_EVENT_INDEX;
			else
				error = LDTP_ERROR_SUCCESS;
			return error;
		}
	}
	error = LDTP_ERROR_UNABLE_TO_SELECT_CALENDAR_EVENT_INDEX;
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	g_print ("%s\n", ldtp_error_get_message (error));

	Accessible_unref (event);
	return error;
}

	
static LDTPErrorCode
select_event (Accessible *object, char *event_name, FILE *log_fp)
{
	long i;
	long count;
	LDTPErrorCode error;
	Accessible *event = NULL;
	gchar *app_name = NULL;

	if (!event_name) {
		error = LDTP_ERROR_ARGUMENT_NULL;
		goto error;
	}
	count = Accessible_getChildCount (object);
	app_name = g_strdup_printf ("Calendar Event: Summary is %s.", event_name);

	for (i = 0; i < count; i++) {
		event = Accessible_getChildAtIndex (object, i);
		if (get_object_type (event) == CALENDAR_EVENT) {
			char *name;
			name = Accessible_getName (event);
			if (ldtp_debug && name && event_name && app_name)
				g_print ("Name: %s - Event Name: %s - app_name - %s\n", name, event_name, app_name);

			if (event_name && (g_utf8_collate (name, app_name) > 0) && Accessible_isComponent (event)) {
				SPIBoolean flag = FALSE;
				AccessibleComponent *accessible_component;

				accessible_component = Accessible_getComponent (event);
				if (accessible_component) {
					flag = AccessibleComponent_grabFocus (accessible_component);
					Accessible_unref (accessible_component);
				}
				Accessible_unref (event);
				SPI_freeString (name);
				if (!flag)
					error = LDTP_ERROR_UNABLE_TO_SELECT_CALENDAR_EVENT_NAME;
				else
					error = LDTP_ERROR_SUCCESS;
				g_free (app_name);
				return error;
			}
			SPI_freeString (name);
		}
		Accessible_unref (event);
	}
	g_free (app_name);
	error = LDTP_ERROR_UNABLE_TO_SELECT_CALENDAR_EVENT_NAME;

 error:
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	g_print ("%s\n", ldtp_error_get_message (error));

	return error;
}

static LDTPErrorCode
verify_event_exist (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	long child_count;
	child_count = Accessible_getChildCount (object);
	if (child_count >= 2)
		return LDTP_ERROR_SUCCESS;
	else {
		/* childcount = 1 (implies, calendar_view has a child (i.e, table)) */
		error = LDTP_ERROR_NO_APPOINTMENTS_IN_CALENDAR;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		g_print ("%s\n", ldtp_error_get_message (error));
	}
	return error;
}

LDTPErrorCode
calendar_view_main (LDTPClientContext* cctxt, int command)
{
	long count = 0;
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_SELECTEVENT:
		error = select_event (cctxt->gui_handle->handle,
				      cctxt->req->arg_list->data, cctxt->log_fp);
		break;
	case LDTP_CMD_SELECTEVENTINDEX:
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			count = atol (cctxt->req->arg_list->data);
		error = select_event_index (cctxt->gui_handle->handle,
					    count, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYEVENTEXIST:
		error = verify_event_exist (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_KBDENTER:
		error = device_main (cctxt, command);
		break;
	default:
		error = LDTP_ERROR_COMMAND_NOT_IMPLEMENTED;
		break;
	}
	return error;
}
