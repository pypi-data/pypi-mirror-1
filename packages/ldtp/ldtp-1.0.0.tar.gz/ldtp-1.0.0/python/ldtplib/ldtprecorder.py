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

__author__ = "Nagappan A"
__maintainer__ = "Nagappan A"
__version__ = "1.0.0"

import re
import os
import sys
import time
import signal
import threading
import traceback

# Let us not register our application under at-spi application list
os.environ ['GTK_MODULES'] = ''

_ldtpDebug = os.getenv ('LDTP_DEBUG') # Enable debugging

try:
    import pyatspi as atspi, Accessibility
except ImportError:
    import atspi
    import Accessibility

from ldtpcommon import *
import ldtplib.ldtplibutils

def __shutdownAndExit (signum, frame):
    try:
        atspi.Registry ().stop ()
    except RuntimeError:
        pass
    if _ldtpDebug:
        print "Goodbye."

class record:
    def __init__ (self, pckt = None):
        self.__pckt = pckt
        self.__fp = sys.stdout
        self.__prevTime = time.time ()
        self.registry = atspi.Registry ()
        self.__panelName  = ''
        self.__textItem   = None
        self.__textName   = None
        self.__tableCell  = ''
        self.__menuItem   = None
        self.__comboBox   = None
        self.__windowName = None
        self.__windowType = None
        self.__objectName = None
        self.__objectType = None
        self.__tableName  = ''
        self.__textContent = ''
        self.__panelParent = ''
        self.__comboBoxName = None
        self.__comboBoxText = None
        self.__treeTableCell   = ''
        self.__tableWindowName = ''
        self.objectInst = objInst ()
        self.appmap = appmap (self.objectInst,  self.registry)
        self.__textType = threading.Event ()
        self.__textType.clear ()
        self.__comboTextType = threading.Event ()
        self.__comboTextType.clear ()
        self.__comboBoxThread = threading.Event ()
        self.__comboBoxThread.set ()
        self.__comboListThread = threading.Event ()
        self.__comboListThread.set ()

    def start (self):
        try:
            self.registry.start ()
        except:
            if _ldtpDebug and _ldtpDebug == '3':
                print traceback.print_exc ()
            pass

    def doesWindowExist (self, name):
        '''Iterates over each app on each desktop til it finds one with a
        matching name, which is then returned.'''
        global recorder
        _old = None
        if name == None:
            return False
        _desktop = self.registry.getDesktop (0)
        if _desktop is None:
            if _ldtpDebug:
                print 'desktop is None'
            return False
        for i in range (0, _desktop.childCount):
            try:
                _app = _desktop.getChildAtIndex (i)
            except:
                if _ldtpDebug:
                    print traceback.print_exc ()
                continue
            if _app is None:
                continue
            if _ldtpDebug:
                print 'child count',  _app.childCount
            for j in range (0, _app.childCount):
                _window = _app.getChildAtIndex (j)
                if _window is None:
                    if _ldtpDebug:
                        print '_window is None'
                    continue
                _windowName = self.appmap.getWinNameAppmapFormat (_window.name, _window.getRole ())
                if _window.name == name or (_windowName and re.search (name,  _windowName)):
                    _desktop.unref ()
                    _app.unref ()
                    _window.unref ()
                    return True
                _window.unref ()
            _app.unref ()
        _desktop.unref ()
        if _ldtpDebug:
            print 'could not find window %s' % name
        return False

    def getObjectName (self, name):
        try:
            return self.getObjectNameDebug (name)
        except:
            print traceback.print_exc ()
            return ''

    def getObjectNameDebug (self, name):
        if _ldtpDebug:
            print name
        _windowName = re.split ('#', name, 1)
        if _ldtpDebug:
            print _windowName,  len (_windowName)
        _name = ''
        if len (_windowName) == 2:
            _name = _windowName [1]
        _windowName = _windowName [0]
        _objName = re.split (';', _name)
        _win = None
        try:
            _win = self.appmap.applicationmap [_windowName]
        except KeyError:
            if _ldtpDebug:
                print _windowName, 'does not exist in appmap'
            return ''
        _parent = _windowName
        index = len (_objName)
        i = 1
        loopedOnce = False
        while i < index:
            _list = re.split (':', _objName [i])
            if _ldtpDebug:
                print 'i =',  i,  index,  _list [0],  _list [1],  len (_list),  _parent
            flag = False
            for obj in _win.children.keys ():
                _childObj = _win.children [obj]
                if _childObj is None:
                    continue
                if len (_list) >= 2 and _childObj.widgetType == _list [0] and _childObj.index == int (_list [1]) and _parent == _childObj.parent:
                    _parent = obj
                    if _ldtpDebug:
                        print 'Inner _parent',  _parent
                    i += 1
                    flag = True
                    break
            if flag == False:
                if _ldtpDebug:
                    print 'flag False'
                _accessible = self.appmap.getAppHandle (_windowName)
                if _ldtpDebug:
                    print _windowName,  _accessible
                if _accessible is not None:
                    parent = _accessible.parent
                    name = None
                    if parent is not None:
                        name = parent.name
                        parent.unref ()
                    try:
                        self.objectInst.reset ()
                        self.appmap.dumpTree (_accessible,  name,  True)
                    except:
                        if _ldtpDebug:
                            print traceback.print_exc ()
                    _accessible.unref ()
                    i = 1
                    _parent = _windowName
                    try:
                        _win = self.appmap.applicationmap [_windowName]
                    except KeyError:
                        if _ldtpDebug:
                            print _windowName, 'does not exist in appmap'
                        return ''
                else:
                    loopedOnce = True
                    i = index
                if loopedOnce == False:
                    loopedOnce = True
        #Uncomment the below segment of code to dump to FS
        #print 'getObjectName', name
        #f = open('/tmp/' + name + '.txt', 'w')
        #for win in self.appmap.applicationmap.keys ():
        #    print 'win', win
        #    f.write (self.get_info (win, self.appmap.applicationmap [win]))
        #    win = self.appmap.applicationmap [win]
        #    for widget in win.children.keys ():
        #        f.write (self.get_info (widget, win.children [widget]))
        #f.close()
        if _ldtpDebug:
            print '_parent',  _parent
        return ldtplib.ldtplibutils.escapeChars (_parent)

    def get_info (self, name, obj):
        foo = name + '={class=' + obj.widgetType
        foo += ', child_index=' + str (obj.index)
        if obj.label != '':
            foo += (', label=' + obj.label)
        foo += (', parent=' + obj.parent + '}\n')
        return foo

    def findApp (self, name):
        '''Iterates over each app on each desktop til it finds one with a
        matching name, which is then returned.'''
        for desknum in range (self.registry.getDesktopCount ()):
            _desktop = self.registry.getDesktop (desknum)
            for i in range (_desktop.childCount):
                _child = _desktop.getChildAtIndex (i)
                if _child.name == name:
                    _desktop.unref ()
                    return child
                _child.unref ()
            _desktop.unref ()
        if _ldtpDebug:
            print 'could not find application %s' % name
        return None

    def timeElapsed (self):
        self.currTime = int (time.time () - self.__prevTime)
        self.__prevTime = time.time ()
        return self.currTime

    def getPrintableChar (self, hwCode):
        if hwCode in keyboard.charKeySynthVals:
            return keyboard.charKeySynthVals [hwCode]
        if hwCode in keyboard.digitKeySynthVals:
            return keyboard.digitKeySynthVals [hwCode]
        if hwCode in keyboard.symbolKeySynth:
            return keyboard.symbolKeySynth [hwCode]
        return None

    def notifyKeystroke (self, event):
        if event.type == 1 and event.hw_code == 23: # 23 is for Tab
            self.__comboTextType.clear ()
#        elif event.hw_code == 23 and self.__comboTextType.isSet () == False:
#            pass # Do nothing
        else:
            self.__comboTextType.set ()
            self.__textType.set ()
        if self.__pckt and event.type == 0:
            nonPrintChar = None
            char = self.getPrintableChar (event.hw_code)
            if char != None:
                self.__textContent += char
            else:
                if self.__textContent != '':
                    _xml = self.__pckt.generatekeyboardxml (self.__textContent)
                    self.__pckt.sendpacket (_xml)
                    self.__textContent = ''
                if event.hw_code in keyboard.nonPrintKeySynth:
                    nonPrintChar = keyboard.nonPrintKeySynth [event.hw_code]
                    _xml = self.__pckt.generatekeyboardxml (nonPrintChar)
                    self.__pckt.sendpacket (_xml)
            if _ldtpDebug and _ldtpDebug == '2':
                print "keystroke type=%d hw_code=%d modifiers=%d event_string=(%s) " \
                      "is_text=%s" \
                      % (event.type, event.hw_code, event.modifiers, event.event_string,
                         event.is_text)
#        if event.event_string == 'F12':
#            stop ()
        return False

    def windowListenerCallback (self, event):
        role = event.source.getRole ()
        if role == Accessibility.ROLE_FRAME or role == Accessibility.ROLE_DIALOG or \
               role == Accessibility.ROLE_ALERT  or role == Accessibility.ROLE_WINDOW:
            if self.__textContent != '':
                _xml = self.__pckt.generatekeyboardxml (self.__textContent)
                self.__pckt.sendpacket (_xml)
                self.__textContent = ''
            self.__windowName = self.appmap.getWinNameAppmapFormat (str (event.source.name), role)
            self.__windowType = event.source.getRoleName ()
            if _ldtpDebug and _ldtpDebug == '2':
                print '***WINDOW', event.type, event.source.name, \
                      event.detail1, event.detail2,  \
                      event.any_data
            parent = event.source.parent
            name = None
            if parent is not None:
                name = parent.name
                parent.unref ()
            try:
                self.objectInst.reset ()
                self.appmap.dumpTree (event.source, name)
                if self.__pckt and (event.type == 'window:create' or event.type == 'window:destroy'):
                    _xml = self.__pckt.generatenotificationxml (self.__windowName, \
                                                              '', \
                                                              self.__windowType, event.type, \
                                                              self.timeElapsed ())
                    self.__pckt.sendpacket (_xml)
            except:
                print traceback.print_exc ()

    def nameChangeListenerCallback (self, event):
        _role = event.source.getRole ()
        if _role == Accessibility.ROLE_FRAME or _role == Accessibility.ROLE_DIALOG or _role == Accessibility.ROLE_ALERT:
            self.__windowName = self.appmap.getWinNameAppmapFormat (str (event.source.name), _role)
            if _ldtpDebug and _ldtpDebug == '2':
                print 'NAMECHANGE', event.type, event.source.name, \
                      event.detail1, event.detail2,  \
                      event.any_data
            _parent = event.source.parent
            _name = None
            if _parent is not None:
                _name = _parent.name
                _parent.unref ()
            try:
                self.objectInst.reset ()
                self.appmap.dumpTree (event.source, _name)
                if self.__pckt and (event.type == 'window:create' or event.type == 'window:destroy'):
                    _xml = self.__pckt.generatenotificationxml (self.__windowName, \
                                                              '', \
                                                              self.__windowType, event.type, \
                                                              self.timeElapsed ())
                    self.__pckt.sendpacket (_xml)
            except:
                print traceback.print_exc ()

    def registerWindowListener (self):
        eventTypes = [
            "window:activate",
            "window:create",
            "window:destroy",
            ]
        for eventType in eventTypes:
            self.registry.registerEventListener (self.windowListenerCallback, eventType)

    def registerNameChangeListener (self):
        eventTypes = [
            "object:property-change:accessible-name"
            ]
        for eventType in eventTypes:
            self.registry.registerEventListener (self.nameChangeListenerCallback, eventType)

    def globalListenerCallback (self, event):
        try:
            self.globalListenerCallbackDebug (event)
        except:
            print traceback.print_exc ()

    def globalListenerCallbackDebug (self, event):
        if event.type == 'object:state-changed:defunct' or \
               event.type == 'object:state-changed:showing' or \
               event.type == 'object:state-changed:visible' or \
               event.type == 'object:state-changed:iconified':
            return
        _name = None
        _role = None
        if event.source:
            _role = event.source.getRole ()
            if os.getenv ('RECORDDEBUG') != None:
                print 'DEBUGING', event.type,
                if event.source is not None:
                    print event.source.getRole () == Accessibility.ROLE_EXTENDED
                else:
                    print ''
                return
        _windowHandle = self.appmap.getWindowHandle (event.source)
        if _windowHandle is not None:
            _stateSet = _windowHandle.getState ()
            if _stateSet.contains (Accessibility.STATE_VISIBLE) and \
                    _stateSet.contains (Accessibility.STATE_SHOWING) and \
                    _stateSet.contains (Accessibility.STATE_ENABLED):
                pass
            else:
                if _ldtpDebug:
                    print 'Window does not exist'
                return

        # Implementation for push button starts
        if event.source and _role == Accessibility.ROLE_PUSH_BUTTON:
            focus = None
            if re.match ('^focus', str (event.type)):
                focus = 'focus:'
            if ((event.detail1 and str (event.type).startswith ('object:state-changed:armed')) or \
                focus != None):
                _name = ''
                if event.source.name == '':
                    _name = self.appmap.getObjRelNameAppmapFormat (event.source)
                else:
                    _name = self.appmap.getObjNameAppmapFormat (event.source)
                _windowHandle = self.appmap.getWindowHandle (event.source)
                _windowName = None
                if _windowHandle:
                    _windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
                    if _windowName is None:
                        _windowName = self.__windowName
                    _windowHandle.unref ()
                else:
                    _windowName = self.__windowName
                self.completeComboOrTextOp ()
                if self.__pckt:
                    eventType = str (event.type)
                    if focus is not None:
                        eventType = focus
                    _xml = self.__pckt.generatenotificationxml (_windowName, _name, \
                                                              event.source.getRoleName (), \
                                                              eventType,
                                                              self.timeElapsed ())
                    self.__pckt.sendpacket (_xml)
                if _ldtpDebug:
                    print 'click (\'' + _windowName + '\', \'' + _name + '\')' + 'PUSH BUTTON'
            # Implementation for push button ends
            return

        # Implementation for check box starts
        if event.source and _role == Accessibility.ROLE_CHECK_BOX:
            if str (event.type).startswith ('object:state-changed:checked'):
                if event.source.name == '':
                    _name = self.appmap.getObjRelNameAppmapFormat (event.source)
                else:
                    _name = self.appmap.getObjNameAppmapFormat (event.source)
                _windowHandle = self.appmap.getWindowHandle (event.source)
                _windowName = None
                if _windowHandle:
                    _windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
                    _windowHandle.unref ()
                else:
                    _windowName = self.__windowName
                self.completeComboOrTextOp ()
                if _ldtpDebug:
                    if event.detail1:
                        print 'check (\'' + _windowName + '\', \'' + _name + '\')'
                    else:
                        print 'uncheck (\'' + _windowName + '\', \'' + _name + '\')'
                if self.__pckt:
                    _xml = self.__pckt.generatenotificationxml (_windowName, _name, \
                                                              event.source.getRoleName (), str (event.type), \
                                                              self.timeElapsed (), detail1 = event.detail1,
                                                              detail2 = event.detail2)
                    self.__pckt.sendpacket (_xml)
            # Implementation for check box ends
            return

        # Implementation for page tab starts
        if event.source and _role == Accessibility.ROLE_PAGE_TAB:
            if str (event.type).startswith ('object:state-changed:selected') and event.detail1:
                if event.source.name == '' or event.source.name == None:
                    _name = self.appmap.getObjRelNameAppmapFormat (event.source)
                else:
                    _name = event.source.name
                if  _name is None or _name == '':
                    return
                _windowHandle = self.appmap.getWindowHandle (event.source)
                _windowName = None
                if _windowHandle:
                    _windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
                    _windowHandle.unref ()
                else:
                    _windowName = self.__windowName
                self.completeComboOrTextOp ()
                self.appmap.hierarchy = ''
                parent = self.appmap.getParentOfRole (event.source, Accessibility.ROLE_PAGE_TAB_LIST)
                if parent is not None:
                    self.appmap.getParentHierarchyWithLabel (parent)
                    parent.unref ()
                if _ldtpDebug:
                    print 'selecttab (\'' + _windowName + '\', \'' + self.appmap.hierarchy + \
                          '\', \'' + _name + '\')'
                if self.__pckt:
                    _xml = self.__pckt.generatenotificationxml (_windowName, \
                                                              self.appmap.hierarchy, \
                                                              event.source.getRoleName (), str (event.type), \
                                                              self.timeElapsed (), data = _name)
                    self.__pckt.sendpacket (_xml)
            # Implementation for page tab ends
            return

        if event.source and _role == Accessibility.ROLE_TREE_TABLE:
            if event.detail1 and str (event.type).startswith ('object:state-changed:focused'):
                _windowHandle = self.appmap.getWindowHandle (event.source)
                _windowName = None
                if _windowHandle:
                    _windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
                    self.__windowName = _windowName
                    _windowHandle.unref ()
                else:
                    _windowName = self.__windowName
                self.__tableWindowName = _windowName
                _name = ''
                if event.source.name == '':
                    _name = self.appmap.getObjRelNameAppmapFormat (event.source)
                else:
                    _name = self.appmap.getObjNameAppmapFormat (event.source)
                self.__tableName = _name
                self.__treeTableCell = ''
                _table = event.source.queryInterface ("IDL:Accessibility/Table:1.0")
                if _table:
                    try:
                        _table = _table._narrow (Accessibility.Table)
                    except:
                        _table = None

                    if not _table:
                        return
                    for i in _table.getSelectedRows ():
                        _columns = _table.getSelectedColumns ()
                        if _columns == []:
                            _columns = [0]
                        for j in _columns:
                            _tmp = _table.getAccessibleAt (i, j)
                            for k in range (0, _tmp.childCount):
                                _againTmp = _tmp.getChildAtIndex (k)
                                if _againTmp is None:
                                    continue
                                if _againTmp.name is not None and _againTmp.name != '':
                                    self.__treeTableCell = _againTmp.name
                                _againTmp.unref ()
                            _tmp.unref ()
                    _table.unref ()
            return

        if event.source and _role == Accessibility.ROLE_PANEL:
            _windowHandle = self.appmap.getWindowHandle (event.source)
            _windowName = None
            self.__panelName = ''
            if _windowHandle:
                _windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
                self.__windowName = _windowName
                _windowHandle.unref ()
            else:
                _windowName = self.__windowName
            if event.source.name == None or event.source.name == '':
                return
            self.appmap.hierarchy = ''
            _parent = event.source.parent
            if _parent is None:
                return
            self.__panelName = event.source.name
            self.appmap.getParentHierarchyWithLabel (_parent)
            _parent.unref ()
            self.__panelParent = self.appmap.hierarchy
            if event.detail1 and str (event.type).startswith ('object:state-changed:focused'):
                if _ldtpDebug:
                    print 'selectpanelname (\'' + _windowName + '\', \'' + self.appmap.hierarchy + \
                          '\', \'' + event.source.name + '\')'
                if self.__pckt:
                    _xml = self.__pckt.generatenotificationxml (_windowName, \
                                                              self.appmap.hierarchy, \
                                                              event.source.getRoleName (), str (event.type), \
                                                              self.timeElapsed (), data = event.source.name)
                    self.__pckt.sendpacket (_xml)
            return

        # Implementation for table cell starts
        if event.source and _role == Accessibility.ROLE_TABLE_CELL:
            if (event.detail1 and str (event.type).startswith ('object:state-changed:selected')) or \
                   str (event.type).startswith ('focus:'):
                if _ldtpDebug:
                    print 'Table cell', event.source.name, event.type, event.detail1, event.detail2
                if event.source.name == '':
                    _name = self.appmap.getRelationName (event.source)
                else:
                    _name = event.source.name
                if _name == '' or _name == None:
                    return
                _windowHandle = self.appmap.getWindowHandle (event.source)
                _windowName = None
                if _windowHandle:
                    _windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
                    self.__windowName = _windowName
                    _windowHandle.unref ()
                else:
                    _windowName = self.__windowName
                _parent = self.appmap.getParentOfRole (event.source, Accessibility.ROLE_TREE_TABLE)
                if _parent is None:
                    _parent = self.appmap.getParentOfRole (event.source, Accessibility.ROLE_TREE)
                if _parent is None:
                    _parent = self.appmap.getParentOfRole (event.source, Accessibility.ROLE_TABLE)
                self.appmap.hierarchy = ''
                if _parent is not None:
                    self.appmap.getParentHierarchyWithLabel (_parent)
                    _parent.unref ()
                self.__tableCell = _name
                self.__tableName = self.appmap.hierarchy
                if re.search ('#', self.appmap.hierarchy) == None:
                    self.appmap.hierarchy = _windowName + '#' + self.appmap.hierarchy
                if _ldtpDebug:
                    print 'selectrow (\'' + _windowName + '\', \'' + self.appmap.hierarchy + \
                          '\', \'' + _name + '\')' + str (event.type)
                if self.__pckt:
                    _xml = self.__pckt.generatenotificationxml (_windowName, \
                                                              self.appmap.hierarchy, \
                                                              event.source.getRoleName (), str (event.type), \
                                                              self.timeElapsed (), data = _name)
                    self.__pckt.sendpacket (_xml)
            # Implementation for table cell ends
            return

        # Implementation for toggle button starts
        if event.source and _role == Accessibility.ROLE_TOGGLE_BUTTON:
            if str (event.type).startswith ('object:state-changed:checked') and event.detail1 == 1:
                if event.source.name == '':
                    _name = self.appmap.getObjRelNameAppmapFormat (event.source)
                else:
                    _name = self.appmap.getObjNameAppmapFormat (event.source)
                if _name is None:
                    return
                _windowHandle = self.appmap.getWindowHandle (event.source)
                _windowName = None
                if _windowHandle:
                    _windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
                    _windowHandle.unref ()
                else:
                    _windowName = self.__windowName
                self.completeComboOrTextOp ()
                if _ldtpDebug:
                    print 'click (\'' + _windowName + '\', \'' + _name + '\')'
                if self.__pckt:
                    _xml = self.__pckt.generatenotificationxml (_windowName, _name, \
                                                              event.source.getRoleName (), \
                                                              str (event.type), self.timeElapsed ())
                    self.__pckt.sendpacket (_xml)
            # Implementation for toggle button ends
            return

        # Implementation for radio button starts
        if event.source and _role == Accessibility.ROLE_RADIO_BUTTON:
            if event.detail1 and str (event.type).startswith ('object:state-changed:checked'):
                if event.source.name == '':
                    _name = self.appmap.getRelationName (event.source)
                else:
                    _name = event.source.name
                _windowHandle = self.appmap.getWindowHandle (event.source)
                _windowName = None
                if _windowHandle:
                    _windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
                    _windowHandle.unref ()
                else:
                    _windowName = self.__windowName
                self.completeComboOrTextOp ()
                if _ldtpDebug:
                    print 'click (\'' + self.__windowName + '\', \'' + _name + '\')'
                if self.__pckt:
                    _xml = self.__pckt.generatenotificationxml (_windowName, _name, \
                                                              event.source.getRoleName (), \
                                                              str (event.type), self.timeElapsed ())
                    self.__pckt.sendpacket (_xml)
            # Implementation for radio button ends
            return

        # Implementation for click release starts
        if str (event.type).startswith ('mouse:button:1r') or \
               str (event.type).startswith ('mouse:button:2r') or \
               str (event.type).startswith ('mouse:button:3r'):
            if self.__textType.isSet ():
                self.completeComboOrTextOp ()
            if str (event.type).startswith ('mouse:button:3r'):
                if self.__tableCell != '':
                    if _ldtpDebug is not None:
                        print 'rightclick (' + self.__windowName + ', ' + self.__tableName + ', ' + self.__tableCell + ')'
                    if self.__pckt:
                        _xml = self.__pckt.generatenotificationxml (self.__windowName, \
                                                                  self.__tableName, \
                                                                  'right click', str (event.type), \
                                                                  self.timeElapsed (), data = self.__tableCell)
                        self.__pckt.sendpacket (_xml)
                    self.__tableCell = ''
                elif self.__treeTableCell != '':
                    if _ldtpDebug is not None:
                        print 'rightclick (' + self.__tableWindowName + ', ' + self.__tableName + ', ' + self.__treeTableCell + ')'
                    if self.__pckt:
                        _xml = self.__pckt.generatenotificationxml (self.__tableWindowName, \
                                                                  self.__tableName, \
                                                                  'right click', str (event.type), \
                                                                  self.timeElapsed (), data = self.__treeTableCell)
                        self.__pckt.sendpacket (_xml)
                    self.__treeTableCell = ''
                elif self.__panelName != '':
                    if _ldtpDebug is not None:
                        print 'rightclick (' + self.__windowName + ', ' + self.__panelParent + ', ' + self.__panelName + ')'
                    if self.__pckt:
                        _xml = self.__pckt.generatenotificationxml (self.__windowName, \
                                                                  self.__panelParent, \
                                                                  'right click', str (event.type), \
                                                                  self.timeElapsed (), data = self.__panelName)
                        self.__pckt.sendpacket (_xml)
            self.__comboTextType.clear ()
            self.__textType.clear ()
            if self.__comboBox and self.__menuItem:
                if self.__pckt:
                    _xml = self.__pckt.generatenotificationxml (self.__windowName, \
                                                              self.__comboBox, \
                                                              'combo box', str (event.type), \
                                                              self.timeElapsed (), \
                                                              data = self.__menuItem)
                    self.__pckt.sendpacket (_xml)
                if _ldtpDebug:
                    print 'comboselect (\'' + self.__windowName + '\', \'' + self.__comboBox + \
                          '\', \'' + self.__menuItem + '\')'
                self.__comboBox = None
                self.__menuItem = None
                self.__comboBoxThread.set ()
            elif self.__menuItem:
                if self.__pckt:
                    _xml = ''
                    _xml = self.__pckt.generatenotificationxml (self.__windowName, \
                                                                  self.__menuItem, \
                                                                  'menu item', \
                                                                  str (event.type), \
                                                                  self.timeElapsed ())
                    self.__pckt.sendpacket (_xml)
                if _ldtpDebug:
                    print 'selectmenuitem (\'' + self.__windowName + '\', \'' + self.__menuItem + '\')'
                self.__menuItem = None
            self.__comboListThread.set ()
            # Implementation for click release ends
            return

        # Implementation for menu item starts
        if event.source and (_role == Accessibility.ROLE_MENU_ITEM or \
                             _role == Accessibility.ROLE_CHECK_MENU_ITEM or \
                             _role == Accessibility.ROLE_RADIO_MENU_ITEM):
            if str (event.type).startswith ('object:state-changed:selected'):
                if event.source.name == '':
                    _name = self.appmap.getObjRelNameAppmapFormat (event.source)
                else:
                    _name = self.appmap.getObjNameAppmapFormat (event.source)
                if event.detail1:
                    self.__menuItem = _name
                    self.__comboBox = None
                # Checking whether the event is from combo box
                _parent = self.appmap.getParentOfRole (event.source, Accessibility.ROLE_COMBO_BOX)
                if _parent:
                    if _parent.getRole () == Accessibility.ROLE_COMBO_BOX:
                        if self.__comboBoxThread.isSet ():
                            # We are getting the combo box event two times
                            # Just to avoid the first instance, as it gives
                            # the info of the currently visible one
                            self.__comboBoxThread.clear ()
                            self.__comboBox = None
                            self.__menuItem = None
                            _parent.unref ()
                            return
                        self.__comboBox = self.appmap.getObjRelNameAppmapFormat (_parent)
                        if self.__comboBox is None:
                            self.__comboBox = self.appmap.getObjNameAppmapFormat (_parent)
                    _parent.unref ()

                _windowRole = None
                _windowHandle = self.appmap.getWindowHandle (event.source)
                if _windowHandle is not None:
                    _windowRole = _windowHandle.getRole ()
                    self.__windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowRole)
                    _windowHandle.unref ()
                if _ldtpDebug:
                    print self.__windowName, _name, event.detail1, event.detail2, self.__menuItem
                # gcalctool does not generates event.detail1 as 1, so menuItem will not be set
                # Its a hack and not the solution
                if _windowRole == Accessibility.ROLE_WINDOW and event.detail1 == 0:
                    # Menuitem invoked on clicking a push button (gcalctool - Advanced option)
                    self.__menuItem = _name
                # gcalctool does not generates event.detail1 as 1
                #if self.__comboBox == None and event.detail1 == 0 and _windowRole != Accessibility.ROLE_WINDOW:
                #    self.__menuItem = None
            # Implementation for menu item ends
            return

        # Implementation for spin button starts
        if event.source and _role == Accessibility.ROLE_SPIN_BUTTON and \
               (str (event.type).startswith ('object:text-changed:insert') or str (event.type).startswith ('object:text-changed:delete')):
            # if event.detail2 == 1 means entered the value through keyboard
            # if event.detail2 == 2 means mouse event
            # Clicked on spin button, either to increase or decrease value
            if event.detail2 == 2 and str (event.type).startswith ('object:text-changed:delete'):
                return
            _windowName = self.__windowName
            _windowHandle = self.appmap.getWindowHandle (event.source)
            if _windowHandle is not None:
                _windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
                _windowHandle.unref ()
            _objName = self.appmap.getObjRelNameAppmapFormat (event.source)
            _objValue = ''
            _text = event.source.queryInterface ("IDL:Accessibility/Text:1.0")
            try:
                _text = _text._narrow (Accessibility.Text)
            except:
                _text = None
            _objValue = None
            if _text:
                try:
                    _stateSet = event.source.getState ()
                    if _stateSet.contains (Accessibility.STATE_VISIBLE) and \
                       _stateSet.contains (Accessibility.STATE_EDITABLE) and \
                       _stateSet.contains (Accessibility.STATE_ENABLED):
                        _objValue = _text.getText (0, -1)
                    else:
                        return
                except AttributeError:
                    print traceback.print_exc ()
                    accessible = atspi.Accessible.makeAccessible (event.source)
                    if accessible and accessible.state.count (Accessibility.STATE_VISIBLE) and \
                           accessible.state.count (Accessibility.STATE_EDITABLE) and \
                           accessible.state.count (Accessibility.STATE_ENABLED):
                        _objValue = _text.getText (0, -1)
                        accessible.unref ()
                    else:
                        if accessible is not None:
                            accessible.unref ()
                        return
            self.completeComboOrTextOp ()
            if self.__pckt:
                _xml = self.__pckt.generatenotificationxml (_windowName, _objName, \
                                                          event.source.getRoleName (), \
                                                          str (event.type), self.timeElapsed (), \
                                                          data = _objValue)
                self.__pckt.sendpacket (_xml)
            if _ldtpDebug:
                print 'setvalue (\'' + _windowName + '\', \'' + _objName + '\', \'' + _objValue + '\')'
            # Implementation for spin button ends
            return

        # Implementation for text starts
        if event.source and (_role == Accessibility.ROLE_COMBO_BOX or _role == Accessibility.ROLE_TEXT) and \
               (str (event.type).startswith ('object:text-changed:insert') or str (event.type).startswith ('object:text-changed:delete')):
            self.__comboBoxName = None
            self.__comboBoxText = None
            _comboBoxName = None
            _parent = self.appmap.getParentOfRole (event.source, Accessibility.ROLE_COMBO_BOX)
            if _parent:
                _comboBoxName = self.appmap.getObjRelNameAppmapFormat (_parent)
                _parent.unref ()
            if _comboBoxName is None:
                self.__textName = self.appmap.getObjNameAppmapFormat (event.source)
            _objValue = ''
            _text = event.source.queryInterface ("IDL:Accessibility/Text:1.0")
            tmpChild = self.appmap.getChildOfRole (event.source, Accessibility.ROLE_TEXT)
            if tmpChild is not None:
                _text = tmpChild.queryInterface ("IDL:Accessibility/Text:1.0")
                try:
                    _text = _text._narrow (Accessibility.Text)
                except:
                    _text = None
                    print traceback.print_exc ()
                if _text:
                    _count = -1
                    if str (event.type).startswith ('object:text-changed:insert'):
                        _count = _text.characterCount
                    else: # object:text-changed:delete
                        _count = _text.characterCount - 1
                    _objValue = _text.getText (0, _count)
                tmpChild.unref ()
            else:
                return
            self.__comboBoxName = _comboBoxName
            if _comboBoxName is None:
                _objName = self.appmap.getObjRelNameAppmapFormat (event.source)
                if _objName is None:
                    self.appmap.hierarchy = ''
                    parent = self.appmap.getParentOfRole (event.source, Accessibility.ROLE_TEXT)
                    if parent is not None:
                        self.appmap.getParentHierarchyWithLabel (parent)
                        parent.unref ()
                    _objName = self.appmap.hierarchy
                self.__textName = _objName
            self.__comboBoxText = _objValue
            self.__comboTextType.set ()
            return
        if event.source and (_role == Accessibility.ROLE_COMBO_BOX or _role == Accessibility.ROLE_TEXT) and \
               (str (event.type).startswith ('object:state-changed:focused')): #and event.detail1 == 0:
            _windowname = self.__windowName
            _windowHandle = self.appmap.getWindowHandle (event.source)
            if _windowHandle is not None:
                _windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
                self.__windowName = _windowName
                _windowHandle.unref ()
            #if self.__textContent != '':
            #    _xml = self.__pckt.generatekeyboardxml (self.__textContent)
            #    self.__pckt.sendpacket (_xml)
            #    self.__textContent = ''
            # Assuming that any relevant text events will be captured over here
            # So, let us empty the typed string
            self.__textContent = ''
            if self.__comboBoxName and self.__comboBoxText and self.__comboTextType.isSet ():
                # FIXME: Should be modified to use comboselect when selected from list item
                self.settextvalue (_windowName, self.__comboBoxName, self.__comboBoxText, 'text', str (event.type))
                self.__comboBoxName = None
                self.__comboBoxText = None
                self.__comboTextType.clear ()
            elif self.__comboBoxText and self.__textType.isSet ():
                _objName = self.appmap.getObjRelNameAppmapFormat (event.source)
                if _objName is None:
                    self.appmap.hierarchy = ''
                    parent = self.appmap.getParentOfRole (event.source, Accessibility.ROLE_TEXT)
                    if parent is not None:
                        self.appmap.getParentHierarchyWithLabel (parent)
                        parent.unref ()
                    _objName = self.appmap.hierarchy
                    #_objInfo = self.appmap.getObjectInfo (event.source, '')
                    #_objName = _objInfo.prefix + str (_objInfo.instIndex)
                    #self.objectInst.reset ()
                #self.__textName = _objName
                self.settextvalue (_windowName, _objName, self.__comboBoxText, 'text', str (event.type))
                self.__comboBoxText = None
                self.__textType.clear ()
            return
        if event.source and _role == Accessibility.ROLE_TEXT and \
               (str (event.type).startswith ('object:state-changed:focused') or \
                str (event.type).startswith ('object:text-changed:insert') or \
                str (event.type).startswith ('object:text-changed:delete')): #and event.detail1 == 0:
            _windowName = self.__windowName
            if self.__textType.isSet () == False:
                return
            _windowHandle = self.appmap.getWindowHandle (event.source)
            if _windowHandle is not None:
                _localWindowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
                _windowHandle.unref ()
                _objName = self.appmap.getObjRelNameAppmapFormat (event.source)
                if _objName is None:
                    self.appmap.hierarchy = ''
                    parent = self.appmap.getParentOfRole (event.source, Accessibility.ROLE_TEXT)
                    if parent is not None:
                        self.appmap.getParentHierarchyWithLabel (parent)
                        parent.unref ()
                    _objName = self.appmap.hierarchy
            _objValue = None
            try:
                _text = event.source.queryInterface ("IDL:Accessibility/Text:1.0")
                _text = _text._narrow (Accessibility.Text)
            except:
                _text = None
            if _text:
                _objValue = _text.getText (0, -1)
            self.__textName = _objName
            self.__textItem = _objValue
            if _ldtpDebug:
                print 'settextvalue (\'' + _windowName + '\', \'' + _objName + '\', \'' + _objValue + '\')'
            if self.__pckt:
                _xml = self.__pckt.generatenotificationxml (_windowName, _objName, \
                                                          event.source.getRoleName (), \
                                                          str (event.type), self.timeElapsed (), \
                                                          data = _objValue)
                self.__pckt.sendpacket (_xml)
            # Implementation for text ends
            return
        if _ldtpDebug and _ldtpDebug == '3':
            pass
        else:
            return
        if event.source.name == '':
            if _ldtpDebug:
                print 'TEST RELATION', str (event.type), event.source.getRoleName (), \
                    self.appmap.getRelationName (event.source), event.detail1, event.detail2
        else:
            if _ldtpDebug:
                print 'TEST', str (event.type), event.detail1, event.detail2
        _windowHandle = self.appmap.getWindowHandle (event.source)
        if _windowHandle is not None:
            _windowName = self.appmap.getWinNameAppmapFormat (_windowHandle.name, _windowHandle.getRole ())
            if _ldtpDebug:
                print '_windowName', _windowName
            _windowHandle.unref ()

    def completeComboOrTextOp (self):
        if self.__comboBoxName and self.__comboBoxText and self.__comboTextType.isSet ():
            # Let us set comb box or text box value and then let us generate the code for push button
            self.settextvalue (self.__windowName, self.__comboBoxName, self.__comboBoxText, 'combo box', 'object:state-changed:focused')
            self.__comboBoxName = None
            self.__comboBoxText = None
            self.__comboTextType.clear ()
        elif self.__comboBoxText and self.__textName and self.__textType.isSet ():
            self.settextvalue (self.__windowName, self.__textName, self.__comboBoxText, 'text', 'object:state-changed:focused')
            self.__comboBoxText = None
            self.__textType.clear ()
        elif self.__textContent != '':
            _xml = self.__pckt.generatekeyboardxml (self.__textContent)
            self.__pckt.sendpacket (_xml)
            self.__textContent = ''
        if self.__tableCell != '':
            self.__tableCell = ''

    def settextvalue (self, windowName, objName, text, roleName, eventType):
        if _ldtpDebug:
            print 'settextvalue (\'' + windowName + '\', \'' + objName + '\', \'' + text + '\')', type (eventType), eventType
        if self.__pckt:
            _xml = self.__pckt.generatenotificationxml (windowName, objName, \
                                                      roleName, \
                                                      eventType, self.timeElapsed (), \
                                                      data = text)
            self.__pckt.sendpacket (_xml)

    def registerGlobalListener (self):
        eventTypes = []
        if _ldtpDebug and _ldtpDebug == '3': # To watch for list of events generated for diff events
            eventTypes = [
                "focus:",
                #"mouse:rel",
                "mouse:button",
                #"mouse:abs",
                #"keyboard:modifiers",
                #"object:property-change",
                #"object:property-change:accessible-name",
                #"object:property-change:accessible-description",
                #"object:property-change:accessible-parent",
                "object:state-changed",
                "object:state-changed:focused",
                "object:selection-changed",
                "object:children-changed"
                "object:active-descendant-changed"
                "object:visible-data-changed"
                "object:text-selection-changed",
                "object:text-caret-moved",
                "object:text-changed",
                "object:column-inserted",
                "object:row-inserted",
                "object:column-reordered",
                "object:row-reordered",
                "object:column-deleted",
                "object:row-deleted",
                "object:model-changed",
                "object:link-selected",
                #"object:bounds-changed",
                "window:minimize",
                "window:maximize",
                "window:restore",
                "window:activate",
                "window:create",
                "window:deactivate",
                "window:close",
                "window:lower",
                "window:raise",
                "window:resize",
                "window:shade",
                "window:unshade",
                "object:property-change:accessible-table-summary",
                "object:property-change:accessible-table-row-header",
                "object:property-change:accessible-table-column-header",
                "object:property-change:accessible-table-summary",
                "object:property-change:accessible-table-row-description",
                "object:property-change:accessible-table-column-description",
                "object:test",
                "window:restyle",
                "window:desktop-create",
                "window:desktop-destroy"
                ]
        else:
            eventTypes = [
                'mouse:button:1r', # Mouse left click
                'mouse:button:2r', # Mouse center click
                'mouse:button:3r', # Mouse right click
                'object:state-changed:checked', # Check box, Toggle button, Radio button
                'object:state-changed:focused', # Combobox menuitem, Combobox listitem, Combobox text, Text
                'object:state-changed:armed', # Push button
                'focus:', # Push button, Combobox listitem
                'object:text-changed', # Spin button, Text
                'object:state-changed:selected' # Table cell, Combobox menuitem, Menuitem, Check menuitem, Radio menuitem
            ]
        for eventType in eventTypes:
            self.registry.registerEventListener (self.globalListenerCallback, eventType)

    def registerNotifyKeystroke (self):
        try:
            self.registry.registerKeystrokeListener (self.notifyKeystroke)
        except AttributeError:
            self.registry.registerKeystrokeListeners (self.notifyKeystroke)

# Global functions / variables

# To start the recording, just call this function once
def start (pckt = None):
    global recorder
    recorder = record (pckt)
    recorder.registerWindowListener ()
    recorder.registerNameChangeListener ()
    recorder.registerGlobalListener ()
    recorder.registerNotifyKeystroke ()

    try:
        recorder.start ()
    except KeyboardInterrupt:
        stop ()
        raise
    except:
        print traceback.print_exc ()
        stop ()

# To stop recording, just call this function once
def stop ():
    __shutdownAndExit (None, None)

recorder = None
# If this file is directly called like
# $ python ldtprecorder.py
if __name__ == "__main__":
    signal.signal (signal.SIGINT, __shutdownAndExit)
    signal.signal (signal.SIGQUIT, __shutdownAndExit)
    start ()
