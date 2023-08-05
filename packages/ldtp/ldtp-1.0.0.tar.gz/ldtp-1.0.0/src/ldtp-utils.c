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

#include "ldtp-utils.h"
#include "ldtp-logger.h"

void
ldtp_read_sizet (int fd, uint32_t *size, LDTPErrorCode *err)
{
	ldtp_read_data (fd, (void *)size, sizeof (uint32_t), NULL, err);
}

void
ldtp_read_data (int socket_fd, void *buf, size_t len, size_t *bytes_read, LDTPErrorCode *err)
{
	int recv_bytes = -1;
	recv_bytes = recv (socket_fd, buf, len, 0);

	if (bytes_read)
		*bytes_read = recv_bytes;

	if (recv_bytes == -1) {
		ldtp_log ("%s:%d:ldtp_read_data() : %s\n", __FILE__, __LINE__, strerror (errno));
		*err = LDTP_ERROR_RECEIVE_RESPONSE;
	}
	else if (recv_bytes == 0) {
		ldtp_log ("%s:%d:ldtp_read_data() : %s\n", __FILE__, __LINE__, strerror (errno));
		*err = LDTP_ERROR_CLIENT_DISCONNECTED;
	}
	else
		*err = LDTP_ERROR_SUCCESS;
}

gchar*
read_line (int fd, LDTPErrorCode *err)
{
	long len = 128;
	long size = 0;
	gchar ch;
	gchar *data = NULL;

	while (read (fd, &ch, 1) > 0) {
		if (!data) {
			data = (char *) malloc (sizeof (char)*len);
		}
		if (size%len == 0) {
			data = (char *) realloc (data, sizeof (char)*len+size+1);
		}
		data[size++] = ch;
		if (ch == '\n') {
			if (size%len == 0) {
				data = (char *) realloc (data, sizeof (char)+size+1);
			}
			data[size] = '\0';
			return data;
		}
	}
	return NULL;
}

void
ldtp_send (int socket_fd, void* msg, size_t len, LDTPErrorCode* err)
{
	int bytes_sent = send (socket_fd, msg, len, 0);
	g_print ("Msg: %s\n", (char *)msg);
	g_print ("Bytes sent: %d\n", bytes_sent);
	if (bytes_sent == -1) {
		ldtp_log ("Client disconnected\n");
		*err = LDTP_ERROR_SENDING_RESPONSE;
		return;
	}
	if (bytes_sent != len) {
		ldtp_log ("ldtp_send(): partial data sent\n");
		*err = LDTP_ERROR_PARTIAL_DATA_SENT;
		return;
	}
	*err = LDTP_ERROR_SUCCESS;
	fflush (NULL);
}

/*
  Copied from LTFX source code
*/

void
ldtp_nsleep (int s, long ns)
{
	int seconds = -1;
	struct timespec sleeping;
	struct timespec timeleft;

	sleeping.tv_sec = s;
	sleeping.tv_nsec = ns;

	while (seconds != 0)
		seconds = nanosleep (&sleeping, &timeleft);
}

gchar*
escape_character (const gchar *text, gchar ch)
{
	GString *str;
	gint length;
	const gchar *p;
	const gchar *end;

	if (!text)
		return NULL;

	length = strlen (text);

	str = g_string_sized_new (length);

	p = text;
	end = text + length;

	while (p != end) {
		const gchar *next;
		next = g_utf8_next_char (p);

		if (*p == ch)
			g_string_append (str, "");
		else
			g_string_append_len (str, p, next - p);

		p = next;
	}

	return g_string_free (str, FALSE);
}

gchar *
escape_xml_character (const gchar *text)
{
	GString *str;
	gint length;
	const gchar *p;
	const gchar *end;
	const gchar *next;
	
	if (!text)
		return NULL;
	length = strlen (text);
	str = g_string_sized_new (length);
	p = text;
	end = text + length;
	while (p != end) {
		next = g_utf8_next_char (p);

		switch (*p) {
		case '<':
			g_string_append (str, "&lt;");
			break;
		case '>':
			g_string_append (str, "&gt;");
			break;
		case '&':
			g_string_append (str, "&amp;");
			break;
		case '\'':
			g_string_append (str, "&apos;");
			break;
		case '\"':
			g_string_append (str, "&quot;");
			break;
		default:
			g_string_append_len (str, p, next-p);
		}
		p = next;
	}
	return g_string_free (str, FALSE);
}
