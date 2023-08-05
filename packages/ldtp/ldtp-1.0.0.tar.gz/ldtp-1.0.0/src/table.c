/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
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

#include "ldtp.h"
#include "ldtp-gui.h"
#include "ldtp-error.h"
#include "ldtp-logger.h"
#include "ldtp-command.h"
#include "ldtp-gui-comp.h"
#include "ldtp-utils.h"

extern gboolean ldtp_debug;
extern gint ldtp_obj_timeout;

/*
  Sort column based on given index
*/  
static LDTPErrorCode
sort_column_index (Accessible *object, int col, FILE *log_fp)
{
	long n_cols;	
	long n_actions, i;
	gboolean flag = FALSE;
	LDTPErrorCode error;
	AccessibleTable *table;
	Accessible *header;
	AccessibleAction *action;
	char *name = NULL;
	char msg[256];

	table = Accessible_getTable (object);
	n_cols = AccessibleTable_getNColumns (table);
	g_print ("Number of columns: %ld\n", n_cols);

	if (col < 0 || col >= n_cols) {
			g_sprintf (msg, "Column %d doesnot exist in table", col);
			log_msg (LDTP_LOG_CAUSE, msg, log_fp);
			Accessible_unref (table);
			error =  (LDTP_ERROR_INVALID_COLUMN_INDEX_TO_SORT);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
	}
	header = AccessibleTable_getColumnHeader (table, col);
	Accessible_unref (table);
  
	action = Accessible_getAction (header);
	Accessible_unref (header);
	n_actions = AccessibleAction_getNActions (action);

	for (i = 0; i < n_actions; i++) {
		name = AccessibleAction_getName (action, i);

		if (g_utf8_collate (name, "sort") == 0) {
			AccessibleAction_doAction (action, i);
			flag = TRUE;
			break;
		}
	}
	Accessible_unref (action);
	SPI_freeString (name);

	if (flag == FALSE) { 
		error =  (LDTP_ERROR_UNABLE_TO_SORT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return  (LDTP_ERROR_SUCCESS);
}  
	
/*
  Sort column based on given name
*/  
static LDTPErrorCode
sort_column (Accessible *object, char *column_header_text, FILE *log_fp)
{
	long n_cols;	
	long n_actions, i, j;
	LDTPErrorCode error;
	gboolean flag = FALSE;
	AccessibleTable *table;
	AccessibleAction *action;
	Accessible *header = NULL;
	char *name = NULL;

	table = Accessible_getTable (object);
	n_cols = AccessibleTable_getNColumns (table);
	g_print ("Number of columns: %ld\n", n_cols);

	for (i = 0; i < n_cols; i++) {	  
		char *name;
		header = AccessibleTable_getColumnHeader (table, i);
		name = Accessible_getName (header);

		if (g_utf8_collate (name, column_header_text) == 0) {      
			Accessible_unref (table);
			table = NULL;
			SPI_freeString (name);
			break;
		}
		Accessible_unref (header);
	}	
  
	if (i == n_cols) {
		if (table)
			Accessible_unref (table);
		Accessible_unref (header);
		error =  (LDTP_ERROR_COLUMN_DOES_NOT_EXIST);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	if (table)
		Accessible_unref (table);
	action = Accessible_getAction (header);
	Accessible_unref (header);
	n_actions = AccessibleAction_getNActions (action);

	for (j = 0; j < n_actions; j++) {
		name = AccessibleAction_getName (action, j);

		if (g_utf8_collate (name, "sort") == 0) {      
			AccessibleAction_doAction (action, j);
			flag = TRUE;
			break;
		}
	}
	Accessible_unref (action);
	SPI_freeString (name);

	if (flag == FALSE) { 
		error =  (LDTP_ERROR_UNABLE_TO_SORT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return  (LDTP_ERROR_SUCCESS);
}  

static Accessible*
get_row (Accessible *object, char *row_text, long *row, long *column, FILE *log_fp)
{
	long i, j;
	long n_rows = 0, n_cols = 0;
	Accessible *cell;
	AccessibleTable *table;
	char msg [256];
	int time_wait = ldtp_obj_timeout;
	time_t start, cur;
	time_t start_rows, cur_rows;

	if (ldtp_obj_timeout <= 0) {
		time_wait = 5; // Max wait for 5 seconds
	}
	start = cur = time (NULL);
	while (difftime (cur, start) < time_wait * 2) {
		table = Accessible_getTable (object);
		if (!table) {
			ldtp_nsleep (0, 30000);

			cur = time (NULL);
			continue;
		}
		/*
		  Copied from LTFX source code
		*/
		start_rows = cur_rows = time (NULL);

		g_print ("Timeout: %d - %d\n", time_wait, ldtp_obj_timeout);
		while (difftime (cur_rows, start_rows) < time_wait) {
			n_rows = AccessibleTable_getNRows (table);
			if (!n_rows) {
				ldtp_nsleep (0, 30000);

				cur_rows = time (NULL);
			} else {
				break;
			}
		}
		n_cols = AccessibleTable_getNColumns (table);
		g_print ("Number of rows: %ld\tColumn: %ld\n", n_rows, n_cols);

		for (i = 0; i < n_rows; i++) {
			for (j = 0; j < n_cols; j++) {
				long child_count;
				cell = AccessibleTable_getAccessibleAt (table, i, j);
				child_count = Accessible_getChildCount (cell);
				g_print ("Child count: %ld\n", child_count);
				if (child_count > 0) {
					long k;
					char *name;
					Accessible *child;
					for (k = 0; k < child_count; k++) {
						child = Accessible_getChildAtIndex (cell, k);
						if (child) {
							name = Accessible_getName (child);
							if (name == NULL) {
								Accessible_unref (child);
								continue;
							}
							if (ldtp_debug) {
								g_print ("Table cell name: %s\n", name);
								g_print ("Table cell child count: %ld\n",
									 Accessible_getChildCount (child));
							}
							if (g_utf8_collate (name, row_text) == 0) {
								SPI_freeString (name);
								Accessible_unref (cell);
								Accessible_unref (table);
								*row = i; *column = j;
								return child;
							} // if
							SPI_freeString (name);
							Accessible_unref (child);
						}
					} // for
				} else {
					char *name;
					name = Accessible_getName (cell);
					if (name) {
						g_print ("Table cell name: %s\n", name);
						if (g_utf8_collate (name, row_text) == 0) {
							SPI_freeString (name);
							Accessible_unref (table);
							*row = i; *column = j;
							return cell;
						} // if
						SPI_freeString (name);
					}
				}
				Accessible_unref (cell);
			} // for j
		} // for i
		ldtp_nsleep (0, 30000);

		cur = time (NULL);
		Accessible_unref (table);
	}

	g_sprintf (msg, "Unable to find %s in table", row_text);
	log_msg (LDTP_LOG_CAUSE, msg, log_fp);
	return NULL;
}

static LDTPErrorCode
get_cell_value (LDTPClientContext* cctxt)
{
	long i, j;
	long row = 0, column = 0, n_rows, n_cols;
	int  child_type;
	long child_count, child_count_level2;
	gboolean flag = FALSE;
	GSList *l;
	LDTPErrorCode error;

	AccessibleTable *table;
	Accessible *child_object, *child_level2, *child_level3;
	Accessible *parent_cell;
	Accessible *object = cctxt->gui_handle->handle;

	l = cctxt->req->arg_list;
	if (l && l->data) {
		row = atol (l->data);
		l = l->next;
		if (l && l->data)
			column = atol (l->data);
	}

	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
	n_cols = AccessibleTable_getNColumns (table);
	g_print ("Rows: %ld -- Columns: %ld", n_rows, n_cols);

	if (n_rows < row) {
		Accessible_unref (table);
		error =  (LDTP_ERROR_ACTUAL_ROW_COUNT_LESS_THAN_GIVEN_ROW_COUNT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}
	if (n_cols < column) {
		Accessible_unref (table);
		error =  (LDTP_ERROR_ACTUAL_COLUMN_COUNT_LESS_THAN_GIVEN_COLUMN_COUNT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}

	parent_cell = AccessibleTable_getAccessibleAt (table, row, column);
	child_count = Accessible_getChildCount (parent_cell);
	child_object = NULL;
  
	if (child_count == 0) {
		flag = TRUE;
		child_object = parent_cell;
	}
	else {
		for (i = 0; i < child_count && flag == 0; i++) {
			child_level2 = Accessible_getChildAtIndex (parent_cell, i);
			child_count_level2 = Accessible_getChildCount (child_level2);
			if (child_count_level2 > 0) {
				for (j = 0; j < child_count_level2 && flag == FALSE; j++) {
					child_level3 = Accessible_getChildAtIndex (child_level2, j);
					if (Accessible_isText (child_level3)) {
						flag = TRUE;
						child_object = child_level3;
						break;
					}
					Accessible_unref (child_level3);
				}
			}
			else {
				if (Accessible_isText (child_level2)) {
					flag = TRUE;
					child_object = child_level2;
				}
			}
			if (flag == FALSE)
				Accessible_unref (child_level2);
		}
		Accessible_unref (parent_cell);
	}
	cctxt->gui_handle->handle = child_object;
	if (flag == TRUE) {
		if (Accessible_isComponent (child_object)) {
			child_type = get_object_type (child_object);
			g_print ("Child type is %d ", child_type);
			if (child_type == SPI_ROLE_TEXT || child_type == SPI_ROLE_TABLE_CELL) {
				if (Accessible_isText (child_object)) {
					g_print ("Table cell is a text object\n");
					cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list,
										"0");
					cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list,
										g_strdup_printf ("0"));
					error = text_main (cctxt, LDTP_CMD_GETTEXTVALUE);
					cctxt->req->arg_list = g_slist_remove_all (cctxt->req->arg_list, "0");
					Accessible_unref (table);
					Accessible_unref (child_object);
					cctxt->gui_handle->handle = object;
					return error;
				}
			}
		} //if
		Accessible_unref (table);
		if (child_object)
			Accessible_unref (child_object);
		cctxt->gui_handle->handle = object;
	}
	else {
		log_msg (LDTP_LOG_CAUSE, "Table cell has no child of type TEXT", cctxt->log_fp);
		Accessible_unref (table);
		if (child_object)
			Accessible_unref (child_object);
		cctxt->gui_handle->handle = object;
		error =  (LDTP_ERROR_NO_CHILD_TEXT_TYPE_UNDER_TABLE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}
	error =  (LDTP_ERROR_GET_TABLE_CELL_FAILED);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
	return error;
}

/*
  Select the row in the given object
*/
static LDTPErrorCode
select_row (LDTPClientContext *cctxt, Accessible *object, char *row_text, FILE *log_fp)
{
	Accessible *cell;
	LDTPErrorCode error;
	int time_wait = ldtp_obj_timeout;
	time_t start, cur;
	long row = -1;
	long column = -1;

	if (!object) {
		g_print ("%s - %d\n", __FILE__, __LINE__);
		error =  (LDTP_ERROR_UNABLE_TO_SELECT_ROW);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	if (ldtp_obj_timeout <= 0) {
		time_wait = 5; // Max wait for 5 seconds
	}

	cell = get_row (object, row_text, &row, &column, log_fp);
	if (cell) {
		if (Accessible_isComponent (cell)) {
			SPIBoolean flag;
			AccessibleComponent *accessible_component;
			start = cur = time (NULL);
			while (difftime (cur, start) < time_wait) {
				accessible_component = Accessible_getComponent (cell);
				if (accessible_component) {
					flag = AccessibleComponent_grabFocus (accessible_component);
					Accessible_unref (accessible_component);
				}
				if (flag) {
					if (Accessible_isText (cell)) {
						AccessibleText *text = Accessible_getText (cell);
						if (text) {
							char *name = AccessibleText_getText (text, 0, LONG_MAX);
							if (name) {
								g_print ("Cell content: %s\n", name);
								SPI_freeString (name);
							}
							Accessible_unref (text);
						}
					}
					break;
				}
				ldtp_nsleep (0, 30000);

				cur = time (NULL);
			}
			Accessible_unref (cell);
			if (flag) {
				g_print ("Grabed focus\n");
				return  (LDTP_ERROR_SUCCESS);
			} else {
				g_print ("Unable to grab focus\n");
				error = LDTP_ERROR_UNABLE_TO_GRAB_FOCUS;
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
				return error;
			}
		}
		else {
			Accessible_unref (cell);
			error =  (LDTP_ERROR_OBJ_NOT_COMPONENT_TYPE);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
	}
	error =  (LDTP_ERROR_UNABLE_TO_SELECT_ROW);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

/*
  Double click
*/
static LDTPErrorCode
double_click (Accessible *object, FILE *log_fp)
{
	long x, y, height, width;
	SPIBoolean flag = FALSE;
	LDTPErrorCode error;
	AccessibleComponent *component;

	if (Accessible_isComponent (object))
		component = Accessible_getComponent (object);
	else {
		Accessible_unref (object);
		error =  (LDTP_ERROR_OBJ_NOT_COMPONENT_TYPE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	AccessibleComponent_getExtents (component, &x, &y, &width, &height, SPI_COORD_TYPE_SCREEN);
	/* NOTE: Some widgets doesnot sense the double click event if they are performed exactly on the 
	 * border. In order to take care of those situtations also we make adjustments in the x and y value
	 * to fire the event at the center of the object.
	 */
	x = x + width / 2;
	y = y + height / 2;
	flag = AccessibleComponent_grabFocus (component);
	Accessible_unref (component);
	if (!flag) {
		error =  (LDTP_ERROR_UNABLE_TO_GRAB_FOCUS);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	flag = SPI_generateMouseEvent (x, y, "b1d");
	if (flag)
		return  (LDTP_ERROR_SUCCESS);
	else {
		error =  (LDTP_ERROR_DOUBLE_CLICK_FAILED);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

/*
  Double click row
*/
static LDTPErrorCode
double_click_row (Accessible *object, char *row_text, FILE *log_fp)
{
	long x, y, height, width;
	SPIBoolean flag = FALSE;
	LDTPErrorCode error;
	Accessible *cell;
	AccessibleComponent *component;

	long row = -1;
	long column = -1;

	cell = get_row (object, row_text, &row, &column, log_fp);
	if (cell) {
		if (Accessible_isComponent (cell))
			component = Accessible_getComponent (cell);
		else {
			Accessible_unref (cell);
			error =  (LDTP_ERROR_OBJ_NOT_COMPONENT_TYPE);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
		AccessibleComponent_getExtents (component, &x, &y, &width, &height, SPI_COORD_TYPE_SCREEN);
		/* NOTE: Some widgets doesnot sense the double click event if they are performed exactly on the 
		 * border. In order to take care of those situtations also we make adjustments in the x and y value
		 * to fire the event at the center of the object.
		 */
		x = x + width / 2;
		y = y + height / 2;
		flag = AccessibleComponent_grabFocus (component);
		Accessible_unref (cell);
		Accessible_unref (component);
		if (!flag) {
			error =  (LDTP_ERROR_UNABLE_TO_GRAB_FOCUS);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
		flag = SPI_generateMouseEvent (x, y, "b1d");
		if (flag)
			return  (LDTP_ERROR_SUCCESS);
		else {
			error =  (LDTP_ERROR_DOUBLE_CLICK_FAILED);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
	}
	error =  (LDTP_ERROR_UNABLE_TO_GET_CELL_HANDLE_FAILED);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

/*
  Select the row in the given object
*/
static LDTPErrorCode
select_row_index (Accessible *object, long row, FILE *log_fp)
{
	long n_rows, n_cols;
	LDTPErrorCode error;
	Accessible *cell;
	AccessibleTable *table;
	char msg[256];

	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
	n_cols = AccessibleTable_getNColumns (table);
	g_print ("Number of rows: %ld\tColumn: %ld\n", n_rows, n_cols);

	if (row < 0 || row >= n_rows) {
		g_sprintf (msg, "Row %ld doesnot exist in table", row);
		log_msg (LDTP_LOG_CAUSE, msg, log_fp);
		Accessible_unref (table);
		error =  (LDTP_ERROR_ROW_DOES_NOT_EXIST);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	cell = AccessibleTable_getAccessibleAt (table, row, 0);

	if (Accessible_isComponent (cell)) {
		SPIBoolean flag;
		AccessibleComponent *accessible_component;

		accessible_component = Accessible_getComponent (cell);
		flag = AccessibleComponent_grabFocus (accessible_component);

		Accessible_unref (accessible_component);
		Accessible_unref (cell);
		Accessible_unref (table);
		if (flag)
			return  (LDTP_ERROR_SUCCESS);
		error =  (LDTP_ERROR_UNABLE_TO_GRAB_FOCUS);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	} else 	{
		g_sprintf (msg, "Table not Accessible component");
		log_msg (LDTP_LOG_CAUSE, msg, log_fp);
		g_print ("Table not Accessible component\n");
		Accessible_unref (cell);
		Accessible_unref (table);
		error =  (LDTP_ERROR_OBJ_NOT_COMPONENT_TYPE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
select_last_row (Accessible *object, FILE *log_fp)
{
	long n_rows;
	Accessible *cell;
	AccessibleTable *table;
	LDTPErrorCode error;

	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
  
	g_print ("table - number of rows:%ld\n", n_rows);
  
	cell = AccessibleTable_getAccessibleAt (table, n_rows-1, 0);
	if (Accessible_isComponent (cell)) {
		SPIBoolean flag;
		AccessibleComponent *accessible_component;

		accessible_component = Accessible_getComponent (cell);
		flag = AccessibleComponent_grabFocus (accessible_component);

		Accessible_unref (accessible_component);
		Accessible_unref (cell);
		Accessible_unref (table);
		if (flag == TRUE)
			return  (LDTP_ERROR_SUCCESS);
		else {
			error =  (LDTP_ERROR_UNABLE_TO_GRAB_FOCUS);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
	} else 	{
		Accessible_unref (cell);
		Accessible_unref (table);
		error =  (LDTP_ERROR_OBJ_NOT_COMPONENT_TYPE);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
does_row_exist (Accessible *object, char *row_text, FILE *log_fp)
{
	long n_rows, n_cols;
	AccessibleTable *table;
	Accessible *cell;
	LDTPErrorCode error;
	SPIBoolean flag = FALSE;
  
	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
	n_cols = AccessibleTable_getNColumns (table);
  
	if (!row_text) {
		if (n_rows != 0) {
			log_msg (LDTP_LOG_INFO, "Rows available in Table cell", log_fp);
			Accessible_unref (table);
			return  (LDTP_ERROR_SUCCESS);
		}
		Accessible_unref (table);
		error =  (LDTP_ERROR_ROW_DOES_NOT_EXIST);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	} else {
		long i, j;
		for (i = 0; i < n_rows; i++) {
			for (j = 0; j < n_cols; j++) {
				long child_count;
				char *name;
				Accessible *child;

				cell = AccessibleTable_getAccessibleAt (table, i, j);
				child_count = Accessible_getChildCount (cell);
				if (child_count > 0) {
					long k;
					for (k = 0; k < child_count; k++) {
						child = Accessible_getChildAtIndex (cell, k);
						name = Accessible_getName (child);
						if (name && g_utf8_collate (name, row_text) == 0) {
							SPI_freeString (name);
							Accessible_unref (child);
							flag = TRUE;
							break;
						} // if
						SPI_freeString (name);
						Accessible_unref (child);
					} // for
					Accessible_unref (cell);
					if (flag == TRUE)
						break;
				} else {
					name = Accessible_getName (cell);
					if (name && g_utf8_collate (name, row_text) == 0) {
						SPI_freeString (name);
						flag = TRUE;
						Accessible_unref (cell);
						break;
					} // if
					Accessible_unref (cell);
				}
			} // for j
			if (flag == TRUE)
				break;
		} // for i
		Accessible_unref (table);
	} // else
	if (flag == TRUE)
		return  (LDTP_ERROR_SUCCESS);
	else {
		error =  (LDTP_ERROR_ROW_DOES_NOT_EXIST);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
}

static LDTPErrorCode
verify_cell_value (LDTPClientContext* cctxt)
{
	char *text;
	int child_type;
	long row = 0, column = 0;
	long n_rows, n_cols;
	long n_actions, j;
	long offset, child_count;
	char *name = NULL;
	GSList *l;
	LDTPErrorCode error;
	AccessibleAction *action;
	AccessibleTable *table;
	Accessible *child_object;
	Accessible *object = cctxt->gui_handle->handle;
  
	l = cctxt->req->arg_list;
	if (l && l->data) {
		row = atol (l->data);
		l = l->next;
		if (l && l->data) {
			column = atol (l->data);
		}
	}
        
	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
	n_cols = AccessibleTable_getNColumns (table);
 
	if (n_rows < row) {
		Accessible_unref (table);
		error =  (LDTP_ERROR_ACTUAL_ROW_COUNT_LESS_THAN_GIVEN_ROW_COUNT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}
	if (n_cols < column) {
		Accessible_unref (table);
		error =  (LDTP_ERROR_ACTUAL_COLUMN_COUNT_LESS_THAN_GIVEN_COLUMN_COUNT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}  
	g_print ("Table - number of rows:%ld\tColumn: %ld\n", n_rows, n_cols);
	child_object = AccessibleTable_getAccessibleAt (table, row, column);

	do {
		child_count = Accessible_getChildCount (child_object);
		if (child_count > 0) {
			Accessible *tmp_child;
			tmp_child = child_object;
			child_object = Accessible_getChildAtIndex (child_object, 0);
			Accessible_unref (tmp_child);
		}
	} while (child_count > 0);

	cctxt->gui_handle->handle = child_object;
	if (Accessible_isComponent (child_object)) {
		child_type = get_object_type (child_object);
		g_print ("Child type is %d\n", child_type);
		if (child_type == SPI_ROLE_TABLE_CELL) {
			action = Accessible_getAction (child_object);
			n_actions = AccessibleAction_getNActions (action);
			if (n_actions) {
				for (j = 0; j < n_actions; j++) {
					/*
					  FIXME: Use Accessible_getRole
					*/
					name = AccessibleAction_getName (action, j);
					/* Handled at present only Toggle & Text type of cell */
					if (g_ascii_strcasecmp (name, "toggle") == 0) {
						GSList *l = g_slist_last (cctxt->req->arg_list);
						cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list, l);
						g_print ("Table cell is of type 'Toggle'\n");
						error = toggle_button_main (cctxt, LDTP_CMD_VERIFYTOGGLED);
						cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, l->data);
						SPI_freeString (name);
						Accessible_unref (action);
						Accessible_unref (table);
						Accessible_unref (child_object);
						cctxt->gui_handle->handle = object;
						return error;
					}
					if (g_ascii_strcasecmp (name, "edit") == 0) {
						GSList *l = g_slist_last (cctxt->req->arg_list);
						cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list, l->data);
						g_print ("Table Table cell is text box\n");
						error = text_main (cctxt, LDTP_CMD_VERIFYSETTEXT);
						cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, l->data);
						SPI_freeString (name);
						Accessible_unref (action);
						Accessible_unref (table);
						Accessible_unref (child_object);
						cctxt->gui_handle->handle = object;
						return error;
					}
					SPI_freeString (name);
				} //for 
				Accessible_unref (action);
			} //if
			else {	
				if (Accessible_isText (child_object)) {	
					AccessibleText *text_object;

					text_object = Accessible_getText (child_object);
					offset = AccessibleText_getCaretOffset (text_object);

					text = AccessibleText_getText (text_object, 0, LONG_MAX);
					g_print ("Table cell is a text object\n");
					cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list, text);
					error = text_main (cctxt, LDTP_CMD_VERIFYSETTEXT);
					cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, text);

					SPI_freeString (name);
					SPI_freeString (text);
					Accessible_unref (table);
					Accessible_unref (action);
					Accessible_unref (text_object);
					Accessible_unref (child_object);
					cctxt->gui_handle->handle = object;
					return error;
				}
				SPI_freeString (name);
				Accessible_unref (action);
			} // else
		} // if (child_type == SPI_ROLE_TABLE_CELL)
		else if (child_type == SPI_ROLE_TEXT) {
			GSList *l = g_slist_last (cctxt->req->arg_list);
			cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list, l->data);
			g_print ("Table cell is text box \n");
			error = text_main (cctxt, LDTP_CMD_VERIFYSETTEXT);
			cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, l->data);
			Accessible_unref (table);
			Accessible_unref (child_object);
			cctxt->gui_handle->handle = object;
			return error;  
		}
		else if (child_type == SPI_ROLE_TOGGLE_BUTTON) {
			GSList *l = g_slist_last (cctxt->req->arg_list);
			cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list, l->data);
			g_print ("Table cell is of type Toggle\n");
			error = toggle_button_main (cctxt, LDTP_CMD_VERIFYTOGGLED);
			cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, l->data);
			Accessible_unref (table);
			Accessible_unref (child_object);
			cctxt->gui_handle->handle = object;
			return error;
		}
	} //if
	Accessible_unref (table);
	Accessible_unref (child_object);
	cctxt->gui_handle->handle = object;
	error =  (LDTP_ERROR_VERIFY_TABLE_CELL_FAILED);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
	return error;
}  

/* This function has to be modified like verify_cell_value */
static LDTPErrorCode
set_cell_value (LDTPClientContext* cctxt)
{
	char *name;
	long row = 0, column= 0;
	long n_rows, n_cols, n_actions;
	GSList *l;
	LDTPErrorCode error;
	Accessible *cell;
	AccessibleAction *action;
	AccessibleTable *table;
	Accessible *object = cctxt->gui_handle->handle;

	l = cctxt->req->arg_list;
	if (l && l->data) {
		row = atol (l->data);
		l = l->next;
		if (l && l->data) {
			column = atol (l->data);
		}
	}
        
	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
	n_cols = AccessibleTable_getNColumns (table);
 
	if (n_rows < row) {
		Accessible_unref (table);
		error =  (LDTP_ERROR_ACTUAL_ROW_COUNT_LESS_THAN_GIVEN_ROW_COUNT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}
	if (n_cols < column) {
		Accessible_unref (table);
		error =  (LDTP_ERROR_ACTUAL_COLUMN_COUNT_LESS_THAN_GIVEN_COLUMN_COUNT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}
	g_print ("Table - number of rows:%ld\tColumn: %ld\n", n_rows, n_cols);

	cell = AccessibleTable_getAccessibleAt (table, row, column);
	cctxt->gui_handle->handle = cell;
	if (cell && Accessible_isComponent (cell)) {
		long j;
		action = Accessible_getAction (cell);
		n_actions = AccessibleAction_getNActions (action);
		for (j = 0; j < n_actions; j++) {
			name = AccessibleAction_getName (action, j);
			/* Handled at present only Toggle & Text type of cell */
			if (g_ascii_strcasecmp (name, "toggle") == 0) {
				GSList *l = g_slist_last (cctxt->req->arg_list);
				cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list, l->data);
				g_print ("Table cell is of type Toggle\n");
				error = toggle_button_main (cctxt, LDTP_CMD_CLICK);
				cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, l->data);
				SPI_freeString (name);
				Accessible_unref (action);
				Accessible_unref (table);
				Accessible_unref (cell);
				cctxt->gui_handle->handle = object;
				return error;
			}
			if (g_ascii_strcasecmp (name, "edit") == 0) {
				GSList *l = g_slist_last (cctxt->req->arg_list);
				cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list, l->data);
				g_print ("Table cell is text box %s - %d\n", __FILE__, __LINE__);
				error = text_main (cctxt, LDTP_CMD_SETTEXTVALUE);
				cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, l->data);
				SPI_freeString (name);
				Accessible_unref (action);
				Accessible_unref (table);
				Accessible_unref (cell);
				cctxt->gui_handle->handle = object;
				return error;
			}
			SPI_freeString (name);
		} //for
		Accessible_unref (action);
	} //if
	Accessible_unref (table);
	if (cell)
		Accessible_unref (cell);
	cctxt->gui_handle->handle = object;
	error =  (LDTP_ERROR_SET_TABLE_CELL_FAILED);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
	return error;
}  

static LDTPErrorCode
check_row (Accessible *object, int row, int col, FILE *log_fp)
{
	long n_rows, n_cols;
	long j, n_actions;
	LDTPErrorCode error;
	Accessible *cell;
	AccessibleTable *table;
	AccessibleAction *action;
	AccessibleStateSet *state;
	char *name = NULL;
	char msg[256];
	
	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
	n_cols = AccessibleTable_getNColumns (table);
	g_print ("Number of rows: %ld\tColumn: %ld\n", n_rows, n_cols);

	if (row < 0 || row >= n_rows) {
		g_sprintf (msg, "Row %d doesnot exist in table", row);
		log_msg (LDTP_LOG_CAUSE, msg, log_fp);
		Accessible_unref (table);
		error =  (LDTP_ERROR_ROW_DOES_NOT_EXIST);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	if (col < 0 || col >= n_cols) {
		g_sprintf (msg, "Column %d doesnot exist in table", col);
		log_msg (LDTP_LOG_CAUSE, msg, log_fp);
		Accessible_unref (table);
		error =  (LDTP_ERROR_COLUMN_DOES_NOT_EXIST);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	cell = AccessibleTable_getAccessibleAt (table, row, col);
	Accessible_unref (table);
	action = Accessible_getAction (cell);

	n_actions = AccessibleAction_getNActions (action);
	
	for (j = 0; j < n_actions; j++) {
		name = AccessibleAction_getName (action, j);                                                           
		if (g_ascii_strcasecmp (name, "toggle") == 0) { 
			state = Accessible_getStateSet (cell);
			Accessible_unref (cell);
			cell = NULL;
			if (AccessibleStateSet_contains (state, SPI_STATE_CHECKED)) {
				Accessible_unref (action);
				SPI_freeString (name);
				AccessibleStateSet_unref (state);
				log_msg (LDTP_LOG_WARNING, "Row is already checked", log_fp);
				return  (LDTP_ERROR_SUCCESS);
			}
			AccessibleStateSet_unref (state);
			if (AccessibleAction_doAction (action, j) == FALSE) {
				error =  (LDTP_ERROR_CHECK_ACTION_FAILED);
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
				return error;
			}
		}
	}
	if (cell)
		Accessible_unref (cell);
	Accessible_unref (action);
	SPI_freeString (name);
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
uncheck_row (Accessible *object, int row, int col, FILE *log_fp)
{
	long n_rows, n_cols;
	int j, n_actions;
	LDTPErrorCode error;
	Accessible *cell;
	AccessibleTable *table;
	AccessibleAction *action;
	AccessibleStateSet *state;
	char *name = NULL;
	char msg[256];
	
	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
	n_cols = AccessibleTable_getNColumns (table);
	g_print ("Number of rows: %ld\tColumn: %ld\n", n_rows, n_cols);

	if (row < 0 || row >= n_rows) {
		g_sprintf (msg, "Row %d doesnot exist in table", row);
		log_msg (LDTP_LOG_CAUSE, msg, log_fp);
		Accessible_unref (table);
		error =  (LDTP_ERROR_ROW_DOES_NOT_EXIST);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	if (col < 0 || col >= n_cols) {
		g_sprintf (msg, "Column %d doesnot exist in table", col);
		log_msg (LDTP_LOG_CAUSE, msg, log_fp);
		Accessible_unref (table);
		error =  (LDTP_ERROR_COLUMN_DOES_NOT_EXIST);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}

	cell = AccessibleTable_getAccessibleAt (table, row, col);
	Accessible_unref (table);
	action = Accessible_getAction (cell);

	n_actions = AccessibleAction_getNActions (action);
	
	for (j = 0; j < n_actions; j++) {
		name = AccessibleAction_getName (action, j);                                                           
		if (g_ascii_strcasecmp (name, "toggle") == 0) { 
			state = Accessible_getStateSet (cell);
			Accessible_unref (cell);
			cell = NULL;
			if (AccessibleStateSet_contains (state, SPI_STATE_CHECKED) == FALSE) {
				Accessible_unref (action);
				SPI_freeString (name);
				AccessibleStateSet_unref (state);
				log_msg (LDTP_LOG_WARNING, "Row is already unchecked", log_fp);
				return  (LDTP_ERROR_SUCCESS);
			}
			AccessibleStateSet_unref (state);
			if (AccessibleAction_doAction (action, j) == FALSE) {
				error =  (LDTP_ERROR_UNCHECK_ACTION_FAILED);
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
				return error;
			}
		}
	}
	if (cell)
		Accessible_unref (cell);
	Accessible_unref (action);
	SPI_freeString (name);
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
get_row_count (Accessible *object, GSList **l)
{
	long n_rows;
	AccessibleTable *table;

	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
  
	g_print ("table - number of rows:%ld\n", n_rows);

	/*IS THIS CONDITION REQUIRED
	  if (n_rows == 0)
	  {
	  log_msg (LDTP_LOG_WARNING, "No Rows in Table ", log_fp);
	  return 0;
	  }
	*/
	Accessible_unref (table);
	*l = g_slist_prepend (*l, g_strdup_printf ("%ld", n_rows));
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
select_row_partial_match (Accessible *object, char *row_text, FILE *log_fp)
{
	long i, j;
	SPIBoolean flag = FALSE;
	long n_rows, n_cols;
	LDTPErrorCode error;
	Accessible *cell;
	AccessibleTable *table;
	char msg[256];

	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
	n_cols = AccessibleTable_getNColumns (table);
	g_print ("Number of rows: %ld\tColumn: %ld\n", n_rows, n_cols);

	for (i = 0; i < n_rows; i++) {
		for (j = 0; j < n_cols; j++) {
			long child_count;
			cell = AccessibleTable_getAccessibleAt (table, i, j);
			child_count = Accessible_getChildCount (cell);
			if (child_count > 0) {
				long k;
				char *name;
				Accessible *child;
				for (k = 0; k < child_count; k++) {
					child = Accessible_getChildAtIndex (cell, k);
					name = Accessible_getName (child);
					g_print ("name =%s\n", name);
					if (strstr (name, row_text) != NULL) {
						SPI_freeString (name);
						if (Accessible_isComponent (cell)) {
							SPIBoolean flag;
							AccessibleComponent *accessible_component;
							accessible_component	= Accessible_getComponent (cell);
							flag = AccessibleComponent_grabFocus (accessible_component);
							Accessible_unref (accessible_component);
							if (flag == FALSE) {
								Accessible_unref (child);
								Accessible_unref (cell);
								error =  (LDTP_ERROR_UNABLE_TO_GRAB_FOCUS);
								log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
								return error;
							}
						}
						Accessible_unref (child);
						Accessible_unref (cell);
						flag = TRUE;
						break;
					} // if
					else
						SPI_freeString (name);
					Accessible_unref (child);
				} // for
			} else {
				char *name;
				name = Accessible_getName (cell);
				/*
				  FIXME: Use *utf8* function
				*/
				if (strstr (name, row_text) != NULL) {
					if (Accessible_isComponent (cell)) {
						SPIBoolean flag;
						AccessibleComponent *accessible_component;
						accessible_component = Accessible_getComponent (cell);
						flag = AccessibleComponent_grabFocus (accessible_component);
						Accessible_unref (accessible_component);
						if (flag == FALSE) {
							Accessible_unref (cell);
							error =  (LDTP_ERROR_UNABLE_TO_GRAB_FOCUS);
							log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
							SPI_freeString (name);
							return error;
						}
					}
					SPI_freeString (name);
					Accessible_unref (cell);
					flag = TRUE;
				} 
			}	
			Accessible_unref (cell);
		} // for j
		if (flag == TRUE)
			break;
	} // for i

	Accessible_unref (table);
	if (flag == FALSE) {
		g_sprintf (msg, "Unable to find %s in table", row_text);
		log_msg (LDTP_LOG_CAUSE, msg, log_fp);
		error =  (LDTP_ERROR_UNABLE_TO_SELECT_ROW);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
		return error;
	}
	return  (LDTP_ERROR_SUCCESS);
}

static LDTPErrorCode
verify_partial_cell_value (LDTPClientContext* cctxt)
{
	char *text;
	long row, column, n_rows, n_cols;
	GSList *l;
	LDTPErrorCode error;
	int  child_type;
	long offset, child_count;
	char *name = NULL;  

	AccessibleTable *table;
	Accessible *child_object;
	Accessible *object = cctxt->gui_handle->handle;

	l = cctxt->req->arg_list;
	if (l && l->data) {
		row = atol (l->data);
		l = l->next;
		if (l && l->data)
			column = atol (l->data);
	}

	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
	n_cols = AccessibleTable_getNColumns (table);
 
	if (n_rows < row) {
		Accessible_unref (table);
		error =  (LDTP_ERROR_ACTUAL_ROW_COUNT_LESS_THAN_GIVEN_ROW_COUNT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}
	if (n_cols < column) {
		Accessible_unref (table);
		error =  (LDTP_ERROR_ACTUAL_COLUMN_COUNT_LESS_THAN_GIVEN_COLUMN_COUNT);
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		return error;
	}  
	g_print ("Table - number of rows:%ld\tColumn: %ld\n", n_rows, n_cols);
	child_object = AccessibleTable_getAccessibleAt (table, row, column);

	do { 
		child_count = Accessible_getChildCount (child_object);
		if (child_count > 0) {
			Accessible *tmp_child;
			tmp_child = child_object;
			child_object = Accessible_getChildAtIndex (child_object, 0);
			Accessible_unref (tmp_child);
		}
	} while (child_count > 0);

	cctxt->gui_handle->handle = child_object;
	if (Accessible_isComponent (child_object)) {
		child_type = get_object_type (child_object);
		g_print ("Child type is %d ", child_type);
		if (child_type == SPI_ROLE_TABLE_CELL) {
			if (Accessible_isText (child_object)) {	
				AccessibleText *text_object;
				GSList *l = g_slist_last (cctxt->req->arg_list);
				cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list, l->data);

				text_object = Accessible_getText (child_object);
				offset = AccessibleText_getCaretOffset (text_object);
				text = AccessibleText_getText (text_object, 0, -1);

				g_print ("Table cell is a text object\n");
				error = text_main (cctxt, LDTP_CMD_VERIFYPARTIALMATCH);
				cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, l->data);

				SPI_freeString (name);
				SPI_freeString (text);

				Accessible_unref (table);
				Accessible_unref (text_object);
				Accessible_unref (child_object);
				cctxt->gui_handle->handle = object;
				return error;				
			}
		}
		else if (child_type == SPI_ROLE_TEXT) {
			GSList *l = g_slist_last (cctxt->req->arg_list);
			cctxt->req->arg_list = g_slist_prepend (cctxt->req->arg_list, l->data);
			g_print ("Table cell is text box \n");
			error = text_main (cctxt, LDTP_CMD_VERIFYPARTIALMATCH);
			cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, l->data);
			Accessible_unref (table);
			Accessible_unref (child_object);
			cctxt->gui_handle->handle = object;
			return error;  
		}
	} //if
	Accessible_unref (table);
	Accessible_unref (child_object);
	cctxt->gui_handle->handle = object;
	error =  (LDTP_ERROR_VERIFY_TABLE_CELL_PARTIAL_MATCH_FAILED);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
	return error;
}

static LDTPErrorCode
get_row_index (Accessible *object, GSList **l, FILE *log_fp)
{
	long i, j;
	long n_rows, n_cols;
	char *name;
	char *row_text;
	LDTPErrorCode error;
	Accessible *cell;
	AccessibleTable *table;
	char msg[256];

	table = Accessible_getTable (object);
	n_rows = AccessibleTable_getNRows (table);
	n_cols = AccessibleTable_getNColumns (table);
	g_print ("Number of rows: %ld\tColumn: %ld\n", n_rows, n_cols);
	row_text = (*l)->data;

	for (i = 0; i < n_rows; i++) {
		for (j = 0; j < n_cols; j++) {
			long child_count;
			cell = AccessibleTable_getAccessibleAt (table, i, j);
			child_count = Accessible_getChildCount (cell);
			if (child_count > 0) {
				long k;
				Accessible *child;
				for (k = 0; k < child_count; k++) {
					child = Accessible_getChildAtIndex (cell, k);
					name = Accessible_getName (child);
					if (g_utf8_collate (name, row_text) == 0) {
						SPI_freeString (name);
						Accessible_unref (child);
						Accessible_unref (cell);
						Accessible_unref (table);
						*l = g_slist_prepend (*l, g_strdup_printf ("%ld", i));
						return  (LDTP_ERROR_SUCCESS);
					} // if
					SPI_freeString (name);
					Accessible_unref (child);
				} // for
			} // if
			else {
				name = Accessible_getName (cell);
				g_print ("Name = %s, Row Text = %s\n", name, row_text);
				if (g_utf8_collate (name, row_text) == 0) {
					SPI_freeString (name);
					Accessible_unref (cell);
					Accessible_unref (table);
					*l = g_slist_prepend (*l, g_strdup_printf ("%ld", i));
					return  (LDTP_ERROR_SUCCESS);
				}
				SPI_freeString (name);
			}
			Accessible_unref (cell);
		} // for j
	} // for i

	Accessible_unref (table);
	g_sprintf (msg, "Unable to find %s in table", row_text);
	*l = g_slist_prepend (*l, g_strdup_printf ("%ld", -1L));
	log_msg (LDTP_LOG_CAUSE, msg, log_fp);
	error =  (LDTP_ERROR_UNABLE_TO_GET_ROW_INDEX);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

/*
  Single click row
*/
static LDTPErrorCode
single_click_row (Accessible *object, char *row_text, FILE *log_fp)
{
	long x, y, height, width;
	SPIBoolean flag = FALSE;
	LDTPErrorCode error;
	Accessible *cell;
	AccessibleComponent *component;

	long row = -1;
	long column = -1;

	cell = get_row (object, row_text, &row, &column, log_fp);
	if (cell) {
		if (Accessible_isComponent (cell))
			component = Accessible_getComponent (cell);
		else {
			Accessible_unref (cell);
			error =  (LDTP_ERROR_OBJ_NOT_COMPONENT_TYPE);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
		AccessibleComponent_getExtents (component, &x, &y, &width, &height, SPI_COORD_TYPE_SCREEN);
		/* NOTE: Some widgets doesnot sense the double click event if they are performed exactly on the 
		 * border. In order to take care of those situtations also we make adjustments in the x and y value
		 * to fire the event at the center of the object.
		 */
		x = x + width / 2;
		y = y + height / 2;
		flag = AccessibleComponent_grabFocus (component);
		Accessible_unref (cell);
		Accessible_unref (component);
		if (!flag) {
			error =  (LDTP_ERROR_UNABLE_TO_GRAB_FOCUS);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
		flag = SPI_generateMouseEvent (x, y, "b1c");
		if (flag)
			return  (LDTP_ERROR_SUCCESS);
		else {
			error =  (LDTP_ERROR_CLICK_FAILED);
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
	}
	error =  (LDTP_ERROR_UNABLE_TO_GET_CELL_HANDLE_FAILED);
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}

LDTPErrorCode
table_main (LDTPClientContext* cctxt, int command)
{
	LDTPErrorCode error;
	switch (command) {
	case LDTP_CMD_SELECTLASTROW:
		error = select_last_row (cctxt->gui_handle->handle, cctxt->log_fp);
		break;
	case LDTP_CMD_SELECTROW:
		g_print ("Select row: %s\n", (char *)cctxt->req->arg_list->data);
		error = select_row (cctxt, cctxt->gui_handle->handle,
				    (char *)cctxt->req->arg_list->data, cctxt->log_fp);
		break;
	case LDTP_CMD_DOUBLECLICK:
		error = double_click (cctxt->gui_handle->handle,
				      cctxt->log_fp);
		break;
	case LDTP_CMD_DOUBLECLICKROW:
		error = double_click_row (cctxt->gui_handle->handle,
					  cctxt->req->arg_list->data, cctxt->log_fp);
		break;
	case LDTP_CMD_VERIFYTABLECELL:
		error = verify_cell_value (cctxt);
		break;
	case LDTP_CMD_VERIFYPARTIALTABLECELL:
		error = verify_partial_cell_value (cctxt);
		break;
	case LDTP_CMD_SETCELLVALUE:
		error = set_cell_value (cctxt);
		break;
	case LDTP_CMD_SETTEXTVALUE: {
		if (Accessible_isText (cctxt->gui_handle->handle)) {
			Accessible *tmp_object = cctxt->gui_handle->handle;
			cctxt->gui_handle->handle = Accessible_getText (tmp_object);
			if (cctxt->gui_handle->handle) {
				error = text_main (cctxt, command);
				Accessible_unref (cctxt->gui_handle->handle);
			} else {
				g_print ("%s - %d\n", __FILE__, __LINE__);
				error = LDTP_ERROR_UNABLE_TO_SET_TEXT;
				log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
			}
			cctxt->gui_handle->handle = tmp_object;
		} else {
			g_print ("%s - %d\n", __FILE__, __LINE__);
			error = LDTP_ERROR_UNABLE_TO_SET_TEXT;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), cctxt->log_fp);
		}
		break;
	}
	case LDTP_CMD_GETROWCOUNT:
		error = get_row_count (cctxt->gui_handle->handle, &cctxt->req->arg_list);
		if (error == LDTP_ERROR_SUCCESS) {
			cctxt->resp->data = cctxt->req->arg_list->data;
			cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
			cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, cctxt->req->arg_list->data);
		}
		break;
	case LDTP_CMD_SINGLECLICKROW:
		error = single_click_row (cctxt->gui_handle->handle, cctxt->req->arg_list->data, cctxt->log_fp);
		break;		
	case LDTP_CMD_CHECKROW: {
		GSList *l;
		long row = 0;
		long col = 0;
		l = cctxt->req->arg_list;
		if (l && l->data) {
			row = atol (l->data);
			l = l->next;
			if (l && l->data)
				col = atol (l->data);
		}
		error = check_row (cctxt->gui_handle->handle, row, col, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_UNCHECKROW: {
		GSList *l;
		long row = 0;
		long col = 0;
		l = cctxt->req->arg_list;
		if (l && l->data) {
			row = atol (l->data);
			l = l->next;
			if (l && l->data)
				col = atol (l->data);
		}
		error = uncheck_row (cctxt->gui_handle->handle, row, col, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_SELECTROWPARTIALMATCH:
		error = select_row_partial_match (cctxt->gui_handle->handle,
						  cctxt->req->arg_list->data,
						  cctxt->log_fp);
		break;
	case LDTP_CMD_SELECTROWINDEX: {
		long row = 0;
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			row = atol (cctxt->req->arg_list->data);
		g_print ("Select row: %ld\n", row);
		error = select_row_index (cctxt->gui_handle->handle, row, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_DOESROWEXIST:
		error = does_row_exist (cctxt->gui_handle->handle,
					cctxt->req->arg_list->data,
					cctxt->log_fp);
		break;
	case LDTP_CMD_GETCELLVALUE:
		error = get_cell_value (cctxt);
		/*
		  NOTE: We no need to copy data to cctxt->resp->data, as the get_cell_value
		  function will already have the required values on success
		*/
		break;
	case LDTP_CMD_GETTABLEROWINDEX:
		error = get_row_index (cctxt->gui_handle->handle,
				       &cctxt->req->arg_list, cctxt->log_fp);
		if (error == LDTP_ERROR_SUCCESS) {
			cctxt->resp->data = cctxt->req->arg_list->data;
			cctxt->resp->data_len = g_utf8_strlen (cctxt->resp->data, -1);
			cctxt->req->arg_list = g_slist_remove (cctxt->req->arg_list, cctxt->req->arg_list->data);
		}
		break;
	case LDTP_CMD_SORTCOLUMNINDEX: {
		long col = 0;
		if (cctxt->req->arg_list && cctxt->req->arg_list->data)
			col = atol (cctxt->req->arg_list->data);
		g_print ("Sort column: %ld\n", col);
		error = sort_column_index (cctxt->gui_handle->handle, col, cctxt->log_fp);
		break;
	}
	case LDTP_CMD_SORTCOLUMN:
		error = sort_column (cctxt->gui_handle->handle,
				     cctxt->req->arg_list->data,
				     cctxt->log_fp);
		break;
	case LDTP_CMD_KBDENTER:
		error = device_main (cctxt, command);
		break;
	default:
		error = LDTP_ERROR_COMMAND_NOT_IMPLEMENTED;
	}
	return error;
}
