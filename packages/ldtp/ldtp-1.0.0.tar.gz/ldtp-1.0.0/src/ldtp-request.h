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

#ifndef _LDTP_REQUEST_H_
#define _LDTP_REQUEST_H_

#include <glib.h>
#include "ldtp-error.h"

typedef struct _LDTPRequest LDTPRequest;

struct _LDTPRequest {
	int request_type;
	long int command;
	gchar* application;
	gchar* request_id;
	gchar* context;
	gchar* component;
	gchar* action_name;
	GSList* arg_list;
};

typedef enum _LDTPRequestType {
	LDTP_SCRIPT = 1
} LDTPRequestType;

void ldtp_request_init (LDTPRequest* req);
void ldtp_request_fill_request (LDTPRequest* req, 
				gchar* packet, size_t len,
				LDTPErrorCode* err);
#endif
