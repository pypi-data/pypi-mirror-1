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
#include <sys/types.h>
#include <glib.h>
#include <libxml/parser.h>

#include "ldtp-request.h"
#include "ldtp-error.h"
#include "ldtp-logger.h"

/* Object initialization function for the ldtp request object */
void
ldtp_request_init (LDTPRequest* req)
{
	req->request_type = 0;
	req->application  = NULL;	
	req->request_id   = NULL;
	req->context      = NULL;
	req->action_name  = NULL;
	req->component    = NULL;
	req->arg_list     = NULL;
}

/* Finalize handler for the ldtp request component object */
static void
ldtp_request_free (LDTPRequest* req, int finalize)
{
	if (req->arg_list) {
		g_slist_foreach (req->arg_list, (GFunc)g_free, NULL);
		g_slist_free (req->arg_list);
		req->arg_list = NULL;
	}

	req->request_type = 0;

	g_free (req->context);
	req->context = NULL;
  
	g_free (req->component);
	req->component = NULL;

	g_free (req->action_name);
	req->action_name = NULL;

	g_free (req->request_id);
	req->request_id = NULL;
}

/**
 * ldtp_request_component_new_from_string:
 *
 * Creates a new ldtp request component object from request-packet.  
 *
 * Return value: A newly-created ldtp request component object.
 **/
void
ldtp_request_fill_request (LDTPRequest* req, gchar* packet, size_t len, LDTPErrorCode* err)
{
	guchar *tmp = NULL;
	xmlDocPtr doc = NULL;
	xmlNodePtr node = NULL;

	if (!req || !packet || len <= 0) {
		*err = LDTP_ERROR_ARGUMENT_NULL;
		return;
	}

	doc = xmlParseMemory (packet, len);
	node = xmlDocGetRootElement (doc);
	if (node == NULL) {
		ldtp_log ("Empty request\n");
		goto error;
	}

	/* First level we expect GUI object attributes*/
	node = node->xmlChildrenNode;
	while (node && xmlIsBlankNode (node)) {
		node = node->next;
	}

	if (node == NULL)
		goto error;

	/* Free the previous contents */
	ldtp_request_free (req, 0);

	/* read the attributes */
	for (;node != NULL; node = node->next) {
		if (!node || !node->name)
			continue;
		/* Read action name*/
		g_print ("Node: %s\n", node->name);		
		if(!xmlStrcmp (node->name, (const xmlChar *) "SCRIPT") ){
			if (doc && node->xmlChildrenNode) {
				req->request_type = LDTP_SCRIPT;
			}
			node = node -> xmlChildrenNode;
		}
		if(!xmlStrcmp (node->name, (const xmlChar *) "APPLICATION") ){
			if (doc && node->xmlChildrenNode) {
				tmp = xmlNodeListGetString (doc, node->xmlChildrenNode, 1);
				if (tmp) {
					req->application = g_strdup ((char *)tmp);
					xmlFree (tmp);
				}
				else {
					req->application = NULL;
				}
			}
			node = node -> next;
		}
		if (!xmlStrcmp (node->name, (const xmlChar *) "ID")) {
			if (doc && node->xmlChildrenNode) {
				tmp = xmlNodeListGetString (doc, 
							    node->xmlChildrenNode, 1);
				if (tmp) {
					req->request_id = g_strdup ((char *)tmp);
					xmlFree (tmp);
				}
				else
					req->request_id = NULL;
				if (req->request_id)
					g_print ("request_id: %s\n", req->request_id);
			}
		}
		if (!xmlStrcmp (node->name, (const xmlChar *) "ACTION")) {
			if (doc && node->xmlChildrenNode) {
				tmp = xmlNodeListGetString (doc, 
							    node->xmlChildrenNode, 1);
				if (tmp) {
					req->action_name = g_strdup ((char *)tmp);
					xmlFree (tmp);
				}
				else
					req->action_name = NULL;
				if (req->action_name)
					g_print ("action_name: %s\n", req->action_name);
			}
		}
		if (!xmlStrcmp (node->name, (const xmlChar *) "CONTEXT")) {
			if (doc && node->xmlChildrenNode) {
				tmp = xmlNodeListGetString (doc, 
							    node->xmlChildrenNode, 1);
				if (tmp) {
					req->context = g_strdup ((char *)tmp);
					xmlFree (tmp);
				}
				else
					req->context = NULL;
				if (req->context)
					g_print ("Window name: %s\n", req->context);
			}
		}
		if (!xmlStrcmp (node->name, (const xmlChar *) "COMPONENT")) {
			if (doc && node->xmlChildrenNode) {
				tmp = xmlNodeListGetString (doc, 
							    node->xmlChildrenNode, 1);
				if (tmp) {
					req->component = g_strdup ((char *)tmp);
					xmlFree (tmp);
				}
				else
					req->component = NULL;
				if (req->component)
					g_print ("Component name: %s\n", req->component);
			}
		}
		if (!xmlStrcmp (node->name, (const xmlChar *) "ARGUMENTS")) {
			/* next level is a list of arguments */
			node = node->xmlChildrenNode;
			g_print ("Has childrens\n");
		}
		/*
		  If ARGUMENTS does not have any children, then the node will be empty
		  and node will be NULL. So its better to break the loop
		  NOTE: A better way to do this is, to have a seperate for loop to iterate
		  childrens of ARGUMENTS
		*/
		if (!node) {
			break;
		}
		if (!xmlStrcmp (node->name, (const xmlChar *) "ARGUMENT")) {
			if (doc && node->xmlChildrenNode) {
				tmp = (guchar *)xmlNodeListGetString (doc, node->xmlChildrenNode, 1);
				if (tmp) {
					req->arg_list = g_slist_prepend (req->arg_list,
									 (guchar *)g_strdup ((gchar *)tmp));
					xmlFree (tmp);
					if (req->arg_list && req->arg_list->data)
						g_print ("Argument value: %s\n", (char *)req->arg_list->data);
				}
			}
		}
	}

	if (!req->request_id)
		goto error;

	/* Reverse the argument list to get the
	   desired order of arguments.
	*/
	req->arg_list = g_slist_reverse (req->arg_list);
	goto success;

 error:
	*err = LDTP_ERROR_PACKET_INVALID;
	ldtp_request_free (req, 0);

	goto cleanup;

 success:
	*err = LDTP_ERROR_SUCCESS;
 cleanup:
	if (doc)
		xmlFreeDoc (doc);
}
