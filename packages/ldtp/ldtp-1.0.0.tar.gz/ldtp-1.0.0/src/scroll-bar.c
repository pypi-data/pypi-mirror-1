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
is_object_scroll_bar (Accessible *object, FILE *log_fp)
{
	if (wait_till_object_state_contains (object, SCROLL_BAR, log_fp) != 0) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return FALSE;
	}
	return TRUE;
}

static gboolean
is_scroll_bar_horizontal (Accessible *object)
{
	AccessibleStateSet *state;
	state = Accessible_getStateSet (object);
	/*
	  Check if the scroll bar is horizontal or vertical
	*/
	if (AccessibleStateSet_contains (state, SPI_STATE_HORIZONTAL))
		return TRUE;  //Horizontal State
	else
		return FALSE; //Vertical State
}
static gboolean
is_scroll_bar_vertical (Accessible *object)
{
	AccessibleStateSet *state;
	state = Accessible_getStateSet (object);
	/*
	  Check if the scroll bar is horizontal or vertical
	*/
	if (AccessibleStateSet_contains (state, SPI_STATE_VERTICAL))
		return TRUE;  //Vertical State
	else
		return FALSE; //Not vertical State
}

static LDTPErrorCode
scroll_up (Accessible *object, FILE *log_fp)
{ 
	long i, count;
	AccessibleValue *value = NULL;
	Accessible *child = NULL;
	Accessible *parent = NULL;
	Accessible *tempchild = NULL;
	SPIBoolean flag, changeflag = FALSE;

	parent = Accessible_getParent (object);
	count = Accessible_getChildCount (parent);

	for (i = 0; i < count; i++) { 
		tempchild = Accessible_getChildAtIndex (parent, i);
		if (is_object_scroll_bar (tempchild, log_fp) == TRUE) {      
			if (is_scroll_bar_vertical (tempchild) == TRUE) { 
				child = Accessible_getChildAtIndex (parent, i);
				changeflag = TRUE;
				Accessible_unref (tempchild);
				break;
			} 
		}      
		Accessible_unref (tempchild);
	}
	Accessible_unref (parent);

	if (changeflag == FALSE) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_NOT_VERTICAL_SCROLL_BAR);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		if (child)
			Accessible_unref (child);
		return error;
	}
	value = Accessible_getValue (child);    
	/*
	  The scroll bar is set to 0 which is the upper limit
	*/
	flag = AccessibleValue_setCurrentValue (value, 0);
	Accessible_unref (value);
	Accessible_unref (child);
	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_UNABLE_TO_SCROLL_WITH_GIVEN_VALUE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
scroll_down (Accessible *object, FILE *log_fp)
{
	double val;
	long count, i;
	Accessible *parent;
	AccessibleValue *value = NULL;
	Accessible *child = NULL;
	Accessible *tempchild = NULL;
	SPIBoolean flag, changeflag = FALSE;

	parent = Accessible_getParent (object);
	count = Accessible_getChildCount (parent);

	for (i = 0; i < count; i++) {
		tempchild = Accessible_getChildAtIndex (parent, i);
		if (is_object_scroll_bar (tempchild, log_fp) == TRUE) {
			if (is_scroll_bar_vertical (tempchild) == TRUE) {
				child = Accessible_getChildAtIndex (parent, i);
				changeflag = TRUE;
				Accessible_unref (tempchild);
				break;
			}
		}
		Accessible_unref (tempchild);
	}
	Accessible_unref (parent);

	if (changeflag == FALSE) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_NOT_VERTICAL_SCROLL_BAR);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		if (child)
			Accessible_unref (child);
		return error;
	}
	value = Accessible_getValue (child);
	val = AccessibleValue_getMaximumValue (value);
	/*
	  The scroll bar is set at the lowest position
	*/
	flag = AccessibleValue_setCurrentValue (value, val);
	Accessible_unref (value);
	Accessible_unref (child);
	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_UNABLE_TO_SCROLL_WITH_GIVEN_VALUE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
scroll_left (Accessible *object, FILE *log_fp)
{
	long i = 0, count;
	Accessible *parent;
	AccessibleValue *value = NULL;
	Accessible *child = NULL;
	Accessible *tempchild = NULL;
	SPIBoolean flag, changeflag = FALSE;

	parent = Accessible_getParent (object);
	count = Accessible_getChildCount (parent);

	while (i < count) {
		tempchild = Accessible_getChildAtIndex (parent, i);
		if (is_object_scroll_bar (tempchild, log_fp) == TRUE) {
			if (is_scroll_bar_horizontal (tempchild) == TRUE) {
				child = Accessible_getChildAtIndex (parent, i);
				changeflag = TRUE;
				Accessible_unref (tempchild);
				break;
			}
		}
		Accessible_unref (tempchild);
		i++;
	}
	Accessible_unref (parent);

	if (changeflag == FALSE) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_NOT_HORIZONTAL_SCROLL_BAR);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		if (child)
			Accessible_unref (child);
		return error;
	}
	value = Accessible_getValue (child);
	/*
	  The scroll bar is set to 0 which is the leftmost limit
	*/
	flag = AccessibleValue_setCurrentValue (value, 0);

	Accessible_unref (value);
	Accessible_unref (child);

	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_UNABLE_TO_SCROLL_WITH_GIVEN_VALUE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
scroll_right (Accessible *object, FILE *log_fp)
{
	double val;
	long i = 0, count;
	Accessible *parent;
	AccessibleValue *value = NULL;
	Accessible *child = NULL;
	Accessible *tempchild = NULL;
	SPIBoolean flag, changeflag = FALSE;

	parent = Accessible_getParent (object);
	count = Accessible_getChildCount (parent);

	while (i < count) {
		tempchild = Accessible_getChildAtIndex (parent, i);
		if (is_object_scroll_bar (tempchild, log_fp) == TRUE) {
			if (is_scroll_bar_horizontal (tempchild) == TRUE) {
				child = Accessible_getChildAtIndex (parent, i);
				changeflag = TRUE;
				Accessible_unref (tempchild);
				break;
			}
		}
		Accessible_unref (tempchild);
		i++;
	}
	Accessible_unref (parent);

	if (changeflag == FALSE) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_NOT_HORIZONTAL_SCROLL_BAR);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		if (child)
			Accessible_unref (child);
		return error;
	}
	value = Accessible_getValue (child);
	val = AccessibleValue_getMaximumValue (value);

	/* 
	   sets the scroll bar at the rigtmost position
	*/

	flag = AccessibleValue_setCurrentValue (value, val);

	Accessible_unref (value);
	Accessible_unref (child);

	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_UNABLE_TO_SCROLL_WITH_GIVEN_VALUE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
one_down (Accessible *object, int num, FILE *log_fp)
{
	int j = 1;
	long i = 0, count;
	double max, val;
	Accessible *parent;
	Accessible *child = NULL;
	Accessible *tempchild = NULL;
	AccessibleValue *value = NULL;
	SPIBoolean flag, changeflag = FALSE;

	parent = Accessible_getParent (object);
	count = Accessible_getChildCount (parent);

	while (i < count) {
		tempchild = Accessible_getChildAtIndex (parent, i);
		if (is_object_scroll_bar (tempchild, log_fp) == TRUE) {
			if (is_scroll_bar_vertical (tempchild) == TRUE) {
				child = Accessible_getChildAtIndex (parent, i);
				changeflag = TRUE;
				Accessible_unref (tempchild);
				break;
			}
		}
		Accessible_unref (tempchild);
		i++;
	}
	Accessible_unref (parent);

	if (changeflag == FALSE) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_NOT_VERTICAL_SCROLL_BAR);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		if (child)
			Accessible_unref (child);
		return error;
	}

	value = Accessible_getValue(child);    
	max = AccessibleValue_getMaximumValue (value);
	max = max / 8;

	while (j <= num) {   
		val = AccessibleValue_getCurrentValue (value);
		val = val + max;
		if (val > (max * 8)) {
			LDTPErrorCode error;
			error =  (LDTP_ERROR_SCROLL_BAR_MAX_REACHED);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			Accessible_unref (value);
			Accessible_unref (child);
			return error;
		}

		/*
		  Moves the scroll bar downwards
		*/

		flag = AccessibleValue_setCurrentValue (value, val);
		ldtp_nsleep (0, 15000);
		j = j + 1;
	}
	Accessible_unref (value);
	Accessible_unref (child);
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
one_up (Accessible *object, int num, FILE *log_fp)
{
	double max, val;
	long count, i = 0, j = 1;
	Accessible *parent;
	Accessible *child = NULL;
	Accessible *tempchild = NULL;
	AccessibleValue *value = NULL;
	SPIBoolean flag, changeflag = FALSE;

	parent = Accessible_getParent (object);
	count = Accessible_getChildCount (parent);

	while (i < count) {
		tempchild = Accessible_getChildAtIndex (parent, i);
		if (is_object_scroll_bar (tempchild, log_fp) == TRUE) {
			if (is_scroll_bar_vertical (tempchild) == TRUE) {
				child = Accessible_getChildAtIndex (parent, i);
				changeflag = TRUE;
				Accessible_unref (tempchild);
				break;
			}
		}
		Accessible_unref (tempchild);
		i++;
	}
	Accessible_unref (parent);

	if (changeflag == FALSE) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_NOT_VERTICAL_SCROLL_BAR);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		if (child)
			Accessible_unref (child);
		return error;
	}
	value = Accessible_getValue(child);
	max = AccessibleValue_getMaximumValue (value);
	max = max / 8;

	while(j <= num) {   
		val = AccessibleValue_getCurrentValue (value);
		val = val - max;
		if (val < 0) {
			LDTPErrorCode error;
			error =  (LDTP_ERROR_SCROLL_BAR_MIN_REACHED);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			Accessible_unref (value);
			Accessible_unref (child);
			return error;
		}

		/*
		  Moves the scroll bar upwards
		*/

		flag = AccessibleValue_setCurrentValue (value, val);
		ldtp_nsleep (0, 15000);
		j++;
	}
	Accessible_unref (value);
	Accessible_unref (child);
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
one_right (Accessible *object, int num, FILE *log_fp)
{
	int j = 1;
	long i = 0, count;
	double max, val;
	Accessible *parent;
	Accessible *child =  NULL;
	Accessible *tempchild = NULL;
	AccessibleValue *value = NULL;
	SPIBoolean flag, changeflag = FALSE;

	parent = Accessible_getParent (object);
	count = Accessible_getChildCount (parent);

	while (i < count) {
		tempchild = Accessible_getChildAtIndex (parent, i);
		if (is_object_scroll_bar (tempchild, log_fp) == TRUE) {
			if (is_scroll_bar_horizontal (tempchild) == TRUE) {
				child = Accessible_getChildAtIndex (parent, i);
				changeflag = TRUE;
				Accessible_unref (tempchild);
				break;
			}
		}
		Accessible_unref (tempchild);
		i++;
	}
	Accessible_unref (parent);

	if (changeflag == FALSE) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_NOT_HORIZONTAL_SCROLL_BAR);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		if (child)
			Accessible_unref (child);
		return error;
	}
	value = Accessible_getValue (child);
	val = AccessibleValue_getCurrentValue (value);
	max = AccessibleValue_getMaximumValue (value);
	max = max / 8;

	while (j <= num) {   
		val = AccessibleValue_getCurrentValue (value);
		val = val + max;
		if (val > (max * 8)) {
			LDTPErrorCode error;
			error =  (LDTP_ERROR_SCROLL_BAR_MAX_REACHED);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			Accessible_unref (value);
			Accessible_unref (child);
			return error;
		}

		/*
		  Moves the scroll bar towards the right
		*/

		flag = AccessibleValue_setCurrentValue (value, val);
		ldtp_nsleep (0, 15000);
		j++;
	}

	Accessible_unref (value);
	Accessible_unref (child);
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
one_left (Accessible *object, int num, FILE *log_fp)
{
	double max, val;
	long i = 0, j = 1, count;
	Accessible *parent;
	Accessible *child = NULL;
	Accessible *tempchild = NULL;
	AccessibleValue *value = NULL;
	SPIBoolean flag, changeflag = FALSE;

	parent = Accessible_getParent (object);
	count = Accessible_getChildCount (parent);

	while (i < count) {
		tempchild = Accessible_getChildAtIndex (parent, i);
		if (is_object_scroll_bar (tempchild, log_fp) == TRUE) {
			if (is_scroll_bar_horizontal (tempchild) == TRUE) {
				child = Accessible_getChildAtIndex (parent, i);
				changeflag = TRUE;
				Accessible_unref (tempchild);
				break;
			}
		}
		Accessible_unref (tempchild);
		i++;
	}
	Accessible_unref (parent);

	if (changeflag == FALSE) {
		LDTPErrorCode error;
		error =  (LDTP_ERROR_NOT_HORIZONTAL_SCROLL_BAR);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		if (child)
			Accessible_unref (child);
		return error;
	}
	value = Accessible_getValue (child);
	val = AccessibleValue_getCurrentValue (value);
	max = AccessibleValue_getMaximumValue (value);
	max = max / 8;

	while (j <= num) {    
		val = AccessibleValue_getCurrentValue (value);
		val = val - max;
		if (val < 0) {
			LDTPErrorCode error;
			error =  (LDTP_ERROR_SCROLL_BAR_MIN_REACHED);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			Accessible_unref (value);
			Accessible_unref (child);
			return error;
		}

		/*
		  Moves the scroll bar in the leftward direction
		*/

		flag = AccessibleValue_setCurrentValue (value, val);
		ldtp_nsleep (0, 15000);
		j++;
	}
	Accessible_unref (value);
	Accessible_unref (child);
	return  (LDTP_ERROR_SUCCESS);
}

LDTPErrorCode
scroll_bar_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_VERIFYSCROLLBAR:
		if (is_object_scroll_bar (cctxt->gui_handle->handle, cctxt->log_fp))
			error =  (LDTP_ERROR_SUCCESS);
		else
			error =  (LDTP_ERROR_INVALID_OBJECT_STATE);
		break;
	case LDTP_CMD_VERIFYSCROLLBARVERTICAL:
		if (is_scroll_bar_vertical (cctxt->gui_handle->handle))
			error =  (LDTP_ERROR_SUCCESS);
		else
			error =  (LDTP_ERROR_NOT_VERTICAL_SCROLL_BAR);
		break;
	case LDTP_CMD_VERIFYSCROLLBARHORIZONTAL:
		if (is_scroll_bar_horizontal (cctxt->gui_handle->handle))
			error =  (LDTP_ERROR_SUCCESS);
		else
			error =  (LDTP_ERROR_NOT_HORIZONTAL_SCROLL_BAR);
		break;
	case LDTP_CMD_SCROLLUP: 
		error = scroll_up (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_SCROLLDOWN: 
		error = scroll_down (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_SCROLLLEFT: 
		error = scroll_left (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_SCROLLRIGHT: 
		error = scroll_right (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_ONEUP: {
		long num = 0;
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			num = atol (cctxt->req->arg_list->data);
		error = one_up (cctxt->gui_handle->handle, num, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_ONEDOWN: {
		long num = 0;
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			num = atol (cctxt->req->arg_list->data);
		error = one_down (cctxt->gui_handle->handle, num, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_ONELEFT: {
		long num = 0;
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			num = atol (cctxt->req->arg_list->data);
		error = one_left (cctxt->gui_handle->handle, num, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_ONERIGHT: {
		long num = 0;
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			num = atol (cctxt->req->arg_list->data);
		error = one_right (cctxt->gui_handle->handle, num, cctxt->log_fp);
		break;
	}
	default:
		error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
		break;
	}
	return error;
}
