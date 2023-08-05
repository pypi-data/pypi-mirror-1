/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Authors:
 *    Poornima Nayak <pnayak@novell.com>
 *    Khasim Shaheed <khasim.shaheed@gmail.com>
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
select_panel_name (Accessible *object, char *panel_name, FILE *log_fp)
{
	long i;
	char *name = NULL;
	long child_count;
	LDTPErrorCode error;
	SPIBoolean flag = FALSE;
	Accessible *child_object = NULL;
	AccessibleComponent *accessible_component = NULL;

	name = Accessible_getName (object);
	if (name) {
		g_print ("Panel name: %s\n", name);
		SPI_freeString (name);
	}

	child_count = Accessible_getChildCount (object);
	if (child_count == -1) {
		error =  (LDTP_ERROR_NO_PANEL_EXIST);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	for (i = 0; i < child_count; i++) {
		child_object = Accessible_getChildAtIndex (object, i);
		if (child_object) {
			name = Accessible_getName (child_object);
			if (name) {
				g_print ("Panel name: %s - %s\n", name, panel_name);
				if (g_pattern_match_simple (panel_name, name)) {
					accessible_component = Accessible_getComponent (child_object);
					SPI_freeString (name);
					break;
				}
				SPI_freeString (name);
			}
			Accessible_unref (child_object);
			child_object = NULL;
		}
	}
	if (accessible_component) {
		flag = AccessibleComponent_grabFocus (accessible_component);
		AccessibleComponent_unref (accessible_component);
	}
	if (child_object)
		Accessible_unref (child_object);
	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		error =  (LDTP_ERROR_PANEL_NAME_SELECTION_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
select_panel (Accessible *object, long panel_no, FILE *log_fp)
{
	long child_count;
	char *name = NULL;
	LDTPErrorCode error;
	SPIBoolean flag = FALSE;
	Accessible *child_object = NULL;
	AccessibleComponent *accessible_component = NULL;

	name = Accessible_getName (object);
	g_print ("name of object is %s\n", name);
	SPI_freeString (name);

	child_count = Accessible_getChildCount (object);
	if (child_count == -1) {
		error =  (LDTP_ERROR_NO_PANEL_EXIST);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	if (child_count < panel_no) {
		error =  (LDTP_ERROR_PANEL_COUNT_LESS_THAN_TOTAL_PANEL);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	child_object = Accessible_getChildAtIndex (object, panel_no - 1);
	accessible_component = Accessible_getComponent (child_object);
	if (accessible_component) {
		flag = AccessibleComponent_grabFocus (accessible_component);
		AccessibleComponent_unref (accessible_component);
	}
	if (child_object)
		Accessible_unref (child_object);
	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		error =  (LDTP_ERROR_PANEL_INDEX_SELECTION_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
get_panel_child_count (Accessible *object, GSList **l, FILE *log_fp)
{
	long child_count = -1;

	child_count = Accessible_getChildCount (object);
	if (child_count == -1) {
		LDTPErrorCode error;
		*l = g_slist_prepend (*l, g_strdup_printf ("%ld", child_count));
		error =  (LDTP_ERROR_NO_PANEL_EXIST);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	*l = g_slist_prepend (*l, g_strdup_printf ("%ld", child_count));
	return  (LDTP_ERROR_SUCCESS);
}

LDTPErrorCode
panel_main (LDTPClientContext* cctxt, int command)
{
	long count = 0;
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_SELECTPANEL:
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			count = atol (cctxt->req->arg_list->data);
		error = select_panel (cctxt->gui_handle->handle,
				      count,
				      cctxt->log_fp);
		break;
	case LDTP_CMD_SELECTPANELNAME:
		error = select_panel_name (cctxt->gui_handle->handle,
					   cctxt->req->arg_list->data,
					   cctxt->log_fp);
		break;
	case LDTP_CMD_GETPANELCHILDCOUNT:
		error = get_panel_child_count (cctxt->gui_handle->handle,
					       &cctxt->req->arg_list,
					       cctxt->log_fp);
		if (error == LDTP_ERROR_SUCCESS) {
			cctxt->resp->data = cctxt->req->arg_list->data;
			cctxt->resp->data_len = g_utf8_strlen (cctxt->req->arg_list->data, -1);
			cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, cctxt->req->arg_list->data);
		}
		break;
	default:
		error = LDTP_ERROR_COMMAND_NOT_IMPLEMENTED;
		break;
	}
	return error;
}
