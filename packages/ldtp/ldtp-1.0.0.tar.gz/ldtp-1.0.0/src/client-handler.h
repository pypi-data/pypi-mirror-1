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

#ifndef _CLIENT_HANDLER_H
#define _CLIENT_HANDLER_H

#include <glib.h>
#include <cspi/spi.h>
#include "ldtp.h"
#include "ldtp-gui.h"
#include "ldtp-request.h"
#include "ldtp-response.h"
#include "ldtp-error.h"

typedef struct _LDTPClientContext LDTPClientContext;
typedef struct _Packet Packet;
typedef struct _MatchingList MatchingList;

typedef struct _LDTPGuiHandle LDTPGuiHandle;
struct _LDTPGuiHandle {
	Accessible* handle;
	int class_id;
};

struct _LDTPClientContext {
	int sock_fd;		      /* socket fd for the connection */
	FILE *log_fp;                 /* Log file fp */
	gchar *locale_lang;           /* Locale language */
	gchar *window_name;           /* Window name in appmap format */
	gboolean locale_set;          /* Locale flag set or not */
	Accessible* app_handle;	      /* Handle to the application's main window - Accessibiliy handle */
	GHashTable* app_map;	      /* Hashtable that maintains the Application Map read from appmap file */
	LDTPRequest* req;	      /* decoded-request-packet from client */
	LDTPResponse* resp;           /* response-structure that will be send to client */
	LDTPGuiHandle* gui_handle;    /* Handle to the gui-object on which the action is sought */
	char* last_successfull_action;/* Last successfull action - in case to report error on operations */
};

struct _Packet {
	char *packet;
	uint32_t len;
};

struct _MatchingList {
	gchar *data;
	gchar *name;
	gchar *role;
};

void *handle_client (void *ptr);

void generate_response_packet (LDTPClientContext* cctxt, LDTPErrorCode* err,
			       char **resp_packet, uint32_t *resp_size);
void generate_notification_packet (LDTPClientContext* cctxt, LDTPErrorCode* err,
			       char **resp_packet, uint32_t *resp_size);
void send_response (int sockfd, char *resp_xml, uint32_t resp_len, LDTPErrorCode* err);

#endif
