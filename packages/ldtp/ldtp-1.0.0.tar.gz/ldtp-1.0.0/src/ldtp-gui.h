/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://www.gnomebangalore.org/ldtp
 *
 * Author:
 *    Nagappan A <nagappan@gmail.com>
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

#ifndef __GUI_H__
#define __GUI_H__

#include "ldtp.h"
#include "client-handler.h"
#include "ldtp-error.h"
#include "ldtp-appmap.h"

/*
  AT-SPI object related definitions
*/

#define INVALID 0
#define ACCEL_LABEL 1
#define ALERT 2
#define ANIMATION 3
#define ARROW 4
#define CALENDAR 5
#define CANVAS 6
#define CHECK_BOX 7
#define CHECK_MENU_ITEM 8
#define COLOR_CHOOSER 9
#define COLUMN_HEADER 10
#define COMBO_BOX 11
#define DATE_EDITOR 12
#define DESKTOP_ICON 13
#define DESKTOP_FRAME 14
#define DIAL 15
#define DIALOG 16
#define DIRECTORY_PANE 17
#define DRAWING_AREA 18
#define FILE_CHOOSER 19
#define FILLER 20
#define FONT_CHOOSER 21
#define FRAME 22
#define GLASS_PANE 23
#define HTML_CONTAINER 24
#define ICON 25
#define IMAGE 26
#define INTERNAL_FRAME 27
#define LABEL 28
#define LAYERED_PANE 29
#define LIST 30
#define LIST_ITEM 31
#define MENU 32
#define MENU_BAR 33
#define MENU_ITEM 34
#define OPTION_PANE 35
#define PAGE_TAB 36
#define PAGE_TAB_LIST 37
#define PANEL 38
#define PASSWORD_TEXT 39
#define POPUP_MENU 40
#define PROGRESS_BAR 41
#define PUSH_BUTTON 42
#define RADIO_BUTTON 43
#define RADIO_MENU_ITEM 44
#define ROOT_PANE 45
#define ROW_HEADER 46
#define SCROLL_BAR 47
#define SCROLL_PANE 48
#define SEPARATOR 49
#define SLIDER 50
#define SPIN_BUTTON 51
#define SPLIT_PANE 52
#define STATUS_BAR 53
#define TABLE 54
#define TABLE_CELL 55
#define TABLE_COLUMN_HEADER 56
#define TABLE_ROW_HEADER 57
#define TEAROFF_MENU_ITEM 58
#define TERMINAL 59
#define TEXT 60
#define TOGGLE_BUTTON 61
#define TOOL_BAR 62
#define TOOL_TIP 63
#define TREE 64
#define TREE_TABLE 65
#define UNKNOWN 66
#define VIEWPORT 67
#define WINDOW 68
#define EXTENDED 69
#define HEADER 70
#define FOOTER 71
#define PARAGRAPH 72
#define RULER 73
#define APPLICATION 74
#define AUTOCOMPLETE 75
#define EDITBAR 76
#define LAST_DEFINED 77
#define CALENDAR_VIEW  1001
#define CALENDAR_EVENT 1002

/*
  LDTP command related definitions
*/

struct object_info
{
	char *prefix;
	char *object_type;
	int instance_index;
	AccessibleRole role;
};

struct parent_path_info
{
	int *child_index;
	int child_index_count;
};

typedef struct parent_path_info PARENT_PATH_INFO;

typedef struct object_info OBJECT_INFO;

struct node
{
	int child_index;
	struct node *next;
};

Accessible *get_list_handle (Accessible *);
Accessible *get_text_handle (Accessible *);
Accessible *get_menu_handle (Accessible *);

int get_child_object_type (Accessible *);
int get_object_type (Accessible *);
int object_state_contains (Accessible *, int, FILE *);
int wait_till_object_state_contains (Accessible *object, int control_type, FILE *log_fp);

LDTPGuiHandle* ldtp_gui_get_gui_handle (LDTPClientContext* cctxt, LDTPErrorCode* err);
char *get_relation_name (Accessible *object, long *length);

int set_new_context (char *, char *);
int release_last_context (void);
GHashTable *get_window_list (void);
void ldtp_gui_free_gui_handle (LDTPGuiHandle *handle);
void ldtp_gui_gui_exist (LDTPClientContext* cctxt, LDTPErrorCode* err);
void ldtp_gui_wait_till_gui_exist (LDTPClientContext* cctxt, LDTPErrorCode* err);
void ldtp_gui_wait_till_gui_not_exist (LDTPClientContext* cctxt, LDTPErrorCode* err);
void update_cur_window_appmap_handle (LDTPClientContext* cctxt, LDTPErrorCode* err);
void update_cur_context_appmap_handle (LDTPClientContext* cctxt, LDTPErrorCode* err);
LDTPErrorCode grab_focus (Accessible *object, FILE *log_fp);

#endif /*__GUI_H__*/
