/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org/
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

#ifndef _LDTP_LOGGER_H
#define _LDTP_LOGGER_H

typedef enum _LDTPLog {
	LDTP_LOG_DEBUG ,
	LDTP_LOG_INFO ,
	LDTP_LOG_WARNING ,
	LDTP_LOG_ERROR ,
	LDTP_LOG_CRITICAL ,
	LDTP_LOG_TESTSTART ,
	LDTP_LOG_TESTCASEID ,
	LDTP_LOG_TESTEND ,
	LDTP_LOG_BEGIN ,
	LDTP_LOG_END ,
	LDTP_LOG_FAIL ,
	LDTP_LOG_PASS ,
	LDTP_LOG_CAUSE ,
	LDTP_LOG_COMMENT ,
	LDTP_LOG_GROUP_START ,
	LDTP_LOG_GROUP_STATUS ,
	LDTP_LOG_GROUP_END ,
	LDTP_LOG_SCRIPT_START ,
	LDTP_LOG_SCRIPT_END ,
	LDTP_LOG_FILE_DELETE ,
	LDTP_LOG_FILE_APPEND ,
	LDTP_LOG_DATA_FILENAME ,
	LDTP_LOG_MEMINFO ,
	LDTP_LOG_CPUINFO ,
} LDTPLogCode;

typedef enum _LDTPLog LDTPLog;


/* group together messages of controls, include each controls messages
 * in alpahbetical order
 */
void close_log_file (FILE **);
gboolean open_log_file (char *, int, FILE **);
void log_msg (int, const char *, FILE *);
char *get_last_log (void);
void clear_last_log (void);
char *replace_white_space (char *, char);

void ldtp_log (const char *template, ...);

#endif 
