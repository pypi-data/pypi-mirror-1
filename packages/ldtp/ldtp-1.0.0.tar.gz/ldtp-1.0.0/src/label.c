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

static char*
get_label (Accessible *object)
{
	char *name  = NULL;
	char *label = NULL;

	name = Accessible_getName (object);
	g_print ("Label: %s\n", name);
	label = g_strdup (name);
	SPI_freeString (name);
	return label;
}

static char*
get_label_at_index (Accessible *object, long index)
{
	char *name  = NULL;
	char *label = NULL;
	Accessible *child = NULL;

	child = Accessible_getChildAtIndex (object, index);

	if (!child)
		return NULL;

	name = Accessible_getName (child);
	g_print ("Label: %s\n", name);
	label = g_strdup (name);
	SPI_freeString (name);
	Accessible_unref (child);
	return label;
}

static Accessible *
get_parent_panel (Accessible *child)
{
	Accessible *tmp;
	Accessible *parent = Accessible_getParent (child);
	if (!parent)
		return NULL;
	if (Accessible_getRole (parent) == SPI_ROLE_PANEL)
		return parent;
	tmp = get_parent_panel (parent);
	Accessible_unref (parent);
	parent = tmp;
	return parent;
}

static LDTPErrorCode
select_labels_panel_by_name (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	Accessible *parent;
	SPIBoolean flag = FALSE;
	gboolean iteration = FALSE;

	parent = get_parent_panel (object);

	while (1) {
		if (!parent)
			break;
		if (Accessible_isComponent (parent)) {
			AccessibleComponent *component;
			component = Accessible_getComponent (parent);
			if (component) {
				flag = AccessibleComponent_grabFocus (component);
				Accessible_unref (component);
				if (iteration)
					break;
				if (!flag) {
					Accessible *tmp_parent = get_parent_panel (parent);
					Accessible_unref (parent);
					parent = tmp_parent;
					/*
					  Beagle specific hack. In few cases label and icon are together
					  under a panel and few cases label is under one panel and this panel
					  combines with a icon under a panel. So, we will traverse one level up
					  to again get the parent panel.
					*/
					iteration = TRUE;
					continue;
				}
				else
					break;
			}
		}
	}
	if (parent)
		Accessible_unref (parent);
	if (flag)
		error =  (LDTP_ERROR_SUCCESS);
	else
		error =  (LDTP_ERROR_UNABLE_TO_SELECT_LABEL);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

LDTPErrorCode
label_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_SELECTLABELSPANELBYNAME: {
		error = select_labels_panel_by_name (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_GETLABEL:
		cctxt->resp->data = get_label (cctxt->gui_handle->handle);
		if (cctxt->resp->data) {
			cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
			error =  (LDTP_ERROR_SUCCESS);
		}
		else
			error =  (LDTP_ERROR_LABEL_NOT_FOUND);
		break;
	case LDTP_CMD_GETLABELATINDEX: {
		long index = 0;
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			index = atol ((char *)cctxt->req->arg_list->data);
		cctxt->resp->data = get_label_at_index (cctxt->gui_handle->handle, index);
		if (cctxt->resp->data) {
			cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
			error =  (LDTP_ERROR_SUCCESS);
		}
		else
			error =  (LDTP_ERROR_LABEL_NOT_FOUND);
	}
		break;
	default:
		error = ( (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED));
		break;
	}
	return error;
}
