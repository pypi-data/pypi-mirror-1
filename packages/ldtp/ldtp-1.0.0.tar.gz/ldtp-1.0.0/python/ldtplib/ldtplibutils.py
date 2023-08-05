############################################################################
#
#  Linux Desktop Testing Project http://ldtp.freedesktop.org
# 
#  Author:
#     A. Nagappan <nagappan@gmail.com>
# 
#  Copyright 2004 - 2006 Novell, Inc.
# 
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Library General Public
#  License as published by the Free Software Foundation; either
#  version 2 of the License, or (at your option) any later version.
# 
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Library General Public License for more details.
# 
#  You should have received a copy of the GNU Library General Public
#  License along with this library; if not, write to the
#  Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#  Boston, MA 02110, USA.
#
#############################################################################

import socket, os, struct, time, traceback
import threading, re, thread, select
import sys, logging, logging.config
from xml.sax import saxutils

try:
    import pyatspi as atspi, Accessibility
except ImportError:
    import atspi
    import Accessibility

ldtpDebug = os.getenv ('LDTP_DEBUG')

# General functions
class command:
    INVALID = 0
    LOG = 1
    STARTLOG = 2
    STOPLOG = 3
    CHECK = 4
    UNCHECK = 5
    MENUCHECK = 6
    MENUUNCHECK = 7
    CLICK = 8
    VERIFYCHECK = 9
    VERIFYUNCHECK = 10
    VERIFYMENUCHECK = 11
    VERIFYMENUUNCHECK = 12
    HIDELIST = 13
    COMBOSELECT = 14
    COMBOSELECTINDEX = 15 
    SELECTINDEX = 16
    ISTEXTSTATEENABLED = 17
    SETTEXTVALUE = 18
    GETTEXTVALUE = 19
    APPENDTEXT = 20
    ACTIVATETEXT = 21
    CUTTEXT = 22
    PASTETEXT = 23
    DELETETEXT = 24
    SELECTTEXTBYNAME = 25
    SELECTTEXTBYINDEXANDREGION = 26
    SHOWLIST = 27
    VERIFYDROPDOWN = 28
    VERIFYHIDELIST = 29
    VERIFYSHOWLIST = 30
    VERIFYSELECT = 31
    VERIFYSETTEXT = 32
    RIGHTCLICK = 33
    GETLABEL = 34
    GETLABELATINDEX = 35
    SELECTPOPUPMENU = 36
    SELECTITEM = 37
    SELECTTEXTITEM = 38
    ISMENUITEMENABLED = 39
    SELECTMENUITEM = 40
    SELECTTAB = 41
    VERIFYPUSHBUTTON = 42
    STATEENABLED = 43
    SETVALUE = 44
    GETVALUE = 45
    VERIFYSETVALUE = 46
    SELECTROW = 47
    SELECTROWINDEX = 48
    SELECTROWPARTIALMATCH = 49
    VERIFYTOGGLED = 50
    ONEDOWN = 51
    ONEUP = 52
    ONERIGHT = 53
    ONELEFT = 54
    SCROLLDOWN = 55
    SCROLLUP = 56
    SCROLLRIGHT = 57
    SCROLLLEFT = 58
    VERIFYSCROLLBAR = 59
    VERIFYSCROLLBARVERTICAL = 60
    VERIFYSCROLLBARHORIZONTAL = 61
    SETMAX = 62
    SETMIN = 63
    INCREASE = 64
    DECREASE = 65
    SELECTPANEL = 66
    SELECTPANELNAME = 67
    GETPANELCHILDCOUNT = 68
    VERIFYTABLECELL = 69
    SETCELLVALUE = 70
    GETCELLVALUE = 71
    SELECTLASTROW = 72
    SELECTLABELSPANELBYNAME = 73
    SETCONTEXT = 74
    RELEASECONTEXT = 75 
    GETSTATUSBARTEXT = 76
    SELECTEVENT = 77
    SELECTEVENTINDEX = 78
    DOESROWEXIST = 79
    DOESMENUITEMEXIST = 80
    LISTSUBMENUS = 81
    CHECKROW = 82
    VERIFYPARTIALMATCH = 83
    GETROWCOUNT = 84
    VERIFYPARTIALTABLECELL = 85
    GRABFOCUS = 86
    VERIFYEVENTEXIST = 87
    EXPANDTABLECELL = 88
    GETTREETABLEROWINDEX = 89
    VERIFYCHECKROW = 90
    VERIFYUNCHECKROW = 91
    VERIFYVISIBLEBUTTONCOUNT = 92
    VERIFYBUTTONCOUNT = 93
    GETEVENTCOUNT = 94
    DOUBLECLICKROW = 95
    GETTABLEROWINDEX = 96
    GETCHARCOUNT = 97
    COPYTEXT = 98
    INSERTTEXT = 99
    UNCHECKROW = 100
    CAPTURETOFILE = 101
    DOUBLECLICK = 102
    GETTEXTPROPERTY = 103
    COMPARETEXTPROPERTY = 104
    CONTAINSTEXTPROPERTY = 105
    SELECTCALENDARDATE = 106
    SELECTTABINDEX = 107
    SORTCOLUMNINDEX = 108
    SORTCOLUMN = 109
    REINITLDTP = 110
    INITAPPMAP = 111
    SETAPPMAP = 112
    VERIFYSLIDER = 113
    VERIFYSLIDERVERTICAL = 114
    VERIFYSLIDERHORIZONTAL = 115
    GETSLIDERVALUE = 116
    VERIFYSTATUSBAR = 117
    VERIFYSTATUSBARVISIBLE = 118
    WAITTILLGUIEXIST = 119
    WAITTILLGUINOTEXIST = 120
    GUIEXIST = 121
    ONWINDOWCREATE = 122
    REMAP = 123
    GETAPPLIST = 124
    GETWINDOWLIST = 125
    GETOBJECTLIST = 126
    GETOBJECTINFO = 127
    GETOBJECTPROPERTY = 128
    BINDTEXT = 129
    GENERATEMOUSEEVENT = 130
    GENERATEKEYEVENT = 131
    MOUSELEFTCLICK = 132
    MOUSERIGHTCLICK = 133
    MOUSEMOVE = 134
    KBDENTER = 135
    SETCURSOR = 136
    GETCURSOR = 137
    GETTABCOUNT = 138
    STOPSCRIPTENGINE = 139
    HASSTATE = 140
    LAUNCHAPP = 141
    SINGLECLICKROW = 142
    SETLOCALE = 143
    INVOKEMENU = 144
    PRESS = 145
    REMOVECALLBACK = 146
    GUITIMEOUT = 147
    OBJTIMEOUT = 148
    GETCHILD = 149
    LASTCOMMAND = 150

class state:
    INVALID = Accessibility.STATE_INVALID
    ACTIVE = Accessibility.STATE_ACTIVE
    ARMED = Accessibility.STATE_ARMED
    BUSY = Accessibility.STATE_BUSY
    CHECKED = Accessibility.STATE_CHECKED
    COLLAPSED = Accessibility.STATE_COLLAPSED
    DEFUNCT = Accessibility.STATE_DEFUNCT
    EDITABLE = Accessibility.STATE_EDITABLE
    ENABLED = Accessibility.STATE_ENABLED
    EXPANDABLE = Accessibility.STATE_EXPANDABLE
    EXPANDED = Accessibility.STATE_EXPANDED
    FOCUSABLE = Accessibility.STATE_FOCUSABLE
    FOCUSED = Accessibility.STATE_FOCUSED
    HORIZONTAL = Accessibility.STATE_HORIZONTAL
    ICONIFIED = Accessibility.STATE_ICONIFIED
    MODAL = Accessibility.STATE_MODAL
    MULTI_LINE = Accessibility.STATE_MULTI_LINE
    MULTISELECTABLE = Accessibility.STATE_MULTISELECTABLE
    OPAQUE = Accessibility.STATE_OPAQUE
    PRESSED = Accessibility.STATE_PRESSED
    RESIZABLE = Accessibility.STATE_RESIZABLE
    SELECTABLE = Accessibility.STATE_SELECTABLE
    SELECTED = Accessibility.STATE_SELECTED
    SENSITIVE = Accessibility.STATE_SENSITIVE
    SHOWING = Accessibility.STATE_SHOWING
    SINGLE_LINE = Accessibility.STATE_SINGLE_LINE
    STALE = Accessibility.STATE_STALE
    TRANSIENT = Accessibility.STATE_TRANSIENT
    VERTICAL = Accessibility.STATE_VERTICAL
    VISIBLE = Accessibility.STATE_VISIBLE
    MANAGES_DESCENDANTS = Accessibility.STATE_MANAGES_DESCENDANTS
    INDETERMINATE = Accessibility.STATE_INDETERMINATE
    LAST_DEFINED = Accessibility.STATE_LAST_DEFINED
    try:
        TRUNCATED = Accessibility.STATE_TRUNCATED
        REQUIRED = Accessibility.STATE_REQUIRED
        INVALID_ENTRY = Accessibility.STATE_INVALID_ENTRY
        SUPPORTS_AUTOCOMPLETION = Accessibility.STATE_SUPPORTS_AUTOCOMPLETION
        SELECTABLE_TEXT = Accessibility.STATE_SELECTABLE_TEXT
        IS_DEFAULT = Accessibility.STATE_IS_DEFAULT
        VISISTED = Accessibility.STATE_VISITED
    except:
        if ldtpDebug is not None:
            print 'New roles'
        pass

class LdtpErrorCode:
    SUCCESS = 0
    ARGUMENT_NULL = -1001
    ACCEPT_FAILED = -1002
    UNABLE_TO_REINIT_LDTP = -1003
    UNABLE_TO_ALLOCATE_MEMORY = -1004
    UNABLE_TO_GET_APPLICATION_LIST = -1005
    UNABLE_TO_GET_OBJECT_LIST = -1006
    THREAD_CREATION_FAILED = -1007
    THREAD_DETACH_FAILED = -1008
    PACKET_INVALID = -1009
    RECEIVE_RESPONSE = -1010
    SENDING_RESPONSE = -1011
    PARTIAL_DATA_SENT = -1012
    INVALID_COMMAND = -1013
    INVALID_STATE = -1014
    APPMAP_NOT_INITIALIZED = -1015
    OPENING_APPMAP_FILE = -1016
    OPENING_LOG_FILE = -1017
    APP_NOT_RUNNING = -1018
    UNABLE_TO_UPDATE_APPMAP = -1019
    WIN_NAME_NOT_FOUND_IN_APPMAP = -1020
    OBJ_NAME_NOT_FOUND_IN_APPMAP = -1021
    WIN_NOT_OPEN = -1022
    UNABLE_TO_GET_CONTEXT_HANDLE = -1023
    UNABLE_TO_GET_COMPONENT_HANDLE = -1024
    UNABLE_TO_GET_PROPERTY = -1025
    GET_OBJ_HANDLE_FAILED = -1026
    UNABLE_TO_GET_CELL_HANDLE_FAILED = -1027
    OBJ_INFO_MISMATCH = -1028
    COMMAND_NOT_IMPLEMENTED = -1029
    GETTEXTVALUE_FAILED = -1030
    STATUSBAR_GETTEXT_FAILED = -1031
    STATUSBAR_NOT_VISIBLE = -1032
    CHILD_TYPE_UNIDENTIFIED = -1033
    SELECTITEM_FAILED = -1034
    VERIFY_ITEM_FAILED = -1035
    SELECTINDEX_FAILED = -1036
    TEXT_NOT_FOUND = -1037
    TEXT_STATE_ENABLED = -1038
    TEXT_STATE_NOT_ENABLED = -1039
    SETTEXTVALUE_FAILED = -1040
    VERIFY_SETTEXTVALUE_FAILED = -1041
    CLICK_FAILED = -1042
    DOUBLE_CLICK_FAILED = -1043
    RIGHT_CLICK_FAILED = -1044
    CHILD_IN_FOCUS = -10045
    CHILD_NOT_FOCUSSED = -1046
    UNABLE_TO_GET_MENU_HANDLE = -1047
    UNABLE_TO_FIND_POPUP_MENU = -1048
    MENU_VISIBLE = -1049
    MENU_NOT_VISIBLE = -1050
    HIDELIST_FAILED = -1051
    SHOWLIST_FAILED = -1052
    VERIFY_SHOWLIST_FAILED = -1053
    ITEM_NOT_FOUND = -1054
    FILECAPTURE_FAILED_OPEN_OUTPUT_FILE = -1055
    VERIFY_DROPDOWN_FAILED = -1056
    CALENDAR_EVENT_INDEX_GREATER = -1057
    UNABLE_TO_SELECT_CALENDAR_EVENT_INDEX = -1058
    UNABLE_TO_SELECT_CALENDAR_EVENT_NAME = -1059
    NO_APPOINTMENTS_IN_CALENDAR = -1060
    UNABLE_TO_GET_VALUE = -1061
    UNABLE_TO_GRAB_FOCUS = -1062
    OBJ_NOT_COMPONENT_TYPE = -1063
    INVALID_DATE = -1064
    INVALID_OBJECT_STATE = -1065
    CHECK_ACTION_FAILED = -1066
    UNCHECK_ACTION_FAILED = -1067
    STATE_CHECKED = -1068
    STATE_UNCHECKED = -1069
    UNABLE_TO_SELECT_LABEL = -1070
    LABEL_NOT_FOUND = -1071
    UNABLE_TO_SELECT_LAYERED_PANE_ITEM = -1072
    UNABLE_TO_SELECT_TEXT_ITEM = -1073
    LIST_INDEX_GREATER = -1074
    UNABLE_TO_GET_SELECTED_CHILD = -1075
    UNABLE_TO_SELECT_CHILD = -1076
    UNABLE_TO_GET_CHILD_MENU_ITEM = -1077
    UNABLE_TO_LIST_MENU_ITEMS = -1078
    UNABLE_TO_SELECT_LIST_ITEM = -1079
    MENU_ITEM_DOES_NOT_EXIST = -1080
    MENU_ITEM_STATE_DISABLED = -1081
    SELECT_MENU_ITEM_FAILED = -1082
    PAGE_TAB_NAME_SELECTION_FAILED = -1083
    PAGE_TAB_NAME_ALREADY_IN_SELECTED_STATE = -1084
    PAGE_TAB_NAME_DOESNOT_EXIST = -1085
    PAGE_TAB_INDEX_DOESNOT_EXIST = -1086
    PAGE_TAB_NAME_INPUT_DOESNOT_EXIST = -1087
    PAGE_TAB_INDEX_INPUT_DOESNOT_EXIST = -1088
    NO_PANEL_EXIST = -1089
    PANEL_NAME_SELECTION_FAILED = -1090
    PANEL_INDEX_SELECTION_FAILED = -1091
    PANEL_COUNT_LESS_THAN_TOTAL_PANEL = -1092
    RADIO_BUTTON_ALREADY_CHECKED = -1093
    RADIO_BUTTON_STATE_NOT_ENABLED = -1094
    RADIO_BUTTON_CHECKED = -1095
    RADIO_BUTTON_NOT_CHECKED = -1096
    RADIO_MENU_ITEM_ALREADY_CHECKED = -1097
    RADIO_MENU_ITEM_CHECKED = -1098
    RADIO_MENU_ITEM_NOT_CHECKED = -1099
    NOT_VERTICAL_SCROLL_BAR = -1100
    UNABLE_TO_SCROLL_WITH_GIVEN_VALUE = -1101
    NOT_HORIZONTAL_SCROLL_BAR = -1102
    SCROLL_BAR_MAX_REACHED = -1103
    SCROLL_BAR_MIN_REACHED = -1104
    NOT_VERTICAL_SLIDER = -1105
    NOT_HORIZONTAL_SLIDER = -1106
    SLIDER_SET_MAX_FAILED = -1107
    SLIDER_SET_MIN_FAILED = -1108
    SLIDER_MAX_REACHED = -1109
    SLIDER_MIN_REACHED = -1110
    UNABLE_TO_INCREASE_SLIDER_VALUE = -1111
    UNABLE_TO_DECREASE_SLIDER_VALUE = -1112
    UNABLE_TO_GET_SLIDER_VALUE = -1113
    UNABLE_TO_SET_SPIN_BUTTON_VALUE = -1114
    UNABLE_TO_SPIN_BUTTON_VALUES_NOT_SAME = -1115
    TOGGLE_ACTION_FAILED = -1116
    TOGGLE_CHECKED = -1117
    TOGGLE_NOT_CHECKED = -1118
    TOOLBAR_VISIBLE_BUTTON_COUNT_FAILED = -1119
    TOOLBAR_BUTTON_COUNT_FAILED = -1120
    UNABLE_TO_SET_TEXT = -1121
    UNABLE_TO_CUT_TEXT = -1122
    UNABLE_TO_COPY_TEXT = -1123
    UNABLE_TO_PASTE_TEXT = -1124
    UNABLE_TO_DELETE_TEXT = -1125
    UNABLE_TO_SELECT_TEXT = -1126
    UNABLE_TO_ACTIVATE_TEXT = -1127
    UNABLE_TO_APPEND_TEXT = -1128
    UNABLE_TO_INSERT_TEXT = -1129
    UNABLE_TO_GET_TEXT_PROPERTY = -1130
    ONE_OR_MORE_PROPERTIES_DOES_NOT_MATCH = -1131
    TEXT_OBJECT_VALUE_CONTAINS_DIFF_PROEPRTY = -1132
    TEXT_OBJECT_DOES_NOT_CONTAIN_PROEPRTY = -1133
    TEXT_PROEPRTY_VALUE_PAIR_IS_INVALID = -1134
    TEXT_TO_INSERT_IS_EMPTY = -1135
    VERIFY_SET_TEXT_FAILED = -1136
    VERIFY_PARTIAL_MATCH_FAILED = -1137
    INVALID_COLUMN_INDEX_TO_SORT = -1138
    UNABLE_TO_SORT = -1139
    ROW_DOES_NOT_EXIST = -1140
    COLUMN_DOES_NOT_EXIST = -1141
    UNABLE_TO_SELECT_ROW = -1142
    UNABLE_TO_GET_ROW_INDEX = -1143
    SET_TABLE_CELL_FAILED = -1144
    GET_TABLE_CELL_FAILED = -1145
    VERIFY_TABLE_CELL_FAILED = -1146
    VERIFY_TABLE_CELL_PARTIAL_MATCH_FAILED = -1147
    ACTUAL_ROW_COUNT_LESS_THAN_GIVEN_ROW_COUNT = -1148
    ACTUAL_COLUMN_COUNT_LESS_THAN_GIVEN_COLUMN_COUNT = -1149
    GET_TREE_TABLE_CELL_FAILED = -1150
    NO_CHILD_TEXT_TYPE_UNDER_TABLE = -1151
    UNABLE_TO_PERFORM_ACTION = -1152
    GUI_EXIST = -1153
    GUI_NOT_EXIST = -1154
    CALLBACK = -1155
    UNABLE_TO_CREATE_PO = -1156
    UNABLE_TO_DELETE_PO = -1157
    ONLY_MO_MODE_SUPPORTED = -1158
    UTF8_ENGLISH_LANG = -1159
    UNABLE_TO_STAT_DIR = -1160
    ROLE_NOT_IMPLEMENTED = -1161
    UNABLE_TO_MOVE_MOUSE = -1162
    INVALID_FORMAT = -1163
    TOKEN_NOT_FOUND = -1164
    UNABLE_TO_ENTER_KEY = -1165
    UNABLE_TO_SET_CARET = -1166
    OFFSET_OUT_OF_BOUND = -1167
    TEXT_NOT_ACCESSIBLE = -1168
    STOP_SCRIPT_ENGINE = -1169
    WRONG_COMMAND_SEQUENCE = -1170
    UNABLE_TO_LAUNCH_APP = -1171
    CLIENT_DISCONNECTED = -1172
    EVENT_NOTIFIER_NOT_ENABLED = -1173
    SET_GUI_TIMEOUT_FAILED = -1174
    SET_OBJ_TIMEOUT_FAILED = -1175
    UNABLE_TO_GET_DEVICE = -1176
    UNABLE_TO_GET_CHILD_WITH_PROVIDED_ROLE = -1177

class XmlTags:
    XML_HEADER                   = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    RESPONSE_ELEMENT             = "<RESPONSE>"
    RESPONSE_ID_ELEMENT          = "<ID>"
    RESPONSE_ID_END_ELEMENT      = "</ID>"
    STATUS_ELEMENT               = "<STATUS>"
    ATTRIBUTE_CODE_ELEMENT       = "<CODE>"
    ATTRIBUTE_CODE_END_ELEMENT   = "</CODE>"
    ATTRIBUTE_MSG_ELEMENT        = "<MESSAGE>"
    ATTRIBUTE_MSG_END_ELEMENT    = "</MESSAGE>"
    STATUS_END_ELEMENT           = "</STATUS>"
    DATA_ELEMENT                 = "<DATA>"
    ATTRIBUTE_LENGTH_ELEMENT     = "<LENGTH>"
    ATTRIBUTE_LENGTH_END_ELEMENT = "</LENGTH>"
    ATTRIBUTE_FILE_ELEMENT       = "<FILE>"
    ATTRIBUTE_FILE_END_ELEMENT   = "</FILE>"
    ATTRIBUTE_NAME_ELEMENT       = "<NAME>"
    ATTRIBUTE_NAME_END_ELEMENT   = "</NAME>"
    ATTRIBUTE_VALUE_ELEMENT      = "<VALUE><![CDATA["
    ATTRIBUTE_VALUE_END_ELEMENT  = "]]></VALUE>"
    DATA_END_ELEMENT             = "</DATA>"
    RESPONSE_END_ELEMENT         = "</RESPONSE>"
    NOTIFICATION_ELEMENT         = "<NOTIFICATION>"
    NOTIFICATION_END_ELEMENT     = "</NOTIFICATION>"

class error (Exception):
    def __init__ (self, value):
        self.value = value
    def __str__ (self):
        return repr (self.value)

class LdtpExecutionError (Exception):
    def __init__ (self, value):
        self.value = value
    def __str__ (self):
        return repr (self.value)

class ConnectionLost (Exception):
    def __init__ (self, value):
        self.value = value
    def __str__ (self):
        return repr (self.value)

def getText (nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def getCData (nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.CDATA_SECTION_NODE:
            rc = rc + node.data
    return rc

def wait (seconds = 5):
    try:
        time.sleep (seconds)
    except TypeError:
        time.sleep (5)

def waitnanoseconds (nanoSeconds = 30000.0):
    try:
        time.sleep (nanoSeconds / pow (10, 9))
    except TypeError:
        time.sleep (30000.0 / pow (10, 9))

# Send given packet to server
def sendpacket (msg):
	flag = False
	try:
		timedelay = os.getenv ('LDTP_DELAY_CMD')
		_sendLck.acquire ()
		if timedelay != None:
			try:
				# Delay each command by 'timedelay' seconds
				time.sleep (int (timedelay))
			except IndexError:
				# Default to 5 seconds delay if LDTP_DELAY_CMD
				# env variable is set
				time.sleep (5)
		flag = True
		# Get client socket fd based on thread id
		client = sockFdPool.get (threading.currentThread ())
		
		# Encode the message in UTF-8 so we don't break on extended
		# characters in the application GUIs
		buf = msg.encode ('utf8')
		
		# Pack length (integer value) in network byte order
		msglen = struct.pack ('!i', len (buf))
		# Send message length
		client.send (msglen)
		# Send message
		client.send (buf)
		if ldtpDebug != None and ldtpDebug == '2':
			print 'Send packet', buf
		#_sendLck.release ()
	except socket.error, msg:
		raise LdtpExecutionError ('Server aborted')
	except:
                if ldtpDebug:
                    print traceback.print_exc ()
                raise LdtpExecutionError (str (traceback.print_exc ()))
        finally:
		if flag:
			# Reason for using the flag:
			# 'Do not call this method when the lock is unlocked.'
			_sendLck.release ()
                        flag = False

def recvpacket (peek_flag = 0, sockfd = None):
	flag = False
	try:
		_recvLck.acquire ()
		flag = True
		client = None
		# Get client socket fd based on thread id
		if sockfd == None:
			client = sockFdPool.get (threading.currentThread ())
		else:
			client = sockfd
		_responsePacket = None
		client.settimeout (5.0)
		# Hardcoded 4 bytes, as the server sends 4 bytes as packet length
		data = client.recv (4, peek_flag)
		if data == '' or data == None:
			if flag == True:
				# Reason for using the flag:
				# 'Do not call this method when the lock is unlocked.'
				_recvLck.release ()
                                flag = False
			return None
		_packetSize, = struct.unpack('!i', data)
		if peek_flag == 0 and ldtpDebug != None and ldtpDebug == '2':
			print 'Received packet size', _packetSize
		# MSG_PEEK
                # This flag causes the receive operation to return data from the beginning
		# of the receive queue without removing that data from  the  queue.
		# Thus, a subsequent receive call will return the same data.

		if peek_flag != 0:
			# MSG_PEEK
			_responsePacket = client.recv (4 + _packetSize, peek_flag)
		else:
			_responsePacket = client.recv (_packetSize, peek_flag)
		if peek_flag != 0:
			_pattern = re.compile ('\<\?xml')
			_searchObj = re.search (_pattern, _responsePacket)
			_finalPacket = _responsePacket[_searchObj.start () :]
			_responsePacket = _finalPacket
		#_recvLck.release ()
		if peek_flag == 0 and ldtpDebug != None and ldtpDebug == '2':
			print 'Received response Packet', _responsePacket
		return _responsePacket
	except struct.error, msg:
		raise LdtpExecutionError ('Invalid packet length ' + str (msg))
	except socket.timeout:
		#if ldtpDebug != None and ldtpDebug == '2':
		#	print 'Timeout'
		return ''
	except:
		raise LdtpExecutionError ('Error while receiving packet ' + str (traceback.print_exc ()))
        finally:
		if flag:
			# Reason for using the flag:
			# 'Do not call this method when the lock is unlocked.'
			_recvLck.release ()
                        flag = False

def getErrorMessage (errorCode, args):
    msg = None
    if errorCode == LdtpErrorCode.SUCCESS: 
        msg = "Successfully completed"
    elif errorCode == LdtpErrorCode.ARGUMENT_NULL:
        msg = "Argument cannot be NULL. Please check the arguments."
    elif errorCode == LdtpErrorCode.ACCEPT_FAILED:
        msg = "Error occurred while accepting request from client.  Please retry."
    elif errorCode == LdtpErrorCode.UNABLE_TO_REINIT_LDTP:
        msg = "Unable to reinitialize LDTP"
    elif errorCode == LdtpErrorCode.UNABLE_TO_ALLOCATE_MEMORY:
        msg = "Unable to allocate memory"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_APPLICATION_LIST:
        msg = "Unable to get application list"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_OBJECT_LIST:
        msg = "Unable to get object list"
    elif errorCode == LdtpErrorCode.THREAD_CREATION_FAILED:
        msg = "Error creating client thread. Please retry."
    elif errorCode == LdtpErrorCode.THREAD_DETACH_FAILED:
        msg = "Unable to detach the thread"
    elif errorCode == LdtpErrorCode.PACKET_INVALID:
        msg = "Packet received from client is not valid"
    elif errorCode == LdtpErrorCode.RECEIVE_RESPONSE:
        msg = "Error occurred while receiving response from client"
    elif errorCode == LdtpErrorCode.SENDING_RESPONSE:
        msg = "Error occurred while sending response to client"
    elif errorCode == LdtpErrorCode.PARTIAL_DATA_SENT:
        msg = "Warning!! Partial data sent"
    elif errorCode == LdtpErrorCode.INVALID_COMMAND:
        msg = "Invalid command"
    elif errorCode == LdtpErrorCode.INVALID_STATE:
        msg = "Invalid state"
    elif errorCode == LdtpErrorCode.APPMAP_NOT_INITIALIZED:
        msg = "Application map not initialized"
    elif errorCode == LdtpErrorCode.OPENING_APPMAP_FILE: # FIXME: its better we show the filename with full path
        msg = "Unable to open appmap file"
    elif errorCode == LdtpErrorCode.OPENING_LOG_FILE: # FIXME: its better we show the filename with full path
        msg = "Unable to open log file"
    elif errorCode == LdtpErrorCode.APP_NOT_RUNNING:
        msg = "Application not running"
    elif errorCode == LdtpErrorCode.UNABLE_TO_UPDATE_APPMAP:
        msg = "Unable to update appmap at runtime"
    elif errorCode == LdtpErrorCode.WIN_NAME_NOT_FOUND_IN_APPMAP:
        msg = "Unable to find window name in application map."
    elif errorCode == LdtpErrorCode.OBJ_NAME_NOT_FOUND_IN_APPMAP:
        msg = "Unable to find object name in application map"
    elif errorCode == LdtpErrorCode.WIN_NOT_OPEN:
        msg = "Window does not exist"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_CONTEXT_HANDLE:
        msg = "Unable to get context handle"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_COMPONENT_HANDLE:
        msg = "Unable to get component handle"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_PROPERTY:
        msg = "Unable to get property"
    elif errorCode == LdtpErrorCode.GET_OBJ_HANDLE_FAILED:
        msg = "Unable to get object handle"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_CELL_HANDLE_FAILED:
        msg = "Unable to get cell handle"
    elif errorCode == LdtpErrorCode.OBJ_INFO_MISMATCH:
        msg = "Object information does not match with application map entry"
    elif errorCode == LdtpErrorCode.COMMAND_NOT_IMPLEMENTED:
        msg = "Requested action on mentioned object is not implemented"
    elif errorCode == LdtpErrorCode.GETTEXTVALUE_FAILED:
        msg = "GetTextValue action on mentioned object failed"
    elif errorCode == LdtpErrorCode.CHILD_TYPE_UNIDENTELIFIED:
        msg = "Unable to identelify the child type of mentioned object"
    elif errorCode == LdtpErrorCode.SELECTITEM_FAILED:
        msg = "SelectItem action on mentioned object failed."
    elif errorCode == LdtpErrorCode.VERELIFY_ITEM_FAILED:
        msg = "Verelification of SelectItem failed on the mentioned object"
    elif errorCode == LdtpErrorCode.SELECTINDEX_FAILED:
        msg = "SelectIndex action on mentioned object failed."
    elif errorCode == LdtpErrorCode.TEXT_NOT_FOUND:
        msg = "Text not found"
    elif errorCode == LdtpErrorCode.TEXT_STATE_ENABLED:
        msg = "Text state enabled"
    elif errorCode == LdtpErrorCode.TEXT_STATE_NOT_ENABLED:
        msg = "Text state not enabled"
    elif errorCode == LdtpErrorCode.SETTEXTVALUE_FAILED:
        msg = "SetTextValue action on mentioned object failed"
    elif errorCode == LdtpErrorCode.VERELIFY_SETTEXTVALUE_FAILED:
        msg = "Verelification of SetTextValue failed on the mentioned object"
    elif errorCode == LdtpErrorCode.CLICK_FAILED:
        msg = "Click action on mentioned object failed"
    elif errorCode == LdtpErrorCode.DOUBLE_CLICK_FAILED:
        msg = "Dobule click action on mentioned object failed"
    elif errorCode == LdtpErrorCode.RIGHT_CLICK_FAILED:
        msg = "Right click action on mentioned object failed"
    elif errorCode == LdtpErrorCode.CHILD_IN_FOCUS:
        msg = "Verelification of HideList failed on the mentioned object as object's list is still in focus"
    elif errorCode == LdtpErrorCode.CHILD_NOT_FOCUSSED:
        msg = "Verelification of DropDown failed on the mentioned object as object's list is not in focus"
    elif errorCode == LdtpErrorCode.MENU_VISIBLE:
        msg = "Verelification of HideList failed on the mentioned object as object's menu is visible"
    elif errorCode == LdtpErrorCode.MENU_NOT_VISIBLE:
        msg = "Verelification of DropDown failed on the mentioned object as object's menu is not visible"
    elif errorCode == LdtpErrorCode.HIDELIST_FAILED:
        msg = "Hide-List action on the mentioned object failed"
    elif errorCode == LdtpErrorCode.SHOWLIST_FAILED:
        msg = "Show-List action on the mentioned object failed"
    elif errorCode == LdtpErrorCode.VERELIFY_SHOWLIST_FAILED:
        msg = "Verelify show list on the mentioned object failed"
    elif errorCode == LdtpErrorCode.ITEM_NOT_FOUND:
        msg = "SelectItem failed as the mentioned item was not found in the object"
    elif errorCode == LdtpErrorCode.FILECAPTURE_FAILED_OPEN_OUTPUT_FILE:
        msg = "Capture to file action failed: Cannot open output file"
    elif errorCode == LdtpErrorCode.VERELIFY_DROPDOWN_FAILED:
        msg = "Verelification of dropdown action failed."
    elif errorCode == LdtpErrorCode.CALENDAR_EVENT_INDEX_GREATER:
        msg = "Calendar event index greater than child count"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SELECT_CALENDAR_EVENT_INDEX:
        msg = "Unable to select calendar event index"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SELECT_CALENDAR_EVENT_NAME:
        msg = "Unable to select calendar event based on name"
    elif errorCode == LdtpErrorCode.NO_APPOINTMENTS_IN_CALENDAR:
        msg = "No appointments in calendar"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_VALUE:
        msg = "Unable to get value"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GRAB_FOCUS:
        msg = "Unable to grab focus"
    elif errorCode == LdtpErrorCode.OBJ_NOT_COMPONENT_TYPE:
        msg = "Object is not of type component"
    elif errorCode == LdtpErrorCode.INVALID_DATE:
        msg = "Ivalid date, can't be selected"
    elif errorCode == LdtpErrorCode.INVALID_OBJECT_STATE:
        msg = "Invalid object state"
    elif errorCode == LdtpErrorCode.CHECK_ACTION_FAILED:
        msg = "Check action failed"
    elif errorCode == LdtpErrorCode.UNCHECK_ACTION_FAILED:
        msg = "Uncheck action failed"
    elif errorCode == LdtpErrorCode.STATE_CHECKED:
        msg = "Object state is checked"
    elif errorCode == LdtpErrorCode.STATE_UNCHECKED:
        msg = "Object state is unchecked"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SELECT_LABEL:
        msg = "Unable to select label"
    elif errorCode == LdtpErrorCode.LABEL_NOT_FOUND:
        msg = "Label not found"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SELECT_LAYERED_PANE_ITEM:
        msg = "Unable to select item in layered pane"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SELECT_TEXT_ITEM:
        msg = "Unable to select text item in the list"
    elif errorCode == LdtpErrorCode.LIST_INDEX_GREATER:
        msg = "List index value is greater than available index"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_SELECTED_CHILD:
        msg = "Unable to get the selected child item from the list"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SELECT_CHILD:
        msg = "Unable to select the child item in the list"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_CHILD_MENU_ITEM:
        msg = "Unable to get the child menu item"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_MENU_HANDLE:
        msg = "Unable to get menu handle"
    elif errorCode == LdtpErrorCode.MENU_ITEM_DOES_NOT_EXIST:
        msg = "Menu item does not exist"
    elif errorCode == LdtpErrorCode.UNABLE_TO_FIND_POPUP_MENU:
        msg = "Unable to find popup menu"
    elif errorCode == LdtpErrorCode.MENU_ITEM_STATE_DISABLED:
        msg = "Menu item state disabled"
    elif errorCode == LdtpErrorCode.SELECT_MENU_ITEM_FAILED:
        msg = "Select menu item failed"
    elif errorCode == LdtpErrorCode.UNABLE_TO_LIST_MENU_ITEMS:
        msg = "Unable to list menu items"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SELECT_LIST_ITEM:
        msg = "Unable to select list item"
    elif errorCode == LdtpErrorCode.PAGE_TAB_NAME_SELECTION_FAILED:
        msg = "Page tab name selection failed"
    elif errorCode == LdtpErrorCode.PAGE_TAB_NAME_ALREADY_IN_SELECTED_STATE:
        msg = "Page tab name already in selected state"
    elif errorCode == LdtpErrorCode.PAGE_TAB_NAME_DOESNOT_EXIST:
        msg = "Page tab name does not exist"
    elif errorCode == LdtpErrorCode.PAGE_TAB_INDEX_DOESNOT_EXIST:
        msg = "Page tab index does not exist"
    elif errorCode == LdtpErrorCode.PAGE_TAB_NAME_INPUT_DOESNOT_EXIST:
        msg = "Page tab name does not exist"
    elif errorCode == LdtpErrorCode.PAGE_TAB_INDEX_INPUT_DOESNOT_EXIST:
        msg = "Page tab index does not exist"
    elif errorCode == LdtpErrorCode.NO_PANEL_EXIST:
        msg = "No panel exist"
    elif errorCode == LdtpErrorCode.PANEL_NAME_SELECTION_FAILED:
        msg = "Panel name selection failed"
    elif errorCode == LdtpErrorCode.PANEL_INDEX_SELECTION_FAILED:
        msg = "Panel index selection failed"
    elif errorCode == LdtpErrorCode.PANEL_COUNT_LESS_THAN_TOTAL_PANEL:
        msg = "Panels count less than total panel number"
    elif errorCode == LdtpErrorCode.RADIO_BUTTON_ALREADY_CHECKED:
        msg = "Radio button already checked"
    elif errorCode == LdtpErrorCode.RADIO_BUTTON_CHECKED:
        msg = "Radio button checked"
    elif errorCode == LdtpErrorCode.RADIO_BUTTON_STATE_NOT_ENABLED:
        msg = "Radio button state not enabled"
    elif errorCode == LdtpErrorCode.RADIO_BUTTON_NOT_CHECKED:
        msg = "Radio button not checked"
    elif errorCode == LdtpErrorCode.RADIO_MENU_ITEM_ALREADY_CHECKED:
        msg = "Radio menu item already checked"
    elif errorCode == LdtpErrorCode.RADIO_MENU_ITEM_CHECKED:
        msg = "Radio menu item checked"
    elif errorCode == LdtpErrorCode.RADIO_MENU_ITEM_NOT_CHECKED:
        msg = "Radio menu item not checked"
    elif errorCode == LdtpErrorCode.NOT_VERTICAL_SCROLL_BAR:
        msg = "Object not a vertical scrollbar"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SCROLL_WITH_GIVEN_VALUE:
        msg = "Unable to scroll with the given value"
    elif errorCode == LdtpErrorCode.NOT_HORIZONTAL_SCROLL_BAR:
        msg = "Object not a horizontal scrollbar"
    elif errorCode == LdtpErrorCode.SCROLL_BAR_MAX_REACHED:
        msg = "Scrollbar trying to access more than maximum limit"
    elif errorCode == LdtpErrorCode.SCROLL_BAR_MIN_REACHED:
        msg = "Scrollbar trying to access less than minimum limit"
    elif errorCode == LdtpErrorCode.NOT_VERTICAL_SLIDER:
        msg = "Object not a vertical slider"
    elif errorCode == LdtpErrorCode.NOT_HORIZONTAL_SLIDER:
        msg = "Object not a horizontal slider"
    elif errorCode == LdtpErrorCode.SLIDER_SET_MAX_FAILED:
        msg = "Slider set maximum value failed"
    elif errorCode == LdtpErrorCode.SLIDER_SET_MIN_FAILED:
        msg = "Slider set minimum value failed"
    elif errorCode == LdtpErrorCode.UNABLE_TO_INCREASE_SLIDER_VALUE:
        msg = "Unable to increase slider value"
    elif errorCode == LdtpErrorCode.UNABLE_TO_DECREASE_SLIDER_VALUE:
        msg = "Unable to decrease slider value"
    elif errorCode == LdtpErrorCode.SLIDER_MAX_REACHED:
        msg = "Slider trying to access more than maximum limit"
    elif errorCode == LdtpErrorCode.SLIDER_MIN_REACHED:
        msg = "Slider trying to access less than minimum limit"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_SLIDER_VALUE:
        msg = "Unable to get slider value"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SET_SPIN_BUTTON_VALUE:
        msg = "Unable to set spin button value"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SPIN_BUTTON_VALUES_NOT_SAME:
        msg = "Spin button values are not same"
    elif errorCode == LdtpErrorCode.STATUSBAR_GETTEXT_FAILED:
        msg = "Unable to get text from status bar"
    elif errorCode == LdtpErrorCode.STATUSBAR_NOT_VISIBLE:
        msg = "Status bar not visible"
    elif errorCode == LdtpErrorCode.TOGGLE_ACTION_FAILED:
        msg = "Toggle action failed"
    elif errorCode == LdtpErrorCode.TOGGLE_CHECKED:
        msg = "Toggle button checked"
    elif errorCode == LdtpErrorCode.TOGGLE_NOT_CHECKED:
        msg = "Toggle button not checked"
    elif errorCode == LdtpErrorCode.TOOLBAR_VISIBLE_BUTTON_COUNT_FAILED:
        msg = "Toolbar visible button count failed"
    elif errorCode == LdtpErrorCode.TOOLBAR_BUTTON_COUNT_FAILED:
        msg = "Toolbar button count failed"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SET_TEXT:
        msg = "Unable to set text"
    elif errorCode == LdtpErrorCode.VERELIFY_SET_TEXT_FAILED:
        msg = "Verelify set text value failed"
    elif errorCode == LdtpErrorCode.VERELIFY_PARTIAL_MATCH_FAILED:
        msg = "Verelify partial match failed"
    elif errorCode == LdtpErrorCode.UNABLE_TO_CUT_TEXT:
        msg = "Unable to cut text"
    elif errorCode == LdtpErrorCode.UNABLE_TO_COPY_TEXT:
        msg = "Unable to copy text"
    elif errorCode == LdtpErrorCode.UNABLE_TO_INSERT_TEXT:
        msg = "Unable to insert text"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_TEXT_PROPERTY:
        msg = "Unable to get text property"
    elif errorCode == LdtpErrorCode.TEXT_OBJECT_VALUE_CONTAINS_DELIFF_PROEPRTY:
        msg = "Text object value contains delifferent property"
    elif errorCode == LdtpErrorCode.TEXT_OBJECT_DOES_NOT_CONTAIN_PROEPRTY:
        msg = "Text object does not contain property"
    elif errorCode == LdtpErrorCode.TEXT_PROEPRTY_VALUE_PAIR_IS_INVALID:
        msg = "Given text property value pair is invalid"
    elif errorCode == LdtpErrorCode.ONE_OR_MORE_PROPERTIES_DOES_NOT_MATCH:
        msg = "One or more properties does not match"
    elif errorCode == LdtpErrorCode.TEXT_TO_INSERT_IS_EMPTY:
        msg = "Text to insert is empty"
    elif errorCode == LdtpErrorCode.UNABLE_TO_ACTIVATE_TEXT:
        msg = "Unable to activate text"
    elif errorCode == LdtpErrorCode.UNABLE_TO_PASTE_TEXT:
        msg = "Unable to paste text"
    elif errorCode == LdtpErrorCode.UNABLE_TO_DELETE_TEXT:
        msg = "Unable to delete text"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SELECT_TEXT:
        msg = "Unable to select text"
    elif errorCode == LdtpErrorCode.UNABLE_TO_APPEND_TEXT:
        msg = "Unable to append text"
    elif errorCode == LdtpErrorCode.INVALID_COLUMN_INDEX_TO_SORT:
        msg = "Invalid column index given for sorting"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SORT:
        msg = "Unable to sort"
    elif errorCode == LdtpErrorCode.ROW_DOES_NOT_EXIST:
        msg = "Row does not exist"
    elif errorCode == LdtpErrorCode.COLUMN_DOES_NOT_EXIST:
        msg = "Column does not exist"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SELECT_ROW:
        msg = "Unable to select row"
    elif errorCode == LdtpErrorCode.VERELIFY_TABLE_CELL_FAILED:
        msg = "Verelify table cell failed"
    elif errorCode == LdtpErrorCode.VERELIFY_TABLE_CELL_PARTIAL_MATCH_FAILED:
        msg = "Verelify table cell partial match failed"
    elif errorCode == LdtpErrorCode.SET_TABLE_CELL_FAILED:
        msg = "Set table cell failed"
    elif errorCode == LdtpErrorCode.GET_TABLE_CELL_FAILED:
        msg = "Get table cell failed"
    elif errorCode == LdtpErrorCode.GET_TREE_TABLE_CELL_FAILED:
        msg = "Get table cell failed"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_ROW_INDEX:
        msg = "Unable to find row index"
    elif errorCode == LdtpErrorCode.NO_CHILD_TEXT_TYPE_UNDER_TABLE:
        msg = "Table cell has no child of type text"
    elif errorCode == LdtpErrorCode.ACTUAL_ROW_COUNT_LESS_THAN_GIVEN_ROW_COUNT:
        msg = "Actual row count less than given row count"
    elif errorCode == LdtpErrorCode.ACTUAL_COLUMN_COUNT_LESS_THAN_GIVEN_COLUMN_COUNT:
        msg = "Actual column count less than given column count"
    elif errorCode == LdtpErrorCode.UNABLE_TO_PERFORM_ACTION:
        msg = "Unable to perform action"
    elif errorCode == LdtpErrorCode.GUI_EXIST:
        msg = "GUI exist"
    elif errorCode == LdtpErrorCode.GUI_NOT_EXIST:
        msg = "GUI does not exist"
    elif errorCode == LdtpErrorCode.CALLBACK:
        msg = "callback"
    elif errorCode == LdtpErrorCode.UNABLE_TO_CREATE_PO:
        msg = "Unable to create po"
    elif errorCode == LdtpErrorCode.UNABLE_TO_DELETE_PO:
        msg = "Unable to delete po"
    elif errorCode == LdtpErrorCode.ONLY_MO_MODE_SUPPORTED:
        msg = "Only MO mode supported"
    elif errorCode == LdtpErrorCode.UTF8_ENGLISH_LANG:
        msg = "UTF8 default English language"
    elif errorCode == LdtpErrorCode.UNABLE_TO_STAT_DIR:
        msg = "Unable to stat directory"
    elif errorCode == LdtpErrorCode.ROLE_NOT_IMPLEMENTED:
        msg = "Mentioned role not implemented."
    elif errorCode == LdtpErrorCode.UNABLE_TO_MOVE_MOUSE:
        msg = "Mouse Cursor move failed"
    elif errorCode == LdtpErrorCode.INVALID_FORMAT:
        msg = "Invalid Format"
    elif errorCode == LdtpErrorCode.TOKEN_NOT_FOUND:
        msg = "Invalid Key"
    elif errorCode == LdtpErrorCode.UNABLE_TO_ENTER_KEY:
        msg = "Error while entering key"
    elif errorCode == LdtpErrorCode.OFFSET_OUT_OF_BOUND:
        msg = "Offset value greater than number of characters"
    elif errorCode == LdtpErrorCode.UNABLE_TO_SET_CARET:
        msg = "Unable to set the cursor position"
    elif errorCode == LdtpErrorCode.TEXT_NOT_ACCESSIBLE:
        msg = "TextBox not Accessible"
    elif errorCode == LdtpErrorCode.STOP_SCRIPT_ENGINE:
        msg = "Stop LDTP script engine"
    elif errorCode == LdtpErrorCode.WRONG_COMMAND_SEQUENCE:
        msg = "Wrong command sequence, stop called before start"
    elif errorCode == LdtpErrorCode.UNABLE_TO_LAUNCH_APP:
        msg = "Unable to launch application"
    elif errorCode == LdtpErrorCode.CLIENT_DISCONNECTED:
        msg = "Client disconnected"
    elif errorCode == LdtpErrorCode.EVENT_NOTELIFIER_NOT_ENABLED:
        msg = "Event notelifier not registered"
    elif errorCode == LdtpErrorCode.SET_GUI_TIMEOUT_FAILED:
        msg = "Unable to set gui timeout period"
    elif errorCode == LdtpErrorCode.SET_OBJ_TIMEOUT_FAILED:
        msg = "Unable to set obj timeout period"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_DEVICE:
        msg = "Unable to get device control"
    elif errorCode == LdtpErrorCode.UNABLE_TO_GET_CHILD_WITH_PROVIDED_ROLE:
        msg = "Unable to get child with provided role";
    else:
        msg = "Error code not found";
    return msg;

LDTP_LOG_TESTSTART = 61
LDTP_LOG_TESTEND   = 62
LDTP_LOG_BEGIN     = 63
LDTP_LOG_END       = 64
LDTP_LOG_FAIL      = 65
LDTP_LOG_PASS      = 66
LDTP_LOG_CAUSE     = 67
LDTP_LOG_COMMENT   = 68
LDTP_LOG_GROUPSTART  = 69
LDTP_LOG_GROUPEND    = 70
LDTP_LOG_SCRIPTSTART = 71
LDTP_LOG_SCRIPTEND   = 72
LDTP_LOG_MEMINFO     = 73
LDTP_LOG_CPUINFO     = 74
LDTP_LOG_CATEGORYSTART  = 75
LDTP_LOG_CATEGORYEND    = 76
LDTP_LOG_CATEGORYSTATUS = 77
LDTP_LOG_LOGSTARTTAG    = 78
LDTP_LOG_LOGSTOPTAG     = 79
LDTP_LOG_GROUPSSTATUS   = 80
LDTP_LOG_TIMEINFO       = 81
LDTP_LOG_TOTALTIMEINFO  = 82

logging.addLevelName (LDTP_LOG_TESTSTART, 'TESTSTART')
logging.addLevelName (LDTP_LOG_TESTEND, 'TESTEND')
logging.addLevelName (LDTP_LOG_BEGIN, 'BEGIN')
logging.addLevelName (LDTP_LOG_END, 'END')
logging.addLevelName (LDTP_LOG_FAIL, 'FAIL')
logging.addLevelName (LDTP_LOG_PASS, 'PASS')
logging.addLevelName (LDTP_LOG_CAUSE, 'CAUSE')
logging.addLevelName (LDTP_LOG_COMMENT, 'COMMENT')
logging.addLevelName (LDTP_LOG_GROUPSTART, 'GROUPSTART')
logging.addLevelName (LDTP_LOG_GROUPSSTATUS, 'GROUPSSTATUS')
logging.addLevelName (LDTP_LOG_GROUPEND, 'GROUPEND')
logging.addLevelName (LDTP_LOG_SCRIPTSTART, 'SCRIPTSTART')
logging.addLevelName (LDTP_LOG_SCRIPTEND, 'SCRIPTEND')
logging.addLevelName (LDTP_LOG_MEMINFO, 'MEMINFO')
logging.addLevelName (LDTP_LOG_CPUINFO, 'CPUINFO')
logging.addLevelName (LDTP_LOG_LOGSTARTTAG, 'LOGSTARTTAG')
logging.addLevelName (LDTP_LOG_LOGSTOPTAG, 'LOGSTOPTAG')
logging.addLevelName (LDTP_LOG_TIMEINFO, 'TIMEINFO')
logging.addLevelName (LDTP_LOG_TOTALTIMEINFO, 'TOTALTIMEINFO')
logging.addLevelName (LDTP_LOG_CATEGORYSTART, 'CATEGORYSTART')
logging.addLevelName (LDTP_LOG_CATEGORYEND, 'CATEGORYEND')
logging.addLevelName (LDTP_LOG_CATEGORYSTATUS, 'CATEGORYSTATUS')

def setInternalLogLevel (level, logger):
    if logger != None:
        if type (level) == unicode or type (level) == str:
            regexp = re.compile ('\A' + level, re.IGNORECASE)
            logLevel = None
            if regexp.search ('CRITICAL') != None:
                logLevel = logging.CRITICAL
            elif regexp.search ('ERROR') != None:
                logLevel = logging.ERROR
            elif regexp.search ('WARNING') != None:
                logLevel = logging.WARNING
            elif regexp.search ('INFO') != None:
                logLevel = logging.INFO
            elif regexp.search ('DEBUG') != None:
                logLevel = logging.DEBUG
                if logLevel != None:
                    logger.setLevel (logLevel)
                    return 1
                else:
                    return 0
            logger.setLevel (level)
            return 1
    return 0

class LdtpLogRecord (logging.LogRecord):
    """
    LogRecord subclass that stores a unique -- transaction -- time
    as an additional attribute
    """
    def __init__ (self, name, level, pathname, lineno, msg, args, exc_info):
	    if level == LDTP_LOG_LOGSTARTTAG:
		    msg = '<' + saxutils.escape (msg) + '>'
	    elif level == LDTP_LOG_LOGSTOPTAG:
		    msg = '</' + saxutils.escape (msg) + '>'
	    elif level == LDTP_LOG_GROUPSTART:
		    msg = '<group name=\"' + saxutils.escape (msg) + '\">'
	    elif level == LDTP_LOG_GROUPEND:
		    msg = '</group>'
	    elif level == LDTP_LOG_CATEGORYSTART:
		    msg = '<category name=\"' + saxutils.escape (msg) + '\">'
	    elif level == LDTP_LOG_CATEGORYEND:
		    msg = '</category>'
	    elif level == LDTP_LOG_SCRIPTSTART:
		    msg = '<script name=\"' + saxutils.escape (msg) + '\">'
	    elif level == LDTP_LOG_SCRIPTEND:
		    msg = '</script>'
	    elif level == LDTP_LOG_TESTSTART:
		    msg = '<test name=\"' + saxutils.escape (msg) + '\">'
	    elif level == LDTP_LOG_TESTEND:
		    msg = '</test>'
	    elif level == LDTP_LOG_BEGIN:
		    msg = '<testsuite name=\"' + saxutils.escape (msg) + '\">'
	    elif level == LDTP_LOG_END:
		    msg = '</testsuite>'
	    elif level == LDTP_LOG_PASS:
		    msg = '<pass>1</pass>'
	    elif level == LDTP_LOG_FAIL:
		    msg = '<pass>0</pass>'
	    elif level == LDTP_LOG_GROUPSSTATUS:
		    msg = '<groupsstatus ' + saxutils.escape (msg) + '></groupsstatus>'
	    elif level == LDTP_LOG_CATEGORYSTATUS:
		    msg = '<categorystatus ' + saxutils.escape (msg) + '></categorystatus>'
	    elif level == LDTP_LOG_TIMEINFO:
		    msg = '<timeinfo ' + saxutils.escape (msg) + '></timeinfo>'
	    elif level == LDTP_LOG_TOTALTIMEINFO:
		    msg = '<totaltimeinfo ' + saxutils.escape (msg) + '></totaltimeinfo>'
	    else:
		    msg = '<' + logging.getLevelName (level) +'>' + saxutils.escape (msg) + '</' + logging.getLevelName (level) + '>'
	    if sys.version_info [0] >= 3 or (sys.version_info [0] >= 2 and sys.version_info [1] >= 5):
		    logging.LogRecord.__init__ (self, name, level, pathname, lineno, msg, args, exc_info, None)
	    else:
		    logging.LogRecord.__init__ (self, name, level, pathname, lineno, msg, args, exc_info)

if sys.version_info [0] >= 3 or (sys.version_info [0] >= 2 and sys.version_info [1] >= 5):
	def makeRecord (self, name, level, fn, lno, msg, args, exc_info, func = None, extra = None):
		if type (level) != int and len (msg) == 0:
			exc_info = args
			args = msg
			msg = lno
			lno = fn
			fn = level
			level = name
			name = logging.getLogger ('XML').name
		return LdtpLogRecord (name, level, fn, lno, msg, args, exc_info)
else:
	def makeRecord (name, level, fn, lno, msg, args, exc_info, func = None, extra = None):
		if type (level) != int and len (msg) == 0:
			exc_info = args
			args = msg
			msg = lno
			lno = fn
			fn = level
			level = name
			name = logging.getLogger ('XML').name
		return LdtpLogRecord (name, level, fn, lno, msg, args, exc_info)

class LdtpLogger (logging.Logger):
    """
    Logger subclass that uses CustomLogRecord as its LogRecord class
    """
    def __init__ (self, name, level = logging.NOTSET):
        logging.Logger.__init__ (self, name, level)

def startInternalLog (logFileName, fileOverWrite, loggerCode):
	try:
		logging.setLoggerClass (LdtpLogger)
		logger = logging.getLogger (loggerCode)
                xmlhdlr = None
		xmlLogMode = 'w'
		if fileOverWrite == 0:
			xmlLogMode = 'a'
		try:
			if logFileName [0] == "~":
				logFileName = os.path.expanduser (logFileName)
			elif logFileName [0] == ".":
				logFileName = os.path.abspath (logFileName)
			xmlhdlr = logging.FileHandler (logFileName, xmlLogMode)
			logger.addHandler (xmlhdlr)
			logger.setLevel (logging.WARNING)
			logger.makeRecord = makeRecord
			if fileOverWrite == 1:
				logger.log (LDTP_LOG_LOGSTARTTAG, 'ldtp')
		except IOError:
                    if ldtpDebug is not None:
                        print traceback.print_exc ()
                    return None, None
		if xmlhdlr == None:
                    # If xmlhdlr handler is not created, then let us enable this
                    logger.manager.emittedNoHandlerWarning = 1
		return logger, xmlhdlr
	except:
            if ldtpDebug is not None:
                print traceback.print_exc ()
            return None, None

def isPriority (priority, givenPriority):
	regexp = re.compile ('\A' + priority, re.IGNORECASE)
	if regexp.search (givenPriority) == None:
		return False
	else:
		return True

def internalLog (message, priority, logger):
    if logger == None:
        # Let us not process anything
        return 1

    if message is None:
        # Let us not process anything
        return 1
    if message.__class__ == LdtpExecutionError:
        message = message.value

    if priority == None or priority == '' or type (priority) != str or isPriority ('DEBUG', priority):
        logger.debug (message)
    elif isPriority ('INFO', priority):
        logger.info (message)
    elif isPriority ('PASS', priority):
        logger.log (LDTP_LOG_PASS, message)
    elif isPriority ('FAIL', priority):
        logger.log (LDTP_LOG_FAIL, message)
    elif isPriority ('ERROR', priority):
        logger.error (message)
    elif isPriority ('CRITICAL', priority):
        logger.critical (message)
    elif isPriority ('WARN', priority):
        logger.warning (message)
    elif isPriority ('CAUSE', priority):
        logger.log (LDTP_LOG_CAUSE, message)
    elif isPriority ('COMMENT', priority):
        logger.log (LDTP_LOG_COMMENT, message)
    elif isPriority ('MEMINFO', priority):
        logger.log (LDTP_LOG_MEMINFO, message)
    elif isPriority ('CPUINFO', priority):
        logger.log (LDTP_LOG_CPUINFO, message)
    elif isPriority ('GROUPSTART', priority):
        logger.log (LDTP_LOG_GROUPSTART, message)
    elif isPriority ('CATEGORYSTART', priority):
        logger.log (LDTP_LOG_CATEGORYSTART, message)
    elif isPriority ('GROUPSSTATUS', priority):
        logger.log (LDTP_LOG_GROUPSSTATUS, message)
    elif isPriority ('GROUPEND', priority):
        logger.log (LDTP_LOG_GROUPEND, message)
    elif isPriority ('CATEGORYEND', priority):
        logger.log (LDTP_LOG_CATEGORYEND, message)
    elif isPriority ('CATEGORYSTATUS', priority):
        logger.log (LDTP_LOG_CATEGORYSTATUS, message)
    elif isPriority ('SCRIPTSTART', priority):
        logger.log (LDTP_LOG_SCRIPTSTART, message)
    elif isPriority ('SCRIPTEND', priority):
        logger.log (LDTP_LOG_SCRIPTEND, message)
    elif isPriority ('TESTSTART', priority):
        logger.log (LDTP_LOG_TESTSTART, message)
    elif isPriority ('TESTEND', priority):
        logger.log (LDTP_LOG_TESTEND, message)
    elif isPriority ('BEGIN', priority):
        logger.log (LDTP_LOG_BEGIN, message)
    elif isPriority ('END', priority):
        logger.log (LDTP_LOG_END, message)
    elif isPriority ('TIMEINFO', priority):
        logger.log (LDTP_LOG_TIMEINFO, message)
    elif isPriority ('TOTALTIMEINFO', priority):
        logger.log (LDTP_LOG_TOTALTIMEINFO, message)
    else:
        logger.debug (message)
    return 1

def internalStopLog (handler, xmlhdlr, logger):
    if handler != None:
        logger.removeHandler (handler)
    elif xmlhdlr != None:
        logger.log (LDTP_LOG_LOGSTOPTAG, 'ldtp')
        logger.removeHandler (xmlhdlr)
    return 1

def addInternalLogger (confFileName):
	logging.config.fileConfig (confFileName)

def escapeChars (str2escape, escapeDot = True):
    str2escape = re.sub ("(?i) +", "", str2escape)
    str2escape = re.sub ("(?i)\n+", "", str2escape)
    if escapeDot:
        str2escape = re.sub ("(?i)\.+", "", str2escape)
        str2escape = re.sub ("(?i)_+", "", str2escape)
        str2escape = re.sub ("(?i):+", "", str2escape)
    # Dialog Save As... (Gedit Save As dialog box ends with 3 dots)
    # with at-spi call, we get them as single unicode char
    str2escape = re.sub (u"(?i)\u2026+", "...", str2escape.decode ('utf-8'))
    return str2escape

def escapeChar (str2escape, char):
    if char == '*':
        char = ".*"
    str2escape = re.sub ("(?i)" + char + "+", "", str2escape)
    return str2escape

# Send lock
_sendLck = threading.Lock ()
# Recieve lock
_recvLck = threading.Lock ()

# Socket fd pool
sockFdPool = {}
