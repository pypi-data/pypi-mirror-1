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

#include <unistd.h>
#include <stdlib.h>
#include <glib.h>

#include "ldtp-error.h"

const char* 
ldtp_error_get_message (LDTPErrorCode error)
{
	char* msg = NULL;

	switch (error) {
	case LDTP_ERROR_SUCCESS: 
		msg = "Successfully completed";
		break;
	case LDTP_ERROR_ARGUMENT_NULL:
		msg = "Argument cannot be NULL. Please check the arguments.";
		break;
	case LDTP_ERROR_ACCEPT_FAILED:
		msg = "Error occurred while accepting request from client.  Please retry.";
		break;
	case LDTP_ERROR_UNABLE_TO_REINIT_LDTP:
		msg = "Unable to reinitialize LDTP";
		break;
	case LDTP_ERROR_UNABLE_TO_ALLOCATE_MEMORY:
		msg = "Unable to allocate memory";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_APPLICATION_LIST:
		msg = "Unable to get application list";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_OBJECT_LIST:
		msg = "Unable to get object list";
		break;
	case LDTP_ERROR_THREAD_CREATION_FAILED:
		msg = "Error creating client thread. Please retry.";
		break;
	case LDTP_ERROR_THREAD_DETACH_FAILED:
		msg = "Unable to detach the thread";
		break;
	case LDTP_ERROR_PACKET_INVALID:
		msg = "Packet received from client is not valid";
		break;
	case LDTP_ERROR_RECEIVE_RESPONSE:
		msg = "Error occurred while receiving response from client";
		break;
	case LDTP_ERROR_SENDING_RESPONSE:
		msg = "Error occurred while sending response to client";
		break;
	case LDTP_ERROR_PARTIAL_DATA_SENT:
		msg = "Warning!! Partial data sent";
		break;
	case LDTP_ERROR_INVALID_COMMAND:
		msg = "Invalid command";
		break;
	case LDTP_ERROR_INVALID_STATE:
		msg = "Invalid state";
		break;
	case LDTP_ERROR_APPMAP_NOT_INITIALIZED:
		msg = "Application map not initialized";
		break;
	case LDTP_ERROR_OPENING_APPMAP_FILE: /* FIXME: its better we show the filename with full path */
		msg = "Unable to open appmap file";
		break;
	case LDTP_ERROR_OPENING_LOG_FILE: /* FIXME: its better we show the filename with full path */
		msg = "Unable to open log file";
		break;
	case LDTP_ERROR_APP_NOT_RUNNING:
		msg = "Application not running";
		break;
	case LDTP_ERROR_UNABLE_TO_UPDATE_APPMAP:
		msg = "Unable to update appmap at runtime";
		break;
	case LDTP_ERROR_WIN_NAME_NOT_FOUND_IN_APPMAP:
		msg = "Unable to find window name in application map.";
		break;
	case LDTP_ERROR_OBJ_NAME_NOT_FOUND_IN_APPMAP:
		msg = "Unable to find object name in application map";
		break;
	case LDTP_ERROR_WIN_NOT_OPEN:
		msg = "Window does not exist";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_CONTEXT_HANDLE:
		msg = "Unable to get context handle";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_COMPONENT_HANDLE:
		msg = "Unable to get component handle";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_PROPERTY:
		msg = "Unable to get property";
		break;
	case LDTP_ERROR_GET_OBJ_HANDLE_FAILED:
		msg = "Unable to get object handle";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_CELL_HANDLE_FAILED:
		msg = "Unable to get cell handle";
		break;
	case LDTP_ERROR_OBJ_INFO_MISMATCH:
		msg = "Object information does not match with application map entry";
		break;
	case LDTP_ERROR_COMMAND_NOT_IMPLEMENTED:
		msg = "Requested action on mentioned object is not implemented";
		break;
	case LDTP_ERROR_GETTEXTVALUE_FAILED:
		msg = "GetTextValue action on mentioned object failed";
		break;
	case LDTP_ERROR_CHILD_TYPE_UNIDENTIFIED:
		msg = "Unable to identify the child type of mentioned object";
		break;
	case LDTP_ERROR_SELECTITEM_FAILED:
		msg = "SelectItem action on mentioned object failed.";
		break;
	case LDTP_ERROR_VERIFY_ITEM_FAILED:
		msg = "Verification of SelectItem failed on the mentioned object";
		break;
	case LDTP_ERROR_SELECTINDEX_FAILED:
		msg = "SelectIndex action on mentioned object failed.";
		break;
	case LDTP_ERROR_TEXT_NOT_FOUND:
		msg = "Text not found";
		break;
	case LDTP_ERROR_TEXT_STATE_ENABLED:
		msg = "Text state enabled";
		break;
	case LDTP_ERROR_TEXT_STATE_NOT_ENABLED:
		msg = "Text state not enabled";
		break;
	case LDTP_ERROR_SETTEXTVALUE_FAILED:
		msg = "SetTextValue action on mentioned object failed";
		break;
	case LDTP_ERROR_VERIFY_SETTEXTVALUE_FAILED:
		msg = "Verification of SetTextValue failed on the mentioned object";
		break;
	case LDTP_ERROR_CLICK_FAILED:
		msg = "Click action on mentioned object failed";
		break;
	case LDTP_ERROR_DOUBLE_CLICK_FAILED:
		msg = "Dobule click action on mentioned object failed";
		break;
	case LDTP_ERROR_RIGHT_CLICK_FAILED:
		msg = "Right click action on mentioned object failed";
		break;
	case LDTP_ERROR_CHILD_IN_FOCUS:
		msg = "Verification of HideList failed on the mentioned object as object's list is still in focus";
		break;
	case LDTP_ERROR_CHILD_NOT_FOCUSSED:
		msg = "Verification of DropDown failed on the mentioned object as object's list is not in focus";
		break;
	case LDTP_ERROR_MENU_VISIBLE:
		msg = "Verification of HideList failed on the mentioned object as object's menu is visible";
		break;
	case LDTP_ERROR_MENU_NOT_VISIBLE:
		msg = "Verification of DropDown failed on the mentioned object as object's menu is not visible";
		break;
	case LDTP_ERROR_HIDELIST_FAILED:
		msg = "Hide-List action on the mentioned object failed";
		break;
	case LDTP_ERROR_SHOWLIST_FAILED:
		msg = "Show-List action on the mentioned object failed";
		break;
	case LDTP_ERROR_VERIFY_SHOWLIST_FAILED:
		msg = "Verify show list on the mentioned object failed";
	case LDTP_ERROR_ITEM_NOT_FOUND:
		msg = "SelectItem failed as the mentioned item was not found in the object";
		break;
	case LDTP_ERROR_FILECAPTURE_FAILED_OPEN_OUTPUT_FILE:
		msg = "Capture to file action failed: Cannot open output file";
		break;
	case LDTP_ERROR_VERIFY_DROPDOWN_FAILED:
		msg = "Verification of dropdown action failed.";
		break;
	case LDTP_ERROR_CALENDAR_EVENT_INDEX_GREATER:
		msg = "Calendar event index greater than child count";
		break;
	case LDTP_ERROR_UNABLE_TO_SELECT_CALENDAR_EVENT_INDEX:
		msg = "Unable to select calendar event index";
		break;
	case LDTP_ERROR_UNABLE_TO_SELECT_CALENDAR_EVENT_NAME:
		msg = "Unable to select calendar event based on name";
		break;
	case LDTP_ERROR_NO_APPOINTMENTS_IN_CALENDAR:
		msg = "No appointments in calendar";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_VALUE:
		msg = "Unable to get value";
		break;
	case LDTP_ERROR_UNABLE_TO_GRAB_FOCUS:
		msg = "Unable to grab focus";
		break;
	case LDTP_ERROR_OBJ_NOT_COMPONENT_TYPE:
		msg = "Object is not of type component";
		break;
	case LDTP_ERROR_INVALID_DATE:
		msg = "Ivalid date, can't be selected";
		break;
	case LDTP_ERROR_INVALID_OBJECT_STATE:
		msg = "Invalid object state";
		break;
	case LDTP_ERROR_CHECK_ACTION_FAILED:
		msg = "Check action failed";
		break;
	case LDTP_ERROR_UNCHECK_ACTION_FAILED:
		msg = "Uncheck action failed";
		break;
	case LDTP_ERROR_STATE_CHECKED:
		msg = "Object state is checked";
		break;
	case LDTP_ERROR_STATE_UNCHECKED:
		msg = "Object state is unchecked";
		break;
	case LDTP_ERROR_UNABLE_TO_SELECT_LABEL:
		msg = "Unable to select label";
		break;
	case LDTP_ERROR_LABEL_NOT_FOUND:
		msg = "Label not found";
		break;
	case LDTP_ERROR_UNABLE_TO_SELECT_LAYERED_PANE_ITEM:
		msg = "Unable to select item in layered pane";
		break;
	case LDTP_ERROR_UNABLE_TO_SELECT_TEXT_ITEM:
		msg = "Unable to select text item in the list";
		break;
	case LDTP_ERROR_LIST_INDEX_GREATER:
		msg = "List index value is greater than available index";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_SELECTED_CHILD:
		msg = "Unable to get the selected child item from the list";
		break;
	case LDTP_ERROR_UNABLE_TO_SELECT_CHILD:
		msg = "Unable to select the child item in the list";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_CHILD_MENU_ITEM:
		msg = "Unable to get the child menu item";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_MENU_HANDLE:
		msg = "Unable to get menu handle";
		break;
	case LDTP_ERROR_MENU_ITEM_DOES_NOT_EXIST:
		msg = "Menu item does not exist";
		break;
	case LDTP_ERROR_UNABLE_TO_FIND_POPUP_MENU:
		msg = "Unable to find popup menu";
		break;
	case LDTP_ERROR_MENU_ITEM_STATE_DISABLED:
		msg = "Menu item state disabled";
		break;
	case LDTP_ERROR_SELECT_MENU_ITEM_FAILED:
		msg = "Select menu item failed";
		break;
	case LDTP_ERROR_UNABLE_TO_LIST_MENU_ITEMS:
		msg = "Unable to list menu items";
		break;
	case LDTP_ERROR_UNABLE_TO_SELECT_LIST_ITEM:
		msg = "Unable to select list item";
		break;
	case LDTP_ERROR_PAGE_TAB_NAME_SELECTION_FAILED:
		msg = "Page tab name selection failed";
		break;
	case LDTP_ERROR_PAGE_TAB_NAME_ALREADY_IN_SELECTED_STATE:
		msg = "Page tab name already in selected state";
		break;
	case LDTP_ERROR_PAGE_TAB_NAME_DOESNOT_EXIST:
		msg = "Page tab name does not exist";
		break;
	case LDTP_ERROR_PAGE_TAB_INDEX_DOESNOT_EXIST:
		msg = "Page tab index does not exist";
		break;
	case LDTP_ERROR_PAGE_TAB_NAME_INPUT_DOESNOT_EXIST:
		msg = "Page tab name does not exist";
		break;
	case LDTP_ERROR_PAGE_TAB_INDEX_INPUT_DOESNOT_EXIST:
		msg = "Page tab index does not exist";
		break;
	case LDTP_ERROR_NO_PANEL_EXIST:
		msg = "No panel exist";
		break;
	case LDTP_ERROR_PANEL_NAME_SELECTION_FAILED:
		msg = "Panel name selection failed";
		break;
	case LDTP_ERROR_PANEL_INDEX_SELECTION_FAILED:
		msg = "Panel index selection failed";
		break;
	case LDTP_ERROR_PANEL_COUNT_LESS_THAN_TOTAL_PANEL:
		msg = "Panels count less than total panel number";
		break;
	case LDTP_ERROR_RADIO_BUTTON_ALREADY_CHECKED:
		msg = "Radio button already checked";
		break;
	case LDTP_ERROR_RADIO_BUTTON_CHECKED:
		msg = "Radio button checked";
		break;
	case LDTP_ERROR_RADIO_BUTTON_STATE_NOT_ENABLED:
		msg = "Radio button state not enabled";
		break;
	case LDTP_ERROR_RADIO_BUTTON_NOT_CHECKED:
		msg = "Radio button not checked";
		break;
	case LDTP_ERROR_RADIO_MENU_ITEM_ALREADY_CHECKED:
		msg = "Radio menu item already checked";
		break;
	case LDTP_ERROR_RADIO_MENU_ITEM_CHECKED:
		msg = "Radio menu item checked";
		break;
	case LDTP_ERROR_RADIO_MENU_ITEM_NOT_CHECKED:
		msg = "Radio menu item not checked";
		break;
	case LDTP_ERROR_NOT_VERTICAL_SCROLL_BAR:
		msg = "Object not a vertical scrollbar";
		break;
	case LDTP_ERROR_UNABLE_TO_SCROLL_WITH_GIVEN_VALUE:
		msg = "Unable to scroll with the given value";
		break;
	case LDTP_ERROR_NOT_HORIZONTAL_SCROLL_BAR:
		msg = "Object not a horizontal scrollbar";
		break;
	case LDTP_ERROR_SCROLL_BAR_MAX_REACHED:
		msg = "Scrollbar trying to access more than maximum limit";
		break;
	case LDTP_ERROR_SCROLL_BAR_MIN_REACHED:
		msg = "Scrollbar trying to access less than minimum limit";
		break;
	case LDTP_ERROR_NOT_VERTICAL_SLIDER:
		msg = "Object not a vertical slider";
		break;
	case LDTP_ERROR_NOT_HORIZONTAL_SLIDER:
		msg = "Object not a horizontal slider";
		break;
	case LDTP_ERROR_SLIDER_SET_MAX_FAILED:
		msg = "Slider set maximum value failed";
		break;
	case LDTP_ERROR_SLIDER_SET_MIN_FAILED:
		msg = "Slider set minimum value failed";
		break;
	case LDTP_ERROR_UNABLE_TO_INCREASE_SLIDER_VALUE:
		msg = "Unable to increase slider value";
		break;
	case LDTP_ERROR_UNABLE_TO_DECREASE_SLIDER_VALUE:
		msg = "Unable to decrease slider value";
		break;
	case LDTP_ERROR_SLIDER_MAX_REACHED:
		msg = "Slider trying to access more than maximum limit";
		break;
	case LDTP_ERROR_SLIDER_MIN_REACHED:
		msg = "Slider trying to access less than minimum limit";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_SLIDER_VALUE:
		msg = "Unable to get slider value";
		break;
	case LDTP_ERROR_UNABLE_TO_SET_SPIN_BUTTON_VALUE:
		msg = "Unable to set spin button value";
		break;
	case LDTP_ERROR_UNABLE_TO_SPIN_BUTTON_VALUES_NOT_SAME:
		msg = "Spin button values are not same";
		break;
	case LDTP_ERROR_STATUSBAR_GETTEXT_FAILED:
		msg = "Unable to get text from status bar";
		break;
	case LDTP_ERROR_STATUSBAR_NOT_VISIBLE:
		msg = "Status bar not visible";
		break;
	case LDTP_ERROR_TOGGLE_ACTION_FAILED:
		msg = "Toggle action failed";
		break;
	case LDTP_ERROR_TOGGLE_CHECKED:
		msg = "Toggle button checked";
		break;
	case LDTP_ERROR_TOGGLE_NOT_CHECKED:
		msg = "Toggle button not checked";
		break;
	case LDTP_ERROR_TOOLBAR_VISIBLE_BUTTON_COUNT_FAILED:
		msg = "Toolbar visible button count failed";
		break;
	case LDTP_ERROR_TOOLBAR_BUTTON_COUNT_FAILED:
		msg = "Toolbar button count failed";
		break;
	case LDTP_ERROR_UNABLE_TO_SET_TEXT:
		msg = "Unable to set text";
		break;
	case LDTP_ERROR_VERIFY_SET_TEXT_FAILED:
		msg = "Verify set text value failed";
		break;
	case LDTP_ERROR_VERIFY_PARTIAL_MATCH_FAILED:
		msg = "Verify partial match failed";
		break;
	case LDTP_ERROR_UNABLE_TO_CUT_TEXT:
		msg = "Unable to cut text";
		break;
	case LDTP_ERROR_UNABLE_TO_COPY_TEXT:
		msg = "Unable to copy text";
		break;
	case LDTP_ERROR_UNABLE_TO_INSERT_TEXT:
		msg = "Unable to insert text";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_TEXT_PROPERTY:
		msg = "Unable to get text property";
		break;
	case LDTP_ERROR_TEXT_OBJECT_VALUE_CONTAINS_DIFF_PROEPRTY:
		msg = "Text object value contains different property";
		break;
	case LDTP_ERROR_TEXT_OBJECT_DOES_NOT_CONTAIN_PROEPRTY:
		msg = "Text object does not contain property";
		break;
	case LDTP_ERROR_TEXT_PROEPRTY_VALUE_PAIR_IS_INVALID:
		msg = "Given text property value pair is invalid";
		break;
	case LDTP_ERROR_ONE_OR_MORE_PROPERTIES_DOES_NOT_MATCH:
		msg = "One or more properties does not match";
		break;
	case LDTP_ERROR_TEXT_TO_INSERT_IS_EMPTY:
		msg = "Text to insert is empty";
		break;
	case LDTP_ERROR_UNABLE_TO_ACTIVATE_TEXT:
		msg = "Unable to activate text";
		break;
	case LDTP_ERROR_UNABLE_TO_PASTE_TEXT:
		msg = "Unable to paste text";
		break;
	case LDTP_ERROR_UNABLE_TO_DELETE_TEXT:
		msg = "Unable to delete text";
		break;
	case LDTP_ERROR_UNABLE_TO_SELECT_TEXT:
		msg = "Unable to select text";
		break;
	case LDTP_ERROR_UNABLE_TO_APPEND_TEXT:
		msg = "Unable to append text";
		break;
	case LDTP_ERROR_INVALID_COLUMN_INDEX_TO_SORT:
		msg = "Invalid column index given for sorting";
		break;
	case LDTP_ERROR_UNABLE_TO_SORT:
		msg = "Unable to sort";
		break;
	case LDTP_ERROR_ROW_DOES_NOT_EXIST:
		msg = "Row does not exist";
		break;
	case LDTP_ERROR_COLUMN_DOES_NOT_EXIST:
		msg = "Column does not exist";
		break;
	case LDTP_ERROR_UNABLE_TO_SELECT_ROW:
		msg = "Unable to select row";
		break;
	case LDTP_ERROR_VERIFY_TABLE_CELL_FAILED:
		msg = "Verify table cell failed";
		break;
	case LDTP_ERROR_VERIFY_TABLE_CELL_PARTIAL_MATCH_FAILED:
		msg = "Verify table cell partial match failed";
		break;
	case LDTP_ERROR_SET_TABLE_CELL_FAILED:
		msg = "Set table cell failed";
		break;
	case LDTP_ERROR_GET_TABLE_CELL_FAILED:
		msg = "Get table cell failed";
		break;
	case LDTP_ERROR_GET_TREE_TABLE_CELL_FAILED:
		msg = "Get table cell failed";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_ROW_INDEX:
		msg = "Unable to find row index";
		break;
	case LDTP_ERROR_NO_CHILD_TEXT_TYPE_UNDER_TABLE:
		msg = "Table cell has no child of type text";
		break;
	case LDTP_ERROR_ACTUAL_ROW_COUNT_LESS_THAN_GIVEN_ROW_COUNT:
		msg = "Actual row count less than given row count";
		break;
	case LDTP_ERROR_ACTUAL_COLUMN_COUNT_LESS_THAN_GIVEN_COLUMN_COUNT:
		msg = "Actual column count less than given column count";
		break;
	case LDTP_ERROR_UNABLE_TO_PERFORM_ACTION:
		msg = "Unable to perform action";
		break;
	case LDTP_ERROR_GUI_EXIST:
		msg = "GUI exist";
		break;
	case LDTP_ERROR_GUI_NOT_EXIST:
		msg = "GUI does not exist";
		break;
	case LDTP_ERROR_CALLBACK:
		msg = "callback";
		break;
	case LDTP_ERROR_UNABLE_TO_CREATE_PO:
		msg = "Unable to create po";
		break;
	case LDTP_ERROR_UNABLE_TO_DELETE_PO:
		msg = "Unable to delete po";
		break;
	case LDTP_ERROR_ONLY_MO_MODE_SUPPORTED:
		msg = "Only MO mode supported";
		break;
	case LDTP_ERROR_UTF8_ENGLISH_LANG:
		msg = "UTF8 default English language";
		break;
	case LDTP_ERROR_UNABLE_TO_STAT_DIR:
		msg = "Unable to stat directory";
		break;
	case LDTP_ERROR_ROLE_NOT_IMPLEMENTED:
		msg = "Mentioned role not implemented.";
		break;
        case LDTP_ERROR_UNABLE_TO_MOVE_MOUSE:
                msg = "Mouse Cursor move failed";
                break;
	case LDTP_ERROR_INVALID_FORMAT:
		msg = "Invalid Format";
		break;
	case LDTP_ERROR_TOKEN_NOT_FOUND:
		msg = "Invalid Key";
		break;
	case LDTP_ERROR_UNABLE_TO_ENTER_KEY:
		msg = "Error while entering key";
		break;
	case LDTP_ERROR_OFFSET_OUT_OF_BOUND:
		msg = "Offset value greater than number of characters";
		break;
	case LDTP_ERROR_UNABLE_TO_SET_CARET:
		msg = "Unable to set the cursor position";
		break;
	case LDTP_ERROR_TEXT_NOT_ACCESSIBLE:
		msg = "TextBox not Accessible";
		break;
	case LDTP_ERROR_STOP_SCRIPT_ENGINE:
		msg = "Stop LDTP script engine";
		break;
	case LDTP_ERROR_WRONG_COMMAND_SEQUENCE:
		msg = "Wrong command sequence, stop called before start";
		break;
	case LDTP_ERROR_UNABLE_TO_LAUNCH_APP:
		msg = "Unable to launch application";
		break;
	case LDTP_ERROR_CLIENT_DISCONNECTED:
		msg = "Client disconnected";
		break;
	case LDTP_ERROR_EVENT_NOTIFIER_NOT_ENABLED:
		msg = "Event notifier not registered";
		break;
	case LDTP_ERROR_SET_GUI_TIMEOUT_FAILED:
		msg = "Unable to set gui timeout period";
		break;
	case LDTP_ERROR_SET_OBJ_TIMEOUT_FAILED:
		msg = "Unable to set obj timeout period";
		break;
	case LDTP_ERROR_UNABLE_TO_GET_CHILD_WITH_PROVIDED_ROLE:
		msg = "Unable to get child with provided role";
		break;
	default:
		msg = "Error code not found";
		break;
	}
	return msg;
}
