/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/* 
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    S. Aishwariya <aishwariyabhavan@yahoo.com >
 *    K. Sree Kamakshi <poorvakrishna@yahoo.com >
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

static gboolean
is_object_slider (Accessible *object, FILE *log_fp)
{
	if (wait_till_object_state_contains (object, SLIDER, log_fp) != 0) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return FALSE;
	}
	return TRUE;
}

static gboolean
is_slider_horizontal (Accessible *object)
{
	AccessibleStateSet *state;
	state = Accessible_getStateSet (object);
	/*
	  Check if the slider is horizontal or vertical
	*/
	if (AccessibleStateSet_contains (state, SPI_STATE_HORIZONTAL))
		return TRUE;  //Horizontal State
	else
		return FALSE; //Vertical State
}

static gboolean
is_slider_vertical (Accessible *object)
{
	AccessibleStateSet *state;
	state = Accessible_getStateSet (object);
	/*
	  Check if the slider is horizontal or vertical
	*/
	if (AccessibleStateSet_contains (state, SPI_STATE_VERTICAL))
		return TRUE;  //Vertical State
	else
		return FALSE; //Not vertical State
}

static LDTPErrorCode
set_max (Accessible *object, FILE *log_fp)
{ 
	double val;
	SPIBoolean flag;
	LDTPErrorCode error;
	AccessibleValue *value = NULL;

	if (is_object_slider (object, log_fp) == FALSE) {
		value = Accessible_getValue(object);    
		val = AccessibleValue_getMaximumValue (value); 
	}
	else {
		error =  (LDTP_ERROR_SLIDER_SET_MAX_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	/*
	  The slider is set to maximum value
	*/
	flag = AccessibleValue_setCurrentValue (value, val);
	Accessible_unref (value);
	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		error =  (LDTP_ERROR_SLIDER_SET_MAX_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
set_min (Accessible *object, FILE *log_fp)
{ 
	double val;
	AccessibleValue *value = NULL;
	LDTPErrorCode error;
	SPIBoolean flag;

	if (is_object_slider (object, log_fp) == FALSE) {
		error =  (LDTP_ERROR_SLIDER_SET_MIN_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	value = Accessible_getValue(object);    
	val = AccessibleValue_getMinimumValue (value); 

	/*
	  The slider is set to minimum value
	*/
	flag = AccessibleValue_setCurrentValue (value, val);
	Accessible_unref (value);
	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		error =  (LDTP_ERROR_SLIDER_SET_MIN_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static double
get_slider_value (Accessible *object, FILE *log_fp)
{
	double current_val = -1;
	if (is_object_slider (object, log_fp)) {
		AccessibleValue *value = NULL;
		value = Accessible_getValue (object);
		if (value) {
			current_val = AccessibleValue_getCurrentValue (value);
			Accessible_unref (value);
		}
	}
	return current_val;
}

static LDTPErrorCode
decrease (Accessible *object, int num, FILE *log_fp)
{
	double min, max, val;
	int i = 1;
	AccessibleValue *value = NULL;
	SPIBoolean flag = FALSE;
	if (is_object_slider (object, log_fp)) {
		value = Accessible_getValue (object);
		val = AccessibleValue_getCurrentValue (value);
		max = AccessibleValue_getMaximumValue (value);
		min = AccessibleValue_getMinimumValue (value);
		max = max / 8;
		while (i <= num) {    
			val = AccessibleValue_getCurrentValue (value);
			val = val - max;
			if (val < min) {
				log_msg (LDTP_LOG_CAUSE, "Reached minimum limit", log_fp);
				Accessible_unref (value);
				return  (LDTP_ERROR_SUCCESS);
			}
			/*
			  Decrease the value of the slider
			*/
 
			flag = AccessibleValue_setCurrentValue (value, val);
			ldtp_nsleep (0, 15000);
			i++;
		}
	}
	Accessible_unref (value);
	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_UNABLE_TO_DECREASE_SLIDER_VALUE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
increase (Accessible *object, int num, FILE *log_fp)
{
	double min, max, val;
	int i = 1;
	AccessibleValue *value = NULL;
	SPIBoolean flag = FALSE;
	if (is_object_slider (object, log_fp)) {
		value = Accessible_getValue (object);
		val = AccessibleValue_getCurrentValue (value);
		max = AccessibleValue_getMaximumValue (value);
		min = AccessibleValue_getMinimumValue (value);
		max = max / 8;
		while (i <= num) {    
			val = AccessibleValue_getCurrentValue (value);
			val = val + max;
			if (val > (max * 8)) {
				log_msg (LDTP_LOG_WARNING, "Reached maximum limit", log_fp);
				Accessible_unref (value);
				return  (LDTP_ERROR_SUCCESS);
			}
			/*
			  Increase the value of the slider
			*/
 
			flag = AccessibleValue_setCurrentValue (value, val);
			ldtp_nsleep (0, 15000);
			i++;
		}
	}
	Accessible_unref (value);
	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_UNABLE_TO_INCREASE_SLIDER_VALUE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

LDTPErrorCode
slider_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_VERIFYSLIDER:
		if (is_object_slider (cctxt->gui_handle->handle, cctxt->log_fp))
			error =  (LDTP_ERROR_SUCCESS);
		else
			error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		break;
	case LDTP_CMD_VERIFYSLIDERVERTICAL:
		if (is_slider_vertical (cctxt->gui_handle->handle))
			error =  (LDTP_ERROR_SUCCESS);
		else
			error =  (LDTP_ERROR_NOT_VERTICAL_SLIDER);
		break;
	case LDTP_CMD_VERIFYSLIDERHORIZONTAL:
		if (is_slider_horizontal (cctxt->gui_handle->handle))
			error =  (LDTP_ERROR_SUCCESS);
		else
			error =  (LDTP_ERROR_NOT_HORIZONTAL_SLIDER);
		break;
	case LDTP_CMD_SETMAX:
		error = set_max (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_SETMIN:
		error = set_min (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_GETSLIDERVALUE: {
		double current_val = -1;
		current_val = get_slider_value (cctxt->gui_handle->handle, cctxt->log_fp);
		if (current_val != -1) {
			cctxt->resp->data = g_strdup_printf ("%lf", current_val);
			cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
			error =  (LDTP_ERROR_SUCCESS);
		}
		else {
			error =  (LDTP_ERROR_UNABLE_TO_GET_SLIDER_VALUE);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		}
		break;
	}
	case LDTP_CMD_INCREASE: {
		long num = 0;
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			num = atol (cctxt->req->arg_list->data);
		error = increase (cctxt->gui_handle->handle, num, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_DECREASE: {
		long num = 0;
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			num = atol (cctxt->req->arg_list->data);
		error = decrease(cctxt->gui_handle->handle, num, cctxt->log_fp);
		break;
	}
	default:
		error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
	}
	return error;
}
