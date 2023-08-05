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

#ifndef _LDTP_UTILS_H
#define _LDTP_UTILS_H

#include "ldtp.h"
#include "ldtp-error.h"

void ldtp_read_sizet (int fd, uint32_t *buf, LDTPErrorCode* err);
void ldtp_read_data (int fd, void *buf, size_t len, size_t *bytes_read, LDTPErrorCode* err);

void ldtp_send (int socket_fd, void *msg, size_t len, LDTPErrorCode* err);
void ldtp_nsleep (int s, long ns);
gchar *escape_character (const gchar *text, gchar ch);
gchar *read_line (int fd, LDTPErrorCode* err);
gchar *escape_xml_character (const gchar *text);

#endif
