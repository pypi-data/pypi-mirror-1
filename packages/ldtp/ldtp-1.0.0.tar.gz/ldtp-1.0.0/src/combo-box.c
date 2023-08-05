/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Poornima Nayak<pnayak@novell.com>
 *    Nagappan A <nagappan@gmail.com>
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
#include "ldtp-error.h"
#include "ldtp-utils.h"
#include "ldtp-logger.h"
#include "ldtp-command.h"
#include "ldtp-gui-comp.h"

static LDTPErrorCode
click (Accessible *object, FILE *log_fp)
{
	SPIBoolean flag = FALSE;
	AccessibleAction *action;
  
	if (wait_till_object_state_contains (object, COMBO_BOX, log_fp) != 0) {
		log_msg (LDTP_LOG_CAUSE, "Not all combo box object properties enabled", log_fp);
		return  (LDTP_ERROR_CLICK_FAILED);
	}
	action = Accessible_getAction (object);
	flag = AccessibleAction_doAction (action, 0);
	Accessible_unref (action);
	if (flag)
		return  (LDTP_ERROR_SUCCESS);
	else
		return  (LDTP_ERROR_CLICK_FAILED);
}

static gboolean 
get_state_visible (Accessible *object)
{
	SPIBoolean visible = FALSE;
	AccessibleStateSet *state;
  
	state = Accessible_getStateSet (object);
	if (state)
		visible = AccessibleStateSet_contains (state, SPI_STATE_VISIBLE);
	
	if (visible)
		return TRUE;
	else
		return FALSE;
}

static LDTPErrorCode
hide_list (Accessible *object, FILE *log_fp)
{
	int type;
	SPIBoolean flag = FALSE;
	Accessible *hide_object;
	AccessibleAction *action;

	if (wait_till_object_state_contains (object, COMBO_BOX, log_fp) != 0) {
		log_msg (LDTP_LOG_CAUSE, "Not all combo box object properties enabled", log_fp);
		return  (LDTP_ERROR_HIDELIST_FAILED);
	}

        type = get_child_object_type (object);
        if (type == SPI_ROLE_LIST) {
                hide_object = get_list_handle (object);
                if (get_state_visible (hide_object) == FALSE) {
                        /*
                          If object is already in hidden state, we can't proceed hiding the object.
			*/
                        log_msg (LDTP_LOG_WARNING, "List already in hidden state", log_fp);
                        Accessible_unref (hide_object);
                        return  (LDTP_ERROR_SUCCESS);
                }

                action = Accessible_getAction (hide_object);
                if (action) {
                        flag = AccessibleAction_doAction (action, 0);
                        Accessible_unref (action);
                }
                Accessible_unref (hide_object);
        } else if (type == SPI_ROLE_MENU) {
                hide_object = get_menu_handle (object);
                if (get_state_visible (hide_object) == FALSE) {
                        /*
                          If object is already in hidden state, we can't proceed hiding the object.
			*/
                        log_msg (LDTP_LOG_WARNING, "Menu already in hidden state", log_fp);
                        Accessible_unref (hide_object);
                        return  (LDTP_ERROR_SUCCESS);
                }

                action = Accessible_getAction (object);
                if (action) {
                        flag = AccessibleAction_doAction (action, 0);
                        Accessible_unref (action);
                }
                Accessible_unref (hide_object);
        }
	if (flag)
		return  (LDTP_ERROR_SUCCESS);
	else
		return  (LDTP_ERROR_HIDELIST_FAILED);
}	

static LDTPErrorCode
show_list (Accessible *object, FILE *log_fp)
{
	int type;
	SPIBoolean flag = FALSE;
	Accessible *show_object;
	AccessibleAction *action;
  
	if (wait_till_object_state_contains (object, COMBO_BOX, log_fp) != 0) {
		g_print ("Not all combo box object properties enabled\n");
		log_msg (LDTP_LOG_CAUSE, "Not all combo box object properties enabled", log_fp);
		return  (LDTP_ERROR_SHOWLIST_FAILED);
	}

        type = get_child_object_type (object);

        if (type == SPI_ROLE_LIST) {
                show_object = get_list_handle (object);
                if (get_state_visible (show_object) == TRUE) {
                        /*
                          If object is already in visible state, we can't proceed with this step.
			*/
                        log_msg (LDTP_LOG_WARNING, "List already in visible state", log_fp);
                        Accessible_unref (show_object);
                        return  (LDTP_ERROR_SUCCESS);
                }
                action = Accessible_getAction (show_object);
		if (action) {
			flag = AccessibleAction_doAction (action, 0);
			Accessible_unref (action);
		}
                Accessible_unref (show_object);
        }

        if (type == SPI_ROLE_MENU) {
                show_object = get_menu_handle (object);
                if (get_state_visible (show_object) == TRUE) {
			/*
                          If object is already in visible state, we can't proceed with this step.
			*/
                        log_msg (LDTP_LOG_WARNING, "Menu already in visible state", log_fp);
                        Accessible_unref (show_object);
                        return  (LDTP_ERROR_SUCCESS);
                }
                action = Accessible_getAction (object);
                if (action) {
                        flag = AccessibleAction_doAction (action, 0);
                        Accessible_unref (action);
                }
                Accessible_unref (show_object);
       }
	g_print ("Flag: %d\n", flag);
	if (flag)
		return  (LDTP_ERROR_SUCCESS);
	else
		return  (LDTP_ERROR_SHOWLIST_FAILED);
}

static LDTPErrorCode
select_item (LDTPClientContext* cctxt)
{
	int type, count, i;
	LDTPErrorCode error;
	char *name = NULL;
	Accessible *object = cctxt->gui_handle->handle;
	Accessible *text = NULL;
	Accessible *child = NULL;
	Accessible *menu_object = NULL;
	char msg [256];

	if (wait_till_object_state_contains (object, COMBO_BOX, cctxt->log_fp) != 0) {
		g_print ("Not all combo box object properties enabled\n");
		log_msg (LDTP_LOG_CAUSE, "Not all combo box object properties enabled", cctxt->log_fp);
		return  (LDTP_ERROR_SELECTITEM_FAILED);
	}
  
	type = get_child_object_type (object);
	g_print ("Object type: %d\n", type);
	if (type == SPI_ROLE_LIST) {
		child = get_list_handle (object);
		if (child) {
			cctxt->gui_handle->handle = child;
			error = list_main (cctxt, LDTP_CMD_SELECTTEXTITEM);
			Accessible_unref (child);
			cctxt->gui_handle->handle = object;
			if (error != LDTP_ERROR_SUCCESS) {
				g_print ("Combo box SelectItem action failed\n");
				log_msg (LDTP_LOG_CAUSE, "Combo box SelectItem action failed", cctxt->log_fp);
				return  (LDTP_ERROR_SELECTITEM_FAILED);
			}
		}
		text = get_text_handle (object);
		if (text) {
			cctxt->gui_handle->handle = text;
			error = text_main (cctxt, LDTP_CMD_VERIFYSETTEXT);
			Accessible_unref (text);
			cctxt->gui_handle->handle = object;
			if (error == LDTP_ERROR_SUCCESS)
				return  (LDTP_ERROR_SUCCESS);
		}
		g_print ("Combo box select verify action failed\n");
		log_msg (LDTP_LOG_CAUSE, "Combo box select verify action failed", cctxt->log_fp);
		return  (LDTP_ERROR_VERIFY_SETTEXTVALUE_FAILED);
	} else if (type == SPI_ROLE_MENU) {
		menu_object = get_menu_handle (object);
		if (menu_object == NULL) {
			g_sprintf (msg, "Combobox: %s item does not exist\n",
				   (char *)cctxt->req->arg_list->data);
			log_msg (LDTP_LOG_CAUSE, msg, cctxt->log_fp);
			return  (LDTP_ERROR_ITEM_NOT_FOUND);
		}
		count = Accessible_getChildCount (menu_object);
		for (i = 0; i < count; i++) {
			child = Accessible_getChildAtIndex (menu_object, i);
			if (child) {
				char *tmp = NULL;
				name = Accessible_getName (child);
				g_print ("Combobox - name: %s - param: %s\n",
					 name, (char *) cctxt->req->arg_list->data);
				if (g_utf8_strchr (name, -1, ' ') != NULL)
					tmp = escape_character (name, ' ');
				/*
				  FIXME: Use g_utf8_*
				*/
				if (strcasecmp (name, cctxt->req->arg_list->data) == 0 ||
				    (tmp && strcasecmp (tmp, cctxt->req->arg_list->data) == 0)) {
					free (tmp);
					SPI_freeString (name);
					
					cctxt->gui_handle->handle = child;
					error = menu_item_main (cctxt, LDTP_CMD_SELECTMENUITEM);
					Accessible_unref (menu_object);
					Accessible_unref (child);
					cctxt->gui_handle->handle = object;
					if (error != LDTP_ERROR_SUCCESS) {
						g_print ("Combo Box: SelectItem action failed\n");
						log_msg (LDTP_LOG_CAUSE, "Combo Box: SelectItem action failed", cctxt->log_fp);
						return  (LDTP_ERROR_SELECTITEM_FAILED);
					} else {
						return  (LDTP_ERROR_SUCCESS);
					}
				}
				g_free (tmp);
				SPI_freeString (name);
				Accessible_unref (child);
			} // if
		} // for
		Accessible_unref (menu_object);
		cctxt->gui_handle->handle = object;
		g_sprintf (msg, "Combobox: %s item does not exist\n",
			   (char *)cctxt->req->arg_list->data);
		log_msg (LDTP_LOG_CAUSE, msg, cctxt->log_fp);
		return  (LDTP_ERROR_ITEM_NOT_FOUND);
	}
	g_print ("Verify combo box click child type is unidentified\n");
	log_msg (LDTP_LOG_CAUSE, "Verify combo box click child type is unidentified", cctxt->log_fp);
	return  (LDTP_ERROR_CHILD_TYPE_UNIDENTIFIED);
}

static LDTPErrorCode 
capture_to_file (Accessible *object, char *file_name, FILE *log_fp)
{
	int type;
	long count, i;
	long child_count;
	char *name;
	FILE *fp = NULL;
	Accessible *child, *menu_object;
	Accessible *child_object, *child_text;
  
	if (file_name)
		fp = fopen (file_name, "w");
	else
		fp = fopen ("comboboxitem.lst", "w");
	if (fp == NULL) {
		log_msg (LDTP_LOG_CAUSE, "Combo box: Cannot open output file", log_fp);
		return  (LDTP_ERROR_FILECAPTURE_FAILED_OPEN_OUTPUT_FILE);
	}
	if (wait_till_object_state_contains (object, COMBO_BOX, log_fp) != 0) {
		log_msg (LDTP_LOG_CAUSE, "Combo Box: SelectItem action failed", log_fp);
		return  (LDTP_ERROR_SELECTITEM_FAILED);
	}
  
	type = get_child_object_type (object);
	g_print ("Object type: %d\n", type);
	if (type == SPI_ROLE_LIST) {
		child = get_list_handle (object);
		if (child != NULL) {
			child_count = Accessible_getChildCount (child);
			for (i = 0; i < child_count; i++) {
				child_object = Accessible_getChildAtIndex (child, i);
				child_text = Accessible_getText (child_object);
				name = AccessibleText_getText (child_text, 0, LONG_MAX);
				g_print ("Item-ID: %ld -- NAME: %s\n", i, name);
				g_fprintf (fp, "%s\n", name);
				SPI_freeString (name);
				Accessible_unref (child_text);
				Accessible_unref (child_object);
			}
		}
		Accessible_unref (child);
	}
	else if (type == SPI_ROLE_MENU) {
		menu_object = get_menu_handle (object);
		if (menu_object) {
			count = Accessible_getChildCount (menu_object);
			if (count > 0) {
				for (i = 0; i < count; i++) {
					child = Accessible_getChildAtIndex (menu_object, i);
					if (child) {
						name = Accessible_getName (child);
						g_print ("Item-ID: %ld -- NAME: %s\n", i, name);
						g_fprintf (fp, "%s\n", name);
						SPI_freeString (name);
						Accessible_unref (child);
					} 
				} 
				Accessible_unref (menu_object);
			}
		}
	}
	else {
		fclose (fp);
		log_msg (LDTP_LOG_CAUSE, "Verify combo box click child type is unidentified", log_fp);
		return  (LDTP_ERROR_CHILD_TYPE_UNIDENTIFIED);
	}
	fclose (fp);
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
select_index (LDTPClientContext* cctxt)
{
	LDTPErrorCode error;
	Accessible *child;
	Accessible *object = cctxt->gui_handle->handle;

	if (wait_till_object_state_contains (object, COMBO_BOX, cctxt->log_fp) != 0) {
		log_msg (LDTP_LOG_CAUSE, "Not all combo box object properties enabled", cctxt->log_fp);
		return  (LDTP_ERROR_SELECTINDEX_FAILED);
	}

	child = get_list_handle (object);
	if (child) {
		cctxt->gui_handle->handle = child;
		error = list_main (cctxt, LDTP_CMD_SELECTINDEX);
		Accessible_unref (child);
		cctxt->gui_handle->handle = object;
		if (error != LDTP_ERROR_SUCCESS) {
			log_msg (LDTP_LOG_CAUSE, "Combo Box: SelectIndex action failed", cctxt->log_fp);
			error =  (LDTP_ERROR_SELECTINDEX_FAILED);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
			return error;
		}
	}
	else {
		error =  (LDTP_ERROR_SELECTINDEX_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
set_text_value (LDTPClientContext* cctxt)
{
	Accessible *text_obj;
	LDTPErrorCode error;
	Accessible *object = cctxt->gui_handle->handle;

	if (wait_till_object_state_contains (object, COMBO_BOX, cctxt->log_fp) != 0) {
		log_msg (LDTP_LOG_CAUSE, "Not all combo box object properties enabled", cctxt->log_fp);
		return  (LDTP_ERROR_SETTEXTVALUE_FAILED);
	}
	if (!cctxt->req->arg_list->data) {
		error =  (LDTP_ERROR_SETTEXTVALUE_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}
	text_obj = get_text_handle (object);
	if (!text_obj) {
		error =  (LDTP_ERROR_SETTEXTVALUE_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}
	cctxt->gui_handle->handle = text_obj;
	error = text_main (cctxt, LDTP_CMD_SETTEXTVALUE);
	if (error != LDTP_ERROR_SUCCESS) {
		Accessible_unref (text_obj);
		cctxt->gui_handle->handle = object;
		log_msg (LDTP_LOG_CAUSE, "Combo Box: SetTextValue action failed during setting", cctxt->log_fp);
		return  (LDTP_ERROR_SETTEXTVALUE_FAILED);
	}
	error = text_main (cctxt, LDTP_CMD_VERIFYSETTEXT);
	if (error != LDTP_ERROR_SUCCESS) {
		Accessible_unref (text_obj);
		cctxt->gui_handle->handle = object;
		log_msg (LDTP_LOG_CAUSE, "Combo Box: SetTextValue verify action failed during verifying", cctxt->log_fp);
		return  (LDTP_ERROR_VERIFY_SETTEXTVALUE_FAILED);
	}
	Accessible_unref (text_obj);
	cctxt->gui_handle->handle = object;
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
verify_drop_down (Accessible *object, FILE *log_fp)
{ 
	int focused, child_type;
	int showing, visible;
	Accessible *child_object;
	AccessibleStateSet *state;
  
	if (wait_till_object_state_contains (object, COMBO_BOX, log_fp) != 0) {
		log_msg (LDTP_LOG_CAUSE, "Not all combo box object properties enabled", log_fp);
		/* Varadhan
		   is it so?
		*/
		return  (LDTP_ERROR_CLICK_FAILED);
	}

	child_type = get_child_object_type (object);
	if (child_type == SPI_ROLE_LIST) {
		child_object = (Accessible *) get_list_handle (object);
		if (child_object) {
			state = Accessible_getStateSet (object);
			focused = AccessibleStateSet_contains (state, SPI_STATE_FOCUSABLE); 
			Accessible_unref (child_object);
			if (focused == 0) {
				log_msg (LDTP_LOG_CAUSE, "Verify Combo box list child is not focused", log_fp);
				return  (LDTP_ERROR_CHILD_NOT_FOCUSSED);
			}
			else
				return  (LDTP_ERROR_SUCCESS);
		}
	}
	else if (child_type == SPI_ROLE_MENU) {
		child_object = (Accessible *) get_menu_handle (object);
		if (child_object) {
			state = Accessible_getStateSet (object);
			showing = AccessibleStateSet_contains (state, SPI_STATE_SHOWING);
			visible = AccessibleStateSet_contains (state, SPI_STATE_VISIBLE); 
			Accessible_unref (child_object);
			if ((showing == 0) && (visible == 0)) {
				log_msg (LDTP_LOG_CAUSE, "Verify combo box menu child is not showing", log_fp);
				return  (LDTP_ERROR_MENU_NOT_VISIBLE);
			}
			else
				return  (LDTP_ERROR_SUCCESS);
		}
	}
	else {	  
		log_msg (LDTP_LOG_CAUSE, "Verify combo box click child type is unidentified", log_fp);
		return  (LDTP_ERROR_CHILD_TYPE_UNIDENTIFIED);
	}
	return  (LDTP_ERROR_VERIFY_DROPDOWN_FAILED);
}

static LDTPErrorCode
verify_hide_list (Accessible *object, FILE *log_fp)
{
	int child_type;
	Accessible *child_object;
	AccessibleStateSet *state;
	SPIBoolean visible;
	SPIBoolean showing;
	SPIBoolean focused;
  
	if (wait_till_object_state_contains (object, COMBO_BOX, log_fp) != 0) {
		log_msg (LDTP_LOG_CAUSE, "Not all combo box object properties enabled", log_fp);
		return  (LDTP_ERROR_CLICK_FAILED);
	}

	child_type = get_child_object_type (object);
	if (child_type == SPI_ROLE_LIST) {
		child_object = get_list_handle (object);
		if (child_object) {
			state = Accessible_getStateSet (object);
			focused = AccessibleStateSet_contains (state, SPI_STATE_FOCUSABLE); 
			Accessible_unref (child_object);
			if (focused == TRUE) {
				log_msg (LDTP_LOG_CAUSE, "Verify Combo box list child is focused", log_fp);
				return  (LDTP_ERROR_CHILD_IN_FOCUS);
			}
			return  (LDTP_ERROR_SUCCESS);
		}
	}
	else if (child_type == SPI_ROLE_MENU) {
		child_object = get_menu_handle (object);
		if (child_object) {
			state = Accessible_getStateSet (object);
			showing = AccessibleStateSet_contains (state, SPI_STATE_SHOWING);
			visible = AccessibleStateSet_contains (state, SPI_STATE_VISIBLE); 
			Accessible_unref (child_object);
			if (showing == FALSE && visible == FALSE) {
				/* Varadhan
				   Are we checking for visibility or invisibility?
				*/
				log_msg (LDTP_LOG_CAUSE, "Verify combo box menu child is showing & visible", log_fp);
				return  (LDTP_ERROR_MENU_VISIBLE);
			}
			return  (LDTP_ERROR_SUCCESS);
		}
	}
	log_msg (LDTP_LOG_CAUSE, "Verify combo box hidelist child type is unidentified", log_fp);
	return  (LDTP_ERROR_CHILD_TYPE_UNIDENTIFIED);
}

static LDTPErrorCode 
verify_show_list (Accessible *object, FILE *log_fp)
{
	if (verify_drop_down (object, log_fp) != 0) {
		log_msg (LDTP_LOG_CAUSE, "Verify combo box showlist action failed", log_fp);
		return  (LDTP_ERROR_VERIFY_SHOWLIST_FAILED);
	}
	else
		return  (LDTP_ERROR_SUCCESS);
}	    	 

static LDTPErrorCode
verify_set_text_value (LDTPClientContext* cctxt)
{
	int child_type;
	LDTPErrorCode error;
	Accessible *text_object;
	Accessible *object = cctxt->gui_handle->handle;

	child_type = get_child_object_type (object);
	if (child_type == SPI_ROLE_LIST) {
		if (wait_till_object_state_contains (object, COMBO_BOX, cctxt->log_fp) != 0) {
			g_print ("Verify Combo box SetTextValue action failed\n");
			log_msg (LDTP_LOG_CAUSE, "Verify Combo box SetTextValue action failed", cctxt->log_fp);
			return  (LDTP_ERROR_VERIFY_SETTEXTVALUE_FAILED);
		}
		text_object = get_text_handle (object);
		if (text_object) {
			cctxt->gui_handle->handle = text_object;
			error = text_main (cctxt, LDTP_CMD_VERIFYSETTEXT);
			Accessible_unref (text_object);
			cctxt->gui_handle->handle = object;
			if (error != LDTP_ERROR_SUCCESS) {
				g_print ("Verify Combo box SetTextValue action failed\n");
				log_msg (LDTP_LOG_CAUSE, "Verify Combo box SetTextValue action failed", cctxt->log_fp);
				return  (LDTP_ERROR_VERIFY_SETTEXTVALUE_FAILED);
			}
			return  (LDTP_ERROR_SUCCESS);
		}
		else {
			g_print ("Verify Combo box SetTextValue child object is NULL\n");
			log_msg (LDTP_LOG_CAUSE, "Verify Combo box SetTextValue child object is NULL", cctxt->log_fp);
			return  (LDTP_ERROR_VERIFY_SETTEXTVALUE_FAILED);
		}
	} else if (child_type == SPI_ROLE_MENU) {
		gboolean flag = FALSE;
		char *name = Accessible_getName (object);
		if (name) {
			if (cctxt && cctxt->req && cctxt->req->arg_list &&
			    cctxt->req->arg_list->data && (g_utf8_collate (cctxt->req->arg_list->data, name) == 0)) {
				g_print ("Name: %s - %s\n", name, (char *)cctxt->req->arg_list->data);
				flag = TRUE;
			}
			SPI_freeString (name);
		}
		if (flag)
			return  (LDTP_ERROR_SUCCESS);
		else {
			g_print ("Ldtp error verify settextvalue failed\n");
			return  (LDTP_ERROR_VERIFY_SETTEXTVALUE_FAILED);
		}
	}
	g_print ("Object type not matched: Ldtp error verify settextvalue failed\n");
	return  (LDTP_ERROR_VERIFY_SETTEXTVALUE_FAILED);
}

static LDTPErrorCode
verify_select_item (LDTPClientContext* cctxt)
{
	LDTPErrorCode error;

	error = verify_set_text_value (cctxt);

	if (error != LDTP_ERROR_SUCCESS) {
		g_print ("verify combo box select action failed\n");
		log_msg (LDTP_LOG_CAUSE, "verify combo box select action failed", cctxt->log_fp);
		return  (LDTP_ERROR_VERIFY_ITEM_FAILED);
	}
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
combo_select_index (LDTPClientContext* cctxt, int index)
{
	int type;
	long count;
	Accessible *child, *menu_object;
	Accessible *object = cctxt->gui_handle->handle;
  
	if (wait_till_object_state_contains (object, COMBO_BOX, cctxt->log_fp) != 0) {
		log_msg (LDTP_LOG_CAUSE, "Not all combo box object properties enabled", cctxt->log_fp);
		return  (LDTP_ERROR_SELECTITEM_FAILED);
	}

	type = get_child_object_type (object);
	if (type == SPI_ROLE_MENU) {
		menu_object = get_menu_handle (object);
		if (menu_object) {
			count = Accessible_getChildCount (menu_object);
			if (count > 0) {          
				child = Accessible_getChildAtIndex (menu_object, index);
				Accessible_unref (menu_object);
				if (child) {
					LDTPErrorCode error;
					cctxt->gui_handle->handle = child;
					error = menu_item_main (cctxt, LDTP_CMD_SELECTMENUITEM);
					cctxt->gui_handle->handle = object;
					Accessible_unref (child);
					if (error != LDTP_ERROR_SUCCESS) {
						log_msg (LDTP_LOG_CAUSE, "Combo Box: SelectItem action failed", cctxt->log_fp);
						return  (LDTP_ERROR_SELECTITEM_FAILED);
					}
					else
						return  (LDTP_ERROR_SUCCESS);
				}
			}// if
			else
				Accessible_unref (menu_object);
		}
		log_msg (LDTP_LOG_CAUSE, "Combo Box: SelectItem does not exist in", cctxt->log_fp);
		/* 
		   Varadhan
		   FIXME: Item does not exist or action failed? 
		*/
		return  (LDTP_ERROR_SELECTITEM_FAILED);
	}
	/* Varadhan
	   FIXME: More specific error should be returned 
	*/
	log_msg (LDTP_LOG_CAUSE, "Verify combo box click child type is unidentified", cctxt->log_fp);
	return  (LDTP_ERROR_SELECTITEM_FAILED);
}

static LDTPErrorCode
get_text_value (LDTPClientContext* cctxt)
{
	int type;
	long child_count, i;
	Accessible *child;
	char *item = NULL;
	AccessibleRole role;
	Accessible *object = cctxt->gui_handle->handle;
  
	if (wait_till_object_state_contains (object, COMBO_BOX, cctxt->log_fp) != 0) {
		log_msg (LDTP_LOG_CAUSE, "Not all combo box object properties enabled", cctxt->log_fp);
		return  (LDTP_ERROR_GETTEXTVALUE_FAILED);
	}

	type = get_child_object_type (object);

	if (type == SPI_ROLE_LIST) {
		child = NULL;
		child_count = Accessible_getChildCount (object);
		for (i = 0; i < child_count; i++) {
			child = Accessible_getChildAtIndex (object, i);
			role = Accessible_getRole (child);
			if (role == SPI_ROLE_TEXT)
				break;
			else {
				Accessible_unref (child);
				child = NULL;
			}
		}
		if (child) {
			LDTPErrorCode error;
			cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list,
							       "0");
			cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list,
							       "0");
			cctxt->gui_handle->handle = child;
			error = text_main (cctxt, LDTP_CMD_GETTEXTVALUE);
			cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, "0");
			cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, "0");
			cctxt->gui_handle->handle = object;
			Accessible_unref (child);
			if (error != LDTP_ERROR_SUCCESS) {
				log_msg (LDTP_LOG_CAUSE, 
					 "Combo box gettextvalue action failed",
					 cctxt->log_fp);
				return  (LDTP_ERROR_GETTEXTVALUE_FAILED);
			}
			cctxt->resp->data_len = g_utf8_strlen (cctxt->req->arg_list->data, -1);
			cctxt->resp->data = g_strdup (cctxt->req->arg_list->data);
			cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list->data, cctxt->resp->data);
			return  (LDTP_ERROR_SUCCESS);
		}
		else {
			log_msg (LDTP_LOG_CAUSE, 
				 "Combo box gettextvalue  action failed",
				 cctxt->log_fp);
			return  (LDTP_ERROR_GETTEXTVALUE_FAILED);
		}
	}
	else if (type == SPI_ROLE_MENU) {
		child = Accessible_getText (object);
		item = AccessibleText_getText (child, 0, LONG_MAX);
		cctxt->resp->data = g_strdup (item);
		cctxt->resp->data_len = AccessibleText_getCharacterCount (child);
		SPI_freeString (item);
		Accessible_unref (child);
		return  (LDTP_ERROR_SUCCESS);
	}
	else {
		log_msg (LDTP_LOG_CAUSE, "Combo box child type is unidentified", cctxt->log_fp);
		return  (LDTP_ERROR_CHILD_TYPE_UNIDENTIFIED);
	}
}

LDTPErrorCode 
combo_box_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_CLICK:
		error = click (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_HIDELIST:
		error = hide_list (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_COMBOSELECT:
		error = select_item (cctxt);
		break;
	case LDTP_CMD_SELECTINDEX:
		error = select_index (cctxt);
		break;
	case LDTP_CMD_SETTEXTVALUE: 
		error = set_text_value (cctxt);
		break;
	case LDTP_CMD_SHOWLIST: 
		error = show_list (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYDROPDOWN:
		error = verify_drop_down (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYHIDELIST:
		error = verify_hide_list (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYSHOWLIST:
		error = verify_show_list (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYSELECT:
		error = verify_select_item (cctxt);
		break;
	case LDTP_CMD_VERIFYSETTEXT:
		error = verify_set_text_value (cctxt);
		break;
	case LDTP_CMD_COMBOSELECTINDEX: {
		long index = 0;
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			index = atol (cctxt->req->arg_list->data);
		error = combo_select_index (cctxt, index);
		break;
	}	
        case LDTP_CMD_CAPTURETOFILE: {
                char *filename = NULL;
                if (cctxt->req->arg_list && cctxt->req->arg_list->data)
                        filename = cctxt->req->arg_list->data;
                error = capture_to_file (cctxt->gui_handle->handle,
                                         filename, cctxt->log_fp);
                break;
	}
	case LDTP_CMD_GETTEXTVALUE:
		error = get_text_value (cctxt);
		break;
        case LDTP_CMD_KBDENTER:
                error = device_main (cctxt, command);
                break;
	default:
		error =  (LDTP_ERROR_COMMAND_NOT_IMPLEMENTED);
		break;
	}
	return error;
}
