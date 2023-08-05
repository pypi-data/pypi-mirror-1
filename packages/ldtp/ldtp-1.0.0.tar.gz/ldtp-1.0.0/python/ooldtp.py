#############################################################################
#
#  Linux Desktop Testing Project http://ldtp.freedesktop.org
# 
#  Author:
#     Nagappan A <nagappan@gmail.com>
# 
#  Copyright 2008 Nagappan Alagappan
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

__author__ = "Nagappan A <nagappan@gmail.com>"
__maintainer__ = "Nagappan A <nagappan@gmail.com>"
__version__ = "1.0.0"

import ldtp

state = ldtp.state

class component:
   def __init__ (self, window, name = '', role = ''):
      self.__window = window
      self.__name = name
      self.role = role

      if name != '' and role == '':
            self.role = ldtp.getobjectproperty (window, name, 'class')
      try:
         self.label = ldtp.getobjectproperty (window, self.getName (name), 'label_by')
      except ldtp.LdtpExecutionError:
         try:
            self.label = ldtp.getobjectproperty (window, self.getName (name), 'label')
         except ldtp.LdtpExecutionError:
            self.label = ''

   def getName (self, name = '', must = True):
      if name != '':
         return name
      elif self.__name != '':
         return self.__name
      else:
         if must == False:
            return ''
         raise ldtp.LdtpExecutionError ('Object \'name\' argument required')

   def waittillguiexist (self, name = '', guiTimeOut = None):
      return ldtp.waittillguiexist (self.__window, self.getName (name, False), guiTimeOut)

   def waittillguinotexist (self, name = '', guiTimeOut = None):
      return ldtp.waittillguinotexist (self.__window, self.getName (name, False), guiTimeOut)

   def hasstate (self, name = '', checkState = state.INVALID):
      return ldtp.hasstate (self.__window, self.getName (name), checkState)

   def getobjectinfo (self, name = ''):
      return ldtp.getobjectinfo (self.__window, self.getName (name))

   # Common (button, check menu, radio menu)

   def click (self, name = ''):
      return ldtp.click (self.__window, self.getName (name))

   # push button

   def stateenabled (self, name = ''):
      return ldtp.stateenabled (self.__window, self.getName (name))

   def verifypushbutton (self, name = ''):
      return ldtp.verifypushbutton (self.__window, self.getName (name))

   # toolbar

   def verifybuttoncount (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.verifybuttoncount (self.__window, self.getName (''), args [0])
      else:
         return ldtp.verifybuttoncount (self.__window, args [0], args [1])

   def verifyvisiblebuttoncount (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.verifyvisiblebuttoncount (self.__window, self.getName (''), args [0])
      else:
         return ldtp.verifyvisiblebuttoncount (self.__window, args [0], args [1])

   # toggle button

   def press (self, name = ''):
      return ldtp.press (self.__window, self.getName (name))

   def verifytoggled (self, name = ''):
      return ldtp.verifytoggled (self.__window, self.getName (name))

   # check box

   def check (self, name = ''):
      return ldtp.check (self.__window, self.getName (name))

   def uncheck (self, name = ''):
      return ldtp.uncheck (self.__window, self.getName (name))

   def verifycheck (self, name = ''):
      return ldtp.verifycheck (self.__window, self.getName (name))

   def verifyuncheck (self, name = ''):
      return ldtp.verifyuncheck (self.__window, self.getName (name))

   # Menu

   def doesmenuitemexist (self, name = ''):
      return ldtp.doesmenuitemexist (self.__window, self.getName (name))

   def menucheck (self, name = ''):
      return ldtp.menucheck (self.__window, self.getName (name))

   def menuuncheck (self, name = ''):
      return ldtp.menuuncheck (self.__window, self.getName (name))

   def verifymenucheck (self, name = ''):
      return ldtp.verifymenucheck (self.__window, self.getName (name))

   def verifymenuuncheck (self, name = ''):
      return ldtp.verifymenuuncheck (self.__window, self.getName (name))

   def selectmenuitem (self, name = ''):
      return ldtp.selectmenuitem (self.__window, self.getName (name))

   def listsubmenus (self, name = ''):
      return ldtp.listsubmenus (self.__window, self.getName (name))

   def invokemenu (self, name = ''):
      return ldtp.invokemenu (self.__window, self.getName (name))

   # Calendar

   def selectcalendardate (self, *args):
      if len (args) < 3:
         raise ldtp.LdtpExecutionError ('3 arguments required (day, month, year)')
      if len (args) == 3:
         return ldtp.selectcalendardate (self.__window, self.getName (''), args [0], args [1], args [2])
      else:
         return ldtp.selectcalendardate (self.__window, args [0], args [1], args [2], args [3])

   def selectevent (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selectevent (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selectevent (self.__window, args [0], args [1])

   def selecteventindex (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selecteventindex (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selecteventindex (self.__window, args [0], args [1])

   def verifyeventexist (self, name = ''):
      return ldtp.verifyeventexist (self.__window, self.getName (name))

   # Text

   def activatetext (self, name = ''):
      return ldtp.activatetext (self.__window, self.getName (name))

   def appendtext (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.appendtext (self.__window, self.getName (''), args [0])
      else:
         return ldtp.appendtext (self.__window, args [0], args [1])

   def comparetextproperty (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      name = self.__name
      textProperty  = ''
      startPosition = None
      endPosition   = None

      if len (args) >= 2:
         if isinstance (args [1], str):
            textProperty = args [1]
            name = args [0]
            if len (args) >= 3:
               startPosition = args [2]
            if len (args) >= 4:
               endPosition = args [3]
         else:
            name = self.getName ('')
            textProperty = args [0]
            if len (args) >= 2:
               startPosition = args [1]
            if len (args) >= 3:
               endPosition = args [2]

      if name == '':
         raise ldtp.LdtpExecutionError ('Component name is required')

      return ldtp.comparetextproperty (self.__window, name, textProperty, startPosition, endPosition)

   def containstextproperty (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      name = self.__name
      textProperty  = ''
      startPosition = None
      endPosition   = None

      if len (args) >= 2:
         if isinstance (args [1], str):
            textProperty = args [1]
            name = args [0]
            if len (args) >= 3:
               startPosition = args [2]
            if len (args) >= 4:
               endPosition = args [3]
         else:
            name = self.getName ('')
            textProperty = args [0]
            if len (args) >= 2:
               startPosition = args [1]
            if len (args) >= 3:
               endPosition = args [2]

      if name == '':
         raise ldtp.LdtpExecutionError ('Component name is required')

      return ldtp.containstextproperty (self.__window, name, textProperty, startPosition, endPosition)

   def copytext (self, *args):
      if len (args) < 2:
         raise ldtp.LdtpExecutionError ('Min 2 arguments required')
      if len (args) == 2:
         return ldtp.copytext (self.__window, self.getName (''), args [0], args [1])
      else:
         return ldtp.copytext (self.__window, args [0], args [1], args [2])

   def cuttext (self, *args):
      if len (args) < 2:
         raise ldtp.LdtpExecutionError ('Min 2 arguments required')
      if len (args) == 2:
         return ldtp.cuttext (self.__window, self.getName (''), args [0], args [1])
      else:
         return ldtp.cuttext (self.__window, args [0], args [1], args [2])

   def deletetext (self, *args):
      if len (args) < 2:
         raise ldtp.LdtpExecutionError ('Min 2 arguments required')
      if len (args) == 2:
         return ldtp.deletetext (self.__window, self.getName (''), args [0], args [1])
      else:
         return ldtp.deletetext (self.__window, args [0], args [1], args [2])

   def enterstring (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.enterstring (self.__window, self.getName (''), args [0])
      else:
         return ldtp.enterstring (self.__window, args [0], args [1])

   def getcharcount (self, name = ''):
      return ldtp.getcharcount (self.__window, self.getName (name))

   def getcursorposition (self, name = ''):
      return ldtp.getcursorposition (self.__window, self.getName (name))

   def gettextproperty (self, *args):
      name = self.__name
      startPosition = None
      endPosition   = None
      length = len (args)

      if length >= 1:
         if isinstance (args [0], str):
            name = args [0]
            if length >= 2:
               startPosition = args [1]
            if length >= 3:
               endPosition = args [2]
         else:
            if length >= 1:
               startPosition = args [0]
            if length >= 2:
               endPosition = args [1]

      if name == '':
         raise ldtp.LdtpExecutionError ('Component name is required')

      return ldtp.gettextproperty (self.__window, name, startPosition, endPosition)

   def gettextvalue (self, *args):
      length = len (args)
      if length < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      name = self.__name
      textProperty  = ''
      startPosition = None
      endPosition   = None

      if length >= 2:
         if isinstance (args [1], str):
            textProperty = args [1]
            name = args [0]
            if length >= 3:
               startPosition = args [2]
            if length >= 4:
               endPosition = args [3]
         else:
            name = self.getName ('')
            textProperty = args [0]
            if length >= 2:
               startPosition = args [1]
            if length >= 3:
               endPosition = args [2]

      if name == '':
         raise ldtp.LdtpExecutionError ('Component name is required')

      return ldtp.gettextvalue (self.__window, name, textProperty, startPosition, endPosition)

   def grabfocus (self, name = ''):
      return ldtp.grabfocus (self.__window, self.getName (name))

   def inserttext (self, *args):
      if len (args) < 2:
         raise ldtp.LdtpExecutionError ('Min 2 arguments required')
      name = self.__name
      text  = ''
      position = None

      if len (args) > 2:
            name = args [0]
            position = args [1]
            text = args [2]
      else:
            position = args [0]
            text = args [1]

      if name == '':
         raise ldtp.LdtpExecutionError ('Component name is required')

      return ldtp.inserttext (self.__window, name, position, text)

   def istextstateenabled (self, name = ''):
      return ldtp.istextstateenabled (self.__window, self.getName (name))

   def mouseleftclick (self, name = ''):
      return ldtp.mouseleftclick (self.__window, self.getName (name))

   def mouserightclick (self, name = ''):
      return ldtp.mouserightclick (self.__window, self.getName (name))

   def mousemove (self, name = ''):
      return ldtp.mousemove (self.__window, self.getName (name))

   def pastetext (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.pastetext (self.__window, self.getName (''), args [0])
      else:
         return ldtp.pastetext (self.__window, args [0], args [1])

   def rightclick (self, *args):
      length = len (args)
      if length < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      name = self.__name
      if length == 3:
         return ldtp.rightclick (self.__window, args [0], args [1], args [2])
      elif length == 2 and name != '':
         return ldtp.rightclick (self.__window, name, args [0], args [1])
      elif length == 1 and name != '':
         return ldtp.rightclick (self.__window, name, args [0])
      elif length == 2:
         return ldtp.rightclick (self.__window, args [0], args [1])
      else:
         raise ldtp.LdtpExecutionError ('Mismatch arguments')

   def selecttextbyindexandregion (self, *args):
      length = len (args)
      if length < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      name = self.__name
      textProperty  = ''
      startPosition = None
      endPosition   = None
      selectionNo   = None

      if length >= 2:
         if isinstance (args [1], str):
            textProperty = args [1]
            name = args [0]
            if length >= 3:
               startPosition = args [2]
            if length >= 4:
               endPosition = args [3]
            if length >= 5:
               selectionNo = args [4]
         else:
            name = self.getName ('')
            textProperty = args [0]
            if length >= 2:
               startPosition = args [1]
            if length >= 3:
               endPosition = args [2]
            if length >= 4:
               selectionNo = args [3]

      if name == '':
         raise ldtp.LdtpExecutionError ('Component name is required')

      return ldtp.selecttextbyindexandregion (self.__window, name, textProperty, startPosition, endPosition)

   def selecttextbyname (self, name = ''):
      return ldtp.selecttextbyname (self.__window, self.getName (name))

   def setcursorposition (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.setcursorposition (self.__window, self.getName (''), args [0])
      else:
         return ldtp.setcursorposition (self.__window, args [0], args [1])

   def settextvalue (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.settextvalue (self.__window, self.getName (''), args [0])
      else:
         return ldtp.settextvalue (self.__window, args [0], args [1])

   def verifypartialmatch (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.verifypartialmatch (self.__window, self.getName (''), args [0])
      else:
         return ldtp.verifypartialmatch (self.__window, args [0], args [1])

   def verifysettext (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.verifysettext (self.__window, self.getName (''), args [0])
      else:
         return ldtp.verifysettext (self.__window, args [0], args [1])

   # Combo box
   def capturetofile (self, *args):
      length = len (args)
      if length == 1 and self.__name != '':
         return ldtp.capturetofile (self.__window, self.getName (''), args [0])
      elif length == 1 and self.__name == '':
         return ldtp.capturetofile (self.__window, args [0])
      else:
         if length < 2:
            raise ldtp.LdtpExecutionError ('Min 1 argument required')
         return ldtp.capturetofile (self.__window, args [0], args [1])

   def comboselect (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.comboselect (self.__window, self.getName (''), args [0])
      else:
         return ldtp.comboselect (self.__window, args [0], args [1])

   def hidelist (self, name = ''):
      return ldtp.hidelist (self.__window, self.getName (name))

   def selectindex (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selectindex (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selectindex (self.__window, args [0], args [1])

   def showlist (self, name = ''):
      return ldtp.showlist (self.__window, self.getName (name))

   def verifydropdown (self, name = ''):
      return ldtp.verifydropdown (self.__window, self.getName (name))

   def verfyhidelist (self, name = ''):
      return ldtp.verfyhidelist (self.__window, self.getName (name))

   def verifyselect (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.verifyselect (self.__window, self.getName (''), args [0])
      else:
         return ldtp.verifyselect (self.__window, args [0], args [1])

   def verifysettext (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.verifysettext (self.__window, self.getName (''), args [0])
      else:
         return ldtp.verifysettext (self.__window, args [0], args [1])

   def verifyshowlist (self, name = ''):
      return ldtp.verifyshowlist (self.__window, self.getName (name))

   # status bar

   def getstatusbartext (self, name = ''):
      return ldtp.getstatusbartext (self.__window, self.getName (name))

   def verifystatusbar (self, name = ''):
      return ldtp.verifystatusbar (self.__window, self.getName (name))

   def verifystatusbarvisible (self, name = ''):
      return ldtp.verifystatusbarvisible (self.__window, self.getName (name))

   # spin button

   def getvalue (self, name = ''):
      return ldtp.getvalue (self.__window, self.getName (name))

   def setvalue (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.setvalue (self.__window, self.getName (''), args [0])
      else:
         return ldtp.setvalue (self.__window, args [0], args [1])

   def verifysetvalue (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.verifysetvalue (self.__window, self.getName (''), args [0])
      else:
         return ldtp.verifysetvalue (self.__window, args [0], args [1])

   # slider

   def decrease (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.decrease (self.__window, self.getName (''), args [0])
      else:
         return ldtp.decrease (self.__window, args [0], args [1])

   def increase (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.increase (self.__window, self.getName (''), args [0])
      else:
         return ldtp.increase (self.__window, args [0], args [1])

   def setmax (self, name = ''):
      return ldtp.setmax (self.__window, self.getName (name))

   def setmin (self, name = ''):
      return ldtp.setmin (self.__window, self.getName (name))

   def verifyslider (self, name = ''):
      return ldtp.verifyslider (self.__window, self.getName (name))

   def verifysliderhorizontal (self, name = ''):
      return ldtp.verifysliderhorizontal (self.__window, self.getName (name))

   def verifyslidervertical (self, name = ''):
      return ldtp.verifyslidervertical (self.__window, self.getName (name))

   # scroll bar

   def onedown (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.onedown (self.__window, self.getName (''), args [0])
      else:
         return ldtp.onedown (self.__window, args [0], args [1])

   def oneleft (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.oneleft (self.__window, self.getName (''), args [0])
      else:
         return ldtp.oneleft (self.__window, args [0], args [1])

   def oneright (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.oneright (self.__window, self.getName (''), args [0])
      else:
         return ldtp.oneright (self.__window, args [0], args [1])

   def oneup (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.oneup (self.__window, self.getName (''), args [0])
      else:
         return ldtp.oneup (self.__window, args [0], args [1])

   def scrolldown (self, name = ''):
      return ldtp.scrolldown (self.__window, self.getName (name))

   def scrolleft (self, name = ''):
      return ldtp.scrolleft (self.__window, self.getName (name))

   def scrollright (self, name = ''):
      return ldtp.scrollright (self.__window, self.getName (name))

   def scrollup (self, name = ''):
      return ldtp.scrollup (self.__window, self.getName (name))

   def verifyscrollbar (self, name = ''):
      return ldtp.verifyscrollbar (self.__window, self.getName (name))

   def verifyscrollbarhorizontal (self, name = ''):
      return ldtp.verifyscrollbarhorizontal (self.__window, self.getName (name))

   def verifyscrollbarvertical (self, name = ''):
      return ldtp.verifyscrollbarvertical (self.__window, self.getName (name))

   # panel

   def getpanelchildcount (self, name = ''):
      return ldtp.getpanelchildcount (self.__window, self.getName (name))

   def selectpanel (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selectpanel (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selectpanel (self.__window, args [0], args [1])

   def selectpanelname (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selectpanelname (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selectpanelname (self.__window, args [0], args [1])

   # page tab list

   def gettabcount (self, name = ''):
      return ldtp.gettabcount (self.__window, self.getName (name))

   def selecttab (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selecttab (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selecttab (self.__window, args [0], args [1])

   def selecttabindex (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selecttabindex (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selecttabindex (self.__window, args [0], args [1])

   # list

   def selectitem (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selectitem (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selectitem (self.__window, args [0], args [1])

   def selectindex (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selectindex (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selectindex (self.__window, args [0], args [1])

   # label

   def getlabel (self, name = ''):
      return ldtp.getlabel (self.__window, self.getName (name))

   def getlabelatindex (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.getlabelatindex (self.__window, self.getName (''), args [0])
      else:
         return ldtp.getlabelatindex (self.__window, args [0], args [1])

   def selectlabelspanelbyname (self, name = ''):
      return ldtp.selectlabelspanelbyname (self.__window, self.getName (name))

   # embedded component

   def invokemenu (self, name = ''):
      return ldtp.invokemenu (self.__window, self.getName (name))

   # Table / Tree table

   def checkrow (self, *args):
      length = len (args)
      if length < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      name = self.__name
      if length == 3:
         return ldtp.checkrow (self.__window, args [0], args [1], args [2])
      elif length == 2 and isinstance (args [0], int):
         return ldtp.checkrow (self.__window, name, args [0], args [1])
      elif length == 1 and name != '':
         return ldtp.checkrow (self.__window, name, args [0])
      elif length == 2 and isinstance (args [0], str):
         return ldtp.checkrow (self.__window, args [0], args [1])
      else:
         raise ldtp.LdtpExecutionError ('Mismatch arguments')

   def doesrowexist (self, *args):
      length = len (args)
      if length < 2:
         raise ldtp.LdtpExecutionError ('Min 2 arguments required')
      name = self.__name
      if length == 3:
         return ldtp.doesrowexist (self.__window, args [0], args [1], args [2])
      elif length == 2:
         return ldtp.doesrowexist (self.__window, name, args [0], args [1])
      else:
         raise ldtp.LdtpExecutionError ('Mismatch arguments')

   def doubleclickrow (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.doubleclickrow (self.__window, self.getName (''), args [0])
      else:
         return ldtp.doubleclickrow (self.__window, args [0], args [1])

   def expandtablecell (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.expandtablecell (self.__window, self.getName (''), args [0])
      else:
         return ldtp.expandtablecell (self.__window, args [0], args [1])

   def getcellvalue (self, *args):
      length = len (args)
      if length < 2:
         raise ldtp.LdtpExecutionError ('Min 2 arguments required')
      name = self.__name
      if length == 3:
         return ldtp.getcellvalue (self.__window, args [0], args [1], args [2])
      elif length == 2:
         return ldtp.getcellvalue (self.__window, name, args [0], args [1])
      else:
         raise ldtp.LdtpExecutionError ('Mismatch arguments')

   def getrowcount (self, name = ''):
      return ldtp.getrowcount (self.__window, self.getName (name))

   def gettablerowindex (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.gettablerowindex (self.__window, self.getName (''), args [0])
      else:
         return ldtp.gettablerowindex (self.__window, args [0], args [1])

   def gettreetablerowindex (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.gettreetablerowindex (self.__window, self.getName (''), args [0])
      else:
         return ldtp.gettreetablerowindex (self.__window, args [0], args [1])

   def selectlastrow (self, name = ''):
      return ldtp.selectlastrow (self.__window, self.getName (name))

   def selectrow (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selectrow (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selectrow (self.__window, args [0], args [1])

   def selectrowindex (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selectrowindex (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selectrowindex (self.__window, args [0], args [1])

   def selectrowpartialmatch (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.selectrowpartialmatch (self.__window, self.getName (''), args [0])
      else:
         return ldtp.selectrowpartialmatch (self.__window, args [0], args [1])

   def setcellvalue (self, *args):
      length = len (args)
      if length < 3:
         raise ldtp.LdtpExecutionError ('Min 3 arguments required')
      name = self.__name
      if length == 4:
         return ldtp.setcellvalue (self.__window, args [0], args [1], args [2], args [3])
      elif length == 3:
         return ldtp.setcellvalue (self.__window, name, args [0], args [1], args [2])
      else:
         raise ldtp.LdtpExecutionError ('Mismatch arguments')

   def singleclickrow (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.singleclickrow (self.__window, self.getName (''), args [0])
      else:
         return ldtp.singleclickrow (self.__window, args [0], args [1])

   def sortcolumn (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.sortcolumn (self.__window, self.getName (''), args [0])
      else:
         return ldtp.sortcolumn (self.__window, args [0], args [1])

   def sortcolumnindex (self, *args):
      if len (args) < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      if len (args) == 1:
         return ldtp.sortcolumnindex (self.__window, self.getName (''), args [0])
      else:
         return ldtp.sortcolumnindex (self.__window, args [0], args [1])

   def uncheckrow (self, *args):
      length = len (args)
      if length < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      name = self.__name
      if length == 3:
         return ldtp.uncheckrow (self.__window, args [0], args [1], args [2])
      elif length == 2 and isinstance (args [0], int):
         return ldtp.uncheckrow (self.__window, name, args [0], args [1])
      elif length == 1 and name != '':
         return ldtp.uncheckrow (self.__window, name, args [0])
      elif length == 2 and isinstance (args [0], str):
         return ldtp.uncheckrow (self.__window, args [0], args [1])
      else:
         raise ldtp.LdtpExecutionError ('Mismatch arguments')

   def verifycheckrow (self, *args):
      length = len (args)
      if length < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      name = self.__name
      if length == 3:
         return ldtp.verifycheckrow (self.__window, args [0], args [1], args [2])
      elif length == 2 and isinstance (args [0], int):
         return ldtp.verifycheckrow (self.__window, name, args [0], args [1])
      elif length == 1 and name != '':
         return ldtp.verifycheckrow (self.__window, name, args [0])
      elif length == 2 and isinstance (args [0], str):
         return ldtp.verifycheckrow (self.__window, args [0], args [1])
      else:
         raise ldtp.LdtpExecutionError ('Mismatch arguments')

   def verifytablecell (self, *args):
      length = len (args)
      if length < 3:
         raise ldtp.LdtpExecutionError ('Min 3 arguments required')
      name = self.__name
      if length == 4:
         return ldtp.verifytablecell (self.__window, args [0], args [1], args [2], args [3])
      elif length == 3:
         return ldtp.verifytablecell (self.__window, name, args [0], args [1], args [2])
      else:
         raise ldtp.LdtpExecutionError ('Mismatch arguments')

   def verifypartialtablecell (self, *args):
      length = len (args)
      if length < 3:
         raise ldtp.LdtpExecutionError ('Min 3 arguments required')
      name = self.__name
      if length == 4:
         return ldtp.verifypartialtablecell (self.__window, args [0], args [1], args [2], args [3])
      elif length == 3:
         return ldtp.verifypartialtablecell (self.__window, name, args [0], args [1], args [2])
      else:
         raise ldtp.LdtpExecutionError ('Mismatch arguments')

   def verifyuncheckrow (self, *args):
      length = len (args)
      if length < 1:
         raise ldtp.LdtpExecutionError ('Min 1 argument required')
      name = self.__name
      if length == 3:
         return ldtp.verifyuncheckrow (self.__window, args [0], args [1], args [2])
      elif length == 2 and isinstance (args [0], int):
         return ldtp.verifyuncheckrow (self.__window, name, args [0], args [1])
      elif length == 1 and name != '':
         return ldtp.verifyuncheckrow (self.__window, name, args [0])
      elif length == 2 and isinstance (args [0], str):
         return ldtp.verifyuncheckrow (self.__window, args [0], args [1])
      else:
         raise ldtp.LdtpExecutionError ('Mismatch arguments')

class context (component):
   def __init__ (self, window) :
      component.__init__ (self, window)
      self.__window = window
      # self.component = component (window)

   def getchild (self, name = '', role = ''):
      if name == '' and role == '':
         raise ldtp.LdtpExecutionError ('Atleast one argument should be provided <object name> or <role name>')
      if role != '':
         childList = ldtp.getchild (self.__window, name, role)
         componentList = []
         for i in childList:
            componentList.append (component (self.__window, i, role))
         return componentList
      else:
         return component (self.__window, name)

   def onwidnowcreate (self, cbFunction):
      return ldtp.onwidnowcreate (self.__window, cbFunction)

   def guiexist (self):
      return ldtp.guiexist (self.__window)

   def getobjectlist (self):
      return ldtp.getobjectlist (self.__window)
