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

#include "ldtp.h"
#include "remap.h"
#include "ldtp-gui.h"
#include "ldtp-utils.h"
#include "ldtp-logger.h"
#include "ldtp-command.h"
#include "localization.h"
#include "ldtp-gui-comp.h"
#include "client-handler.h"
#include "device.h"

#include <locale.h>

extern gboolean ldtp_debug;
extern gint ldtp_gui_timeout;
extern gint ldtp_obj_timeout;
extern GHashTable *event_notifier;
extern GHashTable *client_context;
extern gboolean ldtp_script_service;
extern gboolean ldtp_external_xml_file;

extern pthread_mutex_t cb_mutex;

static gboolean
is_cctxt_registered_callback (gpointer key, gpointer value, gpointer user_data)
{
	if (value && user_data && value == user_data)
		return TRUE;
	return FALSE;
}

static void
register_window_creation_event (LDTPClientContext* cctxt, LDTPErrorCode* err)
{
	if (!cctxt || !cctxt->req || !cctxt->req->context)
		*err = LDTP_ERROR_ARGUMENT_NULL;

	if (!event_notifier)
		event_notifier = g_hash_table_new (&g_str_hash, &g_str_equal);

	g_hash_table_insert (event_notifier, g_strdup ((gchar *)cctxt->req->context), cctxt);
	*err = LDTP_ERROR_SUCCESS;
}

static void
unregister_window_creation_event (LDTPClientContext *cctxt, LDTPErrorCode *err)
{
	g_print ("unregister_window_creation_event - %s - %d\n", __FILE__, __LINE__);
	if (!cctxt || !cctxt->req || !cctxt->req->context) {
		*err = LDTP_ERROR_ARGUMENT_NULL;
		g_print ("%s - %d - Argument NULL\n", __FILE__, __LINE__);
		return;
	}

	if (!event_notifier) {
		*err = LDTP_ERROR_EVENT_NOTIFIER_NOT_ENABLED;
		g_print ("%s - %d - Event notifier not enabled\n", __FILE__, __LINE__);
		return;
	}

	g_print ("Window: %s\n", cctxt->req->context);
	if (g_hash_table_find (event_notifier, search_title_based, cctxt->req->context) != NULL) {
		g_print ("Window unregistered\n");
		g_hash_table_remove (event_notifier, cctxt->req->context);
	}
	*err = LDTP_ERROR_SUCCESS;
}

static char*
write2file (char *content, long len)
{
	char filename [] = "/tmp/LDTP-XML-XXXXXX";
	int fd;

	if (content == NULL || len <= 0) {
		g_print ("Argument NULL\n");
		return NULL;
	}

	if ((fd = mkstemp (filename)) < 0) {
		g_print ("Unable to create tmp file - mkstemp\n");
		return NULL;
	}
	write (fd, content, len);
	close (fd);
	return g_strdup (filename);
}

void
generate_response_packet (LDTPClientContext* cctxt, LDTPErrorCode* err, char **resp_pckt, uint32_t *resp_size)
{
	uint32_t resp_len = 0;
	char buf [16];  
	char buf1 [16];
	char *resp_xml = NULL;
	char *data_pckt = NULL;

	if (!cctxt || !cctxt->resp || !cctxt->req->request_id) {
		*err = LDTP_ERROR_ARGUMENT_NULL;
		return;
	}

	resp_len = XML_HEADER_LEN + 
		RESPONSE_ELEMENT_LEN + 
		RESPONSE_ID_ELEMENT_LEN +
		RESPONSE_ID_END_ELEMENT_LEN +
		STATUS_ELEMENT_LEN +
		ATTRIBUTE_CODE_ELEMENT_LEN +
		ATTRIBUTE_CODE_END_ELEMENT_LEN +
		ATTRIBUTE_MSG_ELEMENT_LEN +
		ATTRIBUTE_MSG_END_ELEMENT_LEN +
		STATUS_END_ELEMENT_LEN +
		RESPONSE_END_ELEMENT_LEN;

	/* Varadhan
	   FIXME: Localization?? 
	*/

	g_print ("resp_len = %d\n", resp_len);

	if (cctxt->req->request_id)
		resp_len += g_utf8_strlen ((gchar *)cctxt->req->request_id, -1);
	if (cctxt->resp->resp_status)
		resp_len += g_utf8_strlen (ldtp_error_get_message (cctxt->resp->resp_status), -1);

	memset (buf, 0x00, 16);
	sprintf (buf, "%d", cctxt->resp->resp_status);
	resp_len += strlen (buf);

	if (cctxt->resp->data && cctxt->resp->data_len > 0) {
		resp_len += DATA_ELEMENT_LEN +
			ATTRIBUTE_LENGTH_ELEMENT_LEN +
			ATTRIBUTE_LENGTH_END_ELEMENT_LEN +
			ATTRIBUTE_VALUE_ELEMENT_LEN +
			ATTRIBUTE_VALUE_END_ELEMENT_LEN +
			DATA_END_ELEMENT_LEN +
			cctxt->resp->data_len;
		memset (buf1, 0x00, 16);
		sprintf (buf1, "%ld", cctxt->resp->data_len);
		resp_len += strlen (buf1);
	}

	if (cctxt->resp->data && cctxt->resp->data_len > 0) {
		char *external_tmp_xml_file = getenv ("LDTP_EXTERNAL_TEMP_FILE");
		if (!ldtp_script_service &&
		    (ldtp_external_xml_file || (external_tmp_xml_file != NULL &&
						g_ascii_strcasecmp (external_tmp_xml_file, "2") == 0)) &&
		    cctxt->resp->data_len > 512) {
			char *filename = write2file (cctxt->resp->data, cctxt->resp->data_len);
			if (filename) {
				data_pckt = g_strconcat (ATTRIBUTE_FILE_ELEMENT,
							 ATTRIBUTE_NAME_ELEMENT,
							 filename,
							 ATTRIBUTE_NAME_END_ELEMENT,
							 ATTRIBUTE_FILE_END_ELEMENT,
							 NULL);
				g_free (filename);
			}
		} else {
			data_pckt = g_strconcat (DATA_ELEMENT,
						 ATTRIBUTE_LENGTH_ELEMENT,
						 buf1, ATTRIBUTE_LENGTH_END_ELEMENT,
						 ATTRIBUTE_VALUE_ELEMENT, 
						 cctxt->resp->data,
						 ATTRIBUTE_VALUE_END_ELEMENT, 
						 DATA_END_ELEMENT, NULL);
		}
	}

	resp_xml = g_strdup_printf ("%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s",
				    XML_HEADER, RESPONSE_ELEMENT,
				    RESPONSE_ID_ELEMENT,
				    cctxt->req->request_id,
				    RESPONSE_ID_END_ELEMENT,
				    STATUS_ELEMENT, ATTRIBUTE_CODE_ELEMENT,
				    buf, ATTRIBUTE_CODE_END_ELEMENT,
				    ATTRIBUTE_MSG_ELEMENT, 
				    ldtp_error_get_message (cctxt->resp->resp_status),
				    ATTRIBUTE_MSG_END_ELEMENT,
				    STATUS_END_ELEMENT,
				    data_pckt ? data_pckt : "",
				    RESPONSE_END_ELEMENT);

	if (data_pckt)
		g_free (data_pckt);

	*err = LDTP_ERROR_SUCCESS;

	*resp_size = strlen (resp_xml);
	*resp_pckt = resp_xml;
}

void
generate_notification_packet (LDTPClientContext* cctxt, LDTPErrorCode* err, char **resp_pckt, uint32_t *resp_size)
{
	uint32_t resp_len = 0;
	char buf [16];  
	char buf1 [16];
	char *resp_xml = NULL;
	char *data_pckt = NULL;

	if (!cctxt || !cctxt->resp) {
		*err = LDTP_ERROR_ARGUMENT_NULL;
		return;
	}

	resp_len = XML_HEADER_LEN + 
		NOTIFICATION_ELEMENT_LEN + 
		STATUS_ELEMENT_LEN +
		ATTRIBUTE_CODE_ELEMENT_LEN +
		ATTRIBUTE_CODE_END_ELEMENT_LEN +
		ATTRIBUTE_MSG_ELEMENT_LEN +
		ATTRIBUTE_MSG_END_ELEMENT_LEN +
		STATUS_END_ELEMENT_LEN +
		NOTIFICATION_END_ELEMENT_LEN;

	/* Varadhan
	   FIXME: Localization?? 
	*/

	g_print ("resp_len = %d\n", resp_len);

	resp_len += strlen (ldtp_error_get_message (cctxt->resp->resp_status));

	memset (buf, 0x00, 16);  
	sprintf (buf, "%d", cctxt->resp->resp_status);
	resp_len += strlen (buf);

	if (cctxt->resp->data && cctxt->resp->data_len > 0) {
		resp_len += DATA_ELEMENT_LEN +
			ATTRIBUTE_LENGTH_ELEMENT_LEN +
			ATTRIBUTE_LENGTH_END_ELEMENT_LEN +
			ATTRIBUTE_VALUE_ELEMENT_LEN +
			ATTRIBUTE_VALUE_END_ELEMENT_LEN +
			DATA_END_ELEMENT_LEN +
			cctxt->resp->data_len;
		memset (buf1, 0x00, 16);
		sprintf (buf1, "%ld", cctxt->resp->data_len);
		resp_len += strlen (buf1);
	}

	if (cctxt->resp->data && cctxt->resp->data_len > 0) 
		data_pckt = g_strconcat (DATA_ELEMENT, 
					 ATTRIBUTE_LENGTH_ELEMENT,
					 buf1, ATTRIBUTE_LENGTH_END_ELEMENT,
					 ATTRIBUTE_VALUE_ELEMENT, 
					 cctxt->resp->data,
					 ATTRIBUTE_VALUE_END_ELEMENT, 
					 DATA_END_ELEMENT, NULL);

	resp_xml = g_strdup_printf ("%s%s%s%s%s%s%s%s%s%s%s%s",
				    XML_HEADER, NOTIFICATION_ELEMENT,
				    STATUS_ELEMENT, ATTRIBUTE_CODE_ELEMENT,
				    buf, ATTRIBUTE_CODE_END_ELEMENT,
				    ATTRIBUTE_MSG_ELEMENT, 
				    ldtp_error_get_message (cctxt->resp->resp_status),
				    ATTRIBUTE_MSG_END_ELEMENT,
				    STATUS_END_ELEMENT,
				    data_pckt ? data_pckt : "",
				    NOTIFICATION_END_ELEMENT);

	*err = LDTP_ERROR_SUCCESS;

	*resp_size = strlen (resp_xml);
	*resp_pckt = resp_xml;
}

void
send_response (int sockfd, char *resp_xml, uint32_t resp_len, LDTPErrorCode *err)
{
	char* resp_packet = NULL;
	//int i = 0;
	int pckt_len = 0;
	uint32_t resp_size = 0;

	resp_size = htonl (resp_len);
	resp_len += sizeof (resp_len);
	resp_packet = calloc (resp_len + 1, 1);
	memcpy (resp_packet, (void *)&resp_size, sizeof (resp_size));

	uint32_t temp = ntohl (resp_size);
	g_print ("Sending..\n%d\n", temp);

	memcpy ((resp_packet + sizeof (resp_len)), 
		resp_xml, resp_len - sizeof (resp_len));

	g_print ("Response packet: %s\n", (resp_packet + sizeof (resp_len)));

	pckt_len = resp_len;

	/*
	  If data sent in chunks from server to client, then the peek code
	  in client was not able to continue reading the next chunk as the
	  recv with peek option always returns the first chunk.
	*/

	ldtp_send (sockfd, resp_packet, resp_len, err);

	/*
	  FIXME: Do not fragment memory.  Use something similar to
	  res-packet thingy.
	*/
	g_free (resp_packet);
}

static void
add_item_to_list (gpointer key, gpointer value, gpointer list)
{
        char **user_data = list;
        if (!key)
                return;
	char *data = *user_data;
        if (data) {
                gchar *tmp = NULL;
                gchar *escaped_xml_data = NULL;
                escaped_xml_data = escape_xml_character (key);

                /*
                  FIXME: Avoid memory fragmentation
		*/
                tmp = g_strdup_printf ("%s<OBJECT>%s</OBJECT>", data, escaped_xml_data);
                g_free (escaped_xml_data);
                g_free (data);
                data = tmp;
        }
        else
                data = g_strdup_printf ("<OBJECT>%s</OBJECT>", (char *) key);
	*user_data = data;
}

static gboolean
is_role_matching (gpointer key, gpointer value, gpointer list)
{
        if (!value || !list)
                return FALSE;
	if (g_utf8_collate (value, list) == 0)
		return TRUE;
	return FALSE;
}

static void
add_matching_item_to_list (gpointer key, gpointer value, gpointer list)
{
	MatchingList *list_item = list;
	gchar *tmp = NULL;
	gchar *data = NULL;
	gchar *label = NULL;
	gchar *escaped_xml_data = NULL;
        if (!key || !value || !list)
                return;
	data = list_item->data;
	if (ldtp_debug)
		g_print ("key: %s\n", (gchar *) key);
	/*
	  list_item->role == NULL, let us add all of the entries to the list
	*/
	if (list_item->role == NULL || g_hash_table_find (value, is_role_matching, list_item->role)) {
		label = get_property (value, "label_by", NULL);
		if (!label)
			label = get_property (value, "label", NULL);
		if (!label)
			escaped_xml_data = escape_xml_character (key);
		else {
			if (g_utf8_strchr (label, -1, '_')) {
				tmp = escape_character (label, '_');
				escaped_xml_data = escape_xml_character (tmp);
				g_free (tmp);
			} else
				escaped_xml_data = escape_xml_character (label);
		}
		if (list_item->name && g_utf8_collate (label, list_item->name) != 0)
			/*
			  If name is not NULL and its label doesn't match, name, then
			  let us not include in the list
			  For example:
			  name = Find, role = push_button in gedit application, just get,
			  the label is Find and role type is push_button.
			*/
			return;
		if (data) {
			tmp = g_strdup_printf ("%s<OBJECT>%s</OBJECT>", data, escaped_xml_data);
			g_free (data);
			data = tmp;
		}
		else
			data = g_strdup_printf ("<OBJECT>%s</OBJECT>", escaped_xml_data);
		g_free (escaped_xml_data);
		list_item->data = data;
	}
}

#ifdef ENABLE_LOCALIZATION
static void
createpo (gchar *package_name, gchar *locale_dir, gchar *file_name,
	  gchar *mode, FILE *log_fp, LDTPErrorCode *err)
{
	gchar *locale_lang = NULL;
	locale_lang = getenv ("LANG");
	if (locale_lang == NULL) {
		log_msg (LDTP_LOG_CAUSE, "Locale language environment not set - LANG",
			 log_fp);
		*err = LDTP_ERROR_UTF8_ENGLISH_LANG;
		return;
	}
	else {
		gchar *tmp = NULL;
		gchar *mofilename = NULL;
		gchar *mopathfilename = NULL;

		struct stat dir_buf;
		gboolean folder_found = FALSE;

		if (g_ascii_strcasecmp (locale_lang, "en_US.UTF-8") == 0) {
			*err = LDTP_ERROR_UTF8_ENGLISH_LANG;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
			return;
		}
		if (stat (locale_dir, &dir_buf) != 0) {
			*err = LDTP_ERROR_UNABLE_TO_STAT_DIR;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
			return;
		}
		if (!S_ISDIR (dir_buf.st_mode)) {
			*err = LDTP_ERROR_UNABLE_TO_STAT_DIR;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
			return;
		}
		if (g_ascii_strcasecmp (mode, "mo") != 0) {
			*err = LDTP_ERROR_ONLY_MO_MODE_SUPPORTED;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
			return;
		}
		tmp = g_strdup_printf ("%s/%s", locale_dir, locale_lang);
		if (!tmp) {
			*err = LDTP_ERROR_UNABLE_TO_ALLOCATE_MEMORY;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
			return;
		}
		mofilename = g_strdup_printf ("/LC_MESSAGES/%s.mo", package_name);
		if (!mofilename) {
			g_free (tmp);
			*err = LDTP_ERROR_UNABLE_TO_ALLOCATE_MEMORY;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
			return;
		}
		g_print ("Checking in %s%s\n", tmp, mofilename);

		if ((stat (tmp, &dir_buf) == 0) && S_ISDIR (dir_buf.st_mode)) {
			mopathfilename = g_strdup_printf ("%s%s", tmp, mofilename);
			if (!mopathfilename) {
				g_free (tmp);
				g_free (mofilename);
				*err = LDTP_ERROR_UNABLE_TO_ALLOCATE_MEMORY;
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
				return;
			}
			g_print ("MO path filename: %s\n", mopathfilename);
			if ((stat (mopathfilename, &dir_buf) == 0) && S_ISREG (dir_buf.st_mode)) {
				folder_found = TRUE;
			}
		}
		if (!folder_found && g_utf8_strchr (tmp, -1, '.')) {
			gchar *stripped_data = strip_delim (tmp, '.');
			g_free (mopathfilename);
			if (!stripped_data) {
				g_free (tmp);
				g_free (mofilename);
				*err = LDTP_ERROR_UNABLE_TO_ALLOCATE_MEMORY;
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
				return;
			}
			g_print ("MO Path sripped: %s\n", stripped_data);
			mopathfilename = g_strdup_printf ("%s%s", stripped_data, mofilename);
			g_free (stripped_data);
			if (!mopathfilename) {
				g_free (tmp);
				g_free (mofilename);
				*err = LDTP_ERROR_UNABLE_TO_ALLOCATE_MEMORY;
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
				return;
			}
			g_print ("MO path filename: %s\n", mopathfilename);
			if ((stat (mopathfilename, &dir_buf) == 0) && S_ISREG (dir_buf.st_mode)) {
				folder_found = TRUE;
				log_msg (LDTP_LOG_INFO, "Folder found", log_fp);
			}
		}
		if (!folder_found && g_utf8_strchr (tmp, -1, '_')) {
			gchar *stripped_data = strip_delim (tmp, '_');
			g_free (mopathfilename);
			if (!stripped_data) {
				g_free (tmp);
				g_free (mofilename);
				*err = LDTP_ERROR_UNABLE_TO_ALLOCATE_MEMORY;
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
				return;
			}
			g_print ("MO Path sripped: %s\n", stripped_data);
			mopathfilename = g_strdup_printf ("%s%s", stripped_data, mofilename);
			g_free (stripped_data);
			if (!mopathfilename) {
				g_free (tmp);
				g_free (mofilename);
				*err = LDTP_ERROR_UNABLE_TO_ALLOCATE_MEMORY;
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
				return;
			}
			g_print ("MO path filename: %s\n", mopathfilename);
			if ((stat (mopathfilename, &dir_buf) == 0) && S_ISREG (dir_buf.st_mode)) {
				folder_found = TRUE;
			}
		}
		g_free (tmp);
		tmp = NULL;
		g_free (mofilename);
		mofilename = NULL;
		if (folder_found) {
			FILE *fp;
			gchar *unformat = NULL;
			gchar *data = NULL;

			log_msg (LDTP_LOG_INFO, mopathfilename, log_fp);
			unformat = g_strdup_printf ("msgunfmt %s -o %s", mopathfilename, file_name);
			g_free (mopathfilename);
			mopathfilename = NULL;
			if (!unformat) {
				*err = LDTP_ERROR_UNABLE_TO_ALLOCATE_MEMORY;
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
				return;
			}
			g_print ("Command: %s\n", unformat);
			fp = popen (unformat, "r");
			if (!fp) {
				g_free (unformat);
				*err = LDTP_ERROR_UNABLE_TO_ALLOCATE_MEMORY;
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
				return;
			}
			data = read_line (fileno (fp), err);
			if (data)
				g_print ("MO unformat command output: %s\n", data);
			g_free (data);
			g_free (unformat);
			pclose (fp);
			log_msg (LDTP_LOG_INFO, "Success", log_fp);
			return;
		}
		g_free (mopathfilename);
	}
}

static void
deletepo (char *filename, FILE *log_fp, LDTPErrorCode *err)
{
	if (unlink (filename) == 0) {
		log_msg (LDTP_LOG_INFO, "Successfully deleted file", log_fp);
		*err = LDTP_ERROR_SUCCESS;
		return;
	}
	else {
		*err = LDTP_ERROR_UNABLE_TO_DELETE_PO;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), log_fp);
		return;
	}
}
#endif

static void
bind_text (LDTPClientContext *cctxt, gchar *mode, LDTPErrorCode* err)
{
#ifdef ENABLE_LOCALIZATION
	gboolean temp_flag;
	gchar *filename = NULL;
	gchar *package_name = cctxt->req->context;
	gchar *locale_dir = cctxt->req->component;

	bindtextdomain (package_name, locale_dir);
	bind_textdomain_codeset (package_name, "UTF-8");
	textdomain (package_name);
	/*
	 * FIXME
	 * Currently only mo files are handled
	 */
	if (g_ascii_strcasecmp (mode, "mo") == 0) {
		filename = g_strdup_printf ("%s/%s-%d.po", g_get_tmp_dir (),
					    package_name, g_random_int_range (G_MININT, G_MAXINT));
		createpo (package_name, locale_dir, filename, mode, cctxt->log_fp, err);
		if (*err != LDTP_ERROR_SUCCESS) {
			*err = LDTP_ERROR_UNABLE_TO_CREATE_PO;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			return;
		}
	}
	else {
		filename = g_strdup_printf ("%s/%s", locale_dir, package_name);
	}
	temp_flag = init_catalog (filename, cctxt->log_fp);
	if (!cctxt->locale_set && temp_flag)
		cctxt->locale_set = temp_flag;
	if (g_ascii_strcasecmp (mode, "mo") == 0)
		deletepo (filename, cctxt->log_fp, err);
	g_free (filename);
#else
	g_print ("Localization option not enabled in LDTP\n");
	*err = LDTP_ERROR_INVALID_COMMAND;
#endif
}

static void
has_state (LDTPClientContext* cctxt,
	   LDTPErrorCode* err)
{
	guint i;
	char *state = NULL;
	long int state_id;
	AccessibleStateSet *state_set;
	guint len = g_slist_length (cctxt->req->arg_list);

	state_set = Accessible_getStateSet (cctxt->gui_handle->handle);

	if (len == 0) {
		*err = LDTP_ERROR_INVALID_STATE;
		goto error;
	}

	for (i = 0; i < len; i++) {
		state = g_slist_nth_data (cctxt->req->arg_list, i);
		if (state) { 
			g_print ("Command: %s\n", state);
			state_id = atol (state);
			g_print ("state_id: %ld\n", state_id);
		}
		else {
			*err = LDTP_ERROR_INVALID_STATE;
			goto error;
		}
		if (state_id == SPI_STATE_INVALID) {
			*err = LDTP_ERROR_INVALID_STATE;
			goto error;
		}
		if (AccessibleStateSet_contains (state_set, state_id) == FALSE) {
			*err = LDTP_ERROR_INVALID_STATE;
			goto error;
		}
	}
	*err = LDTP_ERROR_SUCCESS;
 error:
	AccessibleStateSet_unref (state_set);
	ldtp_gui_free_gui_handle (cctxt->gui_handle);
	cctxt->gui_handle = NULL;
}

static gboolean
remove_app_list_table (gpointer key, gpointer value, gpointer user_data)
{
	g_free (key);
	return TRUE;
}

static void
handle_request (LDTPClientContext* cctxt, 
		Packet* pckt, LDTPErrorCode* err)
{
	static FILE *tmp_fp = NULL;

	LDTPRequest* ldtp_req = NULL;
	//LDTPResponse* ldtp_resp = NULL;
	LDTPGuiHandle* accessible = NULL;

	ldtp_req = cctxt->req;
	ldtp_request_fill_request (ldtp_req, pckt->packet, pckt->len, err);
	if (*err != LDTP_ERROR_SUCCESS) {
		/* FIXME: Error handling */
		return;
	}

	g_print ("Command: %s\n", ldtp_req->action_name);
	ldtp_req->command = atol (ldtp_req->action_name);
	if (ldtp_req->command == LDTP_CMD_INVALID) {
		*err = LDTP_ERROR_INVALID_COMMAND;
		return;
	}
	sleep (1);
	switch (ldtp_req->command) {
	case LDTP_CMD_SETLOCALE:
		if (cctxt->locale_lang)
			g_free (cctxt->locale_lang);
		cctxt->locale_lang = g_strdup (cctxt->req->context);
		cctxt->locale_set = TRUE;
		setlocale (LC_ALL, "");
		return;
	case LDTP_CMD_LAUNCHAPP: {
		GError *error = NULL;
		if (cctxt->req->component && g_ascii_strcasecmp(cctxt->req->component, "1") == 0) {
			g_setenv ("GTK_MODULES", "gail:atk-bridge", TRUE);
			g_setenv ("GNOME_ACCESSIBILITY", "1", TRUE);
		}
		if (cctxt->locale_lang)
			g_setenv ("LANG", cctxt->locale_lang, TRUE);
		if (g_spawn_command_line_async (cctxt->req->context, &error)) {
			// Let us wait so that the application launches
			sleep (5);
		}
		else {
			if (error)
				g_print ("%s\n", error->message);
			*err = LDTP_ERROR_UNABLE_TO_LAUNCH_APP;
		}
		return;
	}
	case LDTP_CMD_SETAPPMAP:
	case LDTP_CMD_INITAPPMAP: {
		char *appmap_filename = NULL;
		appmap_filename = g_slist_nth_data (cctxt->req->arg_list, 0);
		if (!appmap_filename) {
			*err = LDTP_ERROR_OPENING_APPMAP_FILE;
			return;
		}
		g_print ("Appmap file: %s\n", appmap_filename);
		if (cctxt->app_map) {
			ldtp_appmap_free (cctxt->app_map);
			cctxt->app_map = NULL;
		}
		cctxt->app_map = appmap_init (appmap_filename, cctxt->log_fp);
		if (!cctxt->app_map)
			*err = LDTP_ERROR_OPENING_APPMAP_FILE;
		return;
	}

	case LDTP_CMD_LOG: {
		char *log;
		char *mode = "";
		log = (char *)cctxt->req->context;
		if (cctxt->req->component)
			mode = (char *)cctxt->req->component;

		/*
		  If startlog is called only once, let us try to utilize
		  tmp_fp for the rest of connections
		*/
		if (cctxt->log_fp == NULL)
			cctxt->log_fp = tmp_fp;

		if (g_ascii_strcasecmp (mode, "PASS") == 0)
			log_msg (LDTP_LOG_PASS, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "FAIL") == 0)
			log_msg (LDTP_LOG_FAIL, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "ERROR") == 0)
			log_msg (LDTP_LOG_ERROR, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "CAUSE") == 0)
			log_msg (LDTP_LOG_CAUSE, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "COMMENT") == 0)
			log_msg (LDTP_LOG_COMMENT, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "INFO") == 0)
			log_msg (LDTP_LOG_INFO, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "MEMINFO") == 0)
			log_msg (LDTP_LOG_MEMINFO, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "CPUINFO") == 0)
			log_msg (LDTP_LOG_CPUINFO, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "GROUPSTART") == 0)
			log_msg (LDTP_LOG_GROUP_START, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "GROUPSTATUS") == 0)
			log_msg (LDTP_LOG_GROUP_STATUS, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "GROUPEND") == 0)
			log_msg (LDTP_LOG_GROUP_END, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "SCRIPTSTART") == 0)
			log_msg (LDTP_LOG_SCRIPT_START, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "SCRIPTEND") == 0)
			log_msg (LDTP_LOG_SCRIPT_END, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "DATAFILENAME") == 0)
			log_msg (LDTP_LOG_DATA_FILENAME, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "WARNING") == 0)
			log_msg (LDTP_LOG_WARNING, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "TESTSTART") == 0)
			log_msg (LDTP_LOG_TESTSTART, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "TESTCASEID") == 0)
			log_msg (LDTP_LOG_TESTCASEID, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "TESTEND") == 0)
			log_msg (LDTP_LOG_TESTEND, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "BEGIN") == 0)
			log_msg (LDTP_LOG_BEGIN, log, cctxt->log_fp);
		else if (g_ascii_strcasecmp (mode, "END") == 0)
			log_msg (LDTP_LOG_END, log, cctxt->log_fp);
		else
			log_msg (LDTP_LOG_DEBUG, log, cctxt->log_fp); // Default is DEBUG mode
		return;
	}

	case LDTP_CMD_STARTLOG: {
		int overwrite = 1;
		if (cctxt->req->component)
			overwrite = atol ((char *)cctxt->req->component);
		// Open log file
		if (open_log_file ((char *)cctxt->req->context,
				   overwrite == 0 ? LDTP_LOG_FILE_APPEND : LDTP_LOG_FILE_DELETE,
				   &cctxt->log_fp))
			*err = LDTP_ERROR_SUCCESS;
		else
			*err = LDTP_ERROR_OPENING_LOG_FILE;
		tmp_fp = cctxt->log_fp;
		return;
	}

	case LDTP_CMD_STOPLOG:
		close_log_file (&cctxt->log_fp);
		cctxt->log_fp = NULL;
		return;

	case LDTP_CMD_STOPSCRIPTENGINE:
		*err = LDTP_ERROR_STOP_SCRIPT_ENGINE;
		return;

	case LDTP_CMD_GENERATEMOUSEEVENT: {
		long x = 0, y = 0;
		gchar *mode = "b1c";
  
		if (cctxt->req->context)
			x = strtol (cctxt->req->context, NULL, 10);
		if (cctxt->req->component)
			y = strtol (cctxt->req->component, NULL, 10);
		if (cctxt->req->arg_list)
			mode = g_slist_nth_data (cctxt->req->arg_list, 0);
		SPI_generateMouseEvent (x, y, mode);
		return;
	}

	case LDTP_CMD_GENERATEKEYEVENT:
		*err = device_main (cctxt, cctxt->req->command);
		return;

	case LDTP_CMD_SETCONTEXT:
		set_new_context ((char *)cctxt->req->context, (char *)cctxt->req->component);
		return;

	case LDTP_CMD_RELEASECONTEXT:
		release_last_context ();
		return;

	case LDTP_CMD_REINITLDTP: {
		int leaked;
		int  init_error;

		if (cctxt->app_handle) {
			Accessible_unref (cctxt->app_handle);
			cctxt->app_handle = NULL;
		}

		if ((leaked = SPI_exit ())) {
			printf ("Leaked %d SPI handles\n", leaked);
			*err = LDTP_ERROR_UNABLE_TO_REINIT_LDTP;
			return;
		}

		init_error = SPI_init ();

		if (init_error) {
			printf ("Error: SPI Init\n");
			*err = LDTP_ERROR_UNABLE_TO_REINIT_LDTP;
			return;
		}
		*err = LDTP_ERROR_SUCCESS;
		return;
	}

	case LDTP_CMD_GUIEXIST:
		ldtp_gui_gui_exist (cctxt, err);
		return;

	case LDTP_CMD_GUITIMEOUT:
		if (cctxt && cctxt->req && cctxt->req->context) {
			g_print ("GUI Time out: %s\n", cctxt->req->context);
			ldtp_gui_timeout = atoi (cctxt->req->context);
			*err = LDTP_ERROR_SUCCESS;
			return;
		}
		*err = LDTP_ERROR_SET_GUI_TIMEOUT_FAILED;
		return;

	case LDTP_CMD_OBJTIMEOUT:
		if (cctxt && cctxt->req && cctxt->req->context) {
			g_print ("OBJ Time out: %s\n", cctxt->req->context);
			ldtp_obj_timeout = atoi (cctxt->req->context);
			*err = LDTP_ERROR_SUCCESS;
			return;
		}
		*err = LDTP_ERROR_SET_OBJ_TIMEOUT_FAILED;
		return;

	case LDTP_CMD_WAITTILLGUIEXIST:
		ldtp_gui_wait_till_gui_exist (cctxt, err);
		return;

	case LDTP_CMD_WAITTILLGUINOTEXIST:
		ldtp_gui_wait_till_gui_not_exist (cctxt, err);
		return;

	case LDTP_CMD_DOESMENUITEMEXIST:
	case LDTP_CMD_MENUCHECK:
	case LDTP_CMD_MENUUNCHECK:
	case LDTP_CMD_VERIFYMENUCHECK:
	case LDTP_CMD_VERIFYMENUUNCHECK:
	case LDTP_CMD_SELECTMENUITEM:
		if (g_utf8_strchr (ldtp_req->component, -1, ';')) {
			gchar **token = NULL;
			token = g_strsplit (ldtp_req->component, ";", 2);
			gchar *tmp = token [1];
			cctxt->req->arg_list = g_slist_append (cctxt->req->arg_list, 
							       g_strdup (tmp));
			g_free (ldtp_req->component);
			ldtp_req->component = g_strdup (token [0]);
			g_strfreev (token);

			/*
			char *token = NULL;
			char *rest_token = NULL;
			char *rest_params = NULL;

			token = strtok (g_strdup ((gchar *)ldtp_req->component), ";");
			if (!token)
				break;
			
			g_free (ldtp_req->component);
			ldtp_req->component = g_strdup (token);
			rest_token = strtok (NULL, ";");
			while (rest_token) {
				if (!rest_params)
					rest_params  = g_strdup (rest_token);
				else {
					rest_params = g_strconcat (rest_params,
								   ";",
								   rest_token,
								   NULL);
				}
				rest_token = strtok (NULL, ";");
			}
			cctxt->req->arg_list = g_slist_append (cctxt->req->arg_list, 
							       rest_params);
			*/
		}
		break;

	case LDTP_CMD_ONWINDOWCREATE:
		register_window_creation_event (cctxt, err);
		return;

	case LDTP_CMD_REMOVECALLBACK:
		unregister_window_creation_event (cctxt, err);
		return;

	case LDTP_CMD_REMAP:
		if (cctxt->req->component == NULL) {
			update_cur_window_appmap_handle (cctxt, err);
		}
		else {
			update_cur_context_appmap_handle (cctxt, err);
		}
		return;

	case LDTP_CMD_BINDTEXT: {
		gchar *mode = NULL;
  
		if (cctxt->req->arg_list)
			mode = g_slist_nth_data (cctxt->req->arg_list, 0);

		bind_text (cctxt, mode, err);
		return;
	}
	case LDTP_CMD_GETAPPLIST: {
		char *data = NULL;
		GHashTable *table;
		table = get_window_list ();
		if (table) {
			g_hash_table_foreach (table, &add_item_to_list, (gpointer)&data);
			cctxt->resp->data = data;
			if (cctxt->resp->data) {
				char *tmp = NULL;
				/*
				  FRAME the output in XML format
				*/
				tmp = g_strdup_printf ("%s<OBJECTLIST>%s</OBJECTLIST>", XML_HEADER, data);
				if (tmp) {
					g_free (data);
					cctxt->resp->data = tmp;
					g_print ("LIST: %s\n", cctxt->resp->data);
					cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
				}
				else {
					*err = LDTP_ERROR_UNABLE_TO_GET_APPLICATION_LIST;
					g_print ("%s\n", ldtp_error_get_message (*err));
					log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
				}
			}
			else {
				*err = LDTP_ERROR_UNABLE_TO_GET_APPLICATION_LIST;
				g_print ("%s\n", ldtp_error_get_message (*err));
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			}
			g_hash_table_foreach_remove (table, remove_app_list_table, NULL);
		}
		else {
			*err = LDTP_ERROR_UNABLE_TO_GET_APPLICATION_LIST;
			g_print ("%s - %s\n", __FILE__, ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
		}
		return;
	}
	case LDTP_CMD_GETWINDOWLIST: {
		if (cctxt->app_map) {
			char *data = NULL;
			/*
			  If appliction map is not initialized for new windows,
			  then call to update_window_list will get those windows too
			  NOTE: update_window_list will fail if none of the applications
			  has been accessed, ie., atleast one component function has
			  to be called in one of the current running application 
			*/
			g_hash_table_foreach (cctxt->app_map, &add_item_to_list, (gpointer)&data);
			cctxt->resp->data = data;
			if (cctxt->resp->data) {
				char *tmp = NULL;
				/*
				  FRAME the output in XML format
				*/
				tmp = g_strdup_printf ("%s<OBJECTLIST>%s</OBJECTLIST>", XML_HEADER, data);
				if (tmp) {
					g_free (data);
					cctxt->resp->data = tmp;
					g_print ("LIST: %s\n", cctxt->resp->data);
					cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
				}
				else {
					*err = LDTP_ERROR_UNABLE_TO_GET_OBJECT_LIST;
					g_print ("%s\n", ldtp_error_get_message (*err));
					log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
				}
			}
			else {
				*err = LDTP_ERROR_UNABLE_TO_GET_OBJECT_LIST;
				g_print ("%s\n", ldtp_error_get_message (*err));
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			}
		}
		else {
			*err = LDTP_ERROR_APPMAP_NOT_INITIALIZED;
			g_print ("%s - %s\n", __FILE__, ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
		}
		return;
	}
	case LDTP_CMD_GETOBJECTLIST: {
		char *data = NULL;
		GHashTable *ht = NULL;

		if (!cctxt->req->context) {
			*err = LDTP_ERROR_ARGUMENT_NULL;
			g_print ("%s\n", ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			return;
		}
		if (!cctxt->app_map) {
                        /* if appmap not already initialised, do it now */
                        accessible = ldtp_gui_get_gui_handle (cctxt, err);
                        ldtp_gui_free_gui_handle (accessible);
                        if (*err != LDTP_ERROR_SUCCESS) {
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
                                return;
                        }
		}
		ht = get_object_def (cctxt->app_map, (char *)cctxt->req->context, cctxt->log_fp, TRUE);
		if (!ht) {
			update_cur_window_appmap_handle (cctxt,
							 err);
			ht = get_object_def (cctxt->app_map, (char *)cctxt->req->context, cctxt->log_fp, TRUE);
			if (*err != LDTP_ERROR_SUCCESS) {
				g_print ("Unable to update context: %s in appmap", (char *)cctxt->req->context);
				return;
			}
		}
		if (!ht) {
			g_print ("Unable to find context\n");
			*err = LDTP_ERROR_UNABLE_TO_GET_CONTEXT_HANDLE;
			g_print ("%s\n", ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			return;
		}
		g_hash_table_foreach (ht, &add_item_to_list, (gpointer)&data);
		cctxt->resp->data = data;
		if (cctxt->resp->data) {
			char *tmp = NULL;
			/*
			  FRAME the output in XML format
			*/
			tmp = g_strdup_printf ("%s<OBJECTLIST>%s</OBJECTLIST>", XML_HEADER, data);
			if (tmp) {
				g_free (data);
				cctxt->resp->data = tmp;
				g_print ("LIST: %s\n", cctxt->resp->data);
				cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
			}
			else {
				*err = LDTP_ERROR_UNABLE_TO_GET_OBJECT_LIST;
				g_print ("%s\n", ldtp_error_get_message (*err));
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			}
		}
		else {
			*err = LDTP_ERROR_UNABLE_TO_GET_OBJECT_LIST;
			g_print ("%s\n", ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
		}
		return;
	}
	case LDTP_CMD_GETCHILD: {
		char *data = NULL;
		char *name = cctxt->req->component;
		char *role = NULL;
		MatchingList list;
		GHashTable *context_ht = NULL;

		if (!cctxt->req->context) {
			*err = LDTP_ERROR_ARGUMENT_NULL;
			g_print ("%s %s %d\n", ldtp_error_get_message (*err), __FILE__, __LINE__);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			return;
		}
		if (!cctxt->app_map) {
                        /* if appmap not already initialised, do it now */
                        accessible = ldtp_gui_get_gui_handle (cctxt, err);
                        ldtp_gui_free_gui_handle (accessible);
                        if (*err != LDTP_ERROR_SUCCESS) {
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
                                return;
                        }
		}
		context_ht = get_object_def (cctxt->app_map, (char *)cctxt->req->context, cctxt->log_fp, TRUE);
		if (!context_ht) {
			update_cur_window_appmap_handle (cctxt,
							 err);
			context_ht = get_object_def (cctxt->app_map, (char *)cctxt->req->context, cctxt->log_fp, TRUE);
			if (*err != LDTP_ERROR_SUCCESS) {
				g_print ("Unable to update context: %s in appmap", (char *)cctxt->req->context);
				return;
			}
		}
		if (!context_ht) {
			g_print ("Unable to find context\n");
			*err = LDTP_ERROR_UNABLE_TO_GET_CONTEXT_HANDLE;
			g_print ("%s\n", ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			return;
		}
		role = g_slist_nth_data (cctxt->req->arg_list, 0);
		list.data = data;
		list.name = name == NULL ? NULL : g_utf8_collate (name,
								  cctxt->req->context) == 0 ? NULL : name;
		list.role = role;
		g_hash_table_foreach (context_ht, &add_matching_item_to_list, (gpointer) &list);
		cctxt->resp->data = list.data;
		if (cctxt->resp->data) {
			char *tmp = NULL;
			/*
			  FRAME the output in XML format
			*/
			tmp = g_strdup_printf ("%s<OBJECTLIST>%s</OBJECTLIST>", XML_HEADER, cctxt->resp->data);
			if (tmp) {
				g_free (cctxt->resp->data);
				cctxt->resp->data = tmp;
				if (ldtp_debug)
					g_print ("LIST: %s\n", tmp);
				cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
			}
			else {
				g_free (cctxt->resp->data);
				*err = LDTP_ERROR_UNABLE_TO_GET_CHILD_WITH_PROVIDED_ROLE;
				g_print ("%s\n", ldtp_error_get_message (*err));
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			}
		}
		else {
			*err = LDTP_ERROR_UNABLE_TO_GET_CHILD_WITH_PROVIDED_ROLE;
			g_print ("%s\n", ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
		}
		return;
	}
	case LDTP_CMD_GETOBJECTINFO: {
		char *data = NULL;
		GHashTable *context_ht = NULL;
		GHashTable *component_ht = NULL;

		if (!cctxt->req->context || !cctxt->req->component) {
			*err = LDTP_ERROR_ARGUMENT_NULL;
			g_print ("%s\n", ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			return;
		}
		if (!cctxt->app_map) {
                        /* if appmap not already initialised, do it now */
                        accessible = ldtp_gui_get_gui_handle (cctxt, err);
                        ldtp_gui_free_gui_handle (accessible);
                        if (*err != LDTP_ERROR_SUCCESS) {
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
                                return;
                        }
		}
		context_ht = get_object_def (cctxt->app_map, (char *)cctxt->req->context, cctxt->log_fp, TRUE);
		if (!context_ht) {
			update_cur_window_appmap_handle (cctxt,
							 err);
			context_ht = get_object_def (cctxt->app_map, (char *)cctxt->req->context, cctxt->log_fp, TRUE);
			if (*err != LDTP_ERROR_SUCCESS) {
				g_print ("Unable to update context: %s in appmap", (char *)cctxt->req->context);
				return;
			}
		}
		if (!context_ht) {
			g_print ("Unable to find context\n");
			*err = LDTP_ERROR_UNABLE_TO_GET_CONTEXT_HANDLE;
			g_print ("%s\n", ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			return;
		}
		component_ht = get_object_def (context_ht, (char *)cctxt->req->component, cctxt->log_fp, FALSE);
		if (!component_ht) {
			update_cur_window_appmap_handle (cctxt,
							 err);
			context_ht = get_object_def (cctxt->app_map, (char *)cctxt->req->context,
						     cctxt->log_fp, TRUE);
			if (context_ht)
				component_ht = get_object_def (context_ht, (char *)cctxt->req->component,
							       cctxt->log_fp, FALSE);
			if (!component_ht) {
				g_print ("Unable to find component\n");
				*err = LDTP_ERROR_UNABLE_TO_GET_COMPONENT_HANDLE;
				g_print ("%s\n", ldtp_error_get_message (*err));
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
				return;
			}
		}
		g_hash_table_foreach (component_ht, &add_item_to_list, (gpointer)&data);
		cctxt->resp->data = data;
		if (cctxt->resp->data) {
			char *tmp = NULL;
			/*
			  FRAME the output in XML format
			*/
			tmp = g_strdup_printf ("%s<OBJECTLIST>%s</OBJECTLIST>", XML_HEADER, data);
			if (tmp) {
				g_free (data);
				cctxt->resp->data = tmp;
				g_print ("LIST: %s\n", cctxt->resp->data);
				cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
			}
			else {
				*err = LDTP_ERROR_UNABLE_TO_GET_OBJECT_LIST;
				g_print ("%s\n", ldtp_error_get_message (*err));
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			}
		}
		else {
			*err = LDTP_ERROR_UNABLE_TO_GET_OBJECT_LIST;
			g_print ("%s\n", ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
		}
		return;
	}

	case LDTP_CMD_GETOBJECTPROPERTY: {
		char *property = NULL;
		char *obj_property = NULL;
		GHashTable *context_ht = NULL;
		GHashTable *component_ht = NULL;

		if (!cctxt->req->context || !cctxt->req->component) {
			*err =  LDTP_ERROR_ARGUMENT_NULL;
			g_print ("%s\n", ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			return;
		}
		if (!cctxt->app_map) {
                        /* if appmap not already initialised, do it now */
                        accessible = ldtp_gui_get_gui_handle (cctxt, err);
                        ldtp_gui_free_gui_handle (accessible);
                        if (*err != LDTP_ERROR_SUCCESS) {
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
                                return;
                        }
		}
		context_ht = get_object_def (cctxt->app_map, (char *)cctxt->req->context, cctxt->log_fp, TRUE);
		if (!context_ht) {
			update_cur_window_appmap_handle (cctxt,
							 err);
			context_ht = get_object_def (cctxt->app_map, (char *)cctxt->req->context, cctxt->log_fp, TRUE);
			if (*err != LDTP_ERROR_SUCCESS) {
				g_print ("Unable to update context: %s in appmap", (char *)cctxt->req->context);
				return;
			}
		}
		if (!context_ht) {
			g_print ("Unable to find context\n");
			*err = LDTP_ERROR_UNABLE_TO_GET_CONTEXT_HANDLE;
			g_print ("%s\n", ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			return;
		}
		component_ht = get_object_def (context_ht, (char *)cctxt->req->component,
					       cctxt->log_fp, FALSE);
		if (!component_ht) {
			update_cur_window_appmap_handle (cctxt,
							 err);
			context_ht = get_object_def (cctxt->app_map, (char *)cctxt->req->context,
						     cctxt->log_fp, TRUE);
			if (context_ht)
				component_ht = get_object_def (context_ht, (char *)cctxt->req->component,
							       cctxt->log_fp, TRUE);
			if (!component_ht) {
				g_print ("Unable to find component\n");
				*err = LDTP_ERROR_UNABLE_TO_GET_COMPONENT_HANDLE;
				g_print ("%s\n", ldtp_error_get_message (*err));
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
				return;
			}
		}
		property = g_slist_nth_data (cctxt->req->arg_list, 0);
		obj_property = get_property (component_ht, property, cctxt->log_fp);
		if (!obj_property) {
			g_print ("Unable to find property\n");
			*err = LDTP_ERROR_UNABLE_TO_GET_PROPERTY;
			g_print ("%s\n", ldtp_error_get_message (*err));
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
			return;
		}
		cctxt->resp->data = g_strdup (obj_property);
		cctxt->resp->data_len = g_utf8_strlen (obj_property, -1);
		return;
	}
	}

	/* 
	   1)  Get the Accessible object corresponding to "component-name".
	   2)  Get the class-id and
	   3)  Call the corresponding component main function with necessary
	   arguments.
	*/

	accessible = ldtp_gui_get_gui_handle (cctxt, err);
	if (*err != LDTP_ERROR_SUCCESS) {
		/* FIXME: Error handling */
		g_print ("Unable to get handle\n");
		return;
	} else {
		char *name;
		name = Accessible_getRoleName (accessible->handle);
		if (name) {
			g_print ("Got gui handle - %s\n", name);
			SPI_freeString (name);
		}
	}

	/* Update the gui handle in the context */
	cctxt->gui_handle = accessible;

	if (cctxt->req->command == LDTP_CMD_HASSTATE) {
		has_state (cctxt, err);
		return;
	}

	switch (cctxt->gui_handle->class_id) {
	case SPI_ROLE_COMBO_BOX:
		*err = combo_box_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_CHECK_BOX:
		*err = check_box_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_CHECK_MENU_ITEM:
		*err = check_menu_item_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_RADIO_BUTTON:
		*err = radio_button_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_RADIO_MENU_ITEM:
		*err = radio_menu_item_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_PUSH_BUTTON:
		*err = push_button_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_TOGGLE_BUTTON:
		*err = toggle_button_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_EMBEDDED:
		*err = embedded_component_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_LIST:
		*err = list_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_TEXT:
#ifdef ENABLE_NEWROLES
	case SPI_ROLE_ENTRY:
#endif
	case SPI_ROLE_EDITBAR:
	case SPI_ROLE_PARAGRAPH:
	case SPI_ROLE_AUTOCOMPLETE:
	case SPI_ROLE_PASSWORD_TEXT:
		*err = text_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_PANEL:
		*err = panel_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_ICON:
		*err = icon_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_LAYERED_PANE:
		*err = layered_pane_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_LABEL:
		*err = label_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_MENU:
		*err = menu_main (cctxt, cctxt->req->command,
				  (gchar *)ldtp_req->context);
		break;

	case SPI_ROLE_MENU_ITEM:
		*err = menu_item_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_PAGE_TAB_LIST:
		*err = page_tab_list_main (cctxt, cctxt->req->command);
		break;

	case CALENDAR_VIEW:
		*err = calendar_view_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_CALENDAR:
		*err = calendar_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_SPIN_BUTTON:
		*err = spin_button_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_TABLE:
		*err = table_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_TREE:
	case SPI_ROLE_TREE_TABLE:
		*err = tree_table_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_SCROLL_BAR:
		*err = scroll_bar_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_SCROLL_PANE:
		*err = scroll_pane_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_SLIDER:
		*err = slider_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_STATUS_BAR:
		*err = status_bar_main (cctxt, cctxt->req->command);
		break;

	case SPI_ROLE_TOOL_BAR:
		*err = tool_bar_main (cctxt, cctxt->req->command);
		break;
	default:
		if (cctxt->req->command == LDTP_CMD_KBDENTER) {
			*err = device_main (cctxt, cctxt->req->command);
			break;
		}
		else if (cctxt->req->command == LDTP_CMD_GRABFOCUS) {
			AccessibleComponent *accessibleComponent = Accessible_getComponent (cctxt->gui_handle->handle);
			if (accessibleComponent && cctxt->req->context) {
				g_print ("Window: %s - GrabFocus\n", cctxt->req->context);
				if (AccessibleComponent_grabFocus (accessibleComponent) == TRUE)
					*err = LDTP_ERROR_SUCCESS;
				else
					*err = LDTP_ERROR_UNABLE_TO_GRAB_FOCUS;
				Accessible_unref (accessibleComponent);
				break;
			}
			*err = LDTP_ERROR_UNABLE_TO_GRAB_FOCUS;
			break;
		}
		*err = LDTP_ERROR_ROLE_NOT_IMPLEMENTED;
		g_print ("Role not implemented: %s %d", __FILE__, __LINE__);
		break;
	}

	/* Need to update cctxt->resp with appropriate status_code and data.
	   For this, we have to have a switch case on command-id, because
	   not all commands return data.
	*/
	ldtp_gui_free_gui_handle (cctxt->gui_handle);
}

void *
handle_client (void *ptr)
{
	int* sock_fd = (int *)ptr;
	char* packet = NULL;
	char* tmpptr = NULL;
	uint32_t packet_len;
	uint32_t packet_read;
	uint32_t pckt_len = 0;
	uint32_t i = 0;
	size_t bytes_read  = 0;
	uint32_t resp_size = 0;
	char *resp_pckt = NULL;

	LDTPErrorCode status;

	LDTPClientContext *cctxt = NULL;
	Packet *pckt = NULL;

	cctxt = g_new0 (LDTPClientContext, 1);
	cctxt->app_map = NULL;
	cctxt->app_handle = NULL;
	cctxt->req = g_new0 (LDTPRequest, 1);
	ldtp_request_init (cctxt->req);
	cctxt->resp = g_new0 (LDTPResponse, 1);
	cctxt->resp->data = NULL;
	cctxt->sock_fd = *sock_fd;
	cctxt->log_fp = NULL;
	cctxt->locale_set = FALSE;

	while (1) {
		packet_len = 0;
		ldtp_read_sizet (*sock_fd, &packet_len, &status);
		if (status != LDTP_ERROR_SUCCESS) {
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (status), cctxt->log_fp);
			goto error;
		}

		packet_len = ntohl (packet_len);
		g_print ("Client packet len: %d\n", packet_len);

		if (packet_len <= 0) {
			status = LDTP_ERROR_PACKET_INVALID;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (status), cctxt->log_fp);
			goto error;
		}

		packet = g_malloc0 (packet_len + 1);
		tmpptr = packet;

		pckt_len = packet_len;
		packet_read = 0;
		while (pckt_len > 0) {
			g_print ("i = %d\n", i);
			pckt_len = pckt_len > 512 ? 512 : pckt_len;
			ldtp_read_data (*sock_fd, packet, pckt_len, 
					&bytes_read, &status);
			if (status != LDTP_ERROR_SUCCESS) {
				/*
				  FIXME:
				  ldtp_log ("Connection: closed [%s:%d]\n", 
				  client->ip_address, client->socketfd);
				*/
				g_print ("Client data read error\n");
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (status), cctxt->log_fp);
				goto error;
			}

			if (packet)
				g_print ("Data read %d, packet-len = %d, bytes read = %ld, data: %s\n", 
					 pckt_len, packet_len, bytes_read, packet);
			packet += bytes_read;
			packet_read += bytes_read;
			pckt_len = packet_len - packet_read;
			g_print ("PACKET LENGTH: %d\n", pckt_len);
			if (pckt_len <= 0 || bytes_read == 0)
				break;
		}
		packet = tmpptr;

		if (packet)
			g_print ("Received packet [%s] through %d\n", packet, *sock_fd);

		pckt = g_new0 (Packet, 1);
		pckt->packet = packet;
		pckt->len = packet_len;

		handle_request (cctxt, pckt, &status);
		if (status == LDTP_ERROR_STOP_SCRIPT_ENGINE) {
			goto error;
		}

		if (packet)
			g_free (packet);
		packet = NULL;

		if (pckt)
			g_free (pckt);
		pckt = NULL;

		cctxt->resp->resp_status = status;
		generate_response_packet (cctxt, &status, &resp_pckt, &resp_size);
		if (status != LDTP_ERROR_SUCCESS) {
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (status), cctxt->log_fp);
			g_print ("Error generating response\n");
			goto error;
		}

		send_response (cctxt->sock_fd, resp_pckt, resp_size, &status);
		if (status != LDTP_ERROR_SUCCESS) {
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (status), cctxt->log_fp);
			g_print ("Error sending response\n");
			goto error;
		}

		g_free (resp_pckt);
		if (cctxt->resp->data) {
			g_free (cctxt->resp->data);
			cctxt->resp->data = NULL;
		}
		cctxt->resp->data_len = 0;
	}
 error:
	g_print ("handle_client: error:\n");
	cctxt->resp->resp_status = status;
	if (cctxt->window_name) {
		g_free (cctxt->window_name);
		cctxt->window_name = NULL;
	}

	if (status != LDTP_ERROR_CLIENT_DISCONNECTED) {
		generate_response_packet (cctxt, &status, &resp_pckt, &resp_size);
		if (status != LDTP_ERROR_SUCCESS) {
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (status), cctxt->log_fp);
			g_print ("Error generating response\n");
		} else {
			send_response (cctxt->sock_fd, resp_pckt, resp_size, &status);
			if (status != LDTP_ERROR_SUCCESS) {
				log_msg (LDTP_LOG_CAUSE, "", cctxt->log_fp);
				g_print ("Error sending response **\n");
			}
			if (resp_pckt)
				g_free (resp_pckt);
		}
	}

	pthread_mutex_lock (&cb_mutex);
	unregister_window_creation_event (cctxt, &status);

	close_connection (*sock_fd);

	if (packet)
		g_free (packet);

	if (sock_fd)
		g_free (sock_fd);

	if (pckt)
		g_free (pckt);
	if (cctxt->app_handle) {
		/*	
		  FIXME: If the server closes connection, before the client closes connection,
		  then we get 1 SPI handle leak. Should be handled.
		*/
		Accessible_unref (cctxt->app_handle);
		cctxt->app_handle = NULL;
	}

	if (client_context) {
		guint count = g_hash_table_foreach_remove (client_context, is_cctxt_registered_callback, cctxt);
		g_print ("Removed %d entries from client context hash table\n", count);
	}

	ldtp_appmap_free (cctxt->app_map);
	if (cctxt && cctxt->resp)
		status = cctxt->resp->resp_status;
	else
		status = LDTP_ERROR_PACKET_INVALID;

	g_free (cctxt->req);
	cctxt->req = NULL;
	g_free (cctxt->resp);
	cctxt->resp = NULL;
	g_free (cctxt->locale_lang);
	g_free (cctxt);
	cctxt = NULL;
	pthread_mutex_unlock (&cb_mutex);

	if (status == LDTP_ERROR_STOP_SCRIPT_ENGINE) {
		cleanup (0);
	}
	pthread_exit ((void *) 1);
}
