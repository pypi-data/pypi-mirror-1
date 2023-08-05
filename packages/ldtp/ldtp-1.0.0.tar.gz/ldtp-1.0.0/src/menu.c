/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Poornima Nayak <pnayak@novell.com>
 *    Khasim Shaheed <khasim.shaheed@gmail.com>
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
#include "ldtp-error.h"
#include "ldtp-logger.h"
#include "ldtp-command.h"
#include "ldtp-gui-comp.h"

static LDTPErrorCode
select_menu_item (Accessible *object, char *param)
{
	/*
	  FIXME: Commented by Nagappan. When menu->menu item selected, menu's focus
	  is still there. By commenting this code we are not clicking menu directly.
	  Instead we are clicking menu item. This bug is fixed in cvs of at-spi package
	  Thursday, February 03 2005 - 05:43 PM IST
	*/
	//  int i;
	//  Accessible *child_object;
	//  AccessibleSelection *selection;
	//  AccessibleAction *action;
	//
	//  i = menu_item_exist (object, param);
	//  if (i > -1)
	//    {
	//      child_object = Accessible_getChildAtIndex (object, i);
	//      selection = Accessible_getSelection (object);
	//  /*
	//    Select child
	//  */    
	//      AccessibleSelection_selectChild (selection, i);
	//      action = Accessible_getAction (child_object);
	//      AccessibleAction_doAction (action, 0);
	//    }
	//
	//  action = Accessible_getAction (object);
	//  /*
	//    FIXME: If we do this action, then the menu selected doesn't
	//    get deselected. Need to be resolved
	//  */
	//  AccessibleAction_doAction (action, 0);
	//  Accessible_unref (action);
	return LDTP_ERROR_SUCCESS;
}

static LDTPErrorCode
list_child_menu_items (Accessible *object, char **data, FILE *log_fp)
{
	long i;
	long child_count;
	char *name = NULL;
	Accessible *child;
	LDTPErrorCode error;

	child_count = Accessible_getChildCount (object);
	if (child_count > 0) {
		for (i = 0; i < child_count; i++) {
			child = Accessible_getChildAtIndex (object, i);
			if (child) {
				name = Accessible_getName (child);
				if (name && g_ascii_strcasecmp (name, "") != 0) {
					if (*data == NULL)
						*data = g_strdup (name);
					else {
						char *tmp;
						tmp = g_strdup_printf ("%s;%s", *data, name);
						g_free (*data);
						*data = NULL;
						*data = tmp;
					}
					g_print ("Child menu item: %s", name);
					log_msg (LDTP_LOG_INFO, name, log_fp);
					SPI_freeString (name);
				}
				Accessible_unref (child);
			}
		}
	} else {
		error = LDTP_ERROR_MENU_ITEM_DOES_NOT_EXIST;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return LDTP_ERROR_SUCCESS;
}

static LDTPErrorCode
select_popup_menu (LDTPClientContext* cctxt)
{
	long i;
	long count = 0;
	char *name = NULL;
	char *menu_item_name = cctxt->req->arg_list->data;

	LDTPErrorCode error;
	Accessible *pop_menu = NULL;
	Accessible *menu = NULL;
	Accessible *menu_item = NULL;

	count = Accessible_getChildCount (cctxt->app_handle);
	pop_menu = Accessible_getChildAtIndex (cctxt->app_handle, count - 1);

	if (Accessible_getChildCount (pop_menu) == 1) {
		menu = Accessible_getChildAtIndex (pop_menu, 0);
		if (Accessible_getRole (menu) == SPI_ROLE_MENU) {
			count = Accessible_getChildCount (menu);
			Accessible_unref (pop_menu);
			for (i = 0; i < count; i++) {
				menu_item = Accessible_getChildAtIndex (menu, i);
				name = Accessible_getName (menu_item);
				g_print ("ITEM NAME: %s\n", name);
				if (name && g_utf8_collate (name, menu_item_name) == 0) {
					Accessible *object = cctxt->gui_handle->handle;
					cctxt->gui_handle->handle = menu_item;
					error = menu_item_main (cctxt, LDTP_CMD_SELECTMENUITEM);
					SPI_freeString (name);
					Accessible_unref (menu_item);
					Accessible_unref (menu);
					cctxt->gui_handle->handle = object;
					return error;
				}
				Accessible_unref (menu_item);
				SPI_freeString (name);
			}
			error = LDTP_ERROR_MENU_ITEM_DOES_NOT_EXIST;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		} else {
			error = LDTP_ERROR_UNABLE_TO_GET_MENU_HANDLE;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
			Accessible_unref (pop_menu);
		}
		Accessible_unref (menu);
		return error;
	} else {
		error = LDTP_ERROR_UNABLE_TO_FIND_POPUP_MENU;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
	}
	Accessible_unref (pop_menu);
	return error;
}

LDTPErrorCode
menu_main (LDTPClientContext* cctxt, int command, char *window_name)
{
	LDTPErrorCode error;
	char msg[256];

	switch (command) {
	case LDTP_CMD_SELECTMENUITEM:
	case LDTP_CMD_MENUCHECK:
	case LDTP_CMD_MENUUNCHECK:
	case LDTP_CMD_VERIFYMENUCHECK:
	case LDTP_CMD_VERIFYMENUUNCHECK:
	case LDTP_CMD_DOESMENUITEMEXIST: {
		//char *token       = NULL;
		//char *rest_token  = NULL;
		//char *rest_params = NULL;

		AccessibleRole class;
		LDTPRequest* ldtp_req = NULL;
		LDTPGuiHandle *accessible = NULL;
		Accessible *object = cctxt->gui_handle->handle;
	
		select_menu_item (cctxt->gui_handle->handle, cctxt->req->arg_list->data);

		if (cctxt && cctxt->req && cctxt->req->component)
			g_print ("DEBUG: %s - %d - %s\n", __FILE__, __LINE__, cctxt->req->component);

		ldtp_req = cctxt->req;
		//params = mnuFile;mnuNew
		if (cctxt->req && cctxt->req->arg_list && cctxt->req->arg_list->data) {
			gchar **token = NULL;
			token = g_strsplit (ldtp_req->arg_list->data, ";", 2);
			gchar *tmp = token [1];
			ldtp_req->arg_list = g_slist_remove_all (ldtp_req->arg_list,
								 ldtp_req->arg_list->data);
			if (tmp) {
				g_print ("Tmp: %s\n", tmp);
				ldtp_req->arg_list = g_slist_append (ldtp_req->arg_list, 
								     g_strdup (tmp));
			}
			g_free (ldtp_req->component);
			g_print ("Token: %s\n", token [0]);
			ldtp_req->component = g_strdup (token [0]);
			g_strfreev (token);
			if (ldtp_req->component)
				accessible = ldtp_gui_get_gui_handle (cctxt, &error);
			else
				accessible = ldtp_gui_get_gui_handle (cctxt, &error);
		} else {
			//if (token)
			//	g_sprintf (msg, "Unable to get gui handle %s %s %d",
			//		   token, __FILE__, __LINE__);
			//else
			//	g_sprintf (msg, "Unable to get gui handle %s %d",
			//		   __FILE__, __LINE__);
			g_sprintf (msg, "Unable to get gui handle %s %d",
				   __FILE__, __LINE__);
			g_print ("%s\n", msg);
			log_msg (LDTP_LOG_CAUSE, msg, cctxt->log_fp);
			return LDTP_ERROR_UNABLE_TO_GET_CHILD_MENU_ITEM;
		}
		//if (cctxt->req && cctxt->req->arg_list && cctxt->req->arg_list->data) {
		//	token = strtok (cctxt->req->arg_list->data, ";");
		//} else {
		//	if (token)
		//		g_sprintf (msg, "Unable to get gui handle %s %s %d",
		//			   token, __FILE__, __LINE__);
		//	else
		//		g_sprintf (msg, "Unable to get gui handle %s %d",
		//			   __FILE__, __LINE__);
		//	g_print ("%s\n", msg);
		//	log_msg (LDTP_LOG_CAUSE, msg, cctxt->log_fp);
		//	return LDTP_ERROR_UNABLE_TO_GET_CHILD_MENU_ITEM;
		//}
		//ldtp_req = cctxt->req;
		//
		//if (token != NULL) {
		//	g_print ("Component: %s - Token: %s\n", ldtp_req->component, token);
		//	g_free (ldtp_req->component);
		//	ldtp_req->component = g_strdup (token);
		//	rest_token = strtok (NULL, ";");
		//	while (rest_token) {
		//		g_print ("Rest token: %s\n", rest_token);
		//		if (!rest_params)
		//			rest_params  = strdup (rest_token);
		//		else {
		//			rest_params = (char *) realloc (rest_params,
		//							sizeof (char) *
		//							(strlen (rest_params) +
		//							 strlen (rest_token) + 1)
		//							+ 1);
		//			strcat (rest_params, ";");
		//			strcat (rest_params, rest_token);
		//		}
		//		rest_token = strtok (NULL, ";");
		//	}
		//	/*
		//	  Remove existing menu hierarchy from the list
		//	*/
		//	cctxt->req->arg_list = g_slist_remove_all (cctxt->req->arg_list,
		//						   cctxt->req->arg_list->data);
		//	if (rest_params) {
		//		g_print ("Rest params: %s\n", rest_params);
		//		/*
		//		  Add rest of menu in the hierarchy to the list
		//		*/
		//		cctxt->req->arg_list = g_slist_append (cctxt->req->arg_list, rest_params);
		//	}
		//}
		//if (token)
		//	accessible = ldtp_gui_get_gui_handle (cctxt, &error);
		//else
		//	accessible = ldtp_gui_get_gui_handle (cctxt, &error);
					
		if (!accessible) {
			//if (token)
			//	g_sprintf (msg, "Unable to get gui handle %s %s %d",
			//		   token, __FILE__, __LINE__);
			//else
			//	g_sprintf (msg, "Unable to get gui handle %s %s %d",
			//		   (char *)cctxt->req->arg_list->data,
			//		   __FILE__, __LINE__);
			if (cctxt->req->arg_list && cctxt->req->arg_list->data)
				g_sprintf (msg, "Unable to get gui handle %s %s %d",
					   (char *)cctxt->req->arg_list->data,
					   __FILE__, __LINE__);
			else
				g_sprintf (msg, "Unable to get gui handle %s %d",
					   __FILE__, __LINE__);
			g_print ("%s\n", msg);
			log_msg (LDTP_LOG_CAUSE, msg, cctxt->log_fp);
			return LDTP_ERROR_UNABLE_TO_GET_CHILD_MENU_ITEM;
		}
		class = Accessible_getRole (accessible->handle);
		cctxt->gui_handle->handle = accessible->handle;
		if (class == SPI_ROLE_MENU)
			error = menu_main (cctxt, command, window_name);
		else if ((command == LDTP_CMD_DOESMENUITEMEXIST) && class == SPI_ROLE_MENU_ITEM) {
			if (accessible)
				error = LDTP_ERROR_SUCCESS;
			else
				error = LDTP_ERROR_MENU_ITEM_DOES_NOT_EXIST;
		}
		else if (class == SPI_ROLE_MENU_ITEM)
			error = menu_item_main (cctxt, command);
		else if (class == SPI_ROLE_RADIO_MENU_ITEM)
			error = radio_menu_item_main (cctxt, command);
		else if (class == SPI_ROLE_CHECK_MENU_ITEM)
			error = check_menu_item_main (cctxt, command);
		//free (rest_params);
		Accessible_unref (accessible->handle);
		g_free (accessible);
		cctxt->gui_handle->handle = object;
		return error;
	}
	case LDTP_CMD_LISTSUBMENUS:
		cctxt->resp->data = NULL;
		cctxt->resp->data_len = 0;
		error = list_child_menu_items (cctxt->gui_handle->handle,
					       &cctxt->resp->data, cctxt->log_fp);
		if (error == LDTP_ERROR_SUCCESS && cctxt->resp->data)
			cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
		if (cctxt->resp->data)
			g_print ("\nSubmenus: %s - %ld\n", cctxt->resp->data, cctxt->resp->data_len);
		break;
	case LDTP_CMD_SELECTPOPUPMENU:
		error = select_popup_menu (cctxt);
		break;
	default:
		error = LDTP_ERROR_COMMAND_NOT_IMPLEMENTED;
		break;
	}
	return error;
}
