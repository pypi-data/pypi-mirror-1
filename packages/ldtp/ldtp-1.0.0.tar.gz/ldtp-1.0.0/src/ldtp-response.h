/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Veerapuram Varadhan <v.varadhan@gmail.com>
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

#ifndef _LDTP_RESPONSE_H
#define _LDTP_RESPONSE_H

#include <sys/types.h>

#define XML_HEADER                   "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
#define RESPONSE_ELEMENT             "<RESPONSE>"
#define RESPONSE_ID_ELEMENT          "<ID>"
#define RESPONSE_ID_END_ELEMENT      "</ID>"
#define STATUS_ELEMENT               "<STATUS>"
#define ATTRIBUTE_CODE_ELEMENT       "<CODE>"
#define ATTRIBUTE_CODE_END_ELEMENT   "</CODE>"
#define ATTRIBUTE_MSG_ELEMENT        "<MESSAGE>"
#define ATTRIBUTE_MSG_END_ELEMENT    "</MESSAGE>"
#define STATUS_END_ELEMENT           "</STATUS>"
#define DATA_ELEMENT                 "<DATA>"
#define ATTRIBUTE_LENGTH_ELEMENT     "<LENGTH>"
#define ATTRIBUTE_LENGTH_END_ELEMENT "</LENGTH>"
#define ATTRIBUTE_FILE_ELEMENT     "<FILE>"
#define ATTRIBUTE_FILE_END_ELEMENT "</FILE>"
#define ATTRIBUTE_NAME_ELEMENT     "<NAME>"
#define ATTRIBUTE_NAME_END_ELEMENT "</NAME>"
#define ATTRIBUTE_VALUE_ELEMENT      "<VALUE><![CDATA["
#define ATTRIBUTE_VALUE_END_ELEMENT  "]]></VALUE>"
#define DATA_END_ELEMENT             "</DATA>"
#define RESPONSE_END_ELEMENT         "</RESPONSE>"
#define NOTIFICATION_ELEMENT         "<NOTIFICATION>"
#define NOTIFICATION_END_ELEMENT     "</NOTIFICATION>"

#define XML_HEADER_LEN                   38
#define RESPONSE_ELEMENT_LEN             10
#define RESPONSE_ID_ELEMENT_LEN           4
#define RESPONSE_ID_END_ELEMENT_LEN       5
#define STATUS_ELEMENT_LEN                8
#define ATTRIBUTE_CODE_ELEMENT_LEN        6
#define ATTRIBUTE_CODE_END_ELEMENT_LEN    7
#define ATTRIBUTE_MSG_ELEMENT_LEN         9
#define ATTRIBUTE_MSG_END_ELEMENT_LEN    10
#define STATUS_END_ELEMENT_LEN            9
#define DATA_ELEMENT_LEN                  6
#define ATTRIBUTE_LENGTH_ELEMENT_LEN      8
#define ATTRIBUTE_LENGTH_END_ELEMENT_LEN  9
#define ATTRIBUTE_FILE_ELEMENT_LEN        6
#define ATTRIBUTE_FILE_END_ELEMENT_LEN    7
#define ATTRIBUTE_NAME_ELEMENT_LEN        6
#define ATTRIBUTE_NAME_END_ELEMENT_LEN    7
#define ATTRIBUTE_VALUE_ELEMENT_LEN      16
#define ATTRIBUTE_VALUE_END_ELEMENT_LEN  11
#define DATA_END_ELEMENT_LEN              7
#define RESPONSE_END_ELEMENT_LEN         11
#define NOTIFICATION_ELEMENT_LEN         14
#define NOTIFICATION_END_ELEMENT_LEN     15

typedef struct _LDTPResponse LDTPResponse;

struct _LDTPResponse {
	LDTPErrorCode resp_status;
	char* data;
	size_t data_len;
};

#endif
