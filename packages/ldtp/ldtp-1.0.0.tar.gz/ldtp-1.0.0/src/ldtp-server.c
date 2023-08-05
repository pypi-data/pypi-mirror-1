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

#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <glib.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#include "ldtp-server.h"
#include "ldtp-logger.h"

#define LDTP_SCRIPT_ENGINE_PORT 23456

static struct sockaddr_un un_myaddr;   // server address // sockaddr_un
static struct sockaddr_in script_myaddr;   // server address // sockaddr_in
int script_listener = 0;               // listening socket descriptor

char*
get_tmp_file (int server_type)
{
	if (server_type == LDTP_SCRIPT_SERVER)
		return g_strdup_printf ("/tmp/ldtp-%s-%s", getenv ("USER"), getenv ("DISPLAY"));
	else
		return NULL;
}

int
init_ldtp_server (int server_type)
{
	int yes = 1;        // for setsockopt() SO_REUSEADDR, below
	gchar* tmpfile = NULL;
	int listener = 0;
	extern gint ldtp_script_port;
	extern gboolean ldtp_script_service;

	if (server_type == LDTP_SCRIPT_SERVER &&
	    (ldtp_script_service)) {
		// get the listener
		if ((listener = socket (PF_INET, SOCK_STREAM, 0)) == -1) {
			ldtp_log ("ERROR:socket() failed with \"%s\"\n", strerror(errno));
			exit (-1);
		}
	}
	else {
		// get the listener
		if ((listener = socket (AF_UNIX, SOCK_STREAM, 0)) == -1) {
			ldtp_log ("ERROR:socket() failed with \"%s\"\n", strerror(errno));
			exit (-1);
		}
	}
	if (server_type == LDTP_SCRIPT_SERVER)
		script_listener = listener;

	if (setsockopt (listener, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof (int)) == -1) {
		ldtp_log ("ERROR: setsockopt() failed with \"%s\"\n", strerror (errno));
		exit (-1);
	}
	if (server_type == LDTP_SCRIPT_SERVER &&
	    (ldtp_script_service)) {
		/*
		  Puneet Mishra: Palm Source Inc
		 */
		script_myaddr.sin_family = AF_INET;
		g_print ("Port: %d\n", ldtp_script_port);
		if (ldtp_script_port)
			script_myaddr.sin_port = htons (ldtp_script_port);
		else
			script_myaddr.sin_port = htons (LDTP_SCRIPT_ENGINE_PORT);
		script_myaddr.sin_addr.s_addr = htonl (INADDR_ANY);
		memset(&(script_myaddr.sin_zero), '\0', 8);
		g_print ("**Script myaddr.sin_addr.s_addr %s:%d\n",
			 inet_ntoa (script_myaddr.sin_addr), ntohs (script_myaddr.sin_port));
		if (bind (listener, (struct sockaddr *) &script_myaddr, sizeof (struct sockaddr)) == -1) {
			ldtp_log ("Script ERROR: bind() failed with \"%s\"\n", strerror (errno));
			exit (-1);
		}
	}
	else {
		// bind
		tmpfile = get_tmp_file (server_type);
		/*
		  If file already exist, we need to unlink it, otherwise we will get bind error
		*/
		unlink (tmpfile);
		strcpy (un_myaddr.sun_path, tmpfile);
		g_free (tmpfile);
		un_myaddr.sun_family = AF_UNIX;
		if (bind (listener, (struct sockaddr *) &un_myaddr, sizeof (un_myaddr)) == -1) {
			ldtp_log ("ERROR: bind() failed with \"%s\"\n", strerror (errno));
			exit (-1);
		}
	}

	// listen
	if (listen (listener, 10) == -1) {
		ldtp_log ("ERROR: listen() failed with \"%s\"\n", strerror (errno));
		exit (-1);
	}
	return listener;
}

int
get_server_socket (int server_type)
{
	if (server_type == LDTP_SCRIPT_SERVER)
		return script_listener;
	else
		return 0;
}
