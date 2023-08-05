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

#include "ldtp.h"
#include "ldtp-gui.h"
#include "ldtp-appmap.h"
#include "remap.h"
#include "ldtp-server.h"
#include "ldtp-utils.h"
#include "client-handler.h"
#include "ldtp-error.h"
#include "ldtp-logger.h"

#ifndef ENABLE_GOPTIONPARSE
#include <getopt.h>
#endif

gint ldtp_script_port = 0;
gint ldtp_gui_timeout = 0;
gint ldtp_obj_timeout = 0;
gboolean ldtp_debug   = FALSE;
static gboolean ldtp_usage   = FALSE;
static gboolean ldtp_version = FALSE;
gboolean ldtp_script_service = FALSE;
gboolean ldtp_external_xml_file = TRUE;
GHashTable *event_notifier = NULL;
GHashTable *client_context = NULL;
GHashTable *client_thread_pool = NULL;
static AccessibleEventListener *window_listener;
pthread_mutex_t cb_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t client_thread_pool_mutex = PTHREAD_MUTEX_INITIALIZER;

#ifdef ENABLE_GOPTIONPARSE
static GOptionEntry entries [] = 
	{
		{ "gui-timeout", 'g', 0, G_OPTION_ARG_INT, &ldtp_gui_timeout, "Wait gui to appear / disappear till N seconds", "N" },
		{ "no-external-xml-file", 'n', 0, G_OPTION_ARG_NONE, &ldtp_external_xml_file, "Don't use external temp XML file", NULL },
		{ "obj-timeout", 'o', 0, G_OPTION_ARG_INT, &ldtp_obj_timeout, "Wait object to appear till N seconds", "N" },
		{ "port", 'p', 0, G_OPTION_ARG_INT, &ldtp_script_port, "Start LDTP scripting engine on TCP port", "N" },
		{ "script-engine", 's', 0, G_OPTION_ARG_NONE, &ldtp_script_service, "Start LDTP script execution engine as TCP service", NULL },
		{ "usage", 'u', 0, G_OPTION_ARG_NONE, &ldtp_usage, "LDTP engine usage", NULL },
		{ "verbose", 'v', 0, G_OPTION_ARG_NONE, &ldtp_debug, "Verbose mode", NULL },
		{ "version", 'V', 0, G_OPTION_ARG_NONE, &ldtp_version, "LDTP engine version", NULL },
		{ NULL }
	};
#endif

static LDTPClientContext*
is_window_reg_for_events (char *context)
{
	LDTPClientContext *cctxt = NULL;
	if (event_notifier) {
		cctxt = g_hash_table_find (event_notifier, search_title_based, context);
		if (cctxt && context && cctxt->req && cctxt->req->context)
			g_print ("Registered window title: %s - %s\n", context, cctxt->req->context);
	}
	return cctxt;
}

static LDTPClientContext*
is_window_in_cctxt (char *window_name)
{
	LDTPClientContext *cctxt = NULL;
	if (client_context) {
		cctxt = g_hash_table_find (client_context, search_title_based, window_name);
		if (cctxt && window_name)
			g_print ("Registered window title: %s\n", window_name);
	}
	return cctxt;
}

static void
report_window_event  (const AccessibleEvent *event, void *user_data)
{
	g_print ("Event type: %s\n", event->type);
	if (event_notifier && g_ascii_strcasecmp ("window:create", event->type) == 0) {
		uint32_t resp_size = 0;
		LDTPErrorCode status;
		char *resp_pckt = NULL;
		char *window_name = NULL;
		LDTPClientContext *cctxt = NULL;

		char *context = Accessible_getName (event->source);
		char *title = AccessibleWindowEvent_getTitleString (event);
		if (!title) {
			if (context)
				SPI_freeString (context);
			return;
		}
		pthread_mutex_lock (&cb_mutex);
		if ((cctxt = is_window_reg_for_events (title))) {
			/*
			  Notify to client
			*/
			if (!cctxt || !cctxt->resp) {
				g_print ("CCTXT is lost\n");
				pthread_mutex_unlock (&cb_mutex);
				return;
			}
			cctxt->resp->data = g_strdup (title);
			cctxt->resp->data_len = g_utf8_strlen (title, -1);
			cctxt->resp->resp_status = LDTP_ERROR_SUCCESS;

			generate_notification_packet (cctxt, &status, &resp_pckt, &resp_size);
			if (status != LDTP_ERROR_SUCCESS) {
				g_print ("Error generating notification\n");
				pthread_mutex_unlock (&cb_mutex);
				return;
			}
			if (resp_pckt)
				g_print ("Notification: %s - Len - %d", resp_pckt, resp_size);
			send_response (cctxt->sock_fd, resp_pckt, resp_size, &status);
			g_free (cctxt->resp->data);
			cctxt->resp->data = NULL;
			pthread_mutex_unlock (&cb_mutex);
			return;
		}
		/*
		  If window title is used in old appmap format (like dlgFind), then use the following approach
		*/
		window_name = get_window_name_in_appmap_format (title, Accessible_getRole (event->source));
		if (window_name && is_window_reg_for_events (window_name)) {
			/*
			  Notify to client
			*/
			if (window_name)
				g_free (window_name);
			cctxt->resp->resp_status = LDTP_ERROR_SUCCESS;

			generate_notification_packet (cctxt, &status, &resp_pckt, &resp_size);
			if (status != LDTP_ERROR_SUCCESS) {
				g_print ("Error generating notification\n");
				pthread_mutex_unlock (&cb_mutex);
				return;
			}

			g_print ("Notification: %s - Len - %d", resp_pckt, resp_size);
			send_response (cctxt->sock_fd, resp_pckt, resp_size, &status);
			pthread_mutex_unlock (&cb_mutex);
			return;
		}
		if (window_name)
			g_free (window_name);
		pthread_mutex_unlock (&cb_mutex);
		SPI_freeString (context);
		SPI_freeString (title);
	} else if (g_ascii_strcasecmp ("window:destroy", event->type) == 0) {
		LDTPClientContext *cctxt = NULL;
		char *title = AccessibleWindowEvent_getTitleString (event);
		char *window_name;
		if (!title) {
			g_print ("Window title NULL\n");
			return;
		}
		window_name = get_window_name_in_appmap_format (title, Accessible_getRole (event->source));
		if (window_name) {
			g_print ("Window name: %s - %s\n", window_name, title);
			pthread_mutex_lock (&cb_mutex);
			cctxt = is_window_in_cctxt (window_name);
			if (cctxt) {
				GHashTable *context = NULL;
				if (cctxt->app_map)
					context = g_hash_table_lookup (cctxt->app_map, window_name);
				if (context) {
					g_hash_table_foreach_remove (context, (GHRFunc)&remove_context_entries, context);
					g_hash_table_destroy (context);
					g_hash_table_remove (cctxt->app_map, window_name);
					context = NULL;
				}
			}
			pthread_mutex_unlock (&cb_mutex);
		}
		SPI_freeString (title);
	}
}

static void
signal_all_threads (gpointer key, gpointer value, gpointer userdata)
{
	if (value)
		pthread_kill ((pthread_t) value, SIGKILL);
}

void
cleanup (int mysig)
{
	int leaked;
	char *tmpfile = NULL;

	leaked = SPI_exit ();
	if (leaked)
		printf ("Leaked %d SPI handles\n", leaked);

	pthread_mutex_lock (&client_thread_pool_mutex);
	g_hash_table_foreach (client_thread_pool, signal_all_threads, NULL);
	client_thread_pool = NULL;
	pthread_mutex_unlock (&client_thread_pool_mutex);
	/*
	  Close server socket
	*/
	close_connection (get_server_socket (LDTP_SCRIPT_SERVER));

	if (ldtp_script_service)
		goto quit;

	tmpfile = get_tmp_file (LDTP_SCRIPT_SERVER);
	if (tmpfile) {
		/*
		  Remove tmp file
		*/
		unlink (tmpfile);
		g_free (tmpfile);
	}
 quit:
	/*
	  Quit from main SPI event loop
	*/
	SPI_event_quit ();
}

static void 
accept_connection (int listener, LDTPErrorCode* err)
{
	struct sockaddr_in remoteaddr;
	socklen_t addrlen;
	int newfd;
	pthread_t client_thread = 0;
	int* newfd_dup = NULL;
	int retval;
  
	/* handle new connections */
	addrlen = sizeof (remoteaddr);
	newfd = accept (listener, (struct sockaddr *) &remoteaddr, 
			&addrlen);
  
	if (newfd == -1) {
		ldtp_log("ERROR:accept() failed with \"%s\"\n", strerror(errno));
		*err = LDTP_ERROR_ACCEPT_FAILED;
		goto error;
	}

	ldtp_log ("Client connection: accepted\n");

	newfd_dup = malloc (sizeof (newfd));
	*newfd_dup = newfd;
	retval = pthread_create (&client_thread, NULL, &handle_client, 
				 (void *)newfd_dup);
	if (retval == EAGAIN) {
		/* unable to create threads... kindly retry... */
		ldtp_log ("%s:%d: Unable to create client_threads. "
			  "Disconnecting the client.\n", __FILE__, __LINE__);
		close_connection (newfd);
		*err = LDTP_ERROR_THREAD_CREATION_FAILED;
		goto error;
	}
	else {
		char fd [15];
		/* parent process */
		pthread_mutex_lock (&client_thread_pool_mutex);
		sprintf (fd, "%d", newfd);
		g_hash_table_insert (client_thread_pool, g_strdup (fd), NULL);
		pthread_mutex_unlock (&client_thread_pool_mutex);
		*err = LDTP_ERROR_SUCCESS;
		return;
	}

 error:
	if (newfd_dup)
		free (newfd_dup);
	return;
}

static gboolean
is_fd_in_client_pool (gpointer key,
		      gpointer value,
		      gpointer user_data)
{
	if (key && user_data) {
		if (g_utf8_collate (key, user_data) == 0)
			return TRUE;
	}
	return FALSE;
}

void 
close_connection (int fd)
{
	if (client_thread_pool) {
		char tmpfd [15];
		pthread_mutex_lock (&client_thread_pool_mutex);
		sprintf (tmpfd, "%d", fd);
		g_print ("Removing sockfd: %s - %u\n", tmpfd, g_hash_table_size (client_thread_pool));
		g_hash_table_foreach_remove (client_thread_pool, (GHRFunc)&is_fd_in_client_pool, tmpfd);
		g_print ("Removed sockfd: %s - %u\n", tmpfd, g_hash_table_size (client_thread_pool));
		pthread_mutex_unlock (&client_thread_pool_mutex);
	} else
		g_print ("Client thread pool not initalized\n");

	close (fd);
}

static void 
init_pollfd (int fd, struct pollfd *pfd, LDTPErrorCode *err)
{
	if (pfd == NULL) {
		*err = LDTP_ERROR_ARGUMENT_NULL;
		return;
	}

	pfd->fd = fd;
	pfd->events = POLLIN;

	if (!client_thread_pool) {
		pthread_mutex_lock (&client_thread_pool_mutex);
		client_thread_pool = g_hash_table_new_full (&g_str_hash, &g_str_equal, &key_destroy_func, NULL);
		pthread_mutex_unlock (&client_thread_pool_mutex);
	}
	*err = LDTP_ERROR_SUCCESS;
}

static void *
ldtp_server_thread (void *ptr)
{
	struct pollfd pfd;
	int server_socket;
	int client_update_flag;
	int time_out = -1;
	LDTPErrorCode err;

	if (!ldtp_script_service) {
		time_out = 1000 * 60 * 5; // Wait max of 5 minutes, if no clients then quit
	}
	server_socket = init_ldtp_server (LDTP_SCRIPT_SERVER);

	init_pollfd (server_socket, &pfd, &err);
	if (err != LDTP_ERROR_SUCCESS) {
		/* 
		   1) Close the server
		   2) Inform SPI_Main() to close, in some way
		   may be SPI_Quit()?
		*/
		close_connection (server_socket);
		pthread_exit ((void *) 1);
	}

	while (1) {
		if (poll (&pfd, 1, time_out) == -1) {
			if (errno == EINTR) {
				continue;
			}
			else if (errno != EBADF && errno != EFAULT && errno != EINVAL && errno != ENOMEM) {
				ldtp_log ("%d:Continuing\n", getpid ());
				exit (1);
			}
			else {
				ldtp_log ("%d:Exiting : %s\n", getpid (), strerror (errno));
				exit (1);
			}
		}
		client_update_flag = 0;
		if ((pfd.revents & POLLIN) && (pfd.fd == server_socket)) {
			accept_connection (server_socket, &err);
			if (err != LDTP_ERROR_SUCCESS)
				ldtp_log ("******Unable to accept connection*******\n");
			continue;
		} // if check for all fds
		if (client_thread_pool) {
			guint size;
			pthread_mutex_lock (&client_thread_pool_mutex);
			size = g_hash_table_size (client_thread_pool);
			if (ldtp_debug && size)
				g_print ("Clients: %d\n", size);
			if (size == 0) {// Let us break
				pthread_mutex_unlock (&client_thread_pool_mutex);
				cleanup (0);
				break;
			}
			pthread_mutex_unlock (&client_thread_pool_mutex);
		}
	} // while loop forever
	pthread_exit ((void *) 0);
}

static void
ldtp_print (const char *string) 
{
	char *env_ldtp_debug = getenv ("LDTP_DEBUG");
	if (ldtp_debug || (env_ldtp_debug != NULL && g_ascii_strcasecmp (env_ldtp_debug, "2") == 0))
		printf ("%s", string);
}

int
main (int argc, char **argv)
{
	int retval;
	int spi_init;
	LDTPErrorCode err;
	GError *error = NULL;
	char *env_sleep = NULL;
	pthread_t server_thread = 0;
	struct rlimit resource_limit;

#ifdef ENABLE_GOPTIONPARSE
	GOptionContext *context = NULL;

	context = g_option_context_new ("- Linux Desktop Testing Project engine");
	g_option_context_add_main_entries (context, entries, NULL);
	if (g_option_context_parse (context, &argc, &argv, &error) == FALSE) {
		g_print ("%s\n", error->message);
		printf ("Usage help:\n\tldtp --help\n\tldtp --usage\n");
		g_error_free (error);
		g_option_context_free (context);
		exit (1);
	}
	g_option_context_free (context);
#else
	int c;

	while (1) {
		static struct option long_options [] = {
			/* These options set a flag. */
			{"gui-timeout",  required_argument, 0, 'g'},
			{"no-external-xml-file",  no_argument, 0, 'n'},
			{"obj-timeout",  required_argument, 0, 'o'},
			{"port",  required_argument, 0, 'p'},
			{"script-engine", no_argument, &ldtp_script_service, 1},
			{"help",     no_argument, 0, 'h'},
			{"usage",     no_argument, 0, 'u'},
			{"verbose",     no_argument, 0, 'v'},
			{"version",     no_argument, 0, 'V'},
			{0, 0, 0, 0}
		};
		/* getopt_long stores the option index here. */
		int option_index = 0;

		c = getopt_long (argc, argv, "g:o:p:hnsuvV",
				 long_options, &option_index);
     
		/* Detect the end of the options. */
		if (c == -1)
			break;
     
		switch (c) {
		case 'g':
			ldtp_gui_timeout = atol (optarg);
			if (ldtp_gui_timeout <= 0)
				ldtp_gui_timeout = 30;
			break;
     
		case 'o':
			ldtp_obj_timeout = atol (optarg);
			if (ldtp_obj_timeout <= 0)
				ldtp_obj_timeout = 5;
			break;
     
		case 'p':
			ldtp_script_port = atol (optarg);
			break;
     
		case 'h':
			printf ("Usage:\n"
"ldtp [OPTION...] - Linux Desktop Testing Project engine\n"
"\n"
"Help Options:\n"
"	-h, --help              Show help options\n"
"\n"
"Application Options:\n"
"	-g, --gui-timeout=N          Wait gui to appear / disappear till N seconds\n"
"       -n, --no-external-xml-file   Don't use external temp XML file\n"
"	-o, --obj-timeout=N          Wait object to appear till N seconds\n"
"	-p, --port=N                 Start LDTP scripting engine on TCP port\n"
"	-s, --script-engine          Start LDTP script execution engine as TCP service\n"
"	-u, --usage                  LDTP engine usage\n"
"	-v, --verbose                Verbose mode\n"
"	-V, --version                LDTP engine version\n"
"\n");
			exit (0);
     
		case 'n':
			ldtp_external_xml_file = FALSE;
			break;
     
		case 's':
			ldtp_script_service = TRUE;
			break;
     
		case 'u':
			ldtp_usage = TRUE;
			break;
     
		case 'v':
			ldtp_debug = TRUE;
			break;
     
		case 'V':
			ldtp_version = TRUE;
			break;
     
		default:
			ldtp_usage = TRUE;
		}
	}
#endif
	if (ldtp_usage) {
		printf ("ldtp [--script-engine] [--port=N] [--verbose] [--gui-timeout=N]  [--obj-timeout=N] [--version] [--help]\n");
		exit (0);
	}
	if (ldtp_version) {
		printf ("ldtp-%s\n", PACKAGE_VERSION);
		exit (0);
	}

	if (ldtp_script_port)
		ldtp_script_service = TRUE;

	/* generate core dump on seg-fault */
	resource_limit.rlim_cur =
		resource_limit.rlim_max = RLIM_INFINITY;
	if (setrlimit (RLIMIT_CORE, &resource_limit) != 0) {
		perror ("setrlimit");
	}

	signal (SIGCHLD, SIG_IGN);
	signal (SIGTERM, cleanup);
	signal (SIGPIPE, SIG_IGN);
	signal (SIGINT, cleanup);

	// Register local print function
	g_set_print_handler (ldtp_print);

	if (getenv ("LDTP_DEBUG"))
		ldtp_debug = TRUE;
	if ((env_sleep = getenv ("GUI_TIMEOUT")) != NULL) {
		ldtp_gui_timeout = atoi (env_sleep);
		if (!ldtp_gui_timeout)
			ldtp_gui_timeout = 30;
	}
	if ((env_sleep = getenv ("OBJ_TIMEOUT")) != NULL) {
		ldtp_obj_timeout = atoi (env_sleep);
		if (!ldtp_obj_timeout)
			ldtp_obj_timeout = 5;
	}

	retval = pthread_create (&server_thread, NULL, &ldtp_server_thread, 
				 NULL);
	if (retval == EAGAIN) {
		/* unable to create threads... kindly retry... */
		err = LDTP_ERROR_THREAD_CREATION_FAILED;
		g_print ("%s\n", ldtp_error_get_message (err));
		return 1;
	}
	spi_init = SPI_init ();

	window_listener = SPI_createAccessibleEventListener (report_window_event, NULL);

	SPI_registerGlobalEventListener (window_listener,
					 "window:create");
	SPI_registerGlobalEventListener (window_listener,
					 "window:destroy");
	SPI_event_main ();
	return 0;
}
