#!/usr/bin/env python
#############################################################################
#
#  Linux Desktop Testing Project http://ldtp.freedesktop.org
# 
#  Author:
#     A. Nagappan <nagappan@gmail.com>
# 
#  Copyright 2004 - 2007 Novell, Inc.
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

import re
import os
import sys
import time

try:
    import pyatspi as atspi, Accessibility
except ImportError:
    import atspi
    import Accessibility

from ldtplib.ldtplibutils import *

ldtpDebug = os.getenv ('LDTP_DEBUG') # Enable debugging

class objInst:
    table = 0
    canvas = 0
    columnHeader = 0
    comboBox = 0
    pageTabList = 0
    pageTab = 0
    spinButton = 0
    button = 0
    tbutton = 0
    radioButton = 0
    checkBox = 0
    tree = 0
    treeTable = 0
    layeredPane = 0
    text = 0
    calView = 0
    panel = 0
    filler = 0
    menuBar = 0
    menu = 0
    separator = 0
    scrollBar = 0
    scrollPane = 0
    splitPane = 0
    slider = 0
    htmlContainer = 0
    progressBar = 0
    statusBar = 0
    toolBar = 0
    lst = 0
    label = 0
    icon = 0
    alert = 0
    dialog = 0
    unknown = 0
    embeddedComponent = 0

    def reset (self):
        self.table = 0
        self.canvas = 0
        self.columnHeader = 0
        self.comboBox = 0
        self.pageTabList = 0
        self.pageTab = 0
        self.spinButton = 0
        self.button = 0
        self.tbutton = 0
        self.radioButton = 0
        self.checkBox = 0
        self.tree = 0
        self.treeTable = 0
        self.layered_pane = 0
        self.text = 0
        self.calView = 0
        self.panel = 0
        self.filler = 0
        self.menuBar = 0
        self.menu = 0
        self.separator = 0
        self.scrollBar = 0
        self.scrollPane = 0
        self.splitPane = 0
        self.slider = 0
        self.htmlContainer = 0
        self.progressBar = 0
        self.statusBar = 0
        self.toolBar = 0
        self.label = 0
        self.lst = 0
        self.icon = 0
        self.alert = 0
        self.dialog = 0
        self.unknown = 0
        self.embeddedComponent = 0

class LdtpClientContext:
    def __init__ (self, localeLang, windowName, appHandleaccessible, appmap, request, response, guiHandle):
        self.localeLang = localeLang
        self.windowName = windowName
        self.appHandle  = appHandleaccessible
        self.appmap     = appmap
        self.request    = request
        self.response   = response
        self.guiHandle  = guiHandle

class LdtpGuiHandle:
    def __init__ (self, handle, classId):
        self.handle  = handle
        self.classId = classId

class Packet:
    def __init__ (self, packet, length):
        self.packet = packet
        self.length = length

class ParentPathInfo:
    def __init__ (self, childIndex, count):
        self.childIndex = childIndex
        self.count      = count

class Node:
    def __init__ (self, childIndex, node):
        self.childIndex = childIndex
        self.node = node

class LdtpRequest:
    def __init__ (self, requestType, command, application, requestId, context, component, actionName, argsList):
        self.requestType = requestType
        self.command     = command
        self.application = application
        self.requestId   = requestId
        self.context     = context
        self.component   = component
        self.actionName  = actionName
        self.argsList    = argsList

class LdtpResponse:
    def __init__ (self, status, data, length):
        self.status = status
        self.data   = data
        self.length = length

class SearchObjInfo:
    def __init__ (self, key, objIsWindow = False, pattern = None):
        self.key = key
        self.objIsWindow = objIsWindow
        self.pattern = pattern

class objInfo:
    def __init__ (self, prefix, objectType, instanceIndex, parentName):
        self.prefix     = prefix
        self.objType    = objectType
        self.instIndex  = instanceIndex
        self.parentName = parentName
        self.objectInst = objInst ()

class widget:
    def __init__ (self, widgetType, *args):
        self.widgetType = widgetType
        if len (args) == 3:
            self.label = args [0]
            self.parent = args [1]
            self.index = args [2]
        else:
            self.label = ''
            self.parent = args [0]
            self.index = args [1]

class window (widget):
    def __init__ (self, *args):
        self.children = {}
        widget.__init__ (self, *args)

class keyboard:
    def __init__ (self):
        pass
    charKeySynthVals = {38 : 'a', 56 : 'b', 54 : 'c', 40 : 'd', 26 : 'e', 41 : 'f', 42 : 'g', \
                        43 : 'h', 31 : 'i', 44 : 'j', 45 : 'k', 46 : 'l', 58 : 'm', 57 : 'n', \
                        32 : 'o', 33 : 'p', 24 : 'q', 27 : 'r', 39 : 's', 28 : 't', 30 : 'u', \
                        55 : 'v', 25 : 'w', 53 : 'x', 29 : 'y', 52 : 'z'} #A - Z
    digitKeySynthVals = {19 : '0', 10 : '1', 11 : '2', 12 : '3', 13 : '4', 14 : '5', 15 : '6', \
                         16 : '7', 17 : '8', 18 : '9'} #0 - 9
    symbolKeySynth = {20 : '-', 21 : '=', 34 : '[', 35 : ']', 47 : ';', 48 : '\'', 49 : '`', \
                      51 : '\\', 59 : ',', 60 : '.', 61 : '/', 10 : '!', 11 : '@', \
                      12 : '#', 13 : '$', 14 : '%', 15 : '^', 16 : '&', 17 : '*', 18 : '(', \
                      19 : ')', 20 : '_', 21 : '+', 34 : '{', 35 : '}', 47 : ':', 48 : '\"', \
                      49 : '~', 51 : '|', 59 : '<', 60 : '>', 61 : '?'}
    nonPrintKeySynth = {9 : '<escape>', 22 : '<backspace>',
                        37 : '<ctrl>', 115 : '<windowskey>',
                        23 : '<tab>', 36 : '<return>',
                        50 : '<shift>', 62 : '<shiftr>',
                        97 : '<home>', 103 : '<end>', 115 : '<window>',
                        64 : '<alt>', 113 : '<altr>',
                        98 : '<up>', 104 : '<down>', 102 : '<right>',
                        100 : '<left>', 65 : '<space>',
                        66 : '<caps>', 117 : '<menu>',
                        106 : '<insert>', 107 : '<delete>',
                        99 : '<pageup>', 105 : '<pagedown>',
                        77 : '<numlock>', 78 : '<scrolllock>',
                        67 : '<F1>', 68 : '<F2>', 69 : '<F3>', 70 : '<F4>',
                        71 : '<F5>', 72 : '<F6>', 73 : '<F7>', 74 : '<F8>',
                        75 : '<F9>', 76 : '<F10>', 95 : '<F11>', 96 : '<F12>'}

class appmap:
    def __init__ (self, objectInst,  registry):
        self.hashmap = None
        self.hierarchy = ''
        self.registry    = registry
        self.objectInst = objectInst
        self.applicationmap = window ('list_of_windows', None, None).children

    def getObjectInfo (self, accessible, parentName):
        role = accessible.getRole ()
        objectInfo = None
        if role == Accessibility.ROLE_PAGE_TAB:
            objectInfo = objInfo ('ptab', 'page_tab', self.objectInst.pageTab, parentName)
            self.objectInst.pageTab += 1
        elif role == Accessibility.ROLE_PAGE_TAB_LIST:
            objectInfo = objInfo ('ptl', 'page_tab_list', self.objectInst.pageTabList, parentName)
            self.objectInst.pageTabList += 1
        elif role == Accessibility.ROLE_MENU:
            objectInfo = objInfo ('mnu', 'menu', self.objectInst.menu, parentName)
            self.objectInst.menu += 1
        elif role == Accessibility.ROLE_MENU_ITEM:
            objectInfo = objInfo ('mnu', 'menu_item', self.objectInst.menu, parentName)
            self.objectInst.menu += 1
        elif role == Accessibility.ROLE_CHECK_MENU_ITEM:
            objectInfo = objInfo ('mnu', 'check_menu_item', self.objectInst.menu, parentName)
            self.objectInst.menu += 1
        elif role == Accessibility.ROLE_RADIO_MENU_ITEM:
            objectInfo = objInfo ('mnu', 'radio_menu_item', self.objectInst.menu, parentName)
            self.objectInst.menu += 1
        elif role == Accessibility.ROLE_CHECK_BOX:
            objectInfo = objInfo ('chk', 'check_box', self.objectInst.checkBox, parentName)
            self.objectInst.checkBox += 1
        elif role == Accessibility.ROLE_RADIO_BUTTON:
            objectInfo = objInfo ('rbtn', 'radio_button', self.objectInst.radioButton, parentName)
            self.objectInst.radioButton += 1
        elif role == Accessibility.ROLE_SPIN_BUTTON:
            objectInfo = objInfo ('sbtn', 'spin_button', self.objectInst.spinButton, parentName)
            self.objectInst.spinButton += 1
        elif role == Accessibility.ROLE_PUSH_BUTTON:
            objectInfo = objInfo ('btn', 'push_button', self.objectInst.button, parentName)
            self.objectInst.button += 1
        elif role == Accessibility.ROLE_TOGGLE_BUTTON:
            objectInfo = objInfo ('tbtn', 'toggle_button', self.objectInst.tbutton, parentName)
            self.objectInst.tbutton += 1
        elif role == Accessibility.ROLE_TEXT:
            objectInfo = objInfo ('txt', 'text', self.objectInst.text, parentName)
            self.objectInst.text += 1
        elif role == Accessibility.ROLE_PASSWORD_TEXT:
            objectInfo = objInfo ('txt', 'password_text', self.objectInst.text, parentName)
            self.objectInst.text += 1
        elif role == Accessibility.ROLE_EDITBAR:
            objectInfo = objInfo ('txt', 'edit_bar', self.objectInst.text, parentName)
            self.objectInst.text += 1
        elif role == Accessibility.ROLE_ENTRY:
            objectInfo = objInfo ('txt', 'entry', self.objectInst.text, parentName)
            self.objectInst.text += 1
        elif role == Accessibility.ROLE_LIST:
            objectInfo = objInfo ('lst', 'list', self.objectInst.lst, parentName)
            self.objectInst.lst += 1
        elif role == Accessibility.ROLE_TABLE:
            objectInfo = objInfo ('tbl', 'table', self.objectInst.table, parentName)
            self.objectInst.table += 1
        elif role == Accessibility.ROLE_TABLE_COLUMN_HEADER:
            objectInfo = objInfo ('tbl', 'table_column_header', self.objectInst.columnHeader, parentName)
            self.objectInst.columnHeader += 1
        elif role == Accessibility.ROLE_TREE:
            objectInfo = objInfo ('tree', 'tree', self.objectInst.tree, parentName)
            self.objectInst.tree += 1
        elif role == Accessibility.ROLE_TREE_TABLE:
            objectInfo = objInfo ('ttbl', 'tree_table', self.objectInst.treeTable, parentName)
            self.objectInst.treeTable += 1
        elif role == Accessibility.ROLE_TABLE_CELL:
            objectInfo = objInfo ('tblc', 'table_cell', -1, parentName)
        elif role == Accessibility.ROLE_FRAME:
            objectInfo = objInfo ('frm', 'frame', -1, parentName)
        elif role == Accessibility.ROLE_DIALOG:
            objectInfo = objInfo ('dlg', 'dialog', self.objectInst.dialog, parentName)
            self.objectInst.dialog += 1
        elif role == Accessibility.ROLE_WINDOW:
            objectInfo = objInfo ('dlg', 'dialog', self.objectInst.dialog, parentName)
            self.objectInst.dialog += 1
        elif role == Accessibility.ROLE_FONT_CHOOSER:
            objectInfo = objInfo ('dlg', 'font_chooser', -1, parentName)
        elif role == Accessibility.ROLE_FILE_CHOOSER:
            objectInfo = objInfo ('dlg', 'file_chooser', -1, parentName)
        elif role == Accessibility.ROLE_ALERT:
            objectInfo = objInfo ('dlg', 'alert', self.objectInst.alert, parentName)
            self.objectInst.alert += 1
        elif role == Accessibility.ROLE_COMBO_BOX:
            objectInfo = objInfo ('cbo', 'combo_box', self.objectInst.comboBox, parentName)
            self.objectInst.comboBox += 1
        elif role == Accessibility.ROLE_LAYERED_PANE:
            objectInfo = objInfo ('pane', 'layered_pane', self.objectInst.layeredPane, parentName)
            self.objectInst.layeredPane += 1
        elif role == Accessibility.ROLE_CALENDAR:
            objectInfo = objInfo ('calview', 'calendar_view', self.objectInst.calView, parentName)
            self.objectInst.calView += 1
        elif role == Accessibility.ROLE_PANEL:
            objectInfo = objInfo ('pnl', 'panel', self.objectInst.panel, parentName)
            self.objectInst.panel += 1
        elif role == Accessibility.ROLE_LABEL:
            objectInfo = objInfo ('lbl', 'label', self.objectInst.label, parentName)
            self.objectInst.label += 1
        elif role == Accessibility.ROLE_ICON:
            objectInfo = objInfo ('ico', 'icon', self.objectInst.icon, parentName)
            self.objectInst.icon += 1
        elif role == Accessibility.ROLE_MENU_BAR:
            objectInfo = objInfo ('mbr', 'menu_bar', self.objectInst.menuBar, parentName)
            self.objectInst.menuBar += 1
        elif role == Accessibility.ROLE_SCROLL_BAR:
            objectInfo = objInfo ('scbr', 'scroll_bar', self.objectInst.scrollBar, parentName)
            self.objectInst.scrollBar += 1
        elif role == Accessibility.ROLE_SCROLL_PANE:
            objectInfo = objInfo ('scpn', 'scroll_pane', self.objectInst.scrollPane, parentName)
            self.objectInst.scrollPane += 1
        elif role == Accessibility.ROLE_STATUS_BAR:
            objectInfo = objInfo ('stat', 'status_bar', self.objectInst.statusBar, parentName)
            self.objectInst.statusBar += 1
        elif role == Accessibility.ROLE_SEPARATOR:
            objectInfo = objInfo ('spr', 'separator', self.objectInst.separator, parentName)
            self.objectInst.separator += 1
        elif role == Accessibility.ROLE_FILLER:
            objectInfo = objInfo ('flr', 'filler', self.objectInst.filler, parentName)
            self.objectInst.filler += 1
        elif role == Accessibility.ROLE_CANVAS:
            objectInfo = objInfo ('cnvs', 'canvas', self.objectInst.canvas, parentName)
            self.objectInst.canvas += 1
        elif role == Accessibility.ROLE_SLIDER:
            objectInfo = objInfo ('sldr', 'slider', self.objectInst.slider, parentName)
            self.objectInst.slider += 1
        elif role == Accessibility.ROLE_SPLIT_PANE:
            objectInfo = objInfo ('splt', 'split_pane', self.objectInst.splitPane, parentName)
            self.objectInst.splitPane += 1
        elif role == Accessibility.ROLE_HTML_CONTAINER:
            objectInfo = objInfo ('html', 'html_container', self.objectInst.htmlContainer, parentName)
            self.objectInst.htmlContainer += 1
        elif role == Accessibility.ROLE_PROGRESS_BAR:
            objectInfo = objInfo ('pbr', 'progress_bar', self.objectInst.progressBar, parentName)
            self.objectInst.progressBar += 1
        elif role == Accessibility.ROLE_TOOL_BAR:
            objectInfo = objInfo ('tbar', 'tool_bar', self.objectInst.toolBar, parentName)
            self.objectInst.toolBar += 1
        elif role == Accessibility.ROLE_EMBEDDED:
            objectInfo = objInfo ('emb', 'embedded_component', self.objectInst.embeddedComponent, parentName)
            self.objectInst.embeddedComponent += 1
        elif role == Accessibility.ROLE_APPLICATION:
            objectInfo = objInfo ('app', 'application', -1, parentName)
        elif role == Accessibility.ROLE_EXTENDED:
            name = accessible.getRoleName ()
            if name == 'Calendar View':
                objectInfo = objInfo ('cal', 'calendar_view', self.objectInst.calView, parentName)
                self.objectInst.calView += 1
            elif name == 'Calendar Event':
                objectInfo = objInfo ('cal', 'calendar_event', self.objectInst.calView, parentName)
                self.objectInst.calView += 1
            else:
                if name is not None and name != '':
                    name = re.sub (' ', '_', name)
                # print 'extended', accessible.getRoleName (), accessible.getRole (), '*', accessible.name, '*'
                objectInfo = objInfo ('ukn', name, self.objectInst.unknown, parentName)
                self.objectInst.unknown += 1
        else:
            # print 'notlisted', accessible.getRoleName (), accessible.getRole (), '*', accessible.name, '*'
            roleName = accessible.getRoleName ()
            if roleName == None or roleName == '':
                name = 'unknown'
            else:
                name = re.sub (' ', '_', roleName)
            objectInfo = objInfo ('ukn', name, self.objectInst.unknown, parentName)
            self.objectInst.unknown += 1
        return objectInfo

    def get_non_conflicting_name (self, name):
        end_num = re.search ('\d*$', name)
        if end_num.start () == end_num.end (): # Numbers not postfixed yet
            num = 0
        else:
            num = int (name [end_num.start ():]) + 1
            name = name [:end_num.start ()]
        while name + str (num) in self.hashmap:
            num += 1
        return name + str (num)

    def dumpTree (self, accessible, parentName = None,  forceReScan = False):
        role = accessible.getRole ()
        if role == Accessibility.ROLE_TABLE_CELL or \
               role == Accessibility.ROLE_SEPARATOR or \
               role == Accessibility.ROLE_LIST_ITEM:
            return
        name = accessible.name or 'unnamed'
        roleName = accessible.getRoleName ()
        description = accessible.description
        label = 'label'
        if name == 'unnamed':
            relationNames = self.getRelationName (accessible)
            if relationNames is not None and relationNames != '':
                name = relationNames
                label = 'label_by'
        #if ldtpDebug and ldtpDebug == '2':
        #    print '%s* %s "%s": %s' % ('\t', roleName, name, description)
        objectInfo = self.getObjectInfo (accessible, parentName)
        if objectInfo is not None and role != Accessibility.ROLE_APPLICATION:
            flag = False
            if role == Accessibility.ROLE_FRAME or role == Accessibility.ROLE_DIALOG or \
                   role == Accessibility.ROLE_ALERT or role == Accessibility.ROLE_FONT_CHOOSER or \
                   role == Accessibility.ROLE_FILE_CHOOSER or role == Accessibility.ROLE_WINDOW:
                flag = True
            if name != 'unnamed' and re.sub ("(?i) +", "", name) != '':
                strippedStr = escapeChars (name, False)
                own_name = objectInfo.prefix + strippedStr
                if flag:
                    if self.applicationmap != {} and own_name in self.applicationmap and forceReScan == False:
                        if ldtpDebug:
                            print 'has_key', own_name
                        # Since the window info is already in appmap, don't process further
                        return
                    cur_win = window (objectInfo.objType, name, parentName, accessible.getIndexInParent ())
                    if ldtpDebug:
                        print 'Window:',  own_name,  cur_win,  type (own_name),  type (cur_win),  own_name in self.applicationmap,  forceReScan
                    if own_name in self.applicationmap and forceReScan:
                        del self.applicationmap [own_name]
                    if ldtpDebug:
                        print 'Window:',  own_name,  cur_win,  type (own_name),  type (cur_win),  own_name in self.applicationmap,  forceReScan
                    self.applicationmap [own_name] = cur_win
                    self.hashmap = cur_win.children
                #else:
                #    if self.hashmap and own_name in self.hashmap:
                #        own_name = self.get_non_conflicting_name (own_name)
                #    if ldtpDebug and self.hashmap:
                #        assert own_name not in self.hashmap, ('Name Conflict in Hashmap. ' + \
                #                                              own_name + 'already present\n' + foo)
                #    self.hashmap [own_name] = widget (objectInfo.objType, name, parentName, accessible.getIndexInParent ())
                if self.hashmap and own_name in self.hashmap:
                    own_name = self.get_non_conflicting_name (own_name)
                if ldtpDebug and self.hashmap:
                    assert own_name not in self.hashmap, ('Name Conflict in Hashmap. ' + \
                                                          own_name + 'already present\n' + foo)
                self.hashmap [own_name] = widget (objectInfo.objType, name, parentName, accessible.getIndexInParent ())
                if ldtpDebug and ldtpDebug == '2':
                    print own_name  + '={class=' + objectInfo.objType + ',' + \
                          label + '=' + name + ',child_index=' + str (accessible.getIndexInParent ()) + \
                          ',parent=' + parentName + '}'
                parentName = own_name
            else:
                own_name = objectInfo.prefix + str (objectInfo.instIndex)
                if flag:
                    if self.applicationmap != {} and own_name in self.applicationmap:
                        if ldtpDebug:
                            print 'has_key', own_name
                        # Since the window info is already in appmap, don't process further
                        return
                    cur_win = window (objectInfo.objType, name, parentName, accessible.getIndexInParent ())
                    self.applicationmap [own_name] = cur_win
                    self.hashmap = cur_win.children
                else:
                    self.hashmap [own_name] = widget (objectInfo.objType, parentName, accessible.getIndexInParent ())
                if ldtpDebug and ldtpDebug == '2':
                    print own_name + '={class=' + objectInfo.objType + ',child_index='  +\
                          str (accessible.getIndexInParent ()) + ',parent=' + parentName + '}'
                parentName = own_name
        for i in range (accessible.childCount):
            child = accessible.getChildAtIndex (i)
            if child is None:
                continue
            childRole = child.getRole ()
            if childRole == Accessibility.ROLE_FRAME or childRole == Accessibility.ROLE_DIALOG or \
                   childRole == Accessibility.ROLE_ALERT or childRole == Accessibility.ROLE_FONT_CHOOSER or \
                   childRole == Accessibility.ROLE_FILE_CHOOSER:
                self.objectInst.reset ()
            #time.sleep (1.0 / pow (10, 2))
            self.dumpTree (child, parentName)
            child.unref ()

    def isRoleWindowType (self, _role):
        if _role == Accessibility.ROLE_FRAME or _role == Accessibility.ROLE_DIALOG or \
               _role == Accessibility.ROLE_ALERT or _role == Accessibility.ROLE_FONT_CHOOSER or \
               _role == Accessibility.ROLE_FILE_CHOOSER or _role == Accessibility.ROLE_WINDOW:
            return True
        else:
            False

    def getRelationName (self, accessible):
        relations = []
        relationSet = accessible.getRelationSet ()
        for relation in relationSet:
            try:
                relations.append (relation._narrow (Accessibility.Relation))
            except:
                pass
        for relation in relations:
            _relationType = relation.getRelationType ()
            return relation.getTarget (0).name

    def getWinNameAppmapFormat (self, _windowName, _role):
        _windowType = None
        if _role == Accessibility.ROLE_FRAME:
            _windowType = 'frm'
        elif _role == Accessibility.ROLE_DIALOG or \
               _role == Accessibility.ROLE_ALERT or \
               _role == Accessibility.ROLE_WINDOW or \
               _role == Accessibility.ROLE_FONT_CHOOSER or \
               _role == Accessibility.ROLE_FILE_CHOOSER:
            _windowType = 'dlg'
        else:
            if ldtpDebug:
                print 'Not a window type'
            return None
        if _windowName and _windowName != '':
            return _windowType + escapeChars (_windowName, False)
        return _windowType + '0' # FIXME: Index has to be increased, instead of fixed 0

    def getParentNameAppmapFormat (self, accessible):
        # Provide the parent's accessible handle
        # It will be freed over here
        if accessible is None:
            return None
        _parentInfo = self.getObjectInfo (accessible, None)
        _parentName = _parentInfo.prefix + escapeChars (accessible.name)
        accessible.unref ()
        return _parentName

    def getObjNameAppmapFormat (self, accessible):
        if accessible is None:
            return None
        _objInfo = self.getObjectInfo (accessible, \
                                       self.getParentNameAppmapFormat (accessible.parent))
        if accessible.name and accessible.name != '' and _objInfo:
            _objName = _objInfo.prefix + escapeChars (accessible.name)
            return _objName
        return None

    def getObjRelNameAppmapFormat (self, accessible):
        if accessible is None:
            return None
        _objInfo = self.getObjectInfo (accessible, \
                                       self.getParentNameAppmapFormat (accessible.parent))
        _relationName = self.getRelationName (accessible)
        if _relationName and _relationName != '' and _objInfo:
            _objName = _objInfo.prefix + escapeChars (_relationName)
            return _objName
        return None

    def getParentHierarchyWithLabel (self, accessible, parentName = None):
        # Get parent hierarchy having label
        if accessible is None:
            return
        objectInfo = self.getObjectInfo (accessible, None)
        if accessible.name is not None and accessible.name != '':
            _role = accessible.getRole ()
            _name = ''
            _windowName = ''
            if self.isRoleWindowType (_role):
                _windowName = _name = self.getWinNameAppmapFormat (accessible.name, _role)
                self.hierarchy = '%(window)s#%(objtype)s:%(index)d:%(name)s;%(hierarchy)s' % \
                                {'window' : _windowName, 'objtype' : objectInfo.objType,
                                'index' : accessible.getIndexInParent (), \
                                'name' : _name, 'hierarchy' : self.hierarchy}
                return
#            else:
#                _name = self.getObjNameAppmapFormat (accessible)
#                _windowHandle = self.getWindowHandle (accessible)
#                if _windowHandle is not None:
#                    _windowName = self.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
#                    _windowHandle.unref ()
        if objectInfo.objType != 'unknown' and accessible.getIndexInParent () != -1:
            if self.hierarchy == '':
                self.hierarchy = '%(objtype)s:%(index)d' % \
                                 {'objtype' : objectInfo.objType, 'index' : accessible.getIndexInParent ()}
            else:
                self.hierarchy = '%(objtype)s:%(index)d;%(hierarchy)s' % \
                                 {'objtype' : objectInfo.objType, 'index' : accessible.getIndexInParent (), 'hierarchy' : self.hierarchy}
        else:
            if ldtpDebug:
                print 'Unknown objectInfo'
        _parent = accessible.parent
        if _parent is None:
            return
        self.getParentHierarchyWithLabel (_parent)
        _parent.unref ()
        return

    def getParentOfRole (self, accessible, parentRole):
        # Get parent of the given accessible handle based on the role
        # NOTE: parentRole should not be of any window type
        if accessible is None:
            return None
        if parentRole is None:
            return None
        _role = accessible.getRole ()
        if _role == Accessibility.ROLE_FILE_CHOOSER or _role == Accessibility.ROLE_FONT_CHOOSER or \
               _role == Accessibility.ROLE_DIALOG or _role == Accessibility.ROLE_FRAME or \
               _role == Accessibility.ROLE_ALERT or _role == Accessibility.ROLE_WINDOW:
            return None
        if _role == parentRole:
             # Has to be freed in the calling function,
             # assuming that the called function's accessible
             # handle is not equal to the new parent handle
            return accessible
        _parent = accessible.parent
        _handle = self.getParentOfRole (_parent, parentRole)
        if _handle != _parent:
            _parent.unref ()
        return _handle

    def getChildOfRole (self, accessible, childRole):
        if accessible is None:
            return None
        if childRole is None:
            return None
        _role = accessible.getRole ()
        if _role == childRole:
             # Has to be freed in the calling function,
             # assuming that the called function's accessible
             # handle is not equal to the new parent handle
            return accessible
        for i in range (accessible.childCount):
            child = accessible.getChildAtIndex (i)
            if child is None:
                continue
            tmpChild = self.getChildOfRole (child, childRole)
            if tmpChild:
                if tmpChild != child:
                    child.unref ()
                return tmpChild
            child.unref ()
        return None

    def getChildWindowHandle (self, accessible,  name):
        if accessible is None:
            return None
        if ldtpDebug:
            print 'childCount',  accessible.childCount
        for i in range (0, accessible.childCount):
            try:
                _app = accessible.getChildAtIndex (i)
            except:
                if ldtpDebug:
                    print traceback.print_exc ()
                continue
            if _app is None:
                continue
            _role = _app.getRole ()
            if ldtpDebug:
                print 'Role: ',  _app.getRoleName (),  name
                if _app.name != None:
                    print '_app.name',  _app.name,  self.getWinNameAppmapFormat (_app.name,  _role)
            if _app.name is not None and _app.name != '' and \
                (re.search (name,  _app.name) != None or \
                re.search (name,  self.getWinNameAppmapFormat (_app.name,  _role)) != None):
                return _app
            _app.unref ()
        return None

    def getWindowHandle (self, accessible):
        if accessible is None:
            return None
        _role = accessible.getRole ()
        if _role == Accessibility.ROLE_FILE_CHOOSER or _role == Accessibility.ROLE_FONT_CHOOSER or \
               _role == Accessibility.ROLE_DIALOG or _role == Accessibility.ROLE_FRAME or \
               _role == Accessibility.ROLE_ALERT or _role == Accessibility.ROLE_WINDOW:
                return accessible
        _parent = None
        _handle = None
        try:
            _parent = accessible.parent
            _handle = self.getWindowHandle (_parent)
        except:
            pass
        if _handle != _parent and _parent is not None:
            _parent.unref ()
        return _handle

    def getContextHandle ():
        return None

    def getComponentHandle ():
        return None

    def getAppHandle (self,  appName):
        # App handle should be freed, if not None
        if appName == None or appName == '':
            return None
        _desktop = self.registry.getDesktop (0)
        if _desktop is None:
            return None
        _app = ''
        for i in range (0, _desktop.childCount):
            try:
                _app = _desktop.getChildAtIndex (i)
            except:
                if ldtpDebug:
                    print traceback.print_exc ()
                continue
            if _app is None:
                continue
            _name = ''
            if _app.name is not None and _app.name != "":
                if ldtpDebug:
                    print 'DEBUG _app.name, _app.getRoleName',  _app.name,  _app.getRoleName ()
                _name = self.getWinNameAppmapFormat (_app.name,  _app.getRole ())
                if ldtpDebug:
                    print '_name',  _name
            else:
                _app.unref ()
                continue
            if ldtpDebug:
                print 'appName',  appName,  _name,  _app.name
            if _name != None and re.search (appName,  _name) != None or \
                re.search (appName,  _app.name) != None:
                return _app
            else:
                _appHandle = self.getChildWindowHandle (_app,  appName)
                if _appHandle != None:
                    _app.unref ()
                    return _appHandle
            _app.unref ()
        return None

    def searchBasedOnKey (self, key, searchObjInfo):
        if key is None or searchObjInfo is None:
            return False
        #re.match ('(.*focus.*){1}', 'afocu8s123')
        #re.match ('(.*focus.*){1}', 'afocus123')
        #re.match ('(.*focus.*){1}', 'a focus123')
        if searchObjInfo.window is True:
            if key == searchObjInfo.key:
                return True
            if searchObjInfo.pattern is not None or searchObjInfo.pattern != '':
                if re.match (searchObjInfo.pattern, key) is not None:
                    return True
            tmpPattern = 'frm%s' % key
            if re.match (tmpPattern, searchObjInfo.key) is not None:
                return True
            tmpPattern = 'dlg%s' % key
            if re.match (tmpPattern, searchObjInfo.key) is not None:
                return True
            tmpPattern = 'frm%s*' % key
            if re.match (tmpPattern, searchObjInfo.key) is not None:
                return True
            tmpPattern = 'dlg%s*' % key
            if re.match (tmpPattern, searchObjInfo.key) is not None:
                return True
            return False
        if searchObjInfo.pattern is not None:
            return re.match (searchObjInfo.pattern, key)
        return False

    def searchBasedOnLabel (self, value, searchObjInfo):
        if value is None or searchObjInfo is None or searchObjInfo.key is None:
            return False
        flag = False
        if value.type is not None:
            if value.type == 'frame' or value.type == 'dialog' or \
               value.type == 'alert' or value.type == 'file_chooser' or \
               value.type == 'font_chooser':
                flag = True
        if value.label is None or value.label == '':
            return False
        if (searchObjInfo.window is False or flag is True) and \
               (value.label == searchObjInfo.key or \
                (searchObjInfo.pattern is not None and \
                 searchObjInfo.pattern != '' and \
                 re.search (searchObjInfo.pattern, value.label) is not None)):
            return True
        if re.search ('_', value.label) is None:
            return False
        if re.sub ('_', '', value.label) == searchObjInfo.key:
            return True
        return False

    def searchLabelName (self, key, value, unknLabelProperty):
        if key is None or value is None or unknLabelProperty is None:
            return False
        if value.index == unknLabelProperty.childIndex:
            if value.parent is not None and \
               unknLabelProperty.parentName is not None and \
               value.parent == unknLabelProperty.parentName:
                unknLabelProperty.objName = key
        return False

    def searchAfterStrippingSpace (self, key, data):
        if key is None or data is None:
            return False
        if key == data:
            return True
        if re.search (' ', data) is None:
            return False
        tmp = escapeChar (data, ' ')
        if key == tmp:
            return True
        if re.match ("(.*" + tmp + "){1}", key) or re.match (key, tmp):
            return True
        return False

    def getObjectDef (self, ht, context, isWindow):
        if ht is None or context is None or ht.children is None:
            return None
        if context in ht.children:
            return ht.children [context]
        obj = SearchObjInfo (context, isWindow, context)
        for widget in ht.children.keys ():
            if self.searchBasedOnKey (widget, obj):
                return widget
        for widget in ht.children.keys ():
            if self.searchBasedOnLabel (ht.children [widget], obj):
                return widget
        for widget in ht.children.keys ():
            if self.searchAfterStrippingSpace ():
                return widget
        return None
