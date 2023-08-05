/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Prashanth Mohan <prashmohan@gmail.com>
 *
 * Copyright 2004 - 2006 Novell, Inc.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
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
#include "device.h"
     
static LDTPErrorCode
mouse_left_click (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleCoordType screen_cood = SPI_COORD_TYPE_SCREEN;
	SPIBoolean flag;
	long int xpos, ypos;
	xpos=ypos=0;

	if (Accessible_isComponent (object)) {
		AccessibleComponent *accessible_component;
		accessible_component = Accessible_getComponent (object);
		if (!AccessibleComponent_grabFocus (accessible_component)) {
			Accessible_unref (accessible_component);
			error = LDTP_ERROR_UNABLE_TO_GRAB_FOCUS;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}

		AccessibleComponent_getPosition (accessible_component, &xpos, &ypos, screen_cood);
		Accessible_unref (accessible_component);
	}
	else {
		error = LDTP_ERROR_UNABLE_TO_GET_COMPONENT_HANDLE;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	flag = SPI_generateMouseEvent (xpos, ypos, "b1c");
	if (flag == FALSE) {
		error = LDTP_ERROR_CLICK_FAILED;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return LDTP_ERROR_SUCCESS;
}

static LDTPErrorCode
mouse_right_click (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleCoordType screen_cood = SPI_COORD_TYPE_SCREEN;
	SPIBoolean flag;
	long int xpos, ypos;
	xpos = ypos = 0;

	if (Accessible_isComponent (object)) {
		AccessibleComponent *accessible_component;
		accessible_component = Accessible_getComponent (object);
		if (!AccessibleComponent_grabFocus (accessible_component)) {
			Accessible_unref (accessible_component);
			error = LDTP_ERROR_UNABLE_TO_GRAB_FOCUS;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}

		AccessibleComponent_getPosition (accessible_component, &xpos, &ypos, screen_cood);
		Accessible_unref (accessible_component);
	}
	else {
		error = LDTP_ERROR_UNABLE_TO_GET_COMPONENT_HANDLE;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}	     
	flag = SPI_generateMouseEvent (xpos, ypos, "b3c");
	if (flag == FALSE) {
		error = LDTP_ERROR_RIGHT_CLICK_FAILED;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return LDTP_ERROR_SUCCESS;
}

static LDTPErrorCode
mouse_move (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleCoordType screen_cood = SPI_COORD_TYPE_SCREEN;
	SPIBoolean flag;
	long int xpos, ypos;
	//long int width, height;

	if (Accessible_isComponent (object)) {
		AccessibleComponent *accessible_component;
		accessible_component = Accessible_getComponent (object);
		if (!AccessibleComponent_grabFocus (accessible_component)) {
			Accessible_unref (accessible_component);
			error = LDTP_ERROR_UNABLE_TO_GRAB_FOCUS;
			goto error;
		}
		AccessibleComponent_getPosition (accessible_component, &xpos, &ypos, screen_cood);
		Accessible_unref (accessible_component);
	}
	else {
		error = LDTP_ERROR_UNABLE_TO_GET_COMPONENT_HANDLE;
		goto error;
	}	     
	flag = SPI_generateMouseEvent (xpos, ypos, "abs");
	if (flag == FALSE) {
		error = LDTP_ERROR_UNABLE_TO_MOVE_MOUSE;
		goto error;
	}
	error = LDTP_ERROR_SUCCESS;

 error:
	if (error != LDTP_ERROR_SUCCESS)
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

static struct KeyValue
get_key_value (gchar *keyval)
{
	static int Char_Key_Synth_Vals[] = {38, 56, 54, 40, 26, 41, 42, 43, 31,
					    44, 45, 46, 58, 57, 32, 33, 24, 27,
					    39, 28, 30, 55, 25, 53, 29, 52}; /* A - Z */
	static int Digit_Key_Synth_Vals[] = {19, 10, 11, 12, 13, 14, 15, 16, 17, 18}; /* 0 - 9 */
	static struct Symbol_Key_Synth Symbol_Key_Synth_Vals[] = {{'-', 20}, {'=', 21}, {'[', 34},
								  {']', 35}, {';', 47}, {'\'', 48},
								  {'`', 49}, {'\\', 51}, {',', 59},
								  {'.', 60}, {'/', 61}, {' ', 65},
								  {'!', 10}, {'@', 11}, {'#', 12},
								  {'$', 13}, {'%', 14}, {'^', 15},
								  {'&', 16}, {'*', 17}, {'(', 18},
								  {')', 19}, {'_', 20}, {'+', 21},
								  {'{', 34}, {'}', 35}, {':', 47},
								  {'\"',48}, {'~', 49}, {'|', 51},
								  {'<', 59}, {'>', 60}, {'\?', 61}};
	static struct NonPrint_Key_Synth NonPrint_Key_Synth_Vals[] = {{"escape", 9}, {"esc", 9}, {"backspace", 22},
								      {"bksp", 22}, {"ctrl", 37}, {"windowskey", 115},
								      {"tab", 23}, {"return", 36}, {"enter", 36},
								      {"shift", 50}, {"shiftl", 50}, {"shiftr", 62},
								      {"home", 97}, {"end", 103}, {"window", 115},
								      {"alt", 64}, {"altl", 64}, {"altr", 113},
								      {"up", 98}, {"down", 104}, {"right", 102},
								      {"left", 100}, {"space", 65}, {"capslock", 66},
								      {"caps", 66}, {"menu", 117}, {"ins", 106},
								      {"del", 107}, {"insert", 106}, {"delete", 107},
								      {"pageup", 99}, {"pagedown", 105}, {"pgup", 99},
								      {"pgdown", 105}, {"numlock", 77}, {"scrolllock", 78},
								      {"F1", 67}, {"F2", 68}, {"F3", 69}, {"F4", 70},
								      {"F5", 71}, {"F6", 72}, {"F7", 73}, {"F8", 74},
								      {"F9", 75}, {"F10", 76}, {"F11", 95}, {"F12", 96},
								      {NULL, 0}};
	struct KeyValue return_val; /* will contain the return values */
	gint index;

	if (strlen (keyval) == 1) {
		/* This will identify small characters */
		if (*keyval >= 'a' && *keyval <= 'z') {
			return_val.shift = FALSE;
			return_val.non_print_key = FALSE;
			return_val.value = Char_Key_Synth_Vals[*keyval-'a'];
			return return_val;
		}

		/* This will identify Capital Charaters i.e. Shift+Small
		   Character */
		else if (*keyval >= 'A' && *keyval <= 'Z') {
			return_val.shift = TRUE;
			return_val.non_print_key = FALSE;
			return_val.value = Char_Key_Synth_Vals[*keyval-'A'];
			return return_val;
		}

		/* This will identify Digits */
		else if (*keyval >= '0' && *keyval <='9') {
			return_val.shift = FALSE;
			return_val.non_print_key = FALSE;
			return_val.value = Digit_Key_Synth_Vals[*keyval-'0'];
			return return_val;
		}

		/* This will identify Symbols */
		else {
			/* Symbols obtained without using Shift Key */
			for (index = 0; index < DOWNCHAR; index++) 
				if (*keyval == Symbol_Key_Synth_Vals[index].sym) {
					return_val.shift = FALSE;
					return_val.non_print_key = FALSE;
					return_val.value = Symbol_Key_Synth_Vals[index].KeyVal;
					return return_val;
				}
			/* Symbols produced with a key combination
			   including Shift Key */
			for ( ; index < DOWNCHAR + UPCHAR; index++)
				if (*keyval == Symbol_Key_Synth_Vals[index].sym) {
					return_val.shift = TRUE;
					return_val.non_print_key = FALSE;
					return_val.value = Symbol_Key_Synth_Vals[index].KeyVal;
					return return_val;
				}
		}
	}
	else {
		/* This is for identifying non printing keys like numlock,
		   capslock, etc */
		for (index = 0; NonPrint_Key_Synth_Vals[index].sym; index++)
			if (g_ascii_strcasecmp (NonPrint_Key_Synth_Vals[index].sym, keyval) == 0) {
				return_val.shift = FALSE;
				return_val.non_print_key = TRUE;
				return_val.value = NonPrint_Key_Synth_Vals[index].KeyVal;
				return return_val;
			}
	}
     
	/* Key Undefined */
	return_val.shift = FALSE;
	return_val.non_print_key = FALSE;
	return_val.value = UNDEFINED_KEY;
	return return_val;
}

static LDTPErrorCode
get_keyval_id (gchar *input_string, struct KeyValue *keyvals)
{
	struct KeyValue key_val;
	gint index = 0;
	gint keyval_index = 0;
	gchar token[MAX_TOK_SIZE + 1];

	while (*input_string && keyval_index < MAX_TOKENS) {
		index = 0;
		if (*input_string == '<') {
			/* Identified a Non Printing Key */
			input_string++;
			while (*input_string != '>' && *input_string != '\0' && index < MAX_TOK_SIZE) {
				token[index] = *input_string;
				input_string++;
				index++;
			}
			if (*input_string != '>') {
				/* Premature end of string without an opening '<' */
				g_print ("ERROR:: premature EOS\n");
				return LDTP_ERROR_INVALID_FORMAT;
			}
		}
		else {
			token[index] = *input_string;
			index++;
		}
		input_string++;
		token[index] = '\0';

		key_val = get_key_value (token);
		if (key_val.value == UNDEFINED_KEY) {
			g_print ("Invalid Key\n");
			return LDTP_ERROR_TOKEN_NOT_FOUND;
		}
		g_print ("KEY_ID :: %d\n",key_val.value);
		keyvals[keyval_index] = key_val;
		keyval_index++;
	}
	if (keyval_index == MAX_TOKENS) {
		g_print ("ERROR :: Too many tokens\n");
		return LDTP_ERROR_INVALID_FORMAT;
	}
	keyvals [keyval_index].value = UNDEFINED_KEY; /* End Delimiter */
	return LDTP_ERROR_SUCCESS;
}

static LDTPErrorCode
generate_keyboard_sequence (char *input_string, FILE *log_fp)
{
	LDTPErrorCode error;
	AccessibleKeySynthType type = SPI_KEY_PRESS;
	struct KeyValue keyval[MAX_TOKENS+1];
	gint index, history_index;
	SPIBoolean flag;

	error = get_keyval_id (input_string,  keyval);
	if (error != LDTP_ERROR_SUCCESS) {
		goto error;
	}

	for (index=0; keyval[index].value != UNDEFINED_KEY && index < MAX_TOKENS;index++) {
		g_print ("Generating Key Board Value: %d\n",keyval[index].value);
		if (keyval[index].non_print_key == TRUE)
			type = SPI_KEY_PRESS;
		else
			type = SPI_KEY_PRESSRELEASE;
		if (keyval[index].shift == 1)
			SPI_generateKeyboardEvent (50, NULL, SPI_KEY_PRESS); // press shift
		flag = SPI_generateKeyboardEvent (keyval[index].value, NULL, type);
		if (keyval[index].shift == 1)
			SPI_generateKeyboardEvent (50, NULL, SPI_KEY_RELEASE); // release shift
		if (flag == FALSE) {
			error = LDTP_ERROR_UNABLE_TO_ENTER_KEY;
			goto error;
		}
		if (keyval[index].non_print_key == FALSE) {
			history_index = index;
			type = SPI_KEY_RELEASE;
			while (index--) {
				if (keyval[index].non_print_key == FALSE)
					break;
				g_print ("Releasing: %d\n",keyval[index].value);
				flag = SPI_generateKeyboardEvent (keyval[index].value, NULL, type);
				if (flag == FALSE) {
					error = LDTP_ERROR_UNABLE_TO_ENTER_KEY;
					goto error;
				}

			}
			index = history_index;
		}
	}
	type = SPI_KEY_RELEASE;
	while (index--) {
		if (keyval[index].non_print_key == FALSE)
			break;
		g_print ("Releasing: %d\n",keyval[index].value);
		flag = SPI_generateKeyboardEvent (keyval[index].value,NULL,type);
		if (flag == FALSE) {
			error = LDTP_ERROR_UNABLE_TO_ENTER_KEY;
			goto error;
		}
	}
	return error;
 error:
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

LDTPErrorCode
device_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_MOUSELEFTCLICK:
		error = mouse_left_click (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_MOUSERIGHTCLICK:
		error = mouse_right_click (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_MOUSEMOVE:
		error = mouse_move (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_KBDENTER:
		error = grab_focus (cctxt->gui_handle->handle, cctxt->log_fp);
		if (error != LDTP_ERROR_SUCCESS)
			return error;
		error = generate_keyboard_sequence (cctxt->req->arg_list->data, cctxt->log_fp);
		break;
	case LDTP_CMD_GENERATEKEYEVENT:
		error = generate_keyboard_sequence (cctxt->req->context, cctxt->log_fp);
		break;
	default:
		error = LDTP_ERROR_COMMAND_NOT_IMPLEMENTED;
	}
	return error;
}
