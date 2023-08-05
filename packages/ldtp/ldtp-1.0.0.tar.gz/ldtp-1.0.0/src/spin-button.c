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
set_value (Accessible *object, long numvalue, FILE *log_fp)
{
	LDTPErrorCode error;
	SPIBoolean flag;
	AccessibleValue *accessible_value;

	g_print ("Spin button text: %ld\n", numvalue);
	accessible_value = Accessible_getValue (object);
	flag = AccessibleValue_setCurrentValue (accessible_value, numvalue);
	Accessible_unref (accessible_value);
	if (flag)
		return  (LDTP_ERROR_SUCCESS);
	else {
		error =  (LDTP_ERROR_UNABLE_TO_SET_SPIN_BUTTON_VALUE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static double
get_value (Accessible *object)
{
	double value = -1;
	AccessibleValue *accessible;
	if (!object)
		return -1;
	accessible = Accessible_getValue (object);
	if (accessible) {
		value = AccessibleValue_getCurrentValue (accessible);
		Accessible_unref (accessible);
	}
	return value;
}

static LDTPErrorCode
verify_set_value (Accessible *object, double value, FILE *log_fp)
{
	LDTPErrorCode error;

	if (get_value (object) == value)
		return  (LDTP_ERROR_SUCCESS);
	else {
		error =  (LDTP_ERROR_UNABLE_TO_SPIN_BUTTON_VALUES_NOT_SAME);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

LDTPErrorCode
spin_button_main (LDTPClientContext* cctxt, int command)
{
	double value = -1;
	LDTPErrorCode error;
	g_print ("SPIN BUTTON: %d - %d - %d\n", command, LDTP_CMD_SETVALUE, LDTP_CMD_VERIFYSETVALUE);
	switch (command) {
	case LDTP_CMD_SETVALUE:
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			value = strtod (cctxt->req->arg_list->data, NULL);
		error = set_value (cctxt->gui_handle->handle, value,
				   cctxt->log_fp);
		break;
	case LDTP_CMD_GETVALUE:
		value = get_value (cctxt->gui_handle->handle);
		cctxt->resp->data = g_strdup_printf ("%lf", value);
		if (cctxt->resp->data)
			cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
		if (value)
			error =  (LDTP_ERROR_SUCCESS);
		else
			error =  (LDTP_ERROR_UNABLE_TO_GET_VALUE);
		break;
	case LDTP_CMD_VERIFYSETVALUE:
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			value = strtod (cctxt->req->arg_list->data, NULL);
		error = verify_set_value (cctxt->gui_handle->handle, value,
					  cctxt->log_fp);
		break;
	default:
		error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
	}
	return error;
}
