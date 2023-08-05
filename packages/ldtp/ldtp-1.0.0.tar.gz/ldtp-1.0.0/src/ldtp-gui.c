/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Nagappan A <nagappan@gmail.com>
 *    Poornima <pnayak@novell.com>
 *    Premkumar J <jpremkumar@novell.com>
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
#include "localization.h"
#include "ldtp-command.h"

extern gboolean ldtp_debug;
extern gint ldtp_gui_timeout;
extern gint ldtp_obj_timeout;
static char *last_new_context = NULL;
static char *last_existing_context = NULL;
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

extern GHashTable *client_context;
extern pthread_mutex_t cb_mutex;

static struct {
	int states_count;
	int states[10];
} state_list[80] = {
	{0, {0}},  // INVALID 0
	{0, {0}},  // ACCEL_LABEL 1
	{5, { SPI_STATE_ENABLED, SPI_STATE_MODAL, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE }},  // ALERT 2
	{0, {0}},  // ANIMATION 3
	{0, {0}},  // ARROW 4
	{0, {0}},  // CALENDAR 5
	{0, {0}},  //CANVAS 6
	{2, {SPI_STATE_FOCUSABLE, SPI_STATE_VISIBLE}},  // CHECK_BOX 7
	{3, { SPI_STATE_ENABLED, SPI_STATE_SELECTABLE, SPI_STATE_SENSITIVE}},  // CHECK_MENU_ITEM 8

	{0, {0}},  // COLOR_CHOOSER 9
	{0, {0}},  // COLUMN_HEADER 10

	{4,{SPI_STATE_ENABLED, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE}},  // COMBO_BOX 11

	{0, {0}},  // DATE_EDITOR 12
	{0, {0}},  // DESKTOP_ICON 13
	{4, { SPI_STATE_ENABLED, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE }},  // DESKTOP_FRAME 14
	{0, {0}},  // DIAL 15

	{4, { SPI_STATE_ENABLED, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE}}, // DIALOG 16

	{0, {0}},  // DIRECTORY_PANE 17
	{0, {0}},  // DRAWING_AREA 18
	{0, {0}},  // FILE_CHOOSER 19

	{5, { SPI_STATE_ENABLED, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VERTICAL, SPI_STATE_VISIBLE	}},  // FILLER 20

	{0, {0}},  // FONT_CHOOSER 21 

	{5, { SPI_STATE_ENABLED, SPI_STATE_RESIZABLE, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE }},  // FRAME 22

	{0, {0}},  // GLASS_PANE 23
	{5, { SPI_STATE_ENABLED, SPI_STATE_FOCUSABLE, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE }},  // HTML_CONTAINER 24
	{4, { SPI_STATE_FOCUSABLE, SPI_STATE_SELECTABLE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE }},  // ICON 25
	{0, {0}},  // IMAGE 26
	{0, {0}},  // INTERNAL_FRAME 27
	{4, { SPI_STATE_ENABLED, SPI_STATE_MULTI_LINE, SPI_STATE_SENSITIVE, SPI_STATE_VISIBLE }}, // LABEL 28
	{5, { SPI_STATE_ENABLED, SPI_STATE_FOCUSABLE, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE }},  // LAYERED_PANE 29

	{6, { SPI_STATE_ENABLED, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_FOCUSABLE, SPI_STATE_SELECTABLE, SPI_STATE_VISIBLE}},  // LIST 30

	{6, { SPI_STATE_ENABLED, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE}},  //LIST_ITEM 31

	{1, { SPI_STATE_ENABLED}}, //MENU 32

	{4, { SPI_STATE_ENABLED, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE}},//MENU_BAR 33

	{1, { SPI_STATE_ENABLED }}, // MENU_ITEM 34

	{0, {0}},//OPTION_PANE 35

	{6, {SPI_STATE_ENABLED, SPI_STATE_MULTI_LINE, SPI_STATE_SELECTABLE, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE}}, // PAGE_TAB 36

	{4, { SPI_STATE_ENABLED, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE }},//PAGE_TAB_LIST 37

	{3, {SPI_STATE_ENABLED, SPI_STATE_SENSITIVE, SPI_STATE_VISIBLE }}, // PANEL 38

	{0, {0}}, //PASSWORD_TEXT 39
	{0, {0}}, //POPUP_MENU 40
	{0, {0}}, //PROGRESS_BAR 41

	{4, { SPI_STATE_ENABLED, SPI_STATE_VISIBLE, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING}}, //PUSH_BUTTON 42

	{4, { SPI_STATE_ENABLED, SPI_STATE_FOCUSABLE, SPI_STATE_SENSITIVE, SPI_STATE_VISIBLE }},//RADIO_BUTTON 43

	{3, { SPI_STATE_ENABLED, SPI_STATE_SELECTABLE, SPI_STATE_SENSITIVE }},//RADIO_MENU_ITEM 44

	{0, {0}},//ROOT_PANE 45
	{0, {0}},//ROW_HEADER 46
	{2, { SPI_STATE_ENABLED, SPI_STATE_SENSITIVE }},//SCROLL_BAR 47

	{5, { SPI_STATE_ENABLED, SPI_STATE_FOCUSABLE, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE}},//SCROLL_PANE 48

	{3, { SPI_STATE_ENABLED, SPI_STATE_SELECTABLE, SPI_STATE_SENSITIVE }}, //SEPARATOR 49

	{0, {0}},//SLIDER 50

	{6, { SPI_STATE_EDITABLE, SPI_STATE_ENABLED, SPI_STATE_FOCUSABLE, SPI_STATE_SENSITIVE, SPI_STATE_SINGLE_LINE, SPI_STATE_VISIBLE }}, //SPIN_BUTTON 51

	{6, { SPI_STATE_ENABLED, SPI_STATE_FOCUSABLE, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VERTICAL, SPI_STATE_VISIBLE}}, //SPLIT_PANE 52

	{4, { SPI_STATE_ENABLED, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE }},//STATUS_BAR 53

	{6, {SPI_STATE_VISIBLE, SPI_STATE_SHOWING, SPI_STATE_SENSITIVE, SPI_STATE_MANAGES_DESCENDANTS, SPI_STATE_FOCUSABLE, SPI_STATE_ENABLED	}},//TABLE 54

	{6, { SPI_STATE_ENABLED, SPI_STATE_FOCUSABLE, SPI_STATE_SINGLE_LINE, SPI_STATE_TRANSIENT, SPI_STATE_SHOWING, SPI_STATE_VISIBLE }},   //TABLE_CELL 55

	{6, { SPI_STATE_ENABLED, SPI_STATE_SELECTABLE, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_FOCUSABLE, SPI_STATE_VISIBLE}}, //TABLE_COLUMN_HEADER 56

	{0, {0}},//TABLE_ROW_HEADER 57
	{0, {0}},//TEAROFF_MENU_ITEM 58
	{5, { SPI_STATE_ENABLED, SPI_STATE_RESIZABLE, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE }}, //TERMINAL 59

	{7, {SPI_STATE_EDITABLE, SPI_STATE_ENABLED, SPI_STATE_FOCUSABLE, SPI_STATE_MULTI_LINE, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE }}, //TEXT 60

	{2, {SPI_STATE_ENABLED, SPI_STATE_FOCUSABLE}},//TOGGLE_BUTTON 61

	{0, {SPI_STATE_ENABLED,SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE}},//TOOL_BAR 62
	{0, {0}},//TOOL_TIP 63
	{0, {0}},//TREE 64
	{0, {0}},//TREE_TABLE 65

	{5, { SPI_STATE_ENABLED, SPI_STATE_HORIZONTAL, SPI_STATE_SENSITIVE, SPI_STATE_SHOWING, SPI_STATE_VISIBLE}}, //UNKNOWN 66

	{2, { SPI_STATE_ENABLED, SPI_STATE_SENSITIVE }},//VIEWPORT 67
	{0, {0}},//WINDOW 68
	{0, {0}},//EXTENDED 69
	{0, {0}},//HEADER 70
	{0, {0}},//FOOTER 71
	{0, {0}},//PARAGRAPH 72
	{0, {0}},//RULER 73
	{0, {0}},//APPLICATION 74
	{0, {0}},//AUTOCOMPLETE 75
	{0, {0}},//EDITBAR 76
	{0, {0}},//LAST_DEFINED 77
	{0, {0}},//CALENDAR_VIEW 78
	{0, {0}},//CALENDAR_EVENT 79
};			

static int
push (struct node *head, int value)
{
	struct node *new_node;

	new_node = (struct node *) malloc (sizeof (struct node));
	if (new_node) {
		new_node->child_index = value;
		new_node->next = head->next;
		head->next = new_node;
		return 1;
	}
	else
		return 0;
}

static int
pop (struct node *head)
{
	struct node *temp;
	int index;
	if (head->next) {
		index = head->next->child_index;
		temp = head->next;
		head->next = temp->next;
		g_free (temp);
	}
	else
		index = -1;
	return index;
}

static struct node*
init_stack ()
{
	struct node *head;
	head = g_new0 (struct node, 1);
	if (head) {
		head->child_index = -1;
		head->next = NULL;
		return head;
	}
	else
		return NULL;
}

static struct node*
trace_path_to_parent (GHashTable *context, char *context_name,
		      GHashTable *component, char **class_type, FILE *log_fp,
		      LDTPClientContext *cctxt, LDTPErrorCode *err)
{
	struct node *head;
	char *parent_name;
	char *prop = NULL;

	head = init_stack ();
	if (!head) {
		log_msg (LDTP_LOG_CAUSE, "Unable to initialize stack", log_fp);
		return NULL;
	}
	else {
		char *tmp = NULL;
		prop = get_property (component, "child_index", log_fp);
		if (!prop) {
			log_msg (LDTP_LOG_CAUSE, "Unable to get_property", log_fp);
			return NULL;
		}
		if (*class_type == NULL)
			*class_type = get_property (component, "class", log_fp);
		push (head, atoi (prop));
		parent_name = get_property (component, "parent", log_fp);
		if (ldtp_debug && parent_name && context_name)
			g_print ("Parent name: %s - Context name: %s\n", parent_name, context_name);
		while (1) {
			if (g_utf8_strchr (context_name, -1, ' ') != NULL) {
				char *str = escape_character (context_name, ' ');
				tmp = g_strdup_printf ("*%s", str);
				g_free (str);
			}
			else
				tmp = g_strdup_printf ("*%s", context_name);
			g_print ("TMP: %s\n", tmp);
			if (!context_name || !parent_name ||
			    !g_utf8_collate (context_name, parent_name) ||
			    g_pattern_match_simple (context_name, parent_name) ||
			    g_pattern_match_simple (tmp, parent_name)) {
				g_free (tmp);
				break;
			}
			g_free (tmp);
			component = (GHashTable *) get_property (context, parent_name, log_fp);
			if (component) {
				prop = get_property (component, "child_index", log_fp);
				if (!prop) {
					log_msg (LDTP_LOG_CAUSE, "Unable to get_property", log_fp);
					return NULL;
				}
				push (head, atoi (prop));
				parent_name = get_property (component, "parent", log_fp);
				if (ldtp_debug && parent_name && context_name)
					g_print ("InsideWhile: Parent name: %s - Context name: %s - child index: %s\n",
						 parent_name, context_name, prop);
			}
			else
				break;
		}
	}
	return head;
}

int
object_state_contains (Accessible *object, int control_type, FILE *log_fp)
{
	int i;
	int count;
	char msg [256];
	char *name = NULL;
	SPIBoolean object_state;
	AccessibleStateSet *state;

	name = Accessible_getRoleName (object);
	state = Accessible_getStateSet (object);
	count = state_list [control_type].states_count;

	g_print ("State check count: %d - Control type: %d\n", count, control_type);

	for (i = 0; i < count; i++) {
		object_state = AccessibleStateSet_contains (state,
							    state_list [control_type].states [i]);
		if (object_state == FALSE) {
			g_sprintf (msg, "%s required state %d is not enabled", name, i);
			log_msg (LDTP_LOG_CAUSE, msg, log_fp);
			SPI_freeString (name);
			AccessibleStateSet_unref (state);
			return -1;
		}
	}
	SPI_freeString (name);
	AccessibleStateSet_unref (state);
	return 0;
}

int
wait_till_object_state_contains (Accessible *object, int control_type, FILE *log_fp)
{
	int i;
	int count;
	char msg [256];
	char *name = NULL;
	gboolean flag = FALSE;
	SPIBoolean object_state;
	AccessibleStateSet *state;

	int time_wait = ldtp_obj_timeout;
	time_t start, cur;

	/*
	  Copied from LTFX source code
	*/
	start = cur = time (NULL);

	state = Accessible_getStateSet (object);
	count = state_list [control_type].states_count;

	g_print ("State check count: %d - Control type: %d\n", count, control_type);

	if (!ldtp_obj_timeout) {
		time_wait = 5; // Max wait for 5 seconds
	}

	while ((difftime (cur, start) < time_wait) && (state != NULL)) {
		sleep (1);

		cur = time (NULL);
		flag = TRUE;
		for (i = 0; i < count; i++) {
			object_state = AccessibleStateSet_contains (state,
								    state_list [control_type].states [i]);
			if (ldtp_debug)
				g_print ("Object state: %d - %d\n", i, object_state);
			if (object_state == FALSE) {
				flag = FALSE;
				break;
			}
		}
		if (state) {
			AccessibleStateSet_unref (state);
			state = NULL;
		}
		if (flag)
			break;
		state = Accessible_getStateSet (object);
	}
	if (flag) {
		sleep (1);
		return 0;
	}
	name = Accessible_getRoleName (object);
	if (name) {
		g_sprintf (msg, "%s required states are not enabled", name);
		log_msg (LDTP_LOG_CAUSE, msg, log_fp);
		SPI_freeString (name);
	}
	if (state)
		AccessibleStateSet_unref (state);
	return -1;
}

static void
window_info_added_hashtable (char *window_name, LDTPClientContext* cctxt, LDTPErrorCode* err)
{
	if (!cctxt || !window_name)
		*err = LDTP_ERROR_ARGUMENT_NULL;

	if (!client_context)
		client_context = g_hash_table_new_full (&g_str_hash, &g_str_equal, key_destroy_func, NULL);

	g_hash_table_insert (client_context, g_strdup ((gchar *)window_name), cctxt);
	*err = LDTP_ERROR_SUCCESS;
}

/*
  Get accessible handle of the given application
*/
static Accessible*
get_accessible_app_handle (char *app_name)
{
	long i, num_apps;
	Accessible *desktop;

	if (app_name == NULL)
		return NULL;

	/*
	  Get SPI handle of desktop 0
	  FIXME: Need to change the hardcoded value of desktop
	*/
	desktop = SPI_getDesktop (0);

	if (!desktop)
		return NULL;
	/*
	  Get the total count of childs in the desktop
	*/
	num_apps = Accessible_getChildCount (desktop);
	/*
	  Traverse the list of application handle and if application
	  name matches, then return the handle
	*/
	for (i = 0; i < num_apps; i++) {
		char *name, *descr;
		char *window_title = NULL;
		Accessible *child;

		child = Accessible_getChildAtIndex (desktop, i);
		if (!child)
			continue;
		/*
		  Application name of child handle
		*/
		name = Accessible_getName (child);
		/*
		  Description of child handle
		*/
		descr = Accessible_getDescription (child);

		/*
		  Incase of OO.o due to spaces, string compare gives different result.
		  Found because of extra spaces. Now stripped it ;)
		*/
		if (name && g_utf8_strchr (name, -1, ' ') != NULL) {
			gchar *str = NULL;
			str = escape_character (name, ' ');
			window_title = str;
		}
		else
			window_title = g_strdup (name);

		if (name)
			SPI_freeString (name);
		if (descr)
			SPI_freeString (descr);
		if (window_title == NULL) {
			Accessible_unref (child);
			Accessible_unref (desktop);
			return NULL;
		}
		g_print ("Accessible application name: %s\n", window_title);
		if (g_ascii_strcasecmp (window_title, app_name) == 0) {
			/*
			  Application name matched
			*/
			char *role_name;

			role_name = Accessible_getRoleName (child);
			if (ldtp_debug && role_name)
				g_print ("Application: %s \t- Role: %s\n", window_title, role_name);
			SPI_freeString (role_name);

			Accessible_unref (desktop);
			g_free (window_title);
			return child;
		}
		g_free (window_title);
		Accessible_unref (child);
	}
	Accessible_unref (desktop);
	return NULL;
}

/*
  Get window list
*/
GHashTable*
get_window_list (void)
{
	long i, num_apps;
	Accessible *desktop;
	GHashTable *table = g_hash_table_new (&g_str_hash, &g_str_equal);

	/*
	  Get SPI handle of desktop 0
	  FIXME: Need to change the hardcoded value of desktop
	*/
	desktop = SPI_getDesktop (0);

	/*
	  Get the total count of childs in the desktop
	*/
	num_apps = Accessible_getChildCount (desktop);
	/*
	  Traverse the list of application handle and if application
	  name matches, then return the handle
	*/
	for (i = 0; i < num_apps; i++) {
		char *name;
		char *window_title;
		Accessible *child;

		child = Accessible_getChildAtIndex (desktop, i);
		if (!child)
			continue;
		/*
		  Application name of child handle
		*/
		name = Accessible_getName (child);
		/*
		  Incase of OO.o due to spaces, string compare gives different result.
		  Found because of extra spaces. Now stripped it ;)
		*/
		if (g_utf8_strchr (name, -1, ' ') != NULL) {
			window_title = escape_character (name, ' ');
		}
		else
			window_title = g_strdup (name);

		if (name)
			SPI_freeString (name);
		if (window_title == NULL) {
			Accessible_unref (child);
			Accessible_unref (desktop);
			continue;
		}
		g_print ("Accessible application name: %s\n", window_title);
		if (table)
			g_hash_table_insert (table, g_strdup (window_title), NULL);
		Accessible_unref (child);
		g_free (window_title);
	}
	Accessible_unref (desktop);
	return table;
}

/*
 * To get accessible handle of the context (window)
 */
static Accessible*
get_accessible_context_handle (Accessible *app_handle, char *context)
{
	long i, j = 0, k = 1;
	long child_count;
	char *tmp  = NULL;
	char *name = NULL;
	char *child_name  = NULL;
	char *window_name = NULL;
#ifdef ENABLE_LOCALIZATION
	char *temp = NULL;
#endif
	AccessibleRole role;
	Accessible *child = NULL;
	GHashTable *tmpTable = NULL;
	GPatternSpec *context_pattern = NULL;
	GPatternSpec *last_existing_context_pattern = NULL;

	if (!app_handle || !context) {
		g_print ("accessible_context_handle: NULL arguments\n");
		return NULL;
	}

	context_pattern = g_pattern_spec_new (context);
	if (last_existing_context)
		last_existing_context_pattern = g_pattern_spec_new (last_existing_context);

	child_count = Accessible_getChildCount (app_handle);
	name = Accessible_getName (app_handle);
	if (ldtp_debug && name)
		g_print ("Child count: %ld of %s\n", child_count, name);
	SPI_freeString (name);
	if (child_count > 0) {
		tmpTable = g_hash_table_new (&g_str_hash, &g_str_equal);
		for (i = 0; i < child_count; i++) {
			child = Accessible_getChildAtIndex (app_handle, i);
			if (!child)
				continue;
			/*
			  Application name of child handle
			*/
			child_name = Accessible_getName (child);
			role = Accessible_getRole (child);
			if (child_name) {
				g_print ("child_name: %s\n", child_name);
				window_name = get_window_name_in_appmap_format (child_name, role);
			}
			if (!window_name) {
				gchar *tmp = g_strdup_printf ("%ld", j++);
				if (tmp) {
					window_name = get_window_name_in_appmap_format (tmp, role);
					g_free (tmp);
					tmp = NULL;
				}
			}
			if (window_name && tmpTable) {
				g_print ("window_name: %s\n", window_name);
				if (g_hash_table_lookup_extended (tmpTable, window_name, NULL, NULL) == FALSE) {
					g_hash_table_insert (tmpTable, g_strdup (window_name), NULL);
					/* Enable for debugging purpose
					   g_hash_table_foreach (tmpTable, (GHFunc)&print_tmp_table, NULL);
					*/
				} else {
					if (child_name)
						tmp = g_strdup_printf ("%s%ld", child_name, k++);
					if (window_name) {
						g_free (window_name);
						window_name = NULL;
					}
					if (tmp) {
						window_name = get_window_name_in_appmap_format (tmp, role);
						g_free (tmp);
						tmp = NULL;
					}
					if (window_name && g_hash_table_lookup_extended (tmpTable,
											  window_name,
											  NULL, NULL) == FALSE) {
						g_hash_table_insert (tmpTable, g_strdup (window_name), NULL);
					}
				}
			}
			if (last_new_context && last_existing_context) {
				g_print ("Last new: **%s** - existing: %s - context: %s - **%s**\n",
					 last_new_context, last_existing_context, context, child_name);
				if (context_pattern && child_name && last_existing_context_pattern &&
				    (g_pattern_match_string (last_existing_context_pattern, context) ||
				     (window_name && g_pattern_match_string (context_pattern, window_name)))) {
#ifdef ENABLE_LOCALIZATION
					if ((temp = ldtp_compare_with_locale (last_new_context, child_name))) {
						g_free (temp);
						g_free (window_name);
						SPI_freeString (child_name);
						if (last_existing_context_pattern)
							g_pattern_spec_free (last_existing_context_pattern);
						if (context_pattern)
							g_pattern_spec_free (context_pattern);
						return child;
					}
#else
					char *tmp = escape_character (child_name, ' ');
					if (g_utf8_collate (last_new_context, child_name) == 0 ||
					    g_utf8_collate (last_new_context, tmp) == 0 ||
					    g_pattern_match_simple (last_new_context, child_name)) {
						g_free (tmp);
						g_free (window_name);
						SPI_freeString (child_name);
						if (last_existing_context_pattern)
							g_pattern_spec_free (last_existing_context_pattern);
						if (context_pattern)
							g_pattern_spec_free (context_pattern);
						return child;
					}
					g_free (tmp);
#endif
				}
			}
#ifdef ENABLE_LOCALIZATION
			if (context && child_name &&
			    (temp = ldtp_compare_with_locale (context, child_name))) {
				g_print ("Context: %s In_Locale: %s Child_name: %s\n", context, temp, child_name);
				g_free (temp);
				g_free (window_name);
				SPI_freeString (child_name);
				if (last_existing_context_pattern)
					g_pattern_spec_free (last_existing_context_pattern);
				if (context_pattern)
					g_pattern_spec_free (context_pattern);
				return child;
			}
#else
			if (ldtp_debug && context && child_name)
				g_print ("Context: %s Child_name: %s\n", context, child_name);
			if (ldtp_debug && window_name)
				g_print ("Window name: %s\n", window_name);
			if (context_pattern && child_name &&
			    (g_pattern_match_string (context_pattern, child_name) ||
			     (window_name && g_pattern_match_string (context_pattern, window_name)))) {
				g_free (window_name);
				g_print ("Matched - Context: %s Child_name: %s\n", context, child_name);
				SPI_freeString (child_name);
				if (last_existing_context_pattern)
					g_pattern_spec_free (last_existing_context_pattern);
				if (context_pattern)
					g_pattern_spec_free (context_pattern);
				return child;
			}
#endif
			else {
				g_free (window_name);
				window_name = NULL;
				SPI_freeString (child_name);
				Accessible_unref (child);
			}
		}
	}
	if (last_existing_context_pattern)
		g_pattern_spec_free (last_existing_context_pattern);
	if (context_pattern)
		g_pattern_spec_free (context_pattern);
	return NULL;
}

/*
  Get accessible handle of the given object
*/
static Accessible*
get_accessible_component_handle (struct node *head, Accessible *context, FILE *log_fp)
{
	long i;
	char *role;
	Accessible *child, *parent;

	if (!head) {
		g_print ("Head pointer is NULL\n");
		return NULL;
	}
	i = pop (head);
	parent = context;
	while (i != -1) {
		child = Accessible_getChildAtIndex (parent, i);
		if (!child) {
			char msg [256];
			char *child_name = NULL;
			char *parent_name = NULL;
			child_name = Accessible_getName (context);
			parent_name = Accessible_getName (parent);
			if (ldtp_debug && parent_name && child_name)
				g_print ("Parent: %s - Child: %s - %ld\n", parent_name, child_name, i);
			if (parent != context)
				Accessible_unref (parent);
			g_sprintf (msg, "Unable to find child index as available in appmap");
			g_print ("%s\n", msg);
			log_msg (LDTP_LOG_CAUSE, msg, log_fp);
			SPI_freeString (child_name);
			SPI_freeString (parent_name);
			return NULL;
		}
		role = Accessible_getRoleName (child);
		if (role) {
			char *name = Accessible_getName (child);
			if (ldtp_debug && name)
				g_print ("Role: %s - %s %d - %ld\n", role, name, __LINE__, i);
			SPI_freeString (role);
			SPI_freeString (name);
		}
		if (parent != context)
			Accessible_unref (parent);
		parent = child;
		i = pop (head);
	}
	return parent;
}

char*
get_relation_name (Accessible *object, long *len)
{
	long i = 0, j = 0, k = 0;
	int max_accessible = 0;
	char *label_by = NULL;
	AccessibleRelation **relation = NULL;

	relation = Accessible_getRelationSet (object);
	if (!relation) {
		return NULL;
	}
	max_accessible = AccessibleRelation_getNTargets (*relation);
	if (max_accessible <= 0) {
		for (k = 0; relation[k] != NULL; k++)
			AccessibleRelation_unref (relation[k]);
		g_free (relation);
		return NULL;
	}
	for (i = 0; relation[i] != NULL; i++) {
		for (j = 0; j < AccessibleRelation_getNTargets (relation[i]); j++) {
			AccessibleRelationType relation_type;
			relation_type = AccessibleRelation_getRelationType (relation[i]);
			if (relation_type == SPI_RELATION_LABELED_BY ||
			    relation_type == SPI_RELATION_CONTROLLED_BY ||
			    relation_type == SPI_RELATION_LABEL_FOR) {
				char *name = NULL;
				Accessible *tmp_obj;
				//tmp_obj = AccessibleRelation_getTarget (relation[i], i);
				tmp_obj = AccessibleRelation_getTarget (relation[i], j);
				if (tmp_obj)
					name = Accessible_getName (tmp_obj);
				if (name == NULL) {
					if (ldtp_debug)
						g_print ("Relation name: NULL - %ld - %ld\n", i, j);
					if (tmp_obj)
						Accessible_unref (tmp_obj);
					for (k = 0; relation[k] != NULL; k++)
						AccessibleRelation_unref (relation[k]);
					g_free (relation);
					return NULL;
				}
				if (g_ascii_strcasecmp (name, "") == 0) {
					if (ldtp_debug)
						g_print ("Relation name: EMPTY string\n");
					SPI_freeString (name);
					if (tmp_obj)
						Accessible_unref (tmp_obj);
					for (k = 0; relation[k] != NULL; k++)
						AccessibleRelation_unref (relation[k]);
					g_free (relation);
					return NULL;
				}
				g_print ("Relation name: %s\n", name);
				label_by = g_strdup (name);
				SPI_freeString (name);
				if (Accessible_isText (tmp_obj) && len != NULL) {
					AccessibleText *text = NULL;
					text = Accessible_getText (tmp_obj);
					*len = AccessibleText_getCharacterCount (text);
					Accessible_unref (text);
				}
				Accessible_unref (tmp_obj);
				for (k = 0; relation[k] != NULL; k++)
					AccessibleRelation_unref (relation[k]);
				g_free (relation);
				return label_by;
			}
		} // for j
		AccessibleRelation_unref (relation[i]);
	} // for i
	g_free (relation);
	return NULL;
} // get_relation_name

static gboolean
is_object_matching (Accessible *object, GHashTable *comp_attributes, FILE *log_fp)
{
	char *accessible_label;
	char *hash_label;
#ifdef ENABLE_LOCALIZATION
	gchar *value;
#else
	gint value;
#endif
	/*
	 * NOTE: Checking if the obtained object is the required one 
	 * with respect to label/label_by only
	 */
	hash_label = get_property (comp_attributes, "label", log_fp);
	if (hash_label) {
		char *role;
		accessible_label = Accessible_getName (object);
		role = Accessible_getRoleName (object);
		if (role) {
			g_print ("Role: %s %d\n", role, __LINE__);
			SPI_freeString (role);
		}
		g_print ("Label: %s - %s\n", hash_label, accessible_label);
#ifdef ENABLE_LOCALIZATION
		value = ldtp_compare_with_locale (hash_label, accessible_label);
		if (value)
#else
			if (g_utf8_strchr (hash_label, -1, '_') != NULL) {
				gchar *str = NULL;
				str = escape_character (hash_label, '_');
				g_print ("Before: %s - After: %s\n", hash_label, str);
				value = g_utf8_collate (str, accessible_label);
				g_free (str);
			}
			else
				value = g_utf8_collate (hash_label, accessible_label);
		if (value == 0)
#endif
			{
				SPI_freeString (accessible_label);
				g_print ("Object matches\n");
#ifdef ENABLE_LOCALIZATION
				g_free (value);
#endif
				return TRUE;
			}
		else {
			SPI_freeString (accessible_label);
			return FALSE;
		}
	}
	else {
		hash_label = get_property (comp_attributes, "label_by", log_fp);
		if (hash_label) {
			long len = -1;
			accessible_label = get_relation_name (object, &len);
#ifdef ENABLE_LOCALIZATION
			value = ldtp_compare_with_locale (hash_label, accessible_label);
			if (value)
#else
				if (g_utf8_strchr (hash_label, -1, '_') != NULL) {
					gchar *str = NULL;
					str = escape_character (hash_label, '_');
					g_print ("Before: %s - After: %s\n", hash_label, str);
					value = g_utf8_collate (str, accessible_label);
					g_free (str);
				}
				else
					value = g_utf8_collate (hash_label, accessible_label);
			if (value == 0)
#endif
				{
					g_free (accessible_label);
					g_print ("Object matches\n");
#ifdef ENABLE_LOCALIZATION
					g_free (value);
#endif
					return TRUE;
				}
			else {
				g_free (accessible_label);
				return FALSE;
			}
		}
	}
	return TRUE;
}

static gboolean
does_window_exist (char *context, char *name, char *window_name, GPatternSpec *pattern, GPatternSpec *tmp_pattern)
{
	if (name && window_name && context &&
	    (g_utf8_collate (context, name) == 0 ||
	     (pattern && g_pattern_match_string (pattern, name)) ||
	     g_utf8_collate (context, window_name) == 0 ||
	     (pattern && g_pattern_match_string (pattern, window_name)) ||
	     (tmp_pattern && g_pattern_match_string (tmp_pattern, window_name)))) {
		g_print ("Window name matched\n");
		return TRUE;
	}
	return FALSE;
}

static gboolean
remove_tmp_entries (gpointer key, gpointer value, gpointer user_data)
{
	if (key) {
		g_free (key);
		key = NULL;
	}
	return TRUE;
}

void
print_tmp_table (char *key, char *value, char *userdata)
{
	if (key)
		g_print (":%s:\n", key);
}

static Accessible*
get_child_window_handle (Accessible *app_handle, char *context, char **window_name, gboolean *flag)
{
	long i, j = 0, k = 1;
	char *tmp  = NULL;
	char *name = NULL;
	long child_count = 0;
	Accessible *child = NULL;
	AccessibleRole role;
	GPatternSpec *pattern = NULL;
	GPatternSpec *tmp_pattern = NULL;
	GHashTable *tmpTable = NULL;

	/*
	  FIXME: If app_handle is NULL, then get the desktop handle and from there
	  search for window handle instead of directly returning from here
	*/
	if (!app_handle || !context)
		return NULL;

	*flag = FALSE;

	child_count = Accessible_getChildCount (app_handle);
	tmp = g_strdup_printf ("*%s", context);
	if (context)
		pattern = g_pattern_spec_new (context);
	if (tmp) {
		tmp_pattern = g_pattern_spec_new (tmp);
		g_free (tmp);
		tmp = NULL;
	}

	*window_name = NULL;
	tmpTable = g_hash_table_new (&g_str_hash, &g_str_equal);
	for (i = 0; i < child_count; i++) {
		child = Accessible_getChildAtIndex (app_handle, i);
		if (!child)
			continue;

		/*
		  Application name of child handle
		*/
		name = Accessible_getName (child);
		role = Accessible_getRole (child);
		if (name) {
			g_print ("child_name: %s\n", name);
			*window_name = get_window_name_in_appmap_format (name, role);
		}
		if (!*window_name) {
			gchar *tmp = g_strdup_printf ("%ld", j++);
			if (tmp) {
				*window_name = get_window_name_in_appmap_format (tmp, role);
				g_free (tmp);
				tmp = NULL;
			}
		}
		if (*window_name && tmpTable) {
			g_print ("window_name: %s\n", *window_name);
			if (g_hash_table_lookup_extended (tmpTable, *window_name, NULL, NULL) == FALSE) {
				g_hash_table_insert (tmpTable, g_strdup (*window_name), NULL);
				/* Enable for debugging purpose
				  g_hash_table_foreach (tmpTable, (GHFunc)&print_tmp_table, NULL);
				*/
			} else {
				if (name)
					tmp = g_strdup_printf ("%s%ld", name, k++);
				if (*window_name) {
					g_free (*window_name);
					*window_name = NULL;
				}
				if (tmp) {
					*window_name = get_window_name_in_appmap_format (tmp, role);
					g_free (tmp);
					tmp = NULL;
				}
				if (*window_name && g_hash_table_lookup_extended (tmpTable,
										  *window_name,
										  NULL, NULL) == FALSE) {
					g_hash_table_insert (tmpTable, g_strdup (*window_name), NULL);
					*flag = TRUE;
				}
			}
		}

		if (ldtp_debug && context && name && *window_name)
			g_print ("Search window name: %s - %s - %s\n", context, name, *window_name);
		if (does_window_exist (context, name, *window_name, pattern, tmp_pattern)) {
			SPI_freeString (name);
			if (pattern)
				g_pattern_spec_free (pattern);
			if (tmp_pattern)
				g_pattern_spec_free (tmp_pattern);
			g_hash_table_foreach_remove (tmpTable, (GHRFunc)&remove_tmp_entries, NULL);
			g_hash_table_destroy (tmpTable);
			return child;
		}
		SPI_freeString (name);
		Accessible_unref (child);
	}
	if (pattern)
		g_pattern_spec_free (pattern);
	if (tmp_pattern)
		g_pattern_spec_free (tmp_pattern);
	g_hash_table_foreach_remove (tmpTable, (GHRFunc)&remove_tmp_entries, NULL);
	g_hash_table_destroy (tmpTable);
	return NULL;
}

static Accessible*
get_window_handle (Accessible *app_handle, char *context, char **window_name, gboolean *flag)
{
	char *name = NULL;
	long i, num_apps;
	Accessible *child = NULL;
	Accessible *desktop = NULL;
	Accessible *window_handle = NULL;
	if (app_handle) {
		window_handle = get_child_window_handle (app_handle, context, window_name, flag);
		if (window_handle)
			return window_handle;
	}

	/*
	  Get SPI handle of desktop 0
	  FIXME: Need to change the hardcoded value of desktop
	*/
	desktop = SPI_getDesktop (0);

	/*
	  Get the total count of childs in the desktop
	*/
	num_apps = Accessible_getChildCount (desktop);
	/*
	  Traverse the list of application handle and if application
	  name matches, then return the handle
	*/
	for (i = 0; i < num_apps; i++) {
		child = Accessible_getChildAtIndex (desktop, i);
		if (!child)
			continue;
		/*
		  Application name of child handle
		*/
		name = Accessible_getName (child);
		if (!name) {
			Accessible_unref (child);
			continue;
		}
		/*
		  Incase of OO.o due to spaces, string compare gives different result.
		  Found because of extra spaces. Now stripped it ;)
		*/
		if (strchr (name, ' '))
			g_strstrip (name);

		g_print ("Accessible application name: %s\n", name);
		window_handle = get_child_window_handle (child, context, window_name, flag);
		if (window_handle) {
			SPI_freeString (name);
			Accessible_unref (child);
			Accessible_unref (desktop);
			return window_handle;
		}
		SPI_freeString (name);
		Accessible_unref (child);
	}
	Accessible_unref (desktop);
	return NULL;
}

void
update_cur_window_appmap_handle (LDTPClientContext* cctxt,
				 LDTPErrorCode* err)
{
	char *context = NULL;
	char *window_name = NULL;
	char *parent_name = NULL;
	gboolean flag = FALSE;
	Accessible *child = NULL;
	Accessible *parent = NULL;
	GHashTable *new_hashtable = NULL;

	context = (char *) cctxt->req->context;
	if (!context) {
		*err = LDTP_ERROR_ARGUMENT_NULL;
		g_print ("%s", ldtp_error_get_message (*err));
		return;
	}
	child = get_window_handle (cctxt->app_handle, context, &(cctxt->window_name), &flag);
	if (!child) {
		g_print ("%s - %d - Window %s not open\n", __FILE__, __LINE__, context);
		*err = LDTP_ERROR_WIN_NOT_OPEN;
		return;
	}

	/* Unable to find using the new context based on the dynamic context generated */
	window_name = cctxt->window_name;
	parent = Accessible_getParent (child);
	if (flag == FALSE && parent) {
		AccessibleRole role;
		parent_name = Accessible_getName (parent);
		if (ldtp_debug && parent_name)
			g_print ("Parent name: %s\n", parent_name);
		role = Accessible_getRole (parent) == SPI_ROLE_APPLICATION ? SPI_ROLE_APPLICATION : Accessible_getRole (child);
		window_name = get_window_name_in_appmap_format (parent_name, role);
		if (ldtp_debug && window_name && parent_name)
			g_print ("Window name - Stripped: %s - %s\n", window_name, parent_name);
		SPI_freeString (parent_name);
	}
	else
		g_print ("Unable to get parent\n");
	if (parent)
		Accessible_unref (parent);

	pthread_mutex_lock (&mutex);
	if (ldtp_debug && cctxt->window_name)
		g_print ("%s %d %s\n", __FILE__, __LINE__, cctxt->window_name);
	new_hashtable = do_remap (child, window_name, NULL, NULL, cctxt->locale_set, flag, FALSE);
	pthread_mutex_unlock (&mutex);

	if (flag == FALSE && window_name) {
		g_free (window_name);
		window_name = NULL;
	}

	if (new_hashtable) {
		char *name = NULL;

		if (!cctxt->app_map) {
			g_print ("Appmap hashtable not initalized\n");
			cctxt->app_map = g_hash_table_new (&g_str_hash, &g_str_equal);
		}
		name = Accessible_getName (child);

		if (name && window_name) {
			g_print ("Window name: %s - Stripped: %s\n", window_name, name);
		}
		SPI_freeString (name);
		Accessible_unref (child);
		if (cctxt->window_name) {
			g_print ("cctxt->window_name: %s\n", cctxt->window_name);
			pthread_mutex_lock (&mutex);
			g_hash_table_replace (cctxt->app_map, g_strdup (cctxt->window_name), new_hashtable);
			pthread_mutex_unlock (&mutex);
			pthread_mutex_lock (&cb_mutex);
			window_info_added_hashtable (cctxt->window_name, cctxt, err);
			pthread_mutex_unlock (&cb_mutex);
			if (window_name && window_name != cctxt->window_name) {
				g_free (window_name);
				window_name = NULL;
			}
		}
		else {
			*err = LDTP_ERROR_UNABLE_TO_UPDATE_APPMAP;
			g_print ("DEBUG: Window name NULL\n");
			g_hash_table_destroy (new_hashtable);
			return;
		}
	}
	else {
		Accessible_unref (child);
		g_print ("DEBUG: New hash table NULL\n");
		*err = LDTP_ERROR_UNABLE_TO_UPDATE_APPMAP;
		return;
	}
	if (ldtp_debug) {
		g_hash_table_foreach (cctxt->app_map, (GHFunc)&print_context, NULL);
	}
	*err = LDTP_ERROR_SUCCESS;
}

void
update_cur_context_appmap_handle (LDTPClientContext *cctxt,
				  LDTPErrorCode *err)
{
	char *parent_name  = NULL;
	GHashTable *context_table   = NULL;
	GHashTable *component_table = NULL;
	LDTPGuiHandle *gui_handle   = NULL;

	if (!cctxt->req->context || !cctxt->req->component) {
		*err = LDTP_ERROR_ARGUMENT_NULL;
		g_print ("%s", ldtp_error_get_message (*err));
		return;
	}
	if (cctxt->app_map == NULL) {
		*err =  (LDTP_ERROR_APPMAP_NOT_INITIALIZED);
		g_print ("%s - %d - %s\n", __FILE__, __LINE__, ldtp_error_get_message (*err));
		return;
	}
	context_table = get_object_def (cctxt->app_map, cctxt->req->context, cctxt->log_fp, TRUE);
	if (!context_table) {
		*err = LDTP_ERROR_WIN_NAME_NOT_FOUND_IN_APPMAP;
		g_print ("%s", ldtp_error_get_message (*err));
		return;
	}
	component_table = get_object_def (context_table, cctxt->req->component, cctxt->log_fp, FALSE);
	if (!component_table) {
		*err = LDTP_ERROR_OBJ_NAME_NOT_FOUND_IN_APPMAP;
		g_print ("%s", ldtp_error_get_message (*err));
		return;
	}
	parent_name = get_property (component_table, "parent", cctxt->log_fp);

	if (ldtp_debug && cctxt->window_name)
		g_print ("%s %d %s\n", __FILE__, __LINE__, cctxt->window_name);

	gui_handle = ldtp_gui_get_gui_handle (cctxt, err);
	if (*err != LDTP_ERROR_SUCCESS) {
		g_print ("Unable to get handle: %s %d\n", __FILE__, __LINE__);
		return;
	}
	pthread_mutex_lock (&mutex);
	g_hash_table_foreach_remove (context_table, remove_remapped_entry, NULL);
	do_remap (gui_handle->handle, parent_name, context_table, NULL, cctxt->locale_set, FALSE, TRUE);
	pthread_mutex_unlock (&mutex);
	Accessible_unref (gui_handle->handle);
	*err = LDTP_ERROR_SUCCESS;
}

static Accessible*
ldtp_get_component_handle (LDTPClientContext *cctxt, char *window_prop, gchar *context, char *component, LDTPErrorCode* err)
{
	Accessible *context_handle = NULL;
	Accessible *component_handle = NULL;

	char *class_type  = NULL;
	struct node *head = NULL;

	GHashTable *cur_window;
	GHashTable *cur_component;

	int time_wait = ldtp_obj_timeout;
	time_t start, cur;
	gboolean flag = FALSE;

	start = cur = time (NULL);

	if (!ldtp_obj_timeout) {
		time_wait = 5; // Max wait for 5 seconds
	}

	while (difftime (cur, start) < time_wait) {
		/*
		  To avoid runtime remap function to be called, let us call remap here
		*/
		g_print ("Updating appmap - component\n");
		if (cctxt->window_name) {
			g_free (cctxt->window_name);
			cctxt->window_name = NULL;
		}
		update_cur_window_appmap_handle (cctxt, err);
		//updated_appmap = TRUE;
		component_handle = NULL;
		context_handle = get_accessible_context_handle (cctxt->app_handle, window_prop);
		if (!context_handle) {
			context_handle = get_accessible_context_handle (cctxt->app_handle, context);
		}
		if (context_handle) {
			char *name = Accessible_getName (context_handle);
			if (name) {
				char *tmp_context = get_window_name_in_appmap_format (name, Accessible_getRole (context_handle));
				if (tmp_context) {
					cur_window = get_object_def (cctxt->app_map, tmp_context, cctxt->log_fp, TRUE);
					cur_component = get_object_def (cur_window, component, cctxt->log_fp, FALSE);
					head = trace_path_to_parent (cur_window, tmp_context, cur_component,
								     &class_type, cctxt->log_fp, cctxt, err);
					component_handle = get_accessible_component_handle (head, context_handle, cctxt->log_fp);
					g_free (tmp_context);
				}
				SPI_freeString (name);
			}
			Accessible_unref (context_handle);
			g_free (head);
		}
		if (component_handle) {
			char *role = Accessible_getRoleName (component_handle);
			if (role) {
				char *str1 = NULL;
				char *str2 = NULL;
				if (g_utf8_strchr (role, -1, ' ') != NULL) {
					str1 = escape_character (role, ' ');
				} else {
					str1 = g_strdup (role);
				}
				if (g_utf8_strchr (class_type, -1, '_') != NULL) {
					str2 = escape_character (class_type, '_');
				} else {
					str2 = g_strdup (class_type);
				}
				if (str1 && str2) {
					if (ldtp_debug)
						g_print ("str1: %s - str2: %s\n", str1, str2);
					if (g_utf8_collate (str1, str2) != 0) {
						char *tmp_str1 = g_utf8_casefold (str1, -1);
						char *tmp_str2 = g_utf8_casefold (str2, -1);
						if (tmp_str1 && tmp_str2) {
							if (ldtp_debug)
								g_print ("tmp_str1: %s - tmp_str2: %s\n", tmp_str1, tmp_str2);
							if (g_utf8_collate (tmp_str1, tmp_str2) != 0) {
								// Role types are not same, so we need to rescan
								Accessible_unref (component_handle);
								component_handle = NULL;
							}
						} else {
							// Role types are not same, so we need to rescan
							Accessible_unref (component_handle);
							component_handle = NULL;
						}
						if (tmp_str1)
							g_free (tmp_str1);
						if (tmp_str2)
							g_free (tmp_str2);
					}
				}
				if (str1)
					g_free (str1);
				if (str2)
					g_free (str2);
				SPI_freeString (role);
			}
			class_type = NULL;
		}
		if (!component_handle || Accessible_getRole (component_handle) == SPI_ROLE_UNKNOWN) {
			if (component_handle) {
				Accessible_unref (component_handle);
				component_handle = NULL;
			}
			sleep (1);
			cur = time (NULL);
		} else {
			flag = TRUE;
			break;
		}
	}
	return component_handle;
}

/*
  Get gui handle based on context and compoment
*/
LDTPGuiHandle*
ldtp_gui_get_gui_handle (LDTPClientContext* cctxt,
			 LDTPErrorCode* err)
{
	char msg [256]    = "";
	gchar *context    = NULL;
	char *app_name    = NULL;
	char *component   = NULL;
	char *class_type  = NULL;
	char *window_prop = NULL;
	struct node *head = NULL;
	gboolean flag = FALSE;
	gboolean updated_appmap = FALSE;
	AccessibleRole class;
	Accessible *component_handle  = NULL;
	Accessible *context_handle = NULL;
	LDTPGuiHandle* ctxt_handle = NULL;

	GHashTable *cur_window;
	GHashTable *cur_component;

	if (!cctxt || !cctxt->req->context) {
		/* FIXME: Error handling */
		*err = LDTP_ERROR_ARGUMENT_NULL;
		log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (*err), cctxt->log_fp);
		return NULL;
	}

	context = (char *) cctxt->req->context;
	component = (char *) cctxt->req->component;
	/*
	  For guiexist, waittillguiexist functions, both context and component are same
	*/
	if (!cctxt->req->component)
		component = context;

	if (!cctxt->app_map) {
		if (cctxt->window_name) {
			g_free (cctxt->window_name);
			cctxt->window_name = NULL;
		}
		update_cur_window_appmap_handle (cctxt, err);
		updated_appmap = TRUE;
		if (*err != LDTP_ERROR_SUCCESS) {
			g_sprintf (msg, "Unable to update context: %s in appmap", context);
			goto error;
		}
	}

	cur_window = get_object_def (cctxt->app_map, context, cctxt->log_fp, TRUE);
	if (context)
		g_print ("context: %s - cur_window: %d\n", context, cur_window == NULL ? 0 : 1);
	/*
	  If window info, not available in appmap hash table, try to remap it
	  iff, the window exist
	*/
	if (!cur_window) {
		if (cctxt->window_name) {
			g_free (cctxt->window_name);
			cctxt->window_name = NULL;
		}
		update_cur_window_appmap_handle (cctxt, err);
		updated_appmap = TRUE;
		if (*err != LDTP_ERROR_SUCCESS) {
			g_sprintf (msg, "Unable to update context: %s in appmap", context);
			goto error;
		}
		cur_window = get_object_def (cctxt->app_map, context, cctxt->log_fp, TRUE);
		if (!cur_window) {
			Accessible *child;

			if (cctxt->window_name) {
				g_free (cctxt->window_name);
				cctxt->window_name = NULL;
			}
			/*
			  If context is given without window type, then use dynamically created window name
			  Example: if context is Replace, instead of dlgReplace (in gedit app, replace dialog)
			  then we will try to search using our dynamic context dlgReplace
			*/
			child = get_window_handle (cctxt->app_handle, context, &(cctxt->window_name), &flag);
			if (!child) {
				g_print ("%s - %d - Window %s not open\n", __FILE__, __LINE__, context);
				g_sprintf (msg, "Window %s not open", context);
				*err = LDTP_ERROR_WIN_NOT_OPEN;
				goto error;
			}
			/*
			name = Accessible_getName (child);
			window_name = get_window_name_in_appmap_format (name, Accessible_getRole (child));
			*/
			Accessible_unref (child);
			if (cctxt->window_name) {
				gboolean tmpflag = FALSE;
				if (cctxt->req->context == component)
					tmpflag = TRUE;
				if (cctxt->req->context)
					g_free (cctxt->req->context);
				cctxt->req->context = g_strdup (cctxt->window_name);
				context = (char *) cctxt->req->context;
				/* 
				   In case of waittillguiexist and waittillguinotexist,
				   both context and component members of the ClientContext
				   structure points to same string and they don't need 
				   class_id.
				*/
				if (tmpflag)
					component = context;
				if (context)
					cur_window = get_object_def (cctxt->app_map, context, cctxt->log_fp, TRUE);
				//g_free (window_name);
				//window_name = NULL;
			}
		}
		if (!cur_window) {
			g_sprintf (msg, "Unable to find window name: %s in appmap", context);
			*err = LDTP_ERROR_WIN_NAME_NOT_FOUND_IN_APPMAP;
			goto error;
		}
	}
	cur_component = get_object_def (cur_window, context, cctxt->log_fp, TRUE);
	if (!cur_component) {
		g_sprintf (msg, "%s - %d - Unable to find context name: %s in appmap", __FILE__, __LINE__, context);
		*err = LDTP_ERROR_WIN_NAME_NOT_FOUND_IN_APPMAP;
		goto error;
	}
	app_name = get_property (cur_component, "parent", cctxt->log_fp);
	if (app_name)
		g_print ("app_name: %s\n", app_name);
	window_prop = get_property (cur_component, "label", cctxt->log_fp);
	if (ldtp_debug && window_prop)
		g_print ("window_prop: %s\n", window_prop);

	if (context && component &&
	    g_utf8_collate ((const gchar *)context, (const gchar *)component)) {
		cur_component = get_object_def (cur_window, component, cctxt->log_fp, FALSE);

		if (!cur_component) {
			int time_wait = ldtp_obj_timeout;
			time_t start, cur;
			gboolean flag = FALSE;

			g_print ("Unable to get component\n");
			if (cctxt->window_name) {
				g_free (cctxt->window_name);
				cctxt->window_name = NULL;
			}
			/*
			  Copied from LTFX source code
			*/
			start = cur = time (NULL);

			if (!ldtp_obj_timeout) {
				time_wait = 5; // Max wait for 5 seconds
			}

			while (difftime (cur, start) < time_wait) {
				g_print ("Updating appmap - context\n");
				update_cur_window_appmap_handle (cctxt, err);
				updated_appmap = TRUE;
				cur_window = get_object_def (cctxt->app_map, context, cctxt->log_fp, TRUE);
				cur_component = get_object_def (cur_window, component, cctxt->log_fp, FALSE);

				if (!cur_component) {
					sleep (1);

					cur = time (NULL);
				} else {
					flag = TRUE;
					break;
				}
			}
			if (flag == FALSE) {
				g_sprintf (msg, "%s - %d - Unable to find object name: %s in appmap", __FILE__, __LINE__, component);
				*err = LDTP_ERROR_OBJ_NAME_NOT_FOUND_IN_APPMAP;
				goto error;
			}
		}
	}
	/*
	  Update the ClientContext structure with application 
	  handle, iff, it wasn't already updated.
	  FIXME: We should think about scenarios that involve
	  multiple-app-maps and multiple-application-handles.
	*/
	if (app_name && cctxt->window_name)
		g_print ("Appname: %s - %s\n", app_name, cctxt->window_name);

	if (cctxt->app_handle) {
		Accessible_unref (cctxt->app_handle);
		cctxt->app_handle = NULL;
	}

	cctxt->app_handle = get_accessible_app_handle (app_name);
	if (!cctxt->app_handle) {
		g_sprintf (msg, "Application: %s not running", app_name);
		*err = LDTP_ERROR_APP_NOT_RUNNING;
		goto error;
	}

	if (updated_appmap == FALSE) {
		if (cctxt->window_name) {
			g_free (cctxt->window_name);
			cctxt->window_name = NULL;
		}
		if (window_prop)
			cctxt->window_name = g_strdup (window_prop);
	}
	context_handle = get_accessible_context_handle (cctxt->app_handle, window_prop);
	if (!context_handle) {
		context_handle = get_accessible_context_handle (cctxt->app_handle, context);
	}
	if (!context_handle) {
		if (g_utf8_collate (context, component)) {
			g_sprintf (msg, "Window: %s not opened", context);
			*err = LDTP_ERROR_WIN_NOT_OPEN;
		}
		else
			*err = LDTP_ERROR_UNABLE_TO_GET_CONTEXT_HANDLE;
		goto error;
	}

	ctxt_handle = g_new0 (LDTPGuiHandle, 1);
	ctxt_handle->handle = context_handle;

	g_print ("Window: %s - Object: %s\n", context, component);

	/* 
	      In case of waittillguiexist and waittillguinotexist,
	      both context and component members of the ClientContext 
	      structure points to same string and they don't need 
	      class_id.
	*/
	if (context && component &&
	    !g_utf8_collate ((const gchar *)context, (const gchar *)component))
		return ctxt_handle;

	head = trace_path_to_parent (cur_window, context, cur_component, &class_type, cctxt->log_fp, cctxt, err);
	component_handle = get_accessible_component_handle (head, context_handle, cctxt->log_fp);
	Accessible_unref (context_handle);
	ctxt_handle->handle = NULL;
	g_free (head);

	if (component_handle) {
		char *role = Accessible_getRoleName (component_handle);
		if (role) {
			char *str1 = NULL;
			char *str2 = NULL;
			if (g_utf8_strchr (role, -1, ' ') != NULL) {
				str1 = escape_character (role, ' ');
			} else {
				str1 = g_strdup (role);
			}
			if (class_type && g_utf8_strchr (class_type, -1, '_') != NULL) {
				str2 = escape_character (class_type, '_');
			} else {
				str2 = g_strdup (class_type);
			}
			if (str1 && str2) {
				if (ldtp_debug)
					g_print ("str1: %s - str2: %s\n", str1, str2);
				if (g_utf8_collate (str1, str2) != 0) {
					char *tmp_str1 = g_utf8_casefold (str1, -1);
					char *tmp_str2 = g_utf8_casefold (str2, -1);
					if (tmp_str1 && tmp_str2) {
						if (ldtp_debug)
							g_print ("tmp_str1: %s - tmp_str2: %s\n", tmp_str1, tmp_str2);
						if (g_utf8_collate (tmp_str1, tmp_str2) != 0) {
							// Role types are not same, so we need to rescan
							Accessible_unref (component_handle);
							component_handle = NULL;
						}
					} else {
						// Role types are not same, so we need to rescan
						Accessible_unref (component_handle);
						component_handle = NULL;
					}
					if (tmp_str1)
						g_free (tmp_str1);
					if (tmp_str2)
						g_free (tmp_str2);
				}
			}
			if (str1)
				g_free (str1);
			if (str2)
				g_free (str2);
			SPI_freeString (role);
		}
		class_type = NULL;
	}

	if (!component_handle || Accessible_getRole (component_handle) == SPI_ROLE_UNKNOWN) {
		if (component_handle)
			Accessible_unref (component_handle);
		component_handle = ldtp_get_component_handle (cctxt, window_prop, context, component, err);
	}

	if (!component_handle) {
		if (ldtp_debug && component) {
			g_sprintf (msg, "Unable to get object handle %s", component);
			g_print ("%s\n", msg);
		}
		*err = LDTP_ERROR_GET_OBJ_HANDLE_FAILED;
		goto error;
	}

	if (!is_object_matching (component_handle, cur_component, cctxt->log_fp)) {
		char *name = NULL;
		name = Accessible_getName (component_handle);
		if (name) {
			g_sprintf (msg, "Object information: %s does not match with appmap entry", name);
			g_print ("%s\n", msg);
			SPI_freeString (name);
		}
		Accessible_unref (component_handle);
		g_print ("Let us try rescan\n");
		context_handle = get_accessible_context_handle (cctxt->app_handle, window_prop);
		if (!context_handle) {
			context_handle = get_accessible_context_handle (cctxt->app_handle, context);
		}
		name = Accessible_getName (context_handle);
		if (name) {
			char *tmp_context = get_window_name_in_appmap_format (name, Accessible_getRole (context_handle));
			SPI_freeString (name);
			if (tmp_context) {
				component_handle = ldtp_get_component_handle (cctxt, window_prop, tmp_context, component, err);
				if (!component_handle) {
					g_sprintf (msg, "Unable to get object handle %s", tmp_context);
					g_print ("%s\n", msg);
					*err = LDTP_ERROR_GET_OBJ_HANDLE_FAILED;
					Accessible_unref (context_handle);
					goto error;
				}
			}
			cur_window = get_object_def (cctxt->app_map, tmp_context, cctxt->log_fp, TRUE);
			cur_component = get_object_def (cur_window, component, cctxt->log_fp, FALSE);
			g_free (tmp_context);
			if (!is_object_matching (component_handle, cur_component, cctxt->log_fp)) {
				name = Accessible_getName (component_handle);
				if (name) {
					g_sprintf (msg, "Object information: %s does not match with appmap entry", name);
					g_print ("%s\n", msg);
					SPI_freeString (name);
				}
				if (component_handle)
					Accessible_unref (component_handle);
				*err = LDTP_ERROR_OBJ_INFO_MISMATCH;
				Accessible_unref (context_handle);
				goto error;
			}
		}
		Accessible_unref (context_handle);
	}
	ctxt_handle->class_id = 0;
	class = 0;
	if (component_handle)
		class = Accessible_getRole (component_handle);

	if (class == SPI_ROLE_EXTENDED) {
		char *name;
		name = Accessible_getRoleName (component_handle);
		if (g_ascii_strcasecmp (name, "calendar view") == 0)
			ctxt_handle->class_id = CALENDAR_VIEW;
		else if (g_ascii_strcasecmp (name, "calendar event") == 0)
			ctxt_handle->class_id = CALENDAR_EVENT;
		SPI_freeString (name);
	}
	else
		ctxt_handle->class_id = class;

	g_print ("Class id: %d\n", ctxt_handle->class_id);
  
	ctxt_handle->handle = component_handle;
	*err = LDTP_ERROR_SUCCESS;
	return ctxt_handle;

 error:
	g_free (ctxt_handle);
	if (g_ascii_strcasecmp (msg, "") != 0) {
		g_print ("%s\n", msg);
		log_msg (LDTP_LOG_ERROR, msg, cctxt->log_fp);
	}
	return NULL;
}

static Accessible*
get_object_handle (Accessible *accessible, AccessibleRole role)
{
	long i;
	long count;
	Accessible *child, *parent;
	
	count = Accessible_getChildCount (accessible);
	for (i = 0; i < count; i++) {
		child = Accessible_getChildAtIndex (accessible, i);

		if (!child)
			continue;	

		parent = child;
		if (Accessible_getRole (child) == role)
			return child;
		else {
			Accessible *tmp_parent = child;
			child = get_object_handle (tmp_parent, role);
			/*
			  Unref local parent
			*/
			if (child == NULL && parent == tmp_parent)
				parent = NULL;
			if (tmp_parent) {
				Accessible_unref (tmp_parent);
				tmp_parent = NULL;
			}
			if (child != NULL)
				return child;
		}
		if (parent) {
			Accessible_unref (parent);
			parent = NULL;
		}
	}
	return NULL;
}

Accessible *
get_list_handle (Accessible *accessible)
{
	return get_object_handle (accessible, SPI_ROLE_LIST);
}

Accessible *
get_text_handle (Accessible *accessible)
{
	return get_object_handle (accessible, SPI_ROLE_TEXT);
}

Accessible *
get_menu_handle (Accessible *accessible)
{
	return get_object_handle (accessible, SPI_ROLE_MENU);
}

int 
get_object_type (Accessible *accessible)
{
	int object_type = 0;
	AccessibleRole role;
	role = Accessible_getRole (accessible);

	if (role == SPI_ROLE_LIST)
		object_type = SPI_ROLE_LIST;
	else if (role == SPI_ROLE_MENU)
		object_type = SPI_ROLE_MENU;
	else if (role == SPI_ROLE_TEXT)
		object_type = SPI_ROLE_TEXT;
	else if (role == SPI_ROLE_TOGGLE_BUTTON)
		object_type = SPI_ROLE_TOGGLE_BUTTON;
	else if (role == SPI_ROLE_TABLE_CELL)
		object_type = SPI_ROLE_TABLE_CELL;
	else if (role == SPI_ROLE_EXTENDED) {
		char *role_name;
		role_name = Accessible_getRoleName (accessible);
		if (g_ascii_strcasecmp (role_name, "calendar event") == 0)
			object_type = CALENDAR_EVENT;
		SPI_freeString (role_name);
	}
	return object_type;
}

int 
get_child_object_type (Accessible *accessible)
{
	int i;
	int num_child;
	int child_type;
	char *role_name;
	AccessibleRole role;
	Accessible *child;
                                                                                
	num_child = Accessible_getChildCount (accessible);
	if (ldtp_debug) {
		role_name = Accessible_getRoleName (accessible);
		g_print ("Child object type: %s\n", role_name);
		SPI_freeString (role_name);
	}
                                                  
	for (i = 0; i < num_child; i++) {
		child = Accessible_getChildAtIndex (accessible, i);
		if (!child)
			continue;

		if (ldtp_debug) {
			role_name = Accessible_getRoleName (child);
			g_print ("Child object type: %s\n", role_name);
			SPI_freeString (role_name);
		}

		role = Accessible_getRole (child);
		if (role == SPI_ROLE_MENU) {
			Accessible_unref (child);
			return SPI_ROLE_MENU;
		} else if (role == SPI_ROLE_LIST) {
			g_print ("Role: %d\n", SPI_ROLE_LIST);
			Accessible_unref (child);
			return SPI_ROLE_LIST;
		}

		child_type = get_child_object_type (child);
		if (child_type != 0) {
			Accessible_unref (child);
			return child_type;
		}
		Accessible_unref (child);
	}
	return 0;
}

int 
set_new_context (char *existing_context, char *new_context)
{
	if (last_new_context) {
		g_free (last_new_context);
		last_new_context = NULL;
	}
	if (last_existing_context) {
		g_free (last_existing_context);
		last_existing_context = NULL;
	}
	last_new_context = g_strdup (new_context);
	last_existing_context = g_strdup (existing_context);
	return 1;
}

int 
release_last_context ()
{
	if (last_new_context) {
		g_free (last_new_context);
		last_new_context = NULL;
	}
	if (last_existing_context) {
		g_free (last_existing_context);
		last_existing_context = NULL;
	}
	return 1;
}

void
ldtp_gui_free_gui_handle (LDTPGuiHandle *ui_handle)
{
	if (!ui_handle)
		return;
	if (ui_handle->handle) {
		Accessible_unref (ui_handle->handle);
		ui_handle->handle = NULL;
	}
	g_free (ui_handle);
	ui_handle = NULL;
}

void
ldtp_gui_wait_till_gui_exist (LDTPClientContext* cctxt, LDTPErrorCode* err)
{
	int time_wait = ldtp_gui_timeout;
	time_t start, cur;
	LDTPGuiHandle *accessible = NULL;

	/*
	  Copied from LTFX source code
	*/
	start = cur = time (NULL);

	if (cctxt->req->arg_list) {
		char *time_out = NULL;
		time_out = g_slist_nth_data (cctxt->req->arg_list, 0);
		time_wait = atoi (time_out);
		if (!time_wait && !ldtp_gui_timeout)
			time_wait = 30;
	} else if (!ldtp_gui_timeout) {
		time_wait = 30; // Max wait for 30 seconds
	}

	while ((difftime (cur, start) < time_wait) && (accessible == NULL)) {
		sleep (1);
		cur = time (NULL);
		accessible = ldtp_gui_get_gui_handle (cctxt, err);
	}

	if (accessible == NULL)
		*err = LDTP_ERROR_GUI_NOT_EXIST;
	else {
		Accessible_unref (accessible->handle);
		g_free (accessible);
		*err = LDTP_ERROR_SUCCESS;
	}
}

void
ldtp_gui_wait_till_gui_not_exist (LDTPClientContext* cctxt, LDTPErrorCode* err)
{
	int time_wait = ldtp_gui_timeout;
	time_t start, cur;
	LDTPGuiHandle *accessible = NULL;

	/*
	  Copied from LTFX source code
	*/
	start = cur = time (NULL);

	if (cctxt->req->arg_list) {
		char *time_out = NULL;
		time_out = g_slist_nth_data (cctxt->req->arg_list, 0);
		time_wait = atoi (time_out);
		if (!time_wait && !ldtp_gui_timeout)
			time_wait = 30;
	} else if (!ldtp_gui_timeout) {
		time_wait = 30; // Max wait for 30 seconds
	}

	accessible = ldtp_gui_get_gui_handle (cctxt, err);

	while ((difftime (cur, start) < time_wait) && (accessible != NULL)) {
		sleep (1);
		cur = time (NULL);
		if (accessible) {
			Accessible_unref (accessible->handle);
			g_free (accessible);
			accessible = NULL;
		}
		accessible = ldtp_gui_get_gui_handle (cctxt, err);
	}

	if (accessible == NULL)
		*err = LDTP_ERROR_SUCCESS;
	else {
		Accessible_unref (accessible->handle);
		g_free (accessible);
		*err = LDTP_ERROR_GUI_EXIST;
	}
}

void
ldtp_gui_gui_exist (LDTPClientContext* cctxt, LDTPErrorCode* err)
{
	LDTPGuiHandle *accessible = NULL;

	accessible = ldtp_gui_get_gui_handle (cctxt, err);
	if (accessible == NULL)
		*err = LDTP_ERROR_GUI_NOT_EXIST;
	else {
		/*
		  FIXME: Bug 407728
		  AccessibleStateSet_contains returns TRUE on passing SPI_STATE_SHOWING
		  to an object which does not have the state. Need to investigate more.
		if (cctxt->req->component) {
			g_print ("Component: %s - %d\n", cctxt->req->component,
				 object_state_contains (accessible->handle, PUSH_BUTTON, cctxt->log_fp));
			if (object_state_contains (accessible->handle, PUSH_BUTTON, cctxt->log_fp) == -1) {
				Accessible_unref (accessible->handle);
				g_free (accessible);
				*err = LDTP_ERROR_GUI_NOT_EXIST;
				return;
			}
		}
		*/
		Accessible_unref (accessible->handle);
		g_free (accessible);
		*err = LDTP_ERROR_SUCCESS;
	}
}

LDTPErrorCode
grab_focus (Accessible *object, FILE *log_fp)
{
	LDTPErrorCode error;
	SPIBoolean flag = FALSE;
	AccessibleComponent* component;

	component = Accessible_getComponent (object);
	if (component) {
		flag = AccessibleComponent_grabFocus (component);
		Accessible_unref (component);
		if (flag == TRUE)
			return LDTP_ERROR_SUCCESS;
		else {
			error = LDTP_ERROR_UNABLE_TO_GRAB_FOCUS;
			log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
			return error;
		}
	}
	error = LDTP_ERROR_OBJ_NOT_COMPONENT_TYPE;
	log_msg (LDTP_LOG_CAUSE, ldtp_error_get_message (error), log_fp);
	return error;
}
