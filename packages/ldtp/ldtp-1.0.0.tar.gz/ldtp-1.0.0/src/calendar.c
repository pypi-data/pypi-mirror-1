/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org/
 *
 * Author:
 *    Aishwariya Devi S <aishwariyabhavan@yahoo.com>
 *    A Nagappan <nagappan@gmail.com>
 *    J Premkumr <jpremkumar@novell.com>
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
select_calendar_date (Accessible *object, GSList* l, FILE *log_fp)
{
	int day = 0, month = 0, year = 0;
	int child_count, i;
	Accessible *child = NULL;
	char *date = NULL;
	char *child_name = NULL;
	time_t timer;
	struct tm *current_time;
	LDTPErrorCode error;

	if (l && l->data) {
		day = atol (l->data);
		l = l->next;
		if (l && l->data) {
			month = atol (l->data);
			l = l->next;
			if (l && l->data) {
				year = atol (l->data);
			}
		}
	}

	date = g_strdup_printf ("%d-%d-%d", year, month, day);

	timer = time (NULL);
	current_time = localtime (&timer);

	if (day == 0)
		day = current_time->tm_mday;
	if (month == 0) {
		/*
		 *Adding 1 since the localtime API returns 
		 *the month index between 0 and 11
		 */
		month = current_time->tm_mon + 1;
	}
	if (year == 0) {
		/*
		 *Adding 1900 since the localtime API returns 
		 *years passed since 1900 as the year value
		 */
		year = current_time->tm_year + 1900;
	}
	child_count = Accessible_getChildCount (object);
	g_print ("Date to be selected: %s ---- %d\n", date, child_count);
	for (i = 0; i < child_count; i++) {
		child = Accessible_getChildAtIndex (object, i);
		child_name = Accessible_getName (child);
		/*
		  How this can be handled in local format ?
		*/
		if (g_strcasecmp (child_name, date) == 0) {
			if (Accessible_isComponent (child)) {
				SPIBoolean flag = FALSE;
				AccessibleComponent *accessible_component;

				accessible_component = Accessible_getComponent (child);
				flag = AccessibleComponent_grabFocus (accessible_component);
				Accessible_unref (accessible_component);
				SPI_freeString (child_name);
				Accessible_unref (child);
				g_free (date);
				if (flag == TRUE)
					return LDTP_ERROR_SUCCESS;
				else {
					error = LDTP_ERROR_UNABLE_TO_GRAB_FOCUS;
					goto error;
				}
			}
			else {
				g_free (date);
				SPI_freeString (child_name);
				Accessible_unref (child);
				error = LDTP_ERROR_OBJ_NOT_COMPONENT_TYPE;
				goto error;
			}
		}
		else
			Accessible_unref (child);
	}
	g_free (date);
	SPI_freeString (child_name);
	Accessible_unref (child);

	error = LDTP_ERROR_INVALID_DATE;

 error:
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	g_print ("%s\n", ldtp_error_get_message (error));
	return error;
}

LDTPErrorCode
calendar_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_SELECTCALENDARDATE:
		error = select_calendar_date (cctxt->gui_handle->handle,
					      cctxt->req->arg_list, cctxt->log_fp);
		break;
	default:
		error = LDTP_ERROR_COMMAND_NOT_IMPLEMENTED;
		break;
	}
	return error;
}
