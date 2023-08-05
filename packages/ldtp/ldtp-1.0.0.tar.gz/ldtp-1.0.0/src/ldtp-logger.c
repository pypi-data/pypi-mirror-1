/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Veerapuram Varadhan <v.varadhan@gmail.com>
 *    Nagappan <nagappan@gmail.com>
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
#include <stdarg.h>
#include <stdlib.h>
#include <errno.h>
#include <time.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include <glib.h>

#include "ldtp-utils.h"
#include "ldtp-logger.h"

static char *ldtp_log_msg = NULL;

void 
ldtp_log (const char *template, ...)
{
	va_list ap;
	time_t timeval;
	char *curr_time = NULL;
	char *ldtp_debug = getenv ("LDTP_DEBUG");
  
	va_start (ap, template);
	time (&timeval);
	curr_time = g_strdup (ctime (&timeval));
	if (curr_time) {
		curr_time[strlen (curr_time) - 1] = '\0';
		g_print ("%s: ", curr_time);
		g_free (curr_time);
	}
	if (ldtp_debug != NULL && g_ascii_strcasecmp (ldtp_debug, "2") == 0 && template != NULL)
		vprintf (template, ap);
	va_end (ap);
}

char *replace_white_space (char *data, char chr)
{
	int i;
	int j = 0;
	char *replaced_data = NULL;

	replaced_data = (char *) malloc (sizeof (char) * strlen (data) + 1);

	for (i = 0; i < strlen (data); i++) {
		if (data[i] == ' ')
			replaced_data[j++] = chr;
		else
			replaced_data[j++] = data[i];
	}
	replaced_data[j] = '\0';
	return replaced_data;
}

gboolean
open_log_file (char *log_file_name,
	       int log_file_delete,
	       FILE **fp)
{
	if (log_file_delete == LDTP_LOG_FILE_DELETE) {
		*fp = fopen (log_file_name, "w+");
		if (*fp) {
			fprintf (*fp, "<?xml version='1.0' encoding='utf-8'?>\n<!-- XML Logging -->\n<ldtp>\n");
			fflush (*fp);
		}
	}
	else
		*fp = fopen (log_file_name, "a+");

	if (*fp == NULL) {
		g_print ("Log file cannot be created \n");
		return FALSE;
	}
	return TRUE;
}

void
close_log_file (FILE **fp)
{
	if (*fp) {
		fprintf (*fp, "</ldtp>\n");
		fflush (*fp);
		fclose (*fp);
	}
	*fp = NULL;
}

void
log_msg (int level, const char *msg, FILE *fp)
{
	char *log_message = NULL;
	char *message = NULL;

	if (fp == NULL || msg == NULL) {
		return;
	}
	message = escape_xml_character (msg);

	switch (level) {
	case LDTP_LOG_PASS:
		log_message = g_strdup_printf ("<pass>1</pass>");
		break;
	case LDTP_LOG_FAIL:
		log_message = g_strdup_printf ("<pass>0</pass>");
		break;
	case LDTP_LOG_CAUSE:
		if (message && g_ascii_strcasecmp (message, "") != 0)
			log_message = g_strdup_printf ("<cause>%s</cause>", message);
		else
			log_message = g_strdup_printf ("<error>EMPTY MESSAGE</error>");
		break;
	case LDTP_LOG_ERROR:
		if (message && g_ascii_strcasecmp (message, "") != 0)
			log_message = g_strdup_printf ("<error>%s</error>", message);
		else
			log_message = g_strdup_printf ("<error>EMPTY MESSAGE</error>");
		break;
	case LDTP_LOG_DEBUG:
		if (message && g_ascii_strcasecmp (message, "") != 0)
			log_message = g_strdup_printf ("<debug>%s</debug>", message);
		else
			log_message = g_strdup_printf ("<error>EMPTY MESSAGE</error>");
		break;
	case LDTP_LOG_INFO:
		if (message && g_ascii_strcasecmp (message, "") != 0)
			log_message = g_strdup_printf ("<info>%s</info>", message);
		else
			log_message = g_strdup_printf ("<error>EMPTY MESSAGE</error>");
		break;
	case LDTP_LOG_WARNING:
		if (message && g_ascii_strcasecmp (message, "") != 0)
			log_message = g_strdup_printf ("<warning>%s</warning>", message);
		else
			log_message = g_strdup_printf ("<error>EMPTY MESSAGE</error>");
		break;
	case LDTP_LOG_MEMINFO:
		if (message && g_ascii_strcasecmp (message, "") != 0)
			log_message = g_strdup_printf ("<meminfo>%s</meminfo>", message);
		else
			log_message = g_strdup_printf ("<error>EMPTY MESSAGE</error>");
		break;
	case LDTP_LOG_CPUINFO:
		if (message && g_ascii_strcasecmp (message, "") != 0)
			log_message = g_strdup_printf ("<cpuinfo>%s</cpuinfo>", message);
		else
			log_message = g_strdup_printf ("<error>EMPTY MESSAGE</error>");
		break;
	case LDTP_LOG_DATA_FILENAME:
		if (message && g_ascii_strcasecmp (message, "") != 0)
			log_message = g_strdup_printf ("<datafilename>%s</datafilename>", message);
		else
			log_message = g_strdup_printf ("<error>EMPTY MESSAGE</error>");
		break;
	case LDTP_LOG_COMMENT:
		if (message && g_ascii_strcasecmp (message, "") != 0)
			log_message = g_strdup_printf ("<comment>%s</comment>", message);
		else
			log_message = g_strdup_printf ("<error>EMPTY MESSAGE</error>");
		break;
	case LDTP_LOG_GROUP_START: {
		char *data = NULL;
		if (message && strchr (message, ' '))
			data = replace_white_space (message, '-');
		else
			if (message)
				data = g_strdup (message);
		log_message = g_strdup_printf ("<group name=\"%s\">", data);
		g_free (data);
		break;
	}
	case LDTP_LOG_GROUP_STATUS:
		if (message && g_ascii_strcasecmp (message, "") != 0)
			log_message = g_strdup_printf ("<groupstatus>%s</groupstatus>", message);
		else
			log_message = g_strdup_printf ("<error>EMPTY MESSAGE</error>");
		break;
	case LDTP_LOG_GROUP_END:
		log_message = g_strdup_printf ("</group>");
		break;
	case LDTP_LOG_SCRIPT_START: {
		char *data = NULL;
		if (message && strchr (message, ' '))
			data = replace_white_space (message, '-');
		else
			if (message)
				data = g_strdup (message);
		log_message = g_strdup_printf ("<script name=\"%s\">", data);
		g_free (data);
		break;
	}
	case LDTP_LOG_SCRIPT_END:
		log_message = g_strdup_printf ("</script>");
		break;
	case LDTP_LOG_TESTSTART: {
		char *data = NULL;
		if (message && strchr (message, ' '))
			data = replace_white_space (message, '-');
		else
			if (message)
				data = g_strdup (message);
		log_message = g_strdup_printf ("<test name=\"%s\">", data);
		g_free (data);
		break;
	}
	case LDTP_LOG_TESTCASEID:
		if (message && g_ascii_strcasecmp (message, "") != 0)
			log_message = g_strdup_printf ("<testcaseid>%s</testcaseid>", message);
		else
			log_message = g_strdup_printf ("<error>EMPTY MESSAGE</error>");
		break;
	case LDTP_LOG_TESTEND:
		log_message = g_strdup_printf ("</test>");
		break;
	case LDTP_LOG_BEGIN: {
		char *data = NULL;
		if (message && strchr (message, ' '))
			data = replace_white_space (message, '-');
		else
			if (message)
				data = g_strdup (message);
		log_message = g_strdup_printf ("<testsuite name=\"%s\">",
					       data);
		g_free (data);
		break;
	}
	case LDTP_LOG_END:
		log_message = g_strdup_printf ("</testsuite>");
		break;
	}
	if (log_message)
		g_print ("%s\n", log_message);
	if (fp && log_message) {
		fprintf (fp, "%s\n", log_message);
		fflush (fp);
		g_free (log_message); 
	}
	if (ldtp_log_msg != NULL)
		g_free (ldtp_log_msg);
	ldtp_log_msg = NULL;
	if (message)
		ldtp_log_msg = g_strdup (message);
	g_free (message);
}

char *get_last_log ()
{
	return ldtp_log_msg;
}

void clear_last_log ()
{
	if (ldtp_log_msg) {
		g_free (ldtp_log_msg);
		ldtp_log_msg = NULL;
	}
}
