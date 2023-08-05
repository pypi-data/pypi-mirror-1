/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 8; tab-width: 8 -*- */
/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org/
 *
 * Author:
 *    A Nagappan <nagappan@gmail.com>
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

#ifndef _LDTP_GUI_COMP_H
#define _LDTP_GUI_COMP_H

#include "client-handler.h"

//calendar.c
LDTPErrorCode calendar_main (LDTPClientContext* cctxt, int command);

//calendar-view.c
LDTPErrorCode calendar_view_main (LDTPClientContext* cctxt, int command);

// check-box.c
LDTPErrorCode check_box_main (LDTPClientContext* cctxt, int command);

// check-menu-item.c
LDTPErrorCode check_menu_item_main (LDTPClientContext* cctxt, int command);

// combo-box.c
LDTPErrorCode combo_box_main (LDTPClientContext* cctxt, int command);

// icon.c
LDTPErrorCode icon_main (LDTPClientContext* cctxt, int command);

// label.c
LDTPErrorCode label_main (LDTPClientContext* cctxt, int command);

// layered-pane.c
LDTPErrorCode layered_pane_main (LDTPClientContext* cctxt, int command);

// list.c
LDTPErrorCode list_main (LDTPClientContext* cctxt, int command);

// menu.c
LDTPErrorCode menu_main (LDTPClientContext* cctxt, int command, char *window_name);

// menu-item.c
LDTPErrorCode menu_item_main (LDTPClientContext* cctxt,int command);

// panel.c
LDTPErrorCode panel_main (LDTPClientContext* cctxt, int command);

// push-button.c
LDTPErrorCode push_button_main (LDTPClientContext* cctxt, int command);

// page-tab-list.c
LDTPErrorCode page_tab_list_main (LDTPClientContext* cctxt, int command);

// radio-button.c
LDTPErrorCode radio_button_main (LDTPClientContext* cctxt, int command);

// radio-menu-item.c
LDTPErrorCode radio_menu_item_main (LDTPClientContext* cctxt, int command);

// scroll-bar.c
LDTPErrorCode scroll_bar_main (LDTPClientContext* cctxt, int command);

// scroll-pane.c
LDTPErrorCode scroll_pane_main (LDTPClientContext* cctxt, int command);

// status-bar.c
LDTPErrorCode status_bar_main (LDTPClientContext* cctxt, int command);

//slider.c
LDTPErrorCode slider_main (LDTPClientContext* cctxt, int command);

// spin-button.c
LDTPErrorCode spin_button_main (LDTPClientContext* cctxt, int command);

// table.c
LDTPErrorCode table_main (LDTPClientContext* cctxt, int command);

// text.c
LDTPErrorCode text_main (LDTPClientContext* cctxt, int command);

// toggle-button.c
LDTPErrorCode toggle_button_main (LDTPClientContext* cctxt, int command);

// tree-table.c
LDTPErrorCode tree_table_main(LDTPClientContext* cctxt, int command);

//tool-bar.c
LDTPErrorCode tool_bar_main (LDTPClientContext* cctxt, int command);

//device.c
LDTPErrorCode device_main (LDTPClientContext* cctxt, int command);

// embedded-component.c
LDTPErrorCode embedded_component_main (LDTPClientContext* cctxt, int command);

/*
  Common functions
*/
// page-tab-list.c
long get_page_tab_index (Accessible*);

char *get_name_from_hash_table (LDTPClientContext*, Accessible*, char*, 
				int, gboolean);

#endif
