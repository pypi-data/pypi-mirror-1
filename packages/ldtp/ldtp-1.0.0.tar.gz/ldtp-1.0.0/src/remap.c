/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org
 *
 * Author:
 *    Premkumar J <jpremkumar@novell.com>
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
#include "ldtp-gui.h"
#include "remap.h"
#include "ldtp-appmap.h"
#include "ldtp-error.h"
#include "ldtp-utils.h"
#include "ldtp-logger.h"
#include "localization.h"
#include "ldtp-command.h"
#include "ldtp-gui-comp.h"

extern gboolean ldtp_debug;
static gboolean po_flag = FALSE;

static int table = 0,
	canvas = 0,
	column_header = 0,
	combo_box = 0,
	page_tab_list = 0,
	page_tab = 0,
	spin_button = 0,
	button = 0,
	tbutton = 0,
	radio_button = 0,
	check_box = 0,
	tree = 0,
	tree_table = 0,
	layered_pane = 0,
	text = 0,
	cal_view = 0,
	panel = 0,
	filler = 0,
	menubar = 0,
	menu = 0,
	list = 0,
	separator = 0,
	scroll_bar = 0,
	scroll_pane = 0,
	split_pane = 0,
	slider = 0,
	html_container = 0,
	progress_bar = 0,
	status_bar = 0,
	tool_bar = 0,
	label = 0,
	unknown = 0,
	embedded_component = 0,
	dialog = 0,
	frame = 0;

static void
reset_count()
{
	table = 0;
	canvas = 0;
	column_header = 0;
	combo_box = 0;
	page_tab_list = 0;
	page_tab = 0;
	spin_button = 0;
	button = 0;
	tbutton = 0;
	radio_button = 0;
	tree = 0;
	tree_table = 0;
	layered_pane = 0;
	text = 0;
	cal_view = 0;
	panel = 0;
	filler = 0;
	menubar = 0;
	menu = 0;
	list = 0;
	separator = 0;
	scroll_bar = 0;
	scroll_pane = 0;
	split_pane = 0;
	slider = 0;
	html_container = 0;
	progress_bar = 0;
	status_bar = 0;
	tool_bar = 0;
	label = 0;
	check_box = 0;
	unknown = 0;
	embedded_component = 0;
	dialog = 0;
	frame = 0;
}

gchar*
strip_delim (const gchar *text, gchar ch)
{
	GString *str;
	gint length;
	const gchar *p;
	const gchar *end;

	if (!text)
		return NULL;

	length = strlen (text);

	str = g_string_sized_new (length);

	p = text;
	end = text + length;

	while (p != end) {
		const gchar *next;
		if (!p || !*p)
			break;
		next = g_utf8_next_char (p);

		if (*p == ch) {
			if (ch == '.') {
				p = next;
				next = g_utf8_next_char (p);
				if (*p == ch) {
					break;
				} else {
					g_string_append_len (str, ".", 1);
					g_string_append_len (str, p, next - p);
				}
			}
		}
		else
			g_string_append_len (str, p, next - p);

		p = next;
	}
	g_string_append_c (str, '\0');

	return g_string_free (str, FALSE);
}

static gchar*
search_forward (const gchar *text, gchar delimiter)
{
	gint length;
	GString *str;
	const gchar *p;
	const gchar *end;

	g_return_val_if_fail (text != NULL, NULL);

	length = strlen (text);
	str = g_string_sized_new (length);

	p = text;
	end = text + length;

	while (p != end) {
		const gchar *next;
		next = g_utf8_next_char (p);

		if (*p == delimiter)
			break;
		else
			g_string_append_len (str, p, next - p);

		p = next;
	}
	return g_string_free (str, FALSE);
}

static gchar*
search_reverse (const gchar *text, gchar delimiter)
{
	gint length;
	GString *str;
	const gchar *p;
	const gchar *end;
	gboolean flag = FALSE;

	g_return_val_if_fail (text != NULL, NULL);

	length = strlen (text);
	str = g_string_sized_new (length);

	p = text;
	end = text + length;

	while (p != end) {
		const gchar *next;
		next = g_utf8_next_char (p);

		if (!flag && *p != delimiter) {
			p = next;
			continue;
		}
		else if (!flag) {
			flag = TRUE;
			p = next;
			continue;
		}
		g_string_append_len (str, p, next - p);

		p = next;
	}
	return g_string_free (str, FALSE);
}

static char*
get_keybinding (Accessible *object)
{
	char *binding = NULL;
	char *key_binding = NULL;
	AccessibleAction *action = NULL;
	if (object == NULL || !Accessible_isAction (object))
		return NULL;

	action = Accessible_getAction (object);
	if (!action)
		return NULL;
	binding = g_strdup (AccessibleAction_getKeyBinding (action, 0l));
	Accessible_unref (action);

	if (!binding || g_utf8_collate (binding, "") == 0) {
		g_free (binding);
		return NULL;
	}

	key_binding = search_forward (binding, ';');

	if (!key_binding ||  g_utf8_collate (key_binding, "") == 0) {
		g_free (key_binding);
		return binding;
	}
	else {
		g_free (binding);
		binding = g_strdup (key_binding);
		g_free (key_binding);
		key_binding = NULL;
	}


	if (g_utf8_strchr (binding, strlen (binding), '>') == NULL)
		return binding;

	key_binding = search_reverse (binding, '>');

	if (key_binding && g_utf8_collate (key_binding, "") == 0) {
		g_free (key_binding);
		g_free (binding);
		return NULL;
	}
	else if (!key_binding)
		return binding;

	g_free (binding);
	return key_binding;
}

static char*
insert_underscore (gchar *text, gchar *binding)
{
	GString *str;
	GString *tmp;
	gint length;
	const gchar *p;
	const gchar *end;
	gboolean flag = FALSE;

	if (!text || !binding)
		return NULL;

	length = strlen (text);

	str = g_string_sized_new (length);
	tmp = g_string_sized_new (length);

	p = text;
	end = text + length;

	while (p != end) {
		const gchar *next;
		next = g_utf8_next_char (p);

		if (*p == g_unichar_toupper (*binding)) {
			g_string_append (tmp, "_");
			flag = TRUE;
		}
		else if (flag != TRUE && g_unichar_tolower (*p) == g_unichar_tolower (*binding)) {
			g_string_append (str, "_");
			flag = TRUE;
		}
		g_string_append_len (str, p, next - p);
		g_string_append_len (tmp, p, next - p);

		p = next;
	}

	if (g_utf8_collate (str->str, tmp->str) == 0)
		g_free (tmp->str);
	else if (g_utf8_strchr (tmp->str, tmp->len, '_')) {
		g_free (str->str);
		str = tmp;
	}
	else
		g_free (tmp->str);

	return g_string_free (str, FALSE);
}

/*
 * This function filters the appmap entries
 */
static gboolean
filter_appmap_data (Accessible *accessible, OBJECT_INFO *obj_info, char *label)
{
	if (obj_info->object_type &&
	    (g_ascii_strcasecmp (obj_info->object_type, "separator") == 0 ||
	     g_ascii_strcasecmp (obj_info->object_type, "table_cell") == 0))
		return 0;
	if (label && g_ascii_strcasecmp (label, "ukngrip") == 0)
		return 0;
	if (obj_info->object_type && g_ascii_strcasecmp (obj_info->object_type, "menu_item") == 0) {
		Accessible *parent = NULL;
		Accessible *grand_parent = NULL;
		int parent_type = SPI_ROLE_UNKNOWN;
		if (accessible) {
			parent = Accessible_getParent (accessible);
			grand_parent = Accessible_getParent (parent);
			parent_type = Accessible_getRole (grand_parent);
			Accessible_unref (parent);
			Accessible_unref (grand_parent);
		}
		if (parent_type == SPI_ROLE_COMBO_BOX)
			return FALSE;
		else
			return TRUE;
	}

	if (obj_info->object_type && g_ascii_strcasecmp (obj_info->object_type, "list_item") == 0)
		return FALSE;

	if (obj_info->object_type && g_ascii_strcasecmp (obj_info->object_type, "unknown") == 0) {
		Accessible *parent;
		int parent_type = 0;
		parent = Accessible_getParent (accessible);
		if (parent) {
			parent_type = Accessible_getRole (parent);
			Accessible_unref (parent);
		}
		if (parent_type == SPI_ROLE_TABLE || parent_type == SPI_ROLE_TREE ||
		    parent_type == SPI_ROLE_TREE_TABLE)
			return FALSE;
		else
			return TRUE;
	}

	return TRUE;
}

/*
 * This function returns the information about the accessible object passed
 */
static OBJECT_INFO*
get_object_info (Accessible *accessible)
{
	int role;
	OBJECT_INFO *obj_info = NULL;

	if (!accessible)
		return NULL;

	obj_info = (OBJECT_INFO *) malloc (sizeof (OBJECT_INFO));
	role = Accessible_getRole (accessible);

	if (role == SPI_ROLE_PAGE_TAB) {
		obj_info->prefix = g_strdup ("ptab");
		obj_info->instance_index = page_tab;
		page_tab++;
		obj_info->object_type = g_strdup ("page_tab");
	}
	else if (role == SPI_ROLE_PAGE_TAB_LIST) {
		obj_info->prefix = g_strdup ("ptl");
		obj_info->instance_index = page_tab_list;
		page_tab_list++;
		obj_info->object_type = g_strdup ("page_tab_list");
	}
	else if (role == SPI_ROLE_TABLE) {
		obj_info->prefix = g_strdup ("tbl");
		obj_info->instance_index = table;
		table++;
		obj_info->object_type = g_strdup ("table");
	}
	else if (role == SPI_ROLE_COMBO_BOX) {
		obj_info->prefix = g_strdup ("cbo");
		obj_info->instance_index = combo_box;
		combo_box++;
		obj_info->object_type = g_strdup ("combo_box");
	}
	else if (role == SPI_ROLE_SPIN_BUTTON) {
		obj_info->prefix = g_strdup ("sbtn");
		obj_info->instance_index = spin_button;
		spin_button++;
		obj_info->object_type = g_strdup ("spin_button");
	}
	else if (role == SPI_ROLE_FONT_CHOOSER) {
		obj_info->prefix = g_strdup ("dlg");
		obj_info->instance_index = -1; /* Value -1 signifies not applicable */
		obj_info->object_type = g_strdup ("font_chooser");
	}
	else if (role == SPI_ROLE_COLOR_CHOOSER) {
		obj_info->prefix = g_strdup ("dlg");
		obj_info->instance_index = -1; /* Value -1 signifies not applicable */
		obj_info->object_type = g_strdup ("color_chooser");
	}
	else if (role == SPI_ROLE_RADIO_BUTTON) {
		obj_info->prefix = g_strdup ("rbtn");
		obj_info->instance_index = radio_button;
		radio_button++;
		obj_info->object_type = g_strdup ("radio_button");
	}
	else if (role == SPI_ROLE_TREE) {
		obj_info->prefix = g_strdup ("tree");
		obj_info->instance_index = tree;
		tree++;
		obj_info->object_type = g_strdup ("tree");
	}
	else if (role == SPI_ROLE_TREE_TABLE) {
		obj_info->prefix = g_strdup ("ttbl");
		obj_info->instance_index = tree_table;
		tree_table++;
		obj_info->object_type = g_strdup ("tree_table");
	}
	else if (role == SPI_ROLE_LAYERED_PANE) {
		obj_info->prefix = g_strdup ("pane");
		obj_info->instance_index = layered_pane;
		layered_pane++;
		obj_info->object_type = g_strdup ("layered_pane");
	}
	else if (role == SPI_ROLE_FRAME) {
		obj_info->prefix = g_strdup ("frm");
		obj_info->instance_index = frame++; /* Value -1 signifies not applicable */
		obj_info->object_type = g_strdup ("frame");
	}
	else if (role == SPI_ROLE_DIALOG) {
		obj_info->prefix = g_strdup ("dlg");
		obj_info->instance_index = dialog++; /* Value -1 signifies not applicable */
		obj_info->object_type = g_strdup ("dialog");
	}
	else if (role == SPI_ROLE_WINDOW) {
		obj_info->prefix = g_strdup ("dlg");
		obj_info->instance_index = dialog++;
		obj_info->object_type = g_strdup ("dialog");
	}
	else if (role == SPI_ROLE_FILE_CHOOSER) {
		obj_info->prefix = g_strdup ("dlg");
		obj_info->instance_index = dialog++; /* Value -1 signifies not applicable */
		obj_info->object_type = g_strdup ("file_chooser");
	}
	else if (role == SPI_ROLE_ALERT) {
		obj_info->prefix = g_strdup ("dlg");
		obj_info->instance_index = dialog++; /* Value -1 signifies not applicable */
		obj_info->object_type = g_strdup ("alert");
	}
	else if (role == SPI_ROLE_CALENDAR) {
		obj_info->prefix = g_strdup ("calview");
		obj_info->instance_index = cal_view;
		cal_view++;
		obj_info->object_type = g_strdup ("calendar_view");
	}
	else if (role == SPI_ROLE_PANEL) {
		obj_info->prefix = g_strdup ("pnl");
		obj_info->instance_index = panel;
		panel++;
		obj_info->object_type = g_strdup ("panel");
	}
	else if (role == SPI_ROLE_LABEL) {
		obj_info->prefix = g_strdup ("lbl");
		obj_info->instance_index = label;
		label++;
		obj_info->object_type = g_strdup ("label");
	}
	else if (role == SPI_ROLE_MENU_BAR) {
		obj_info->prefix = g_strdup ("mbr");
		obj_info->instance_index = menubar;
		menubar++;
		obj_info->object_type = g_strdup ("menu_bar");
	}
	else if (role == SPI_ROLE_MENU) {
		obj_info->prefix = g_strdup ("mnu");
		obj_info->instance_index = menu;
		menu++;
		obj_info->object_type = g_strdup ("menu");
	}
	else if (role == SPI_ROLE_MENU_ITEM) {
		obj_info->prefix = g_strdup ("mnu");
		obj_info->instance_index = menu;
		menu++;
		obj_info->object_type = g_strdup ("menu_item");
	}
	else if (role == SPI_ROLE_LIST_ITEM) {
		obj_info->prefix = g_strdup ("lst");
		obj_info->instance_index = -1;
		obj_info->object_type = g_strdup ("list_item");
	}
	else if (role == SPI_ROLE_LIST) {
		obj_info->prefix = g_strdup ("lst");
		obj_info->instance_index = list;
		list++;
		obj_info->object_type = g_strdup ("list");
	}
	else if (role == SPI_ROLE_CHECK_MENU_ITEM) {
		obj_info->prefix = g_strdup ("mnu");
		obj_info->instance_index = menu;
		menu++;
		obj_info->object_type = g_strdup ("check_menu_item");
	}
	else if (role == SPI_ROLE_RADIO_MENU_ITEM) {
		obj_info->prefix = g_strdup ("mnu");
		obj_info->instance_index = menu;
		menu++;
		obj_info->object_type = g_strdup ("radio_menu_item");
	}

	else if (role == SPI_ROLE_PUSH_BUTTON) {
		obj_info->prefix = g_strdup ("btn");
		obj_info->instance_index = button;
		button++;
		obj_info->object_type = g_strdup ("push_button");
	}
	else if (role == SPI_ROLE_TOGGLE_BUTTON) {
		obj_info->prefix = g_strdup ("tbtn");
		obj_info->instance_index = tbutton;
		tbutton++;
		obj_info->object_type = g_strdup ("toggle_button");
	}
	else if (role == SPI_ROLE_SCROLL_BAR) {
		obj_info->prefix = g_strdup ("scbr");
		obj_info->instance_index = scroll_bar;
		scroll_bar++;
		obj_info->object_type = g_strdup ("scroll_bar");
	}
	else if (role == SPI_ROLE_SCROLL_PANE) {
		obj_info->prefix = g_strdup ("scpn");
		obj_info->instance_index = scroll_pane;
		scroll_pane++;
		obj_info->object_type = g_strdup ("scroll_pane");
	}
	else if (role == SPI_ROLE_TEXT) {
		obj_info->prefix = g_strdup ("txt");
		obj_info->instance_index = text;
		text++;
		obj_info->object_type = g_strdup ("text");
	}
#ifdef ENABLE_NEWROLES
	else if (role == SPI_ROLE_ENTRY) {
		obj_info->prefix = g_strdup ("txt");
		obj_info->instance_index = text;
		text++;
		obj_info->object_type = g_strdup ("entry");
	}
#endif
	/*
	else if (role == SPI_ROLE_AUTOCOMPLETE) {
		obj_info->prefix = g_strdup ("txt");
		obj_info->instance_index = text;
		text++;
		obj_info->object_type = g_strdup ("auto_complete");
	}
	*/
	else if (role == SPI_ROLE_PARAGRAPH) {
		obj_info->prefix = g_strdup ("txt");
		obj_info->instance_index = text;
		text++;
		obj_info->object_type = g_strdup ("paragraph");
	}
	else if (role == SPI_ROLE_PASSWORD_TEXT) {
		obj_info->prefix = g_strdup ("txt");
		obj_info->instance_index = text;
		text++;
		obj_info->object_type = g_strdup ("password_text");
	}
	else if (role == SPI_ROLE_STATUS_BAR) {
		obj_info->prefix = g_strdup ("stat");
		obj_info->instance_index = status_bar;
		status_bar++;
		obj_info->object_type = g_strdup ("statusbar");
	}
	else if (role == SPI_ROLE_EDITBAR) {
		obj_info->prefix = g_strdup ("txt");
		obj_info->instance_index = text;
		text++;
		obj_info->object_type = g_strdup ("edit_bar");
	}
	else if (role == SPI_ROLE_TABLE_COLUMN_HEADER) {
		obj_info->prefix = g_strdup ("tch");
		obj_info->instance_index = column_header;
		column_header++;
		obj_info->object_type = g_strdup ("table_column_header");
	}
	else if (role == SPI_ROLE_SEPARATOR) {
		obj_info->prefix = g_strdup ("spr");
		obj_info->instance_index = separator;
		separator++;
		obj_info->object_type = g_strdup ("separator");
	}
	else if (role == SPI_ROLE_FILLER) {
		obj_info->prefix = g_strdup ("flr");
		obj_info->instance_index = filler;
		filler++;
		obj_info->object_type = g_strdup ("filler");
	}
	else if (role == SPI_ROLE_CANVAS) {
		obj_info->prefix = g_strdup ("cnvs");
		obj_info->instance_index = canvas;
		canvas++;
		obj_info->object_type = g_strdup ("canvas");
	}
	else if (role == SPI_ROLE_SPLIT_PANE) {
		obj_info->prefix = g_strdup ("splt");
		obj_info->instance_index = split_pane;
		split_pane++;
		obj_info->object_type = g_strdup ("split_pane");
	}
	else if (role == SPI_ROLE_SLIDER) {
		obj_info->prefix = g_strdup ("sldr");
		obj_info->instance_index = slider;
		slider++;
		obj_info->object_type = g_strdup ("slider");
	}
	else if (role == SPI_ROLE_HTML_CONTAINER) {
		obj_info->prefix = g_strdup ("html");
		obj_info->instance_index = html_container;
		html_container++;
		obj_info->object_type = g_strdup ("html_container");
	}
	else if (role == SPI_ROLE_PROGRESS_BAR) {
		obj_info->prefix = g_strdup ("pbar");
		obj_info->instance_index = progress_bar;
		progress_bar++;
		obj_info->object_type = g_strdup ("progress_bar");
	}
	else if (role == SPI_ROLE_TOOL_BAR) {
		obj_info->prefix = g_strdup ("tbar");
		obj_info->instance_index = tool_bar;
		tool_bar++;
		obj_info->object_type = g_strdup ("tool_bar");
	}
	else if (role == SPI_ROLE_CHECK_BOX) {
		obj_info->prefix = g_strdup ("chk");
		obj_info->instance_index = check_box;
		check_box++;
		obj_info->object_type = g_strdup ("check_box");
	}
	else if (role == SPI_ROLE_TABLE_CELL) {
		obj_info->prefix = g_strdup ("tblc");
		obj_info->instance_index = -1;
		obj_info->object_type = g_strdup ("table_cell");
	}
	else if (role == SPI_ROLE_EMBEDDED) {
		obj_info->prefix = g_strdup ("emb");
		obj_info->instance_index = embedded_component;
		embedded_component++;
		obj_info->object_type = g_strdup ("embedded_component");
	}
	else if (role == SPI_ROLE_EXTENDED) {
		char *name;
		name = Accessible_getRoleName (accessible);
		if (name) {
			if (g_utf8_collate (name, "Calendar View") == 0) {
				obj_info->prefix = g_strdup ("cal");
				obj_info->instance_index = cal_view;
				obj_info->object_type = g_strdup ("calendar_view");
				cal_view++;
			}
			else if (g_utf8_collate (name, "Calendar Event") == 0) {
				obj_info->prefix = g_strdup ("cal");
				obj_info->instance_index = cal_view;
				obj_info->object_type = g_strdup ("calendar_event");
				cal_view++;
			}
			else {
				obj_info->prefix = g_strdup ("ukn");
				obj_info->instance_index = unknown;
				unknown++;
				obj_info->object_type = g_strdup (name);
			}
			SPI_freeString (name);
		}
		else {
			obj_info->prefix = g_strdup ("ukn");
			obj_info->instance_index = unknown;
			unknown++;
			obj_info->object_type = g_strdup ("unknown");
		}
	}
	else {
		char *name;
		obj_info->prefix = g_strdup ("ukn");
		obj_info->instance_index = unknown;
		unknown++;
		name = Accessible_getRoleName (accessible);
		if (name) {
			obj_info->object_type = g_strdup (name);
			SPI_freeString (name);
		} else
			obj_info->object_type = g_strdup ("unknown");
	}
	return obj_info;
}

/*
 * This function creates entry in the Appmap file corresponding to the object passed to it
 */
static char*
add_appmap_data (Accessible *accessible, char *parent_name, int child_index,
		 GHashTable *current_context, gboolean overloadedWindowName,
		 gboolean remap_context)
{
	gchar *name = NULL;
	gchar *label = NULL;
	long length = -1;
	long label_index = 1;
	char *label_by = NULL;
	char *accessible_name = NULL;
	char *accessible_desc = NULL;
	char *tmp_parent_name = parent_name;
	gchar *key_binding = NULL;
	GHashTable *hash_attributes;
	OBJECT_INFO *cur_obj_info = NULL;

	if (!accessible)
		return NULL;
	cur_obj_info = get_object_info (accessible);

	if (overloadedWindowName) {
		Accessible *parent = Accessible_getParent (accessible);
		if (parent) {
			char *name = Accessible_getName (parent);
			if (name) {
				tmp_parent_name = g_strdup (name);
				SPI_freeString (name);
			}
			Accessible_unref (parent);
		}
		accessible_name = g_strdup (parent_name);
	} else {
		char *tmp_accessible_name = Accessible_getName (accessible);
		accessible_name = g_strdup (tmp_accessible_name);
		SPI_freeString (tmp_accessible_name);
	}

	accessible_desc = Accessible_getDescription (accessible);
	if (ldtp_debug && accessible_name)
		g_print ("Label: %s\n", accessible_name);
	if (ldtp_debug && cur_obj_info &&
	    cur_obj_info->prefix &&
	    cur_obj_info->object_type) {
		g_print ("%s %d %s\n",
			 cur_obj_info->prefix,
			 cur_obj_info->instance_index,
			 cur_obj_info->object_type);
	}
	label_by = get_relation_name (accessible, &length);
	if (label_by) {
		if (g_ascii_strcasecmp (label_by, "") == 0) {
			label = g_strdup (accessible_name);
		} else
			label = g_strdup (label_by);
	} else {
		if (accessible_name)
			label = g_strdup (accessible_name);
	}

	key_binding = get_keybinding (accessible);
	if (label_by && g_ascii_strcasecmp (label_by, "") != 0) {
		if (key_binding) {
			gchar *tmp = NULL;
			tmp = insert_underscore (label_by, key_binding);
			if (tmp) {
				g_free (label_by);
				label_by = tmp;
				tmp = NULL;
			}
		}  
	}
	if (label && g_ascii_strcasecmp (label, "") != 0) {
		if (key_binding) {
			gchar *tmp = NULL;
			tmp = insert_underscore (label, key_binding);
			if (tmp) {
				g_free (label);
				label = tmp;
				tmp = NULL;
			}
		}  
	}
	g_free (key_binding);

#ifdef ENABLE_LOCALIZATION
	if (po_flag) {
		gchar *tmp = NULL;
		if (g_ascii_strcasecmp (label, "") != 0) {
			tmp = reverse_lookup (label);
			if (tmp) {
				g_free (label);
				label = tmp;
				tmp = NULL;
			}
		}
		if (label_by && g_ascii_strcasecmp (label_by, "") != 0) {      
			tmp = reverse_lookup (label_by);
			if (tmp) {
				g_free (label_by);
				label_by = tmp;
				tmp = NULL;
			}
		}
	}
#endif
	if (label && g_ascii_strcasecmp (label, "") != 0 && overloadedWindowName == FALSE) {
		char *stripped_data = NULL;
		char *value = NULL;
		gboolean flag = FALSE;
		AccessibleRole role;
		role = Accessible_getRole (accessible);
		if (role == SPI_ROLE_FRAME || role == SPI_ROLE_DIALOG ||
		    role == SPI_ROLE_ALERT || role == SPI_ROLE_FONT_CHOOSER ||
		    role == SPI_ROLE_FILE_CHOOSER || role == SPI_ROLE_WINDOW ||
		    role == SPI_ROLE_COLOR_CHOOSER)
			flag = TRUE;
		if (g_utf8_strchr (label, -1, ' '))
			stripped_data = escape_character (label, ' ');
		else
			stripped_data = g_strdup (label);
		if (!flag && g_utf8_strchr (stripped_data, -1, '.')) {
			value = strip_delim (stripped_data, '.');
			g_free (stripped_data);
			stripped_data = g_strdup (value);
			g_free (value);
			value = NULL;
		}
		if (!flag && g_utf8_strchr (stripped_data, -1, ':')) {
			value = strip_delim (stripped_data, ':');
			g_free (stripped_data);
			stripped_data = g_strdup (value);
			g_free (value);
			value = NULL;
		}
		if (!flag && g_utf8_strchr (stripped_data, -1, '_')) {
			value = escape_character (stripped_data, '_');
			g_free (stripped_data);
			stripped_data = g_strdup (value);
			g_free (value);
			value = NULL;
		}
		if (g_utf8_strchr (stripped_data, -1, '\n')) {
			value = strip_delim (stripped_data, '\n');
			g_free (stripped_data);
			stripped_data = g_strdup (value);
			g_free (value);
			value = NULL;
		}
		name = g_strdup_printf ("%s%s", cur_obj_info->prefix, stripped_data);
		if (!remap_context) {
			gboolean flag = g_hash_table_lookup_extended (current_context, name, NULL, NULL);
			while (flag) {
				if (name)
					g_free (name);
				name = g_strdup_printf ("%s%s%ld", cur_obj_info->prefix, stripped_data, label_index);
				if (name)
					g_print ("Name: %s - %d - %d\n", name, flag, remap_context);
				label_index++;
				flag = g_hash_table_lookup_extended (current_context, name, NULL, NULL);
			}
		} else if (name && current_context) {
			GHashTable *context = NULL;
			while (1) {
				g_print ("Name: %s\n", name);
				if (g_hash_table_lookup_extended (current_context, name, NULL, (gpointer) &context)) {
					if (context) {
						char *prop = get_property (context, "parent", NULL);
						char *remap = get_property (context, "remap", NULL);
						g_hash_table_foreach (context, (GHFunc)&print_attributes, NULL);
						if (prop && parent_name)
							g_print ("remap_context: parent: %s - prop: %s %s %d\n",
								 parent_name, prop, name, __LINE__);
						if (!remap && prop && (g_utf8_collate (prop, parent_name) == 0)) {
							g_print ("remap_context: parent: %s - prop: %s %s %d\n",
								 parent_name, prop, name, __LINE__);
							break;
						}
					}
				} else {
					g_print ("Lookup fails: %s\n", name);
					break;
				}
				g_free (name);
				name = g_strdup_printf ("%s%s%ld", cur_obj_info->prefix, stripped_data, label_index);
				label_index++;
			}
		}
		if (ldtp_debug && name && tmp_parent_name)
			g_print ("Stripped name, prefix, index: %s - Parent: %s\n", name, tmp_parent_name);
		g_free (stripped_data);
	} else if (overloadedWindowName) {
		name = g_strdup (accessible_name);
	} else {
		name = g_strdup_printf ("%s%d", cur_obj_info->prefix, cur_obj_info->instance_index);
		if (remap_context && name && current_context) {
			GHashTable *context = NULL;
			while (1) {
				if (g_hash_table_lookup_extended (current_context, name, NULL, (gpointer) &context)) {
					if (context) {
						char *prop = get_property (context, "parent", NULL);
						char *remap = get_property (context, "remap", NULL);
						if (prop && parent_name)
							g_print ("remap_context: parent: %s - prop: %s %d\n",
								 parent_name, prop, __LINE__);
						if (!remap && prop && (g_utf8_collate (prop, parent_name) == 0)) {
							g_print ("remap_context: parent: %s - prop: %s %d\n",
								 parent_name, prop, __LINE__);
							break;
						}
					}
				} else {
					g_print ("Lookup fails: %s\n", name);
					break;
				}
				g_free (name);
				cur_obj_info->instance_index++;
				name = g_strdup_printf ("%s%d", cur_obj_info->prefix, cur_obj_info->instance_index);
			}
		}
	}

	if (ldtp_debug && name && tmp_parent_name)
		g_print ("Stripped name, prefix, index: %s - Parent: %s\n", name, tmp_parent_name);
	g_free (label);
	label = g_strdup (accessible_name);
	if (label) {
		gchar *key_binding = NULL;
       
		key_binding = get_keybinding (accessible);
		if (key_binding) {
			gchar *tmp = NULL;
			tmp = insert_underscore (label, key_binding);
			g_free (key_binding);
			if (tmp) {
				g_free (label);
				label = tmp;
			}
		}
	}
#ifdef ENABLE_LOCALIZATION
	if (po_flag) {
		gchar *tmp = NULL;
		tmp = reverse_lookup (label);
		if (tmp) {
			g_free (label);
			label = g_strdup (tmp);
			g_free (tmp);
		}
	}
#endif
	/*
	 * Following code is for limiting appmap from generating label
	 * with value as string made of only space characters
	 */
	if (g_utf8_strchr (label, -1, ' ')) {
		char *stripped_data = NULL;
		stripped_data = escape_character (label, -1);
		if (g_ascii_strcasecmp (stripped_data, "") == 0) {
			g_free (label);
			label = g_strdup (stripped_data);
		}
		g_free (stripped_data);
	}
	if (filter_appmap_data (accessible, cur_obj_info, name)) {
		hash_attributes = g_hash_table_new_full (&g_str_hash, &g_str_equal,
							 key_destroy_func, value_destroy_func);
		if (hash_attributes) {
			if (cur_obj_info->object_type)
				g_hash_table_insert (hash_attributes,
						     g_strdup ("class"),
						     g_strdup (cur_obj_info->object_type));
			if (tmp_parent_name)
				g_hash_table_insert (hash_attributes,
						     g_strdup ("parent"),
						     g_strdup (tmp_parent_name));
			g_hash_table_insert (hash_attributes,
					     g_strdup ("child_index"),
					     g_strdup_printf ("%d", child_index));
			if (g_ascii_strcasecmp (label, "") != 0 && cur_obj_info->object_type &&
			    (g_ascii_strcasecmp (cur_obj_info->object_type,
						 "combo_box") != 0 &&
			     g_ascii_strcasecmp (cur_obj_info->object_type,
						 "calendar_view") != 0)) {
				g_hash_table_insert (hash_attributes,
						     g_strdup ("label"),
						     g_strdup (label));
			} else {
				if (label_by) {
					g_hash_table_insert (hash_attributes, g_strdup ("label_by"), g_strdup (label_by));
				}
			}
			if (g_ascii_strcasecmp (accessible_desc, "") != 0) {
				g_hash_table_insert (hash_attributes,
						     g_strdup ("description"),
						     g_strdup (accessible_desc));
			}
		}
		if (current_context) {
			if (remap_context) {
				g_hash_table_insert (hash_attributes,
						     g_strdup ("remap"),
						     g_strdup ("1"));
				g_hash_table_replace (current_context, g_strdup (name), hash_attributes);
			} else {
				g_hash_table_insert (current_context, g_strdup (name), hash_attributes);
			}
			g_print ("Added: %s to current_context\n", name);
		}
		g_free (label);
		g_free (label_by);
		g_free (cur_obj_info->object_type);
		g_free (cur_obj_info->prefix);
		g_free (cur_obj_info);
		if (accessible_name) {
			g_free (accessible_name);
			accessible_name = NULL;
		}

		if (overloadedWindowName)
			g_free (tmp_parent_name);

		SPI_freeString (accessible_desc);

		return name;
	}
	else {
		g_free (name);
		g_free (label);
		g_free (label_by);
		g_free (cur_obj_info->object_type);
		g_free (cur_obj_info->prefix);
		g_free (cur_obj_info);
		if (accessible_name) {
			g_free (accessible_name);
			accessible_name = NULL;
		}
		if (overloadedWindowName)
			g_free (tmp_parent_name);

		SPI_freeString (accessible_desc);

		return NULL;
	}
}

/*
  Get accessible handle of the given object
*/
static void
accessible_object_handle (Accessible *accessible, char *parent_name, 
			  long child_index, GHashTable *current_context,
			  gboolean overloadedWindowName, gboolean remap_context)
{
	long i, num_child;
	Accessible *child;
	char *role;
	char *temp_parent = NULL;
	char *current_parent = NULL;

	role = Accessible_getRoleName (accessible);
	if (ldtp_debug && role && parent_name)
		g_print ("Accessible: %s - %s - %ld\n", role, parent_name, child_index);
	SPI_freeString (role);
	num_child = Accessible_getChildCount (accessible);
	if (child_index != -1) {
		if (ldtp_debug)
			g_print ("Child Index: %ld\n", child_index);
		temp_parent = add_appmap_data (accessible, parent_name, child_index,
					       current_context, overloadedWindowName,
					       remap_context);
		if (overloadedWindowName)
			overloadedWindowName = FALSE;
	}
	else
		temp_parent = parent_name;
	if (temp_parent) {
		if (ldtp_debug)
			g_print ("Parent: %s - Child Index: %ld\n", temp_parent, child_index);
		current_parent = temp_parent;
		for (i = 0; i < num_child; i++) {
			child = Accessible_getChildAtIndex (accessible, i);
			if (!child)
				continue;
			if (Accessible_getRole (child) == SPI_ROLE_TABLE_CELL) {
				Accessible_unref (child);
				break;
			}
			/*
			  Call this function recursively, until we reach the end of
			  depth first search in all the given object handle
			*/
			accessible_object_handle (child, current_parent,
						  i, current_context,
						  overloadedWindowName,
						  remap_context);
			Accessible_unref (child);
		}
		g_free (current_parent);
	}
}

char*
get_window_name_in_appmap_format (char *window_name, AccessibleRole role)
{
	char *type = NULL;
	char *retval = NULL;

	if (role == SPI_ROLE_FRAME)
		type = g_strdup ("frm");
	else if (role == SPI_ROLE_DIALOG || role == SPI_ROLE_ALERT ||
		 role == SPI_ROLE_FONT_CHOOSER || role == SPI_ROLE_FILE_CHOOSER ||
		 role == SPI_ROLE_WINDOW || role == SPI_ROLE_COLOR_CHOOSER)
		type = g_strdup ("dlg");
	else
		type = g_strdup ("");
	if (window_name && g_utf8_collate (window_name, "") != 0) {
		char *stripped_data = NULL;
		if (g_utf8_strchr (window_name, -1, ' ') != NULL) {
			stripped_data = escape_character (window_name, ' ');
			if (ldtp_debug && stripped_data)
				g_print ("Stripped space: %s\n", stripped_data);
		}
		else
			stripped_data = g_strdup (window_name);
		if (ldtp_debug && window_name && stripped_data)
			g_print ("Before strip %s - After %s\n", window_name, stripped_data);
		if (g_utf8_strchr (stripped_data, -1, '\n')) {
			char *value = strip_delim (stripped_data, '\n');
			g_free (stripped_data);
			stripped_data = value;
		}
		if (type && stripped_data)
			retval = g_strdup_printf ("%s%s", type, stripped_data);
		g_free (type);
		g_free (stripped_data);
		return retval;
	}
	g_free (type);
	return NULL;
}

GHashTable *do_remap (Accessible *accessible_context, char *name, GHashTable *context,
		      GHashTable *context_attributes, gboolean locale_flag,
		      gboolean overloadedWindowName, gboolean remap_context)
{
	GHashTable *current_context = NULL;

	if (!name)
		return NULL;

	reset_count ();
	po_flag = locale_flag;
	if (remap_context) {
		accessible_object_handle (accessible_context, name,
					  Accessible_getIndexInParent (accessible_context),
					  context, overloadedWindowName, remap_context);
		return NULL;
	}
	current_context = g_hash_table_new (&g_str_hash, &g_str_equal);
	if (context_attributes) {
		if (ldtp_debug)
			g_print ("Context Attributes NOT NULL - FLAG: %d\n", overloadedWindowName);
		g_hash_table_insert (current_context, g_strdup (name), context_attributes);
		/*
		 * NOTE: Passing -1 as parameter signifies that the first entry has
		 * already been added, so should not do add_appmap_data for this call
		 */
		accessible_object_handle (accessible_context, name, -1,
					  current_context, overloadedWindowName,
					  remap_context);
	} else {
		char *role = Accessible_getRoleName (accessible_context);
		if (ldtp_debug && name && role)
			g_print ("Context Attributes NULL - %s - %s - %ld - FLAG: %d\n",
				 name,
				 role,
				 Accessible_getIndexInParent (accessible_context),
				 overloadedWindowName);
		SPI_freeString (role);
		accessible_object_handle (accessible_context, name,
					  Accessible_getIndexInParent (accessible_context),
					  current_context, overloadedWindowName, remap_context);
	}
	return current_context;
}
