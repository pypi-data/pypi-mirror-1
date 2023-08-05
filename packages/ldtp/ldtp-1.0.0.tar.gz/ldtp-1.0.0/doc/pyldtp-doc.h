/*
 * Linux Desktop Testing Project http://ldtp.freedesktop.org/
 *
 * Author
 *    Nagappan A <nagappan@gmail.com>
 *    Premkumar J <prem.jothimani@gmail.com>
 *
 * Copyright 2004 - 2007 Novell, Inc.
 * Copyright 2008 Nagappan Alagappan
 *
 * Permission is granted to copy, distribute and/or modify this document
 * under the terms of the GNU Lesser General Public License, Version 2
 * or any later version published by the Free Software Foundation;
 * with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
 * A copy of the license is included in the section entitled "GNU
 * Lesser General Public License".
 *
 * You should have received a copy of the GNU GNU Lesser General Public
 * License along with this documentation; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

/** \mainpage LDTP User manual
 *
 * \section AboutLDTP About LDTP
 *
 * Linux Desktop Testing Project (LDTP) is aimed at producing high
 * quality test automation framework and cutting-edge tools that can
 * be used to test Linux Desktop and improve it. It uses the
 * Accessibility libraries to poke through the application's user
 * interface. The framework also has tools to record test-cases based
 * on user-selection on the application. For more information check
 * our site - http://ldtp.freedesktop.org
 *
 * \section scriptwritter Components list
 *
 * <TABLE align=left border=0 cellpadding=10 cellspacing=0>
 * <TR>
 * <TD>
 * \subpage calendar
 * </TD>
 * <TD>
 * \subpage calendarview
 * </TD>
 * <TD>
 * \subpage checkbox
 * </TD>
 * <TD>
 * \subpage checkmenuitem
 * </TD>
 * <TD>
 * \subpage combobox
 * </TD>
 * <TD>
 * \subpage embeddedcomponent
 * </TD>
 * </TR>
 * <TR>
 * <TD>
 * \subpage general
 * </TD>
 * <TD>
 * \subpage imaging
 * </TD>
 * <TD>
 * \subpage icon
 * </TD>
 * <TD>
 * \subpage label
 * </TD>
 * <TD>
 * \subpage layeredpane
 * </TD>
 * <TD>
 * \subpage list
 * </TD>
 * </TR>
 * <TR>
 * <TD>
 * \subpage logging
 * </TD>
 * <TD>
 * \subpage menuitem
 * </TD>
 * <TD>
 * \subpage pagetablist
 * </TD>
 * <TD>
 * \subpage panel
 * </TD>
 * <TD>
 * \subpage ProcessStatistics
 * </TD>
 * <TD>
 * \subpage pushbutton
 * </TD>
 * </TR>
 * <TR>
 * <TD>
 * \subpage radiobutton
 * </TD>
 * <TD>
 * \subpage radiomenuitem
 * </TD>
 * <TD>
 * \subpage scrollbar
 * </TD>
 * <TD>
 * \subpage slider
 * </TD>
 * <TD>
 * \subpage spinbutton
 * </TD>
 * <TD>
 * \subpage statusbar
 * </TD>
 * </TR>
 * <TR>
 * <TD>
 * \subpage table
 * </TD>
 * <TD>
 * \subpage text
 * </TD>
 * <TD>
 * \subpage togglebutton
 * </TD>
 * <TD>
 * \subpage toolbar
 * </TD>
 * <TD>
 * \subpage treetable
 * </TD>
 * <TD>
 * \subpage Window
 * </TD>
 * </TR>
 * <TR>
 * <TD>
 * \subpage LTFX
 * </TD>
 * </TR>
 * </TABLE>
 *
 * <a><img HEIGHT="30" src="../ldtp-logo-small.png" style="float:center;center:0px;top:0px;position:absolute;" alt="Linux Desktop Testing Project"/></a>
 *
 */

/** \page calendar calendar
 * \section CalendarSection About Calendar functions
 *
 * To operate on a calendar object and based on your requirement, you can use any of these functions
 *
 * \section CalendarAPI Calendar python API's
 * \subpage selectcalendardate - Select the given date in a calendar object
 *
 */

/** \page calendarview calendarview
 * \section CalendarViewSection About Calendar view functions
 *
 * To operate on a calendar view object and based on your requirement, you can use any of these functions
 *
 * \section CalendarViewAPI Calendar View python API's
 * \subpage enterstring - Generate keyboard events as if the user
 * types manually
 * \n
 * \n
 * \subpage selectevent - Select the calendar event based on event name
 * \n
 * \n
 * \subpage selecteventindex - Select the calendar event based on event index
 * \n
 * \n
 * \subpage verifyeventexist - Verify whether the calendar event exist
 * or not
 *
 */

/** \page checkbox checkbox
 * \section CheckboxSection About Checkbox functions
 *
 * To operate on a check box object and based on your requirement, you can use any of these functions
 *
 * \section CheckboxAPI Checkbox python API's
 *
 * \subpage check - Tick the check box
 * \n
 * \n
 * \subpage click - Click on the check box
 * \n
 * \n
 * \subpage uncheck - Un tick the check box
 * \n
 * \n
 * \subpage verifycheck - Verify whether the check box is ticked
 * \n
 * \n
 * \subpage verifyuncheck - Verify whether the check box is unticked
 *
 */

/** \page checkmenuitem checkmenuitem
 * \section CheckmenuitemSection About Checkmenuitem functions
 *
 * To operate on a check menuitem object and based on your requirement, you can use any of these functions
 *
 * \section CheckmenuitemAPI Checkmenuitem python API's
 *
 * \subpage click - Click on the check menu item
 * \n
 * \n
 * \subpage menucheck - Tick the menu item
 * \n
 * \n
 * \subpage menuuncheck - Un tick the menu item
 * \n
 * \n
 * \subpage selectmenuitem - Select the menu item
 * \n
 * \n
 * \subpage verifymenucheck - Verify whether the check menu item is ticked
 * \n
 * \n
 * \subpage verifymenuuncheck - Verify whether the check menu item is unticked
 *
 */

/** \page combobox combobox
 * \section ComboboxSection About Combobox functions
 *
 * To operate on a combobox object and based on your requirement, you can use any of these functions
 *
 * \section ComboboxAPI Combobox python API's
 *
 * \subpage capturetofile - Get the entires of list box and dump it to
 * a file
 * \n
 * \n
 * \subpage click - Click on a combo box
 * \n
 * \n
 * \subpage comboselect - Select an item from the combo box list or
 * menu item
 * \n
 * \n
 * \subpage hidelist - Hide the combo box drop down list
 * \n
 * \n
 * \subpage selectindex - Select combo box item based on index
 * \n
 * \n
 * \subpage settextvalue - Set a text in the combo box list
 * \n
 * \n
 * \subpage showlist - Show the combo box drop down list
 * \n
 * \n
 * \subpage verifydropdown - Verify whether the drop down list pops up
 * \n
 * \n
 * \subpage verifyhidelist - Verify whether the drop down list is in
 * hidden state
 * \n
 * \n
 * \subpage verifyselect - Verify whether the item is selected in the
 * combo box list
 * \n
 * \n
 * \subpage verifysettext - Verify whether the text set is available
 * \n
 * \n
 * \subpage verifyshowlist - Verify whether the drop down list is
 * displayed
 *
 */

/** \page general general
 * \section GeneralSection About General functions
 *
 * General ldtp functions. Based on your requirement, you can use any of these functions
 *
 * \section GeneralAPI General python API's
 *
 * \subpage generatekeyevent - Generate keyboard event on currently
 * focused window
 * \n
 * \n
 * \subpage generatemouseevent - Generate mouse event based on x, y coordinates
 * \n
 * \n
 * \subpage hasstate - Checks whether the object has a state
 * \n
 * \n
 * \subpage initappmap - Initialize application map
 * \n
 * \n
 * \subpage launchapp - Launch application
 * \n
 * \n
 * \subpage reinitldtp - Reinitialize LDTP
 * \n
 * \n
 * \subpage releasecontext - Release the context information
 * \n
 * \n
 * \subpage remap - Force remap the window information
 * \n
 * \n
 * \subpage setcontext - Set the context information
 * \n
 * \n
 * \subpage wait - Suspend the operation for specified duration
 *
 */

/** \page imaging imaging
 * \section ImagingSection About Imaging functions
 *
 * To manipulate with image processing and based on your requirement, you can use any of these functions
 *
 * \section ImagingAPI Imaging python API's
 *
 * \subpage blackoutregion - Black out the specified region in the image
 * \n
 * \n
 * \subpage imagecapture - Capture the screen shot of a window
 * \n
 * \n
 * \subpage imagecompare - Compare two images
 *
 */

/** \page label label
 * \section LabelSection About Label functions
 *
 * To operate on a label object and based on your requirement, you can use any of these functions
 *
 * \section LabelAPI Label python API's
 *
 * \subpage getlabel - Get label of an object
 * \n
 * \n
 * \subpage getlabelatindex - Get label at the specified index in a window
 * \n
 * \n
 * \subpage selectlabelspanelbyname - Select the labels based on panel name
 *
 */

/** \page layeredpane layeredpane
 * \section LayeredpaneSection About Layeredpane functions
 *
 * To operate on a layered pane object and based on your requirement, you can use any of these functions
 *
 * \section LayeredpaneAPI Layeredpane python API's
 *
 * \subpage rightclick - Generate right click event
 * \n
 * \n
 * \subpage selectitem - Select an item
 *
 */

/** \page list list
 * \section ListSection About List functions
 *
 * To operate on a list object and based on your requirement, you can use any of these functions
 *
 * \section ListAPI List python API's
 *
 * \subpage selecttextitem - Select the item in the list based on name
 * \n
 * \n
 * \subpage selectindex - Select the item in the list based on index
 *
 */

/** \page logging logging
 * \section LoggingSection About Logging functions
 *
 * Log functions are used to log the operations performed. Output format of log file is XML file
 *
 * \section LoggingAPI Logging python API's
 *
 * \subpage addlogger - Add more logging handler
 * \n
 * \n
 * \subpage ldtplog - Log the operations in LDTP engine side
 * \n
 * \n
 * \subpage log - Log the operations
 * \n
 * \n
 * \subpage setloglevel - Set the level of logging
 * \n
 * \n
 * \subpage startldtplog - Start LDTP engine logging to a file
 * \n
 * \n
 * \subpage startlog - Start logging to a file
 * \n
 * \n
 * \subpage stopldtplog - Stop LDTP engine logging to a file
 * \n
 * \n
 * \subpage stoplog - Stop logging to a file
 *
 */

/** \page menuitem menuitem
 * \section MenuitemSection About Menuitem functions
 *
 * To operate on a menuitem object and based on your requirement, you can use any of these functions
 *
 * \section MenuitemAPI Menuitem python API's
 *
 * \subpage doesmenuitemexist - Check whether a menu item exist
 * \n
 * \n
 * \subpage invokemenu - Invoke a menu in embedded component
 * \n
 * \n
 * \subpage listsubmenus - Get list of menu items under a menu
 * \n
 * \n
 * \subpage selectmenuitem - Select the given menu item
 *
 */

/** \page panel panel
 * \section PanelSection About Panel functions
 *
 * To operate on a panel object and based on your requirement, you can use any of these functions
 *
 * \section PanelAPI Panel python API's
 *
 * \subpage getpanelchildcount - Get the number of childrens under a panel
 * \n
 * \n
 * \subpage selectpanel - Select panel based on index
 * \n
 * \n
 * \subpage selectpanelname - Select panel based on name
 *
 */

/** \page ProcessStatistics ProcessStatistics
 * \section ProcessStatisticsSection About Process Statistics functions
 *
 * To monitor the CPU and memory utilization you can use this class
 *
 * \section ProcessStatisticsAPI  Process Statistics python API's
 *
 * \subpage Classpstats - Python class to monitor CPU / Memory utilization
 *
 */

/** \page pushbutton pushbutton
 * \section PushbuttonSection About Pushbutton functions
 *
 * To operate on a push button object and based on your requirement, you can use any of these functions
 *
 * \section PushbuttonAPI Pushbutton python API's
 *
 * \subpage click - Generates mouse left click event on the object
 * \n
 * \n
 * \subpage mouseleftclick - Generate mouse left click event
 * \n
 * \n
 * \subpage stateenabled - Checks whether the push button is in
 * enabled state
 * \n
 * \n
 * \subpage verifypushbutton - Verify whether the object is a push button
 *
 */

/** \page radiobutton radiobutton
 * \section RadiobuttonSection About Radiobutton functions
 *
 * To operate on a radio button object and based on your requirement, you can use any of these functions
 *
 * \section RadiobuttonAPI Radiobutton python API's
 *
 * \subpage click - Click on a radio button
 * \n
 * \n
 * \subpage check - Select the radio button
 * \n
 * \n
 * \subpage stateenabled - Checks whether the radio button is in
 * eanbled state
 * \n
 * \n
 * \subpage verifycheck - Verify whether the radio button is selected
 * \n
 * \n
 * \subpage verifyuncheck - Verify whether the radio button is deselected
 *
 */

/** \page radiomenuitem radiomenuitem
 * \section RadiomenuitemSection About Radiomenuitem functions
 *
 * To operate on a radio menuitem object and based on your requirement, you can use any of these functions
 *
 * \section RadiomenuitemAPI Radiomenuitem python API's
 *
 * \subpage click - Click on a radio menu item
 * \n
 * \n
 * \subpage menucheck - Select the radio menu item
 * \n
 * \n
 * \subpage selectmenuitem - Select the radio menu item
 * \n
 * \n
 * \subpage verifymenucheck - Verify whether the radio menu item is selected
 * \n
 * \n
 * \subpage verifymenuuncheck - Verify whether the radio menu item is deselected
 *
 */

/** \page scrollbar scrollbar
 * \section ScrollbarSection About Scrollbar functions
 *
 * To operate on a scrollbar object and based on your requirement, you can use any of these functions
 *
 * \section ScrollbarAPI Scrollbar python API's
 *
 * \subpage onedown - Scroll down one time
 * \n
 * \n
 * \subpage oneleft - Scroll left one time
 * \n
 * \n
 * \subpage oneright - Scroll right one time
 * \n
 * \n
 * \subpage oneup - Scroll up one time
 * \n
 * \n
 * \subpage scrolldown - Scroll down
 * \n
 * \n
 * \subpage scrollleft - Scroll left
 * \n
 * \n
 * \subpage scrollright - Scroll right
 * \n
 * \n
 * \subpage scrollup - Scroll up
 * \n
 * \n
 * \subpage verifyscrollbar - Verify whether the object is scroll bar
 * \n
 * \n
 * \subpage verifyscrollbarhorizontal - Verify whether the object is
 * horizontal scroll bar
 * \n
 * \n
 * \subpage verifyscrollbarvertical - Verify whether the object is
 * vertical scroll bar
 *
 */

/** \page slider slider
 * \section SliderSection About Slider functions
 *
 * To operate on a slider object and based on your requirement, you can use any of these functions
 *
 * \section SliderAPI Slider python API's
 *
 * \subpage decrease - Decrease the slider
 * \n
 * \n
 * \subpage increase - Increase the slider
 * \n
 * \n
 * \subpage setmax - Set the slider to max value
 * \n
 * \n
 * \subpage setmin - Set the slider to min value
 * \n
 * \n
 * \subpage verifyslider - Verify whether the object is slider
 * \n
 * \n
 * \subpage verifysliderhorizontal - Verify whether the object is
 * horizontal slider
 * \n
 * \n
 * \subpage verifyslidervertical - Verify whether the object is
 * vertical slider
 *
 */

/** \page spinbutton spinbutton
 * \section SpinbuttonSection About Spinbutton functions
 *
 * To operate on a spin button object and based on your requirement, you can use any of these functions
 *
 * \section SpinbuttonAPI Spinbutton python API's
 *
 * \subpage getvalue Get value from spin button
 * \n
 * \n
 * \subpage setvalue - Set value in spin button
 * \n
 * \n
 * \subpage verifysetvalue - Verify the value of spin button with the
 * given value
 *
 */

/** \page pagetablist pagetablist
 * \section PagetabSection About Pagetab functions
 *
 * To operate on a page tab object and based on your requirement, you can use any of these functions
 *
 * \section PagetabAPI Pagetab python API's
 *
 * \subpage gettabcount - Get number of tabs in a page tab list
 * \n
 * \n
 * \subpage selecttab - Select tab based on tab name
 * \n
 * \n
 * \subpage selecttabindex - Select tab based on tab index
 *
 */

/** \page statusbar statusbar
 * \section StatusbarSection About Statusbar functions
 *
 * To operate on a status bar object and based on your requirement, you can use any of these functions
 *
 * \section PagetabAPI Pagetab python API's
 *
 * \subpage getstatusbartext - Get text displayed in status bar
 * \n
 * \n
 * \subpage verifystatusbar - Verify the status bar text with the
 * given text
 * \n
 * \n
 * \subpage verifystatusbarvisible - Verify whether the status bar
 * object is visible
 *
 */

/** \page table table
 * \section TableSection About Table functions
 *
 * To operate on a table object and based on your requirement, you can use any of these functions
 *
 * \section TableAPI Table python API's
 *
 * \subpage checkrow - Tick the table cell row of type toggle button
 * \n
 * \n
 * \subpage doesrowexist - Checks whether the row with the given name exist
 * \n
 * \n
 * \subpage doubleclickrow - Generate double click event on the row
 * with matches the given name
 * \n
 * \n
 * \subpage getcellvalue - Get the table cell value
 * \n
 * \n
 * \subpage getrowcount - Get the rows count
 * \n
 * \n
 * \subpage gettablerowindex - Get the index of the row, where the
 * given name matches
 * \n
 * \n
 * \subpage selectlastrow - Select last row in the table
 * \n
 * \n
 * \subpage selectrow - Select a row with the given name
 * \n
 * \n
 * \subpage selectrowindex - Select a row with an index
 * \n
 * \n
 * \subpage selectrowpartialmatch - Select a row with the given
 * partial name
 * \n
 * \n
 * \subpage setcellvalue - Set the table cell value with the given value
 * \n
 * \n
 * \subpage singleclickrow - Generate single click event on the row
 * with matches the given name
 * \n
 * \n
 * \subpage sortcolumn - Sort the column based on the given field name
 * \n
 * \n
 * \subpage sortcolumnindex - Sort the column based on the given field index
 * \n
 * \n
 * \subpage uncheckrow - Un check the table cell of type toggle button
 * \n
 * \n
 * \subpage verifytablecell - Verify whether the cell value is same as
 * the given value
 * \n
 * \n
 * \subpage verifypartialtablecell - Verify whether the cell value
 * partially matches the given value
 *
 */

/** \page text text
 * \section TextSection About Text functions
 *
 * To operate on a text object and based on your requirement, you can use any of these functions
 *
 * \section TextAPI Text python API's
 *
 * \subpage activatetext - Activate the text
 * \n
 * \n
 * \subpage appendtext - Append the given text to the existing text
 * \n
 * \n
 * \subpage comparetextproperty - Checks the availability of all the given text property
 * \n
 * \n
 * \subpage containstextproperty - Checks the availability of one given text property
 * \n
 * \n
 * \subpage copytext - Copy text to clipboard
 * \n
 * \n
 * \subpage cuttext - Cut the text
 * \n
 * \n
 * \subpage deletetext - Deletes the text
 * \n
 * \n
 * \subpage enterstring - Genereate keyboard events as if user key-ins
 * \n
 * \n
 * \subpage getcharcount - Get the number of characters present in a
 * text field
 * \n
 * \n
 * \subpage getcursorposition - Get the current cursor position
 * \n
 * \n
 * \subpage gettextproperty - Get the properties of text
 * \n
 * \n
 * \subpage gettextvalue - Get the text content
 * \n
 * \n
 * \subpage grabfocus - Grab the focus
 * \n
 * \n
 * \subpage inserttext - Insert a text in specified location
 * \n
 * \n
 * \subpage istextstateenabled - Verify whether the text field is enabled
 * \n
 * \n
 * \subpage mouseleftclick - Generate mouse left click event
 * \n
 * \n
 * \subpage mouserightclick - Generate mouse right click event
 * \n
 * \n
 * \subpage mousemove - Simulate mouse move event
 * \n
 * \n
 * \subpage pastetext - Paste the text from clip board to the text area
 * \n
 * \n
 * \subpage rightclick - Generate right click event
 * \n
 * \n
 * \subpage selecttextbyindexandregion - Select text by index and region
 * \n
 * \n
 * \subpage selecttextbyname - Select text by the given name
 * \n
 * \n
 * \subpage setcursorposition - Move the cursor position to the
 * specified location
 * \n
 * \n
 * \subpage settextvalue - Sets the text value in the text field
 * \n
 * \n
 * \subpage verifypartialmatch - Verify whether the given text
 * partially matches with the existing text
 * \n
 * \n
 * \subpage verifysettext - Verify whether the given text is same as
 * the text available in the text field
 *
 */

/** \page togglebutton togglebutton
 * \section TogglebuttonSection About Togglebutton functions
 *
 * To operate on a toggle object and based on your requirement, you can use any of these functions
 *
 * \section TogglebuttonAPI Togglebutton python API's
 *
 * \subpage click - Click on a toggle button
 * \n
 * \n
 * \subpage enterstring - Generate keyboard event as if user keys-in
 * \n
 * \n
 * \subpage press - Toggle's the button state
 * \n
 * \n
 * \subpage verifytoggled - Verify whether the button is in toggled state
 *
 */

/** \page embeddedcomponent embeddedcomponent
 * \section EmbeddedcomponentSection About Embeddedcomponent functions
 *
 * To operate on a embedded component (accessible) object and based on your requirement, you can use any of these functions
 *
 * \section EmbeddedcomponentAPI Embeddedcomponent python API's
 *
 * \subpage click - Click on an embedded component object
 * \n
 * \n
 * \subpage enterstring - Generate keyboard event as if user keys-in
 * \n
 * \n
 * \subpage invokemenu - Invokes the menu in an embedded component object
 * \n
 * \n
 * \subpage rightclick - Right clicks on an embedded component object
 *
 */

/** \page toolbar toolbar
 * \section ToolbarSection About Toolbar functions
 *
 * To operate on a toolbar object and based on your requirement, you can use any of these functions
 *
 * \section ToolbarAPI Toolbar python API's
 *
 * \subpage verifybuttoncount - Verify the number of buttons matches
 * with the given button count
 * \n
 * \n
 * \subpage verifyvisiblebuttoncount - Verify the visible number of
 * buttons matches the given button count
 *
 */

/** \page treetable treetable
 * \section TreetableSection About Treetable functions
 *
 * To operate on a tree table object and based on your requirement, you can use any of these functions
 *
 * \section TreetableAPI Treetable python API's
 *
 * \subpage checkrow - Tick the table cell row of type toggle button
 * \n
 * \n
 * \subpage doesrowexist - Checks whether the row with the given name exist
 * \n
 * \n
 * \subpage doubleclickrow - Generate double click event on the row
 * with matches the given name
 * \n
 * \n
 * \subpage expandtablecell - Expand or collapse tree table
 * \n
 * \n
 * \subpage getcellvalue - Get the table cell value
 * \n
 * \n
 * \subpage getrowcount - Get the rows count
 * \n
 * \n
 * \subpage gettreetablerowindex - Get the index of the row, where the
 * given name matches
 * \n
 * \n
 * \subpage rightclick - Generate right click event
 * \n
 * \n
 * \subpage selectlastrow - Select last row in the table
 * \n
 * \n
 * \subpage selectrow - Select a row with the given name
 * \n
 * \n
 * \subpage selectrowindex - Select a row with an index
 * \n
 * \n
 * \subpage selectrowpartialmatch - Select a row with the given
 * partial name
 * \n
 * \n
 * \subpage setcellvalue - Set the table cell value with the given value
 * \n
 * \n
 * \subpage singleclickrow - Generate single click event on the row
 * with matches the given name
 * \n
 * \n
 * \subpage sortcolumn - Sort the column based on the given field name
 * \n
 * \n
 * \subpage sortcolumnindex - Sort the column based on the given field index
 * \n
 * \n
 * \subpage uncheckrow - Un check the table cell of type toggle button
 * \n
 * \n
 * \subpage verifycheckrow - Verify whether the table cell of type
 * toggle button is ticked
 * \n
 * \n
 * \subpage verifytablecell - Verify whether the cell value is same as
 * the given value
 * \n
 * \n
 * \subpage verifypartialtablecell - Verify whether the cell value
 * partially matches the given value
 * \n
 * \n
 * \subpage verifyuncheckrow - Verify whether the table cell of type
 * toggle button is un-ticked
 *
 */

/** \page Window Window functions
 * \section WindowSection About Window functions
 *
 * Window based functions
 * \n
 * \n
 *
 * \section WindowAPI Window python API's
 *
 * \subpage getapplist - Get list of accessibility enabled applications
 * \n
 * \n
 * \subpage getchild - Get child object of a window which matches label or role name or both
 * \n
 * \n
 * \subpage getobjectinfo - Get list of available property classes of an object
 * \n
 * \n
 * \subpage getobjectlist - Get list of objects in a window
 * \n
 * \n
 * \subpage getobjectproperty - Get a class (label, type) property of an object
 * \n
 * \n
 * \subpage getwindowlist - Get current list of window titles in LDTP
 * engine hash table
 * \n
 * \n
 * \subpage guiexist - Checks whether a window exist
 * \n
 * \n
 * \subpage guitimeout - Modifies the global gui timeout period
 * \n
 * \n
 * \subpage objectexist - To check whether a component exist in a given window
 * \n
 * \n
 * \subpage objtimeout - Modifies the global object timeout period
 * \n
 * \n
 * \subpage onwindowcreate - Register callback function to be called
 * when the specified window is created
 * \n
 * \n
 * \subpage removecallback - Remove the registered callback function using onwindowcreate
 * \n
 * \n
 * \subpage waittillguiexist - Suspend the operation till the window exist
 * \n
 * \n
 * \subpage waittillguinotexist - Suspend the operation till the
 * window quits
 *
 */

/** \page LTFX LTFX functions
 * \section LTFXSection About LTFX functions
 *
 * To operate on an window in which accessibility is not enabled we
 * use external application Linux Test For X (In short LTFX) -
 * http://sf.net/projects/ltfx
 * \n
 *
 * \section LTFXAPI LTFX python API's
 *
 * \subpage activatewin - Activate the window with the given title
 * \n
 * \n
 * \subpage activatewinpartialname - Activate the window with the
 * given partial title
 * \n
 * \n
 * \subpage getactivewin - Get the window title thats currently in focus
 * \n
 * \n
 * \subpage partialexists - Check the window whether it exist based on
 * the partial given title
 * \n
 * \n
 * \subpage typekey - Generate keyboard events as if user key in
 * \n
 * \n
 * \subpage waitwinname - Wait for window to appear with the given title
 * \n
 * \n
 * \subpage waitwinpartialname - Wait for window to appear with the
 * given partial title
 * \n
 * \n
 * \subpage windowexists - Check the window whether it exist based on
 * the given title
 * \n
 *
 * \section LTFXAssumptions Assumptions
 *
 * LTFX functions assumes that the window to be operated is in
 * focus. It directly generates the X key board events. It does not
 * know whether the object exist or the operation is successfully
 * done.
 *
 */

/** \page icon icon
 * \section IconSection About Icon functions
 *
 * To operate on an icon object
 *
 * \section IconAPI Icon python API's
 *
 * \subpage rightclick
 *
 */

/**
 * \page initappmap initappmap
 * \section Syntax
 * 
 * initappmap ('\<application map name\>')
 * 
 * \section Description
 * 
 * Application map will be loaded
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c, http://webcvs.freedesktop.org/ldtp/ldtp/src/appmap.c
 * 
 * \section Example
 * 
 * from ldtp import *
 * 
 * initappmap ('nautilus.map')
 * 
 * \author Nagappan <nagappan@gmail.com>
 */

/**
 * \page guiexist guiexist
 * \section Syntax
 * 
 * guiexist ('\<window name\>'[, \<object name\>])
 * 
 * \section Description
 * 
 * If the given window name exist, this function returns 1. If window doesnot exist, then this function returns 0.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 * 
 * \section ImplementationDetails
 * 
 * \retval 1 on success and 0 on no existing window
 * 
 * \section Example
 * 
 * With respect to gedit Open dialog
 *
 * from ldtp import *
 *
 * # if GTK File selector is opened the following function will return 1, else 0
 *
 * guiexist ('dlgOpenFile...')
 * 
 * guiexist ('dlgOpenFile...', 'btnOpen') # Returns 1, If window exist and also the object exist
 * 
 * guiexist ('dlgOpenFile...', 'btnabc') # Returns 0
 * 
 * \author Nagappan <nagappan@gmail.com>
 */

/**
 * \page waittillguiexist waittillguiexist
 * \section Syntax
 * 
 * waittillguiexist ('\<window name\>'[, '\<component name\>'[, guiTimeOut]])
 * 
 * \section Description
 * 
 * If the given window name exist, this function returns 1. If window doesnot exist, then this function returns 0. Difference between \ref guiexist and waitguiexist is, waitguiexist waits for maximum 30 seconds. Still the window doesn't appear, then 0 is returned. We can set the environment variable 'GUI_TIMEOUT' to change the default waiting time. We can wait for component also and its an optional argument. The default value of guiTimeOut is None and it can be changed either by environment variable or by passing an integer argument > 0. This timeout will be for this specific window and it will not affect the global default time out settings. If you want to change the global default time out settings use guitimeout or objtimeout function appropriately.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 * 
 * \retval 1 on success, 0 otherwise
 * 
 * \section Example
 * 
 * waittillguiexist ('dlgOpen')
 * 
 * This function will be useful, when some event is fired and after that if a new window is expected, we can use this function to wait for window to appear.
 * 
 * \author Nagappan <nagappan@gmail.com>
 */

/**
 * \page waittillguinotexist waittillguinotexist
 * \section Syntax
 * 
 * waittillguinotexist ('\<window name\>'[, '\<component name\>'[, guiTimeOut]])
 * 
 * \section Description
 * 
 * If the given window name does not exist, this function returns 1. If window exist, then this function returns 0. Difference between \ref guiexist and waitguinotexist is, waitguinotexist waits for maximum 30 seconds. Still the window does not disappear, then 0 is returned. We can set the environment variable 'GUI_TIMEOUT' to change the default waiting time. We can wait for component also and its an optional argument. The default value of guiTimeOut is None and it can be changed either by environment variable or by passing an integer argument > 0. This timeout will be for this specific window and it will not affect the global default time out settings. If you want to change the global default time out settings use guitimeout or objtimeout function appropriately.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 * 
 * \retval 1 on success, 0 otherwise
 * 
 * \section Example
 * 
 * waittillguinotexist ('dlgOpen')
 * 
 * This function will be useful, when some event is fired and after that if an existing window should close, we can use this function to wait till the window closes.
 * 
 * \author Nagappan <nagappan@gmail.com>
 */

/**
 * \page log log
 * \section Syntax
 * 
 * log ('\<Message to be logged\>', '\<tag\>')
 * 
 * where tag can be any of these
 * 
 * \subsection debug
 * 
 * messages can be logged while executing in debug mode
 * 
 * \subsection warning
 * 
 * warning message  can be logged
 * 
 * \subsection teststart
 * 
 * tag used to indicate the beginning of the test suite
 * 
 * \subsection testend
 * 
 * tag used to indicate the end of the test suite
 * 
 * \subsection begin
 * 
 * tag used to indicate the beginning of test case
 * 
 * \subsection end
 * 
 * tag used at the end of the test case
 * 
 * \subsection error
 * 
 * error messages can be logged with this message
 * 
 * \subsection pass
 * 
 * message will be logged on successful execution of the testcases
 *  
 * \subsection fail
 * 
 * message will be logged on if execution of testcases fail
 * 
 * \note Messges for the Tags teststart and testend should not contain spaces in between
 * 
 * begin and end: These keywords are to be used with the same logging message and at beginning and end of testscripts
 * 
 * teststart and testend: These keywords are to be used with the same logging message and at the beginning and end of testcases
 * 
 * \section Description
 * 
 * Logs the message in the log.xml with the tag which can be viewed after the execution of scripts
 * 
 * \section ImplementationDetails
 * 
 * The required message will be logged into the log.xml on execution of scripts
 * 
 * \retval 1 on success and 0 on error
 * 
 * \section Example
 * 
 * With Respect to Evolution:
 * 
 * 1) log ('EvolutionSuite', 'begin')
 * 
 * execfile ('evolution.py')
 * 
 * log ('EvolutionSuite', 'end')
 * 
 * 2) With respect to Appointment-to check the checkbox, 
 * 
 * In Try Block:
 * 
 * selecttab('dlgAppointment-NoSummary', 'ptlAppointment-Nosummary', '1')
 *       
 * log ('Selecttab-In-Appointment', 'pass')
 * 
 * In except block:
 * 
 * print "Error"
 * 
 * log ('Selecttab','fail')
 * 
 * 3) With respect to creation of vFolders
 * 
 * log ('Creation-of-vFolders', 'teststart')
 * 
 * Create_folder()
 * 
 * log ('Creation-of-vFolders', 'testend')
 * 
 * 4) Log message showing success of some test case 
 * 
 * from ldtp import *
 * 
 * You can log the message to start the test case before writing the test case as
 * 
 * log ('Open a file', 'teststart')
 * 
 * log ('opening a file', 'pass')
 * 
 * \author Nagashree <mnagashree@novell.com>
 */

/**
 * \page ldtplog ldtplog
 * \section Syntax
 * 
 * ldtplog ('\<Message to be logged\>', '\<tag\>')
 * 
 * where tag can be any of these
 * 
 * \subsection debug
 * 
 * messages can be logged while executing in debug mode
 * 
 * \subsection warning
 * 
 * warning message  can be logged
 * 
 * \subsection teststart
 * 
 * tag used to indicate the beginning of the test suite
 * 
 * \subsection testend
 * 
 * tag used to indicate the end of the test suite
 * 
 * \subsection begin
 * 
 * tag used to indicate the beginning of test case
 * 
 * \subsection end
 * 
 * tag used at the end of the test case
 * 
 * \subsection error
 * 
 * error messages can be logged with this message
 * 
 * \subsection pass
 * 
 * message will be logged on successful execution of the testcases
 *  
 * \subsection fail
 * 
 * message will be logged on if execution of testcases fail
 * 
 * \note Messges for the Tags teststart and testend should not contain spaces in between
 * 
 * begin and end: These keywords are to be used with the same logging message and at beginning and end of testscripts
 * 
 * teststart and testend: These keywords are to be used with the same logging message and at the beginning and end of testcases
 * 
 * \section Description
 * 
 * Logs the message in the specified log file in LDTP engine side, with the tag which can be viewed after the execution of scripts
 * 
 * \section ImplementationDetails
 * 
 * The required message will be logged into the log.xml on execution of scripts
 * 
 * \retval 1 on success and 0 on error
 * 
 * \section Example
 * 
 * With Respect to Evolution:
 * 
 * 1) ldtplog ('EvolutionSuite', 'begin')
 * 
 * execfile ('evolution.py')
 * 
 * ldtplog ('EvolutionSuite', 'end')
 * 
 * 2) With respect to Appointment-to check the checkbox, 
 * 
 * In Try Block:
 * 
 * selecttab('dlgAppointment-NoSummary', 'ptlAppointment-Nosummary', '1')
 *       
 * ldtplog ('Selecttab-In-Appointment', 'pass')
 * 
 * In except block:
 * 
 * print "Error"
 * 
 * ldtplog ('Selecttab','fail')
 * 
 * 3) With respect to creation of vFolders
 * 
 * ldtplog ('Creation-of-vFolders', 'teststart')
 * 
 * Create_folder()
 * 
 * ldtplog ('Creation-of-vFolders', 'testend')
 * 
 * 4) Log message showing success of some test case 
 * 
 * from ldtp import *
 * 
 * You can log the message to start the test case before writing the test case as
 * 
 * ldtplog ('Open a file', 'teststart')
 * 
 * ldtplog ('opening a file', 'pass')
 * 
 * \author Nagashree <mnagashree@novell.com>
 */

/**
 * \page reinitldtp reinitldtp
 * \section Syntax
 * 
 * reinitldtp ()
 *
 * \section Description
 * 
 * When we work with applications like nautilus, if we open a new window, the new window will not be recognized, until we close and open the session. In case of Mozilla Firefox also we could notice the same behaviour. Like opening Preference window, opening printer dialog etc.
 * 
 * \section ImplementationDetails
 * 
 * Closes the existing accessibility connection with at-spi-registryd and opens a new connection.
 *
 * \retval 1 on success, LdtpExecutionError on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 * 
 * \section Example
 * 
 * reinitldtp ()
 * 
 * \author Nagappan <nagappan@gmail.com>
 */

/**
 * \page check check
 * \section Syntax
 * 
 * check ('\<window name\>', '\<component name\>')
 * 
 * \section Description
 * 
 * Check (tick) the check box state.
 * 
 * \section ImplementationDetails
 * 
 * \retval 1 if state is checked, else 0.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/check-box.c
 * 
 * \section Example
 * 
 * from ldtp import *
 * 
 * For check menu item with respect to gedit menu
 * 
 * check ('gedit', 'mnuOutputWindow')
 * 
 * For check menu item with respect to gedit menu
 * 
 * check ('gedit', 'mnuToolbar')
 * 
 * For check box with respect to gedit preferences
 * 
 * check ('dlgPreferences', 'cboxEnableAutoIndentation')
 * 
 * \author Nagappan <nagappan@gmail.com>
 * \author Khasim Shaheed <khasim.shaheed@gmail.com>
 */

/** \page uncheck uncheck
 * \section Syntax
 * 
 * uncheck ('\<window name\>', '\<component name\>')
 * 
 * \section Description
 * 
 * Uncheck (un-tick) the check  state.
 * 
 * \section ImplementationDetails
 * 
 * \retval 1 if state is unchecked, else 0.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/check-box.c
 * 
 * \section Example
 * 
 * from ldtp import *
 * 
 * To uncheck menu item with respect to gedit menu
 * 
 * uncheck ('gedit', 'mnuOutputWindow')
 * 
 * For check menu item with respect to gedit menu
 * 
 * uncheck ('gedit', 'mnuToolbar')
 * 
 * To uncheck box with respect to gedit preferences
 * 
 * uncheck ('dlgPreferences', 'cboxEnableAutoIndentation')
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page click click
 * \section Syntax
 * 
 * click ('\<window name\>', '\<component name\>')
 * 
 * \section Description
 * 
 * click on radio button / check box / push button/ combo box/ radio menu item/ toggle button/ radio button.
 * 
 * \section ImplementationDetails
 * 
 * \subsection Radio Radio Button
 * 
 * If radio button is already in checked state, then this function will uncheck (unset) it.
 * 
 * If radio button is already in unchecked state, then this function will check (set) it.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/radio-button.c
 * 
 * \subsection Check Check Box
 * 
 * If check box is already in checked state, then this function will uncheck (unset) it.
 * 
 * If check box is already in unchecked state, then this function will check (set) it.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/check-box.c
 * 
 * \subsection Push Push Button
 * 
 * If push button state is enabled, then click on the object.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/push-button.c
 * 
 * \subsection Toggle Toggle Button
 * 
 * Click on the toggle button.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/toggle-button.c
 * 
 * \subsection Combo Combo Box
 * 
 * Clicks on combo box, drop down list of combo box will be visible if not already else drop down list of combo box closes.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 * 
 * \section Examples
 * 
 * Example for push button (With respect to gedit open dialog)
 * 
 * click ('dlgOpen', 'btnOpen')
 * 
 * For Check box, Check menu item, on doing this action, the state will be toggled.
 * 
 * For Radio button, Radio menu item, if they are not already selected, they are selected, otherwise silently ignored.
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page verifycheck verifycheck
 * \section Syntax
 * 
 * verifycheck ('\<window name\>', '\<component name\>')
 * 
 * \section Description
 * 
 * Checks the state of check box
 * 
 * \retval On check box state is checked returns 1, else 0.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/check-box.c
 * 
 * \section Examples
 * 
 * from ldtp import *
 * 
 * For check menu item with respect to gedit menu
 * 
 * verifycheck ('gedit', 'mnuView;mnOutputWindow')
 * 
 * For check box with respect to gedit preferences
 * 
 * verifycheck ('dlgPreferences', 'cboxEnableAutoIndentation')
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Aishwariya <aishwariyabhavan@yahoo.com>
 * \author Khasim Shaheed <khasim.shaheed@gmail.com>
 */

/** \page verifyuncheck verifyuncheck
 * \section Syntax
 * 
 * verifyuncheck ('\<window name\>', '\<component name\>')
 * 
 * \section Description
 * 
 * Checks the state of check box.
 * 
 * \retval On check box state is un-checked returns 1, else 0.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/check-box.c
 * 
 * \section Examples
 * 
 * from ldtp import *
 * 
 * To verify uncheck menu item with respect to gedit menu
 * 
 * verifyuncheck ('gedit', 'mnuView;mnOutputWindow')
 * 
 * To verify uncheck box with respect to gedit preferences
 * 
 * verifyuncheck ('dlgPreferences', 'cboxEnableAutoIndentation')
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Khasim Shaheed <khasim.shaheed@gmail.com>
 */

/** \page verifymenucheck verifymenucheck
 * \section Syntax
 * 
 * verifymenucheck ('\<window name\>', '\<menu item\>')
 *
 * \section Description
 * 
 * Verify whether a menu is checked or not
 * 
 * \retval 1 on success, 0 on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/check-menu-item.c
 * 
 * \section Example
 *
 * With respect to gedit, View menu and Toolbar check menuitem, we can verify whether the menu is checked or not. If checked 1 will be returned, else 0 will be returned.
 *
 * verifymenucheck ('*-gedit', 'mnuView;mnuToolbar')
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page verifymenuuncheck verifymenuuncheck
 * \section Syntax
 * 
 * verifymenuuncheck ('\<window name\>', '\<menu item\>')
 *
 * \section Description
 * 
 * Verify whether a menu is unchecked or checked
 * 
 * \retval 1 on success, 0 on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/check-menu-item.c
 * 
 * \section Example
 *
 * With respect to gedit, View menu and Toolbar check menuitem, we can verify whether the menu is unchecked or not. If unchecked 1 will be returned, else 0 will be returned.
 *
 * verifymenuuncheck ('*-gedit', 'mnuView;mnuToolbar')
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page menucheck menucheck
 * \section Syntax
 * 
 * menucheck ('\<window name\>', '\<menu item\>')
 *
 * \section Description
 * 
 * Checks a menu item, if its already checked it will be silently ignored
 * 
 * \retval 1 on success, LdtpExecutionError exception on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/check-menu-item.c
 * 
 * \section Example
 * 
 * With respect to gedit, View menu and Toolbar check menuitem, we can check the menuitem. If its already checked, it will be silently ignored.
 *
 * menucheck ('*-gedit', 'mnuView;mnuToolbar')
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page menuuncheck menuuncheck
 * \section Syntax
 * 
 * menuuncheck ('\<window name\>', '\<menu item\>')
 *
 * \section Description
 * 
 * Unchecks a menu item, if its already unchecked it will be silently ignored
 * 
 * \retval 1 on success, LdtpExecutionError exception on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/check-menu-item.c
 * 
 * \section Example
 * 
 * With respect to gedit, View menu and Toolbar check menuitem, we can uncheck the menuitem. If its already unchecked, it will be silently ignored.
 *
 * menuuncheck ('*-gedit', 'mnuView;mnuToolbar')
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page setcursorposition setcursorposition
 * \section Syntax
 * 
 * setcursorposition ('\<window name\>', '\<text object name\>', \<position\>)
 *
 * \section Description
 * 
 * Sets cursor position in a text field
 * 
 * \retval 1 on success, LdtpExecutionError exception on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 * 
 * \section Example
 * 
 * from ldtp import *
 *
 * # Assuming that gedit is opened
 *
 * settextvalue ('*-gedit', 'txt0', 'Testing setcursorposition function of LDTP')
 *
 * setcursorposition ('*-gedit', 'txt0', 9)
 *
 * The above example will set the given text value in first tab of gedit window and the cursor position will be moved to column number 10 of the first row.
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page istextstateenabled istextstateenabled
 * \section Syntax
 * 
 * istextstateenabled ('\<window name\>', '\<text object name\>')
 *
 * \section Description
 * 
 * Checks whether the text object is in editable state or not.
 * 
 * \retval 1 on success, 0 on failure.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 * 
 * \section Example
 * 
 * \todo
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page getstatusbartext getstatusbartext
 * \section Syntax
 * 
 * getstatusbartext ('\<window name\>', '\<status bar name\>')
 *
 * \section Description
 * 
 * Gets the text displayed in the status bar
 * 
 * \retval text content displayed in the status bar on success, LdtpExecutionError exception on failure.
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/status-bar.c
 * 
 * \section Example
 * 
 * \todo
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page verifystatusbar verifystatusbar
 * \section Syntax
 * 
 * verifystatusbar ('\<window name\>', '\<status bar name\>')
 *
 * \section Description
 * 
 * Checks whether the object is status bar or not
 * 
 * \retval 1 on success, 0 on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/status-bar.c
 * 
 * \section Example
 * 
 * With respect to gedit status bar text
 *
 * from ldtp import *
 *
 * verifystatusbar ('*-gedit', 'stat0')
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page verifystatusbarvisible verifystatusbarvisible
 * \section Syntax
 * 
 * verifystatusbarvisible ('\<window name\>', '\<status bar name\>')
 *
 * \section Description
 * 
 * Checks whether the status bar object is visible or not
 * 
 * \retval 1 on success, 0 on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/status-bar.c
 * 
 * \section Example
 * 
 * With respect to gedit status bar text
 *
 * from ldtp import *
 *
 * verifystatusbarvisible ('*-gedit', 'stat0')
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page selecttextbyindexandregion selecttextbyindexandregion
 * \section Syntax
 * 
 * selecttextbyindexandregion ('\<window name\>', '\<text object name\>'[, <start position\>[, <end position\>[, <selection number\>]]])
 *
 * \section Description
 * 
 * Select text by index (text selection change based on index) and the region (start and end position)
 *
 * Reference: http://developer.gnome.org/doc/API/2.0/at-spi/at-spi-cspi-AccessibleText-Interface.html#AccessibleText-setSelection
 * 
 * \retval 1 on success, LdtpExecutionError exception on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 * 
 * \section Example
 * 
 * \todo
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page selecttextbyname selecttextbyname
 * \section Syntax
 * 
 * selecttextbyname ('\<window name\>', '\<text object name\>')
 *
 * \section Description
 * 
 * Select text by name
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 * 
 * \section Example
 * 
 * \todo
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page getcursorposition getcursorposition
 * \section Syntax
 * 
 * getcursorposition ('\<window name\>', '\<text object name\>')
 *
 * \section Description
 * 
 * Gets the current cursor position of the given text object
 * 
 * \retval cursor position which is of type long on success, LdtpExecutionError exception on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 * 
 * \section Example
 *
 * from ldtp import *
 *
 * # Assuming that gedit is opened
 *
 * settextvalue ('*-gedit', 'txt0', 'Testing setcursorposition function of LDTP')
 *
 * getcursorposition ('*-gedit', 'txt0')
 *
 * The above example will get the current cursor position in the text object of gedit windows first tab.
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page hidelist hidelist
 * \section Syntax
 * 
 * hidelist ('\<dlgName\>', '\<cmbName\>')
 *
 * \section Description
 * 
 * Hides combo box drop down list in the current dialog. Suppose in previous operation one testcase has clicked on combo box, its drop down list will be displayed. If further no any operation has been done on that combo box then to close that drop down list 'HideList' action is required
 * 
 * \section ImplementationDetails
 * 
 * Combo box will generally have a list as its child or a menu as its child. So this function gets object handle of list object, checks if list of combo box is visible, if yes then just click on combo box, click operation will close drop down list of combo box.
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 * 
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 * 
 * \section Example
 * 
 * \todo
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page comboselect comboselect
 * \section Syntax
 *
 * comboselect ('\<window name\>', '\<component name\>', '\<menu item name\>')
 *
 * \section Description
 *
 * Select a menu item or list item in a combo box
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * In gnome-search-tool combo box 'Available options' to select the menu item 'Contains the text'
 * 
 * comboselect ('SearchForFiles', 'cmbAvailableoptions', 'Contains the text')
 * 
 * or
 * 
 * comboselect ('SearchForFiles', 'cmbAvailableoptions', 'Containsthetext') 
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page selectindex selectindex
 * \section Syntax
 *
 * selectindex ('\<dlgName\>', '\<cmbName\>', \<index\>)
 *
 * \section Description
 *
 * SelectIndex action will select an item from combo box where value of index is pointing to its position in list/menu.
 *
 * \section ImplementationDetails
 *
 * Combo box will generally have a list as its child or a menu as its child. SelectIndex function will try to find whether child type is menu or list, if child type is list then there will be a text box associated with combo box. When child type is list, selects item at index value from list box and sets that value to the text box associated with combo box. If child type is menu, value specified in tha argument will be index of menu item, corressponding menu item will be selected.
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page settextvalue settextvalue
 * \section Syntax
 *
 * settextvalue ('\<window name\>', '\<component name\>', '\<text\>')
 *
 * \section Description
 *
 * puts the text into the component given by the component name
 *
 * \section ImplementationDetails
 *
 * In text.c
 *
 * \retval 1 on success and 0 otherwise
 *
 * In combo-box.c
 *
 * Combo box will be associated with child of type 'Text' when one of its child is 'List'. This action gets object handle of 'Text' object associated with combo box and then sets value given in argument in that text box 
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * With respect to gnome search tool text field
 * 
 * settextvalue ('SearchforFiles', 'txtNameContainsEntry', 'abcd')
 * 
 * This is to insert the text 'abcd' into the 'txtNameContainsEntry' field.
 * 
 * In combo box:
 * 
 * \todo settextvalue ('\<dlgName\>', '\<cmbName\>', '\<argument\>') 
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page appendtext appendtext 
 * \section Syntax
 *
 * appendtext ('\<window name\>', '\<component name\>', '\<text\>')
 *
 * \section Description
 *
 * Appends the given text with already present text
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 otherwise
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * With respect to gedit structure
 * 
 * appendtext('gedit','txtmain','Sample text')
 * 
 * This to append 'Sample text' to the 'main' text box contents in gedit 
 *
 * \author Shagan <shagan.glare@gmail.com>
 */

/** \page activatetext activatetext
 * \section Syntax
 *
 * activatetext ('\<window name\>', '\<component name\>')
 *
 * \section Description
 *
 * activates the text box ( similar to press enter after setting text)
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 otherwise
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * With respect to gftp-gtk structure
 * 
 * activatetext ('gFTP', 'txtUser')
 * 
 * This is to activate the text box 'txtUser' in gftp-gtk 
 *
 * \author Shagan <shagan.glare@gmail.com>
 */

/** \page getcharcount getcharcount
 * \section Syntax
 *
 * getcharcount ('\<window name\>', '\<component name\>')
 *
 * \section Description
 *
 * Return the number of characters present in the component identified by the \<component name\>.
 *
 * \section ImplementationDetails
 *
 * \retval number of characters
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * With respect to gedit
 * 
 * getcharcount ('gedit', 'txt0')
 * 
 * This will return the number of characters in the file presently open. 
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page cuttext cuttext
 * \section Syntax
 *
 * cuttext ('\<window name\>', '\<component name\>', \<startindex\>, \<endindex\>)
 *
 * \section Description
 *
 * Cut the text from startindex till the endindex in the component given by the component name
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 otherwise
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * With respect to gedit tool structure
 * 
 * cuttext ('gedit', 'txtName', 1, 3)
 * 
 * This is to cut the text from the startindex position till the endindex in the 'txtName' field.
 *
 * \author Kamakshi <poorvakrishna@yahoo.com>
 */

/** \page  copytext copytext
 * \section Syntax
 *
 * copytext ('\<window name\>', '\<component name\>', \<startoffset\>, \<endoffset\>)
 *
 * \section Description
 *
 * Copies text within specified offset present in the specified \<component\> into clipboard
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 otherwise
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * With respect to gedit tool structure
 * 
 * copytext ('gedit', 'txt0', 5,10)
 * 
 * This is to copy the text within the offset specified from the 'txt0' field into clipboard. 
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page inserttext inserttext
 * \section Syntax
 *
 * inserttext ('\<window name\>', '\<component name\>', \<position\>, '\<text\>')
 *
 * \section Description
 *
 * Insert the text in the specified position in the component given by the component name
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 otherwise
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * With respect to gedit
 * 
 * inserttext ('*-gedit', 'txt0', 5, 'sample text')
 * 
 * This is to insert the given text at the specified position in the 'txtName' field. 
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page pastetext pastetext
 * \section Syntax
 *
 * pastetext ('\<window name\>', '\<component name\>', \<position\>)
 *
 * \section Description
 *
 * paste the text from the position specified in the component given by the component name
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 otherwise
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * With respect to gedit tool structure
 * 
 * pastetext ('gedit', 'txtName', 1)
 * 
 * This is to paste the text from the position specified in the 'txtName' field. 
 *
 * \author Kamakshi <poorvakrishna@yahoo.com>
 */

/** \page deletetext deletetext
 * \section Syntax
 *
 * deletetext ('\<window name\>', '\<component name\>', \<startindex\>, \<endindex\>)
 *
 * \section Description
 *
 * delete the text from the startindex till the endindex in the component given by the component name
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 otherwise
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * With respect to gedit tool structure
 * 
 * deletetext ('gedit', 'txtName', 1, 3)
 * 
 * This is to delete the text from the startindex to endindex specified in the 'txtName'field. 
 *
 * \author Kamakshi <poorvakrishna@yahoo.com>
 */

/** \page showlist showlist
 * \section Syntax
 *
 * showlist ('\<dlgName\>', '\<cmbName\>')
 *
 * \section Description
 *
 * Displays combo box drop down list in the current dialog.
 *
 * \section ImplementationDetails
 *
 * Combo box will generally have a list as its child or a menu as its child. So this function gets object handle of list object, checks if list of combo box is visible, if not then just click on combo box, click operation will display drop down list of combo box. 
 *
 * \retval 1 on success, LdtpExecutionError on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page verifydropdown verifydropdown
 * \section Syntax
 *
 * verifydropdown ('\<window name\>', '\<combo box / list name\>')
 *
 * \section Description
 *
 * \retval 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page verifyhidelist verifyhidelist
 * \section Syntax
 *
 * verfyhidelist ('\<dlgName\>', '\<cmbName\>')
 *
 * \section Description
 *
 * Verifies if combo box drop down list in the current dialog is not visible.
 *
 * \section ImplementationDetails
 *
 * Combo box will generally have a list as its child or a menu as its child. So this function gets object handle of list or menu object, checks if list or menu items of combo box is visible, if yes then return minus one else returns zero.
 *
 * \retval 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page verifyshowlist verifyshowlist
 * \section Syntax
 *
 * verifyshowlist ('\<dlgName\>', '\<cmbName\>')
 *
 * \section Description
 *
 * Verifies if combo box drop down list in the current dialog is visible.
 *
 * \section ImplementationDetails
 *
 * Combo box will generally have a list as its child or a menu as its child. So this function gets object handle of list or menu object, checks if list or menu items of combo box is visible, if yes then return zero else minus one.
 *
 * \retval 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page verifyselect verifyselect
 * \section Syntax
 *
 * verifyselect ('\<dlgName\>', '\<cmbName\>', '\<argument\>')
 *
 * \section Description
 *
 * VerfySelect action will verify if combo box is set to value given in argument.
 *
 * \section ImplementationDetails
 *
 * VerifySelect function will try to find if text box associated with combo box is set to value specified in the argument.
 *
 * \retval 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * In gnome-search-tool combo box 'Available options' to select the menu item 'Contains the text'
 * 
 * verifyselect ('SearchForFiles', 'cmbAvailableoptions', 'Contains the text')
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page verifysettext verifysettext
 * \section Syntax
 *
 * verifysettext ('\<window name\>', '\<component name\>', '\<text\>')
 *
 * \section Description
 *
 * checks if the text is inserted into the component given by the component name
 *
 * \section ImplementationDetails
 *
 * \retval 1 if the text is inserted into the specified component else returns 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * With respect to gnome search tool structure
 * 
 * verifysettext ('SearchforFiles', 'txtNameContainsEntry', 'abcd')
 * 
 * This is to verify if the previous settextvalue function has inserted 'abcd' into the txtNameContainsEntry field in the gnome search tool 
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page rightclick rightclick
 * \section Syntax
 *
 * rightclick ('\<window name\>', '\<component name\>', '\<menu item\>', '[data]')
 *
 * \todo icon - rightclick ('\<window name\>', '\<component name\>')
 *
 * \section Description
 *
 * Right click on the given object.
 *
 * \section ImplementationDetails
 *
 * This function gets the coordinate of the given object and the right click event is generated.
 *
 * \note If the object's window is not in focus, then this function will fail
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 * http://webcvs.freedesktop.org/ldtp/ldtp/src/layered-pane.c
 *
 * \section Example
 *
 * # Right click on an embedded component object type
 *
 * rightclick ('frmBottomExpandedEdgePanel', 'Volume Control', None)
 *
 * \author Thanikachalam S <thanika1999@yahoo.com>
 * \author Poornima <pnayak@novell.com>
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page getlabel getlabel
 * \section Syntax
 *
 * getlabel ('\<window name\>', '\<label name\>')
 *
 * \section Description
 *
 * \retval label string on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/label.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Thanikachalam S <thanika1999@yahoo.com>
 */

/** \page getlabelatindex getlabelatindex
 * \section Syntax
 *
 * getlabelatindex ('\<window name\>', '\<panel name\>', index)
 *
 * \section Description
 *
 * Gets label name based on index from the panel.
 *
 * \retval label name on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/label.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page selectitem selectitem
 * \section Syntax
 *
 * selectitem ('\<window name\>', '\<combo box name\>', '\<item\>')
 *
 * \section Description
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/layered-pane.c, http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Thanikachalam S <thanika1999@yahoo.com>
 */

/** \page selecttextitem selecttextitem
 * \section Syntax
 *
 * selectitem ('\<window name\>', '\<combo box name\>', '\<item\>')
 *
 * \section Description
 *
 * Selects a text item in a combox box and the combo box may contain either list or menu item.
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 * http://webcvs.freedesktop.org/ldtp/ldtp/src/list.c
 *
 * \section Example
 *
 * With respect to gedit, find dialog
 *
 * from ldtp import *
 *
 * click ('*-gedit', 'btnFind')
 *
 * # assuming that LDTP string is available in the list of searched strings
 *
 * selectitem ('dlgFind', 'cboSearchFor', 'LDTP')
 *
 * \author Poornima Nayak <pnayak@novell.com>
 */

/** \page selectmenuitem selectmenuitem
 * \section Syntax
 *
 * selectmenuitem ('\<window name\>', '\<menu hierarchy\>')
 *
 * \section Description
 *
 * Selects the menu item specified.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/menu.c
 * http://webcvs.freedesktop.org/ldtp/ldtp/src/check-menu-item.c
 *
 * http://webcvs.freedesktop.org/ldtp/ldtp/src/menu-item.c
 * http://webcvs.freedesktop.org/ldtp/ldtp/src/radio-menu-item.c
 *
 * \section Example
 *
 * With respect to gedit menu structure
 * 
 * selectmenuitem ('*-gedit', 'mnuFile;mnuNew') 
 *
 * \author Nagappan A <nagappan@gmail.com>
 * \author Thanikachalam S <thanika1999@yahoo.com>
 */

/** \page selecttab selecttab
 * \section Syntax
 *
 * selecttab ('\<window name\>', '\<tab list name\>', '\<tab name\>')
 *
 * \section Description
 *
 * Select the given tab name in the tab list
 *
 * \section ImplementationDetails
 *
 * \retval 1 if the tab is selected, \exception otherwise ldtp.error will be thrown
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/page-tab-list.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For selecting Editor tab with respect to gedit preferences
 * 
 * selecttab ('dlgPreferences', 'ptlPreferences', 'Editor') 
 *
 * \author Thanikachalam S <thanika1999@yahoo.com>
 */

/** \page selecttabindex selecttabindex
 * \section Syntax
 *
 * selecttabindex ('\<window name\>', '\<tab list name\>', \<index of the tab\>)
 *
 * \section Description
 *
 * Select a particular tab in the list of tabs
 *
 * \section ImplementationDetails
 *
 * \retval 1 if the tab is selected, \exception otherwise ldtp.error will be thrown
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/page-tab-list.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For selecting Editor tab with respect to gedit preferences
 * 
 * selecttabindex ('dlgPreferences', 'ptlPreferences', 1)
 * 
 * \note 0 based index
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page gettabcount gettabcount
 * \section Syntax
 *
 * gettabcount ('\<window name\>', '\<tab list name\>')
 *
 * \section Description
 *
 * Returns the page tab count of a page tab list
 *
 * \retval tab count of type long is returned on success, LdtpExecutionError on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/page-tab-list.c
 *
 * \section Example
 *
 * With respect to Preferences dialog of gedit
 *
 * from ldtp import *
 *
 * selectmenuitem ('*-gedit', 'mnuEdit;mnuPreferences')
 *
 * gettabcount ('dlgPreferences', 'ptl0')
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page verifypushbutton verifypushbutton
 * \section Syntax
 *
 * verifypushbutton ('\<window name\>', '\<component name\>')
 *
 * \section Description
 *
 * Verify whether the given object is push button or not.
 *
 * \section ImplementationDetails
 *
 * \retval 1 if object is push button, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/push-button.c
 *
 * \section Example
 *
 * With respect to gedit open dialog window, verify open button is push button or not.
 * 
 * verifypushbutton ('dlgOpenFile', 'btnOpen') 
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page stateenabled stateenabled
 * \section Syntax
 *
 * stateenabled ('\<window name\>', '\<component name\>')
 *
 * \section Description
 *
 * Checks the radio button object state enabled or not
 *
 * \section ImplementationDetails
 *
 * \retval 1 if state is enabled, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/push-button.c
 * http://webcvs.freedesktop.org/ldtp/ldtp/src/radio-button.c
 *
 * \section Example
 *
 * Push button: With respect to gedit open dialog, this function checks open button state enabled or not
 * 
 * stateenabled ('dlgOpenFile', 'btnOpen')
 * 
 * \todo Radiobutton
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page setvalue setvalue
 * \section Syntax
 *
 * setvalue ('\<window name\>', '\<spinbutton name\>', '\<value\>')
 *
 * \section Description
 *
 * Sets the value of the spin button.
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else LdtpExecutionError exception
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/spin-button.c
 *
 * \section Example
 *
 * Creation of Appointment in Evolution:
 * 
 * setvalue ('dlgAppointment-Nosummary','sbtnOccurence','2') 
 *
 * \author Thanikachalam S <thanika1999@yahoo.com>
 */

/** \page getvalue getvalue
 * \section Syntax
 *
 * getvalue ('\<window name\>', '\<spinbutton name\>')
 *
 * \section Description
 *
 * Gets the value in the spin button.
 *
 * \section ImplementationDetails
 *
 * \retval value in the spin button on success, else LdtpExecutionError exception
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/spin-button.c
 *
 * \section Example
 *
 * Creation of Appointment in Evolution:
 * 
 * getvalue ('dlgAppointment-Nosummary', 'sbtnOccurence')
 *
 * \author Thanikachalam S <thanika1999@yahoo.com>
 */

/** \page verifysetvalue verifysetvalue
 * \section Syntax
 *
 * verifysetvalue ('\<window name\>', '\<spinbutton name\>', '\<value\>')
 *
 * \section Description
 *
 * Verifies the value set in spin button.
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 on error.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/spin-button.c
 *
 * \section Example
 *
 * In the Creation of Appointment:
 * 
 * verifysetvalue ('dlgAppointment-Nosummary','sbtnOccurence','2') 
 *
 * \author Sheetal <svnayak18@yahoo.com>
 */

/** \page selectrow selectrow
 * \section Syntax
 *
 * selectrow ('\<window name\>', '\<table name\>', '\<value of row in first column\>')
 *
 * \section Description
 *
 * Selects the row in table whose first column's (0th column) value is same as the contents of the third argument in the function call.
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 on error.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 * http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to gedit open dialog
 * 
 * selectrow ('dlgOpen', 'dlgFiles', 'readme') 
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page selectrowindex selectrowindex
 * \section Syntax
 *
 * selectrowindex ('\<window name\>', '\<table name\>', \<row index\>) 
 *
 * \section Description
 *
 * Selects the row with the given index value in table. Index value starts from 0.
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 on error.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 * http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to gedit open dialog
 * 
 * selectrowindex ('dlgOpen', 'dlgFiles', 0) 
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page selectrowpartialmatch selectrowpartialmatch
 * \section Syntax
 *
 * selectrowpartialmatch ('\<window name\>', '\<tree table name\>', '\<texttobesearchedfor\>')
 *
 * \section Description
 *
 * selects the row having cell that contains the given text.
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and throws an exception on error
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 * http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * With respect to evolution
 * 
 * selectrowpartialmatch ('evolution', 'ttblMailFolder','Inbox')
 * 
 * The 'Inbox' folder's name changes depending on the number of unread mails. In such cases we can use the above method to select the 'Inbox' folder. 
 *
 * \author Nagashree <mnagashree@novell.com>
 */

/** \page verifytoggled verifytoggled
 * \section Syntax
 *
 * verifytoggled ('<window name\>', 'component name\>')
 *
 * \section Description
 *
 * Verify whether the toggle button is toggled or not
 *
 * \retval 1 on success, else 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/toggle-button.c
 *
 * \section Example
 *
 * 1. With respect to GTK File Selector - Open dialog in gedit application
 *
 * from ldtp import *
 *
 * verifytoggled ('Open File*', 'Type a file name') # If 'Type a file name' button is toggled then location text box will be in editable state in GTK file selector
 *
 * 2. With respect to GTK File Selector in gedit
 *
 * from ldtp import *
 *
 * click ('*-gedit', 'btnOpen')
 *
 * verifytoggled ('dlgOpenFile...', 'tbtnTypeafilename')
 *
 * \author Poornima Nayak <pnayak@novell.com>
 * \author Premkumar J <prem.jothimani@gmail.com> 
 */

/** \page onedown onedown
 * \section Syntax
 *
 * onedown ('\<window name\>', '\<scroll component name\>', \<number of iterations\>)
 *
 * \section Description
 *
 * Move the scroll bar down 'n' times, where 'n' is the number of iterations specified in the argument field.
 *
 * \section ImplementationDetails
 *
 * Scrolls down if value does not exceed the maximum limit, else fails.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/scroll-bar.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For scroll bar item with respect to gedit
 * 
 * onedown ('gedit', 'scrollBar', 3) 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page oneleft oneleft
 * \section Syntax
 *
 * oneleft ('\<window name\>', '\<scroll component name\>', \<number of iterations\>)
 *
 * \section Description
 *
 * Move the (horizontal) scroll bar left 'n' times, where 'n' is the number of iterations specified in the argument field.
 *
 * \section ImplementationDetails
 *
 * Scrolls left if value does not drop below the minimum limit, else fails.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/scroll-bar.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For scroll bar item with respect to gedit
 * 
 * oneleft ('gedit', 'scrollBar', 3) 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page oneright oneright
 * \section Syntax
 *
 * oneright ('\<window name\>', '\<scroll component name\>', \<number of iterations\>)
 *
 * \section Description
 *
 * Move the (horizontal) scroll bar right 'n' times, where 'n' is the number of iterations specified in the argument field.
 *
 * \section ImplementationDetails
 *
 * Scrolls right if value does not exceed the maximum limit, else fails.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/scroll-bar.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For scroll bar item with respect to gedit
 * 
 * oneright ('gedit', 'scrollBar', 3) 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page oneup oneup
 * \section Syntax
 *
 * oneup ('\<window name\>', '\<scroll component name\>', \<number of iterations\>)
 *
 * \section Description
 *
 * Move the (vertical) scroll bar up 'n' times, where 'n' is the number of iterations specified in the argument field.
 *
 * \section ImplementationDetails
 *
 * Scrolls up if value does not drop below the minimum limit, else fails.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/scroll-bar.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For scroll bar item with respect to gedit
 * 
 * oneup ('gedit', 'scrollBar', 3) 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page scrolldown scrolldown
 * \section Syntax
 *
 * scrolldown ('\<window name\>', '\<scroll component name\>')
 *
 * \section Description
 *
 * Move the (vertical) scroll bar to the bottom.
 *
 * \section ImplementationDetails
 *
 * \retval 1 if action is performed, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/scroll-bar.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For scroll bar item with respect to gedit
 * 
 * scrolldown ('gedit', 'scrollBar') 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page scrollleft scrollleft
 * \section Syntax
 *
 * scrolleft ('\<window name\>', '\<scroll component name\>')
 *
 * \section Description
 *
 * Move the (horizontal) scroll bar to the extreme left.
 *
 * \section ImplementationDetails
 *
 * \retval 1 if action is performed, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/scroll-bar.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For scroll bar item with respect to gedit
 * 
 * scrolleft ('gedit', 'scrollBar') 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page scrollright scrollright
 * \section Syntax
 *
 * scrollright ('\<window name\>', '\<scroll component name\>')
 *
 * \section Description
 *
 * Move the (horizontal) scroll bar to the extreme right.
 *
 * \section ImplementationDetails
 *
 * \retval 1 if action is performed, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/scroll-bar.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For scroll bar item with respect to gedit
 * 
 * scrollright ('gedit', 'scrollBar') 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page scrollup scrollup
 * \section Syntax
 *
 * scrollup ('\<window name\>', '\<scroll component name\>')
 *
 * \section Description
 *
 * Move the (vertical) scroll bar to the extreme top.
 *
 * \section ImplementationDetails
 *
 * \retval 1 if action is performed, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/scroll-bar.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For scroll bar item with respect to gedit
 * 
 * scrollup ('gedit', 'scrollBar') 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page setmax setmax
 * \section Syntax
 *
 * setmax ('\<window name\>', '\<slider name\>')
 *
 * \section Description
 *
 * Set the slider to the maximum value.
 *
 * \section ImplementationDetails
 *
 * \retval 1 if action is performed, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/slider.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For slider component with respect to gnome-terminal
 * 
 * setmax ('dlgEditingProfile"Default"', 'slider') 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page setmin setmin
 * \section Syntax
 *
 * setmin ('\<window name\>', '\<slider name\>')
 *
 * \section Description
 *
 * Set the slider to the minimum value.
 *
 * \section ImplementationDetails
 *
 * \retval 1 if action is performed, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/slider.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For slider component with respect to gnome-terminal
 * 
 * setmin ('dlgEditingProfile"Default"', 'slider') 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page getslidervalue getslidervalue
 * \section Syntax
 *
 * getslidervalue ('\<window name\>', '\<slider name\>')
 *
 * \section Description
 *
 * Returns the slider value of the given object. Volume controller of type slider
 *
 * \retval slider value of type float is returned on success, LdtpExecutionError on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/slider.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page increase increase
 * \section Syntax
 *
 * increase ('\<window name\>', '\<slider name\>', \<number of iterations\>)
 *
 * \section Description
 *
 * Increase the value of the slider 'n' times, where 'n' is the number of iterations specified in the argument field.
 *
 * \section ImplementationDetails
 *
 * Increases the value if it does not exceed the maximum limit, else fails.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/slider.c
 *
 * \section Example
 *
 * from ldtp import *

 * For slider component with respect to gnome-terminal
 * 
 * increase ('dlgEditingProfile"Default"', 'slider', 3) 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page decrease decrease
 * \section Syntax
 *
 * decrease ('\<window name\>', '\<slider name\>', \<number of iterations\>)
 *
 * \section Description
 *
 * Decrease the value of the slider 'n' times, where 'n' is the number of iterations specified in the argument field.
 *
 * \section ImplementationDetails
 *
 * Decreases the value if it does not fall below the minimum limit, else fails.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/slider.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * For slider component with respect to gnome-terminal
 * 
 * decrease ('dlgEditingProfile"Default"', 'slider', 3) 
 *
 * \author Aishwariya & Kamakshi <poorvaishoo@yahoo.com>
 */

/** \page selectpanel selectpanel
 * \section Syntax
 *
 * selectpanel ('\<window name\>', '\<component name\>', \<panel number\>)
 *
 * \section Description
 *
 * Select a panel using the panel number in a list of panels
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 on error
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/panel.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Evolution Contacts
 * 
 * selectpanel ('frmEvolution-Contacts', 'pnlAddbook', 1) 
 *
 * \author Poornima Nayak <pnayak@novell.com>
 */

/** \page selectlabelspanelbyname selectlabelspanelbyname
 * \section Syntax
 *
 * selectlabelspanelbyname ('<window name\>', '<label name\>')
 *
 * \section Description
 *
 * \retval 1 on success, LdtpExecutionError on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/label.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page verifytablecell verifytablecell
 * \section Syntax
 *
 * verifytablecell ('\<window name\>', '\<table name\>', \<row no\>, \<column no\>, '\<string to be compared\>')
 *
 * \section Description
 *
 * Verifies the tablecell value with the String Passed ie., fifth argument
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success and 0 on error.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Evolution, open message
 * 
 * verifytablecell ('frmReadOnlyMail', 'tblcheck', 1, 1, 'xyz\@yahoo.com') 
 *
 * \author Bhargavi <kbhargavi_83@yahoo.co.in>
 */

/** \page settablecell settablecell
 * \section Syntax
 *
 * \todo
 *
 * \section Description
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page setcellvalue setcellvalue
 * \section Syntax
 *
 * setcellvalue ('<window name\>', '<table name\>', <row\>, <column\>, '<item\>')
 *
 * \section Description
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page selectlastrow selectlastrow
 * \section Syntax
 *
 * selectlastrow ('\<window name\>', '\<table name\>')
 *
 * \section Description
 *
 * Selects the last row of a table.
 *
 * \retval 1 on success, 0 otherwise.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Contact List Members dialog of Contact List Editor
 * 
 * selectlastrow ('dlgContactListMembers', 'tblContacts') 
 *
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page setcontext setcontext
 * \section Syntax
 *
 * setcontext ('\<previous title name\>', '\<new title name\>')
 *
 * \section Description
 *
 * LDTP selects window (frame / dialog / alert / font chooser) based on the title name.
 *
 * \section ImplementationDetails
 *
 * set the context to new title name. Changes are done in is_matching function in gui.c
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 *
 * \section Example
 *
 * In some applications the window title changes based on the operation we are doing. For example, when we browse any URL in Firefox browser, the title bar changes. Once title bar changed, then we can change the context using this function.
 * 
 * setcontext ('Mozilla Firefox', 'NOVELL: Novell and Linux - Mozilla Firefox') 
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page releasecontext releasecontext
 * \section Syntax
 *
 * releasecontext ()
 *
 * \section Description
 *
 * Release the last context set.
 *
 * \section ImplementationDetails
 *
 * Release the existing (last) context set using \ref setcontext function.
 *
 * \retval 1 on success, LdtpExecutionError on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 *
 * \section Example
 *
 * In some applications the window title changes based on the operation we are doing. For example, when we browse any URL in Firefox browser, the title bar changes. Once title bar changed, then we can change the context using this function.
 * 
 * releasecontext () 
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page selectevent selectevent
 * \section Syntax
 *
 * selectevent ('\<window name\>', '\<Calendar_view name\>', '\<calendar event summary\>')
 *
 * \section Description
 *
 * Selects the row from the table of calendar events based on the calendar event name specified
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/calendar-view.c
 *
 * \section Example
 *
 * In Evolution Calendars,for selecting an appointment-(calendar event) present in the table
 * 
 * from ldtp import *
 * 
 * selectevent ('Evolution-Calendars', 'calview', 'abc') 
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page selecteventindex selecteventindex
 * \section Syntax
 *
 * selecteventindex ('\<window name\>', '\<component name\>', \<event number\>)
 *
 * \section Description
 *
 * Select an event from a calendar table using its index. Index for a calendar event starts from 1.
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/calendar-view.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Evolution-Calendars
 * 
 * selecteventindex ('Evolution-Calendars', 'calview', 1) 
 *
 * \author Poornima <pnayak@novell.com>
 */

/** \page doesrowexist doesrowexist
 * \section Syntax
 *
 * doesrowexist ('\<window name\>', '\<table name\>', '\<string to be matched\>', no of matches)
 *
 * \section Description
 *
 * Checks whether the table contains any row with any of its cell containing the given string as its value.Please note that it checks for an exact match.
 *
 * \section ImplementationDetails
 *
 * \retval 1 if there are rows with the given string in any of its cell, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to the message list table in Evolution Mailer, the following call will return 1 if there is atleast one mail in the list with the given string in the subject field or sender field or in any other field for that matter.
 * 
 * doesrowexist ('dlgContactListMembers', 'tblContacts', 'Sample subject') 
 *
 * \author Manu <manunature@rediffmail.com>
 */

/** \page checkrow checkrow
 * \section Syntax
 *
 * checkrow ('\<window name\>', '\<table name\>', \<row index\>[, \<col index\>])
 *
 * \section Description
 *
 * checks the row with the given index value in table. This can take an optional column index and perform the action on that particular column. If the column index is not given, 0 is taken as the default value.Index value starts from 0. 
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Categories in Appointment in Evolution
 * 
 * checkrow('dlgCategories','tblcategories',3) 
 *
 * \author Bhargavi <kbhargavi_83@yahoo.co.in>
 */

/** \page verifycheckrow verifycheckrow
 * \section Syntax
 *
 * verifycheckrow ('\<window name\>', '\<table name\>', \<row index\>[, \<col index\>])
 *
 * \section Description
 *
 * 
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Categories in Appointment in Evolution
 * 
 * verifycheckrow ('dlgCategories', 'tblcategories', 3)
 *
 * \author Bhargavi <kbhargavi_83@yahoo.co.in>
 */

/** \page uncheckrow uncheckrow
 * \section Syntax
 *
 * uncheckrow ('\<window name\>', '\<table name\>', \<row index\>[, \<col index\>])
 *
 * \section Description
 *
 * unchecks the row with the given index value in table. This can take an optional column index and perform the action on that particular column. If the column index is not given, 0 is taken as the default value.Index value starts from 0. 
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Categories in Appointment in Evolution
 * 
 * uncheckrow('dlgCategories','tblcategories',3) 
 *
 * \author Bhargavi <kbhargavi_83@yahoo.co.in>
 */

/** \page verifyuncheckrow verifyuncheckrow
 * \section Syntax
 *
 * verifyuncheckrow ('\<window name\>', '\<table name\>', \<row index\>[, \<col index\>])
 *
 * \section Description
 *
 *
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Categories in Appointment in Evolution
 * 
 * verifyuncheckrow ('dlgCategories', 'tblcategories', 3) 
 *
 * \author Bhargavi <kbhargavi_83@yahoo.co.in>
 */

/** \page sortcolumn sortcolumn
 * \section Syntax
 *
 * sortcolumn ('<window name\>', '<table name\>', '<column name\>')
 *
 * \section Description
 *
 * Sort table based on column name.
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c, http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 *
 * \section Example
 *
 * \todo
 *
 * \author 
 */

/** \page sortcolumnindex sortcolumnindex
 * \section Syntax
 *
 * sortcolumnindex ('<window name\>', '<table name\>', <column index\>)
 *
 * \section Description
 *
 * Sort table based on column index.
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c, http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 *
 * \section Example
 *
 * \todo
 *
 * \author 
 */

/** \page verifypartialmatch verifypartialmatch
 * \section Syntax
 *
 * verifypartialmatch ('\<window name\>', '\<textbox name\>' , '\<substring\>' )
 *
 * \section Description
 *
 * Verifies the textbox with the partial string
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Evolution, to verify textbox with partial string
 * 
 * verifypartialmatch ('frmComposeamessage', 'txtto','nove') 
 *
 * \author Bhargavi <kbhargavi_83yahoo.co.in>
 */

/** \page getrowcount getrowcount
 * \section Syntax
 *
 * getrowcount ('\<window name\>', '\<table name\>')
 *
 * \section Description
 *
 * Returns the number of rows present in the table mentioned
 *
 * \retval number of rows present in the table on success, else -1
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 * \n
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Evolution, to check no of mails
 * 
 * getrowcount ('frmReadOnlyMail', 'tblmails')
 *
 * \author Bhargavi <kbhargavi_83@yahoo.co.in>
 */

/** \page verifypartialtablecell verifypartialtablecell
 * \section Syntax
 *
 * verifypartialtablecell ('\<window name\>', '\<table name\>', \<row no\>, \<column no\>, '\<sub string to be compared\>')
 *
 * \section Description
 *
 * Verifies the tablecell value with the sub String Passed ie., fifth argument
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Evolution, open message
 * 
 * verifypartialtablecell ('frmReadOnlyMail', 'tblcheck', 1, 1, 'xyz') 
 *
 * \author Bhargavi <kbhargavi_83@yahoo.co.in>
 */

/** \page grabfocus grabfocus
 * \section Syntax
 *
 * grabfocus ('\<window name\>'[, '\<component name\>'])
 *
 * \section Description
 *
 * gives focus to the specified context or component, in case of a text box the cursor is placed in it.
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else LdtpExecutionError exception
 *
 * \section Example
 *
 * With respect to gnome search tool structure
 * 
 * settextvalue ('SearchforFiles', 'txtNameContainsEntry')
 * 
 * This places the cursor in the 'txtNameContainsEntry' field. 
 *
 */

/** \page selectpanelname selectpanelname
 * \section Syntax
 *
 * selectpanelname ('\<window name\>', '\<component name\>', '\<panel name\>')
 *
 * \section Description
 *
 * Select a panel using the panel name in a list of panels
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else LdtpExecutionError exception
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/panel.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Evolution Contacts
 * 
 * selectpanelname ('Evolution-Contacts', 'pnlAddbook', 'ldtp') 
 *
 * \author Khasim Shaheed <khasim.shaheed@gmail.com>
 */

/** \page verifyeventexist verifyeventexist
 * \section Syntax
 *
 * verifyeventexist ('\<window name\>', '\<component name\>')
 *
 * \section Description
 *
 * verifies whether any events are present in a calendar table 
 *
 * \section ImplementationDetails
 *
 * \retval 1 on success, else 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/calendar-view.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to Evolution-Calendars
 * 
 * verifyeventexist ('Evolution-Calendars', 'calview') 
 *
 * \author Manu <manunature@rediffmail.com>
 */

/** \page expandtablecell expandtablecell
 * \section Syntax
 *
 * expandtablecell ('<window name\>', '<tree table object name\>', <row\>)
 *
 * \section Description
 *
 * Expand or contract the tree table cell on a row
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * With respect to Evolution Mail component
 *
 * from ldtp import *
 *
 * expandtablecell ('frm*-Evolution', 'ttblMailFolderTree', 0) # In mail folder view
 *
 * \author 
 */

/** \page gettreetablerowindex gettreetablerowindex
 * \section Syntax
 *
 * gettreetablerowindex ('\<window name\>', '\<tree table name\>', '\<name of a table cell\>')
 *
 * \section Description
 *
 * Used to obtain the index of any table cell whose whose name is give in the last field.
 *
 * \section ImplementationDetails
 *
 * \retval index of table cell, else -1.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * from ldtp import *
 * 
 * With respect to the tree table in Mail in Evolution
 * 
 * i = gettreetablerowindex ('Evolution', 'treetblMail', 'Cabinet')
 * 
 * here 'i' will be having the index of the Cabinet which is a table cell under tree table mail. 
 *
 * \author Aginesh <sraginesh@novell.com>
 */

/** \page gettablerowindex gettablerowindex
 * \section Syntax
 *
 * gettablerowindex ('\<window name\>', '\<tablename\>', '\<cellvalue\>')
 *
 * \section Description
 *
 * Returns the id of the row containing the given \<cellvalue\>
 *
 * \section ImplementationDetails
 *
 * \retval Return id of the row containing the given cell value, if it is found else return -1
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 *
 * \section Example
 *
 * In case of Evolution Calendar, to select the category form the list of categories
 * 
 * gettablerowindex ('dlgMeeting', 'tblCategoryList', 'Business')
 * 
 * The above call would return the row id of the cell containing Business. 
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page comboselectindex comboselectindex
 * \section Syntax
 *
 * \todo
 *
 * \section Description
 *
 *
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * \todo
 *
 * \author 
 */

/** \page verifyvisiblebuttoncount verifyvisiblebuttoncount
 * \section Syntax
 *
 * verifyvisiblebuttoncount ('<window name\>', '<toolbar name\>', <count\>)
 *
 * \section Description
 *
 * Verifies whether the toolbar button count matches with the argument count. 1 based index.
 *
 * \retval 1 on success, else 0
 *
 * \section Example
 *
 * With respect to gedit application toolbar
 *
 * from ldtp import *
 *
 * verifyvisiblebuttoncount ('*-gedit', 'tbar0', 12) # Gedit 2.12 default without any plugin
 *
 * \author J Premkumar <jpremkumar@novell.com>
 */

/** \page verifybuttoncount verifybuttoncount
 * \section Syntax
 *
 * verifybuttoncount ('<window name\>', '<toolbar name\>', <count\>)
 *
 * \section Description
 *
 * Verifies whether the toolbar button count matches with the argument count. 1 based index.
 *
 * \retval 1 on success, else 0
 *
 * \section Example
 *
 * With respect to gedit application toolbar
 *
 * from ldtp import *
 *
 * verifybuttoncount ('*-gedit', 'tbar0', 12) # Gedit 2.12 default without any plugin
 *
 * \author J Premkumar <jpremkumar@novell.com>
 */

/** \page geteventcount geteventcount
 * \section Syntax
 *
 * \todo
 *
 * \section Description
 *
 *
 *
 * \section Example
 *
 * \todo
 *
 * \author 
 */

/** \page gettextvalue gettextvalue
 * \section Syntax
 *
 * gettextvalue ('\<window name\>', '\<component name\>', \<startoffset\>, \<endoffset\>)
 *
 * \section Description
 *
 * returns the text within the given range in the component given by the component name. \<startoffset\> and \<endoffset\> are optional. If they are ommited, the entire text is returned. 
 *
 * \retval text data of string type on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * With respect to gnome search tool structure
 * 
 * gettextvalue ('SearchforFiles', 'txtNameContainsEntry')
 * 
 * The above statement will return the text present in 'txtNameContainsEntry' field.
 * 
 * gettextvalue ('SearchforFiles', 'txtNameContainsEntry', 5)
 * 
 * The above statement will return the text present in 'txtNameContainsEntry' field starting from the fifth character.
 * 
 * gettextvalue ('SearchforFiles', 'txtNameContainsEntry', 5, 10)
 * 
 * The above statement will return the text present in 'txtNameContainsEntry' field starting from the fifth character
 * 
 * till the tenth character. 
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page getcellvalue getcellvalue
 * \section Syntax
 *
 * getcellvalue ('\<window name\>', '\<component name\>', '\<row\>', '\<column\>')
 *
 * \section Description
 *
 * returns the text in a cell at given row and column of a tree table 
 *
 * \retval cell value of type string on success, else LdtpExecutionError exception
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * With respect to Evolution Messages tree table
 * 
 * gettextvalue ('Evolution-Mail', 'treetblMails', 2, 4)
 * 
 * This will return the subject of 3rd message in the message list. 
 *
 * \author Khasim Shaheed <khasim.shaheed@gmail.com>
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page capturetofile capturetofile
 * \section Syntax
 *
 * capturetofile ('\<window name\>', '\<combo box name\>'[, '\<file name\>'])
 *
 * \section Description
 *
 * Capture the list of contents of a combox box to a file. If file name argument is None, then by default the list contents are written to comboboxitem.lst file of current working directory of LDTP engine.
 *
 * \retval 1 on success, LdtpExecutionError on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/combo-box.c
 *
 * \section Example
 *
 * With respect to Find dialog of gedit application
 *
 * from ldtp import *
 *
 * # Without specifiying the filename
 *
 * capturetofile ('dlgFind', 'cboSearchfor')
 *
 * # With specifiying the filename
 *
 * capturetofile ('dlgFind', 'cboSearchfor', '/tmp/comboboxlistitem.txt') # Not relative path won't work !!!
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page gettextproperty gettextproperty
 * \section Syntax
 *
 * gettextproperty ('<window name\>', '<text object name\>'[, <start position\>[, <end position\>]])
 *
 * \section Description
 *
 * Get the text attributes
 *
 * \retval text attributes of type string on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page comparetextproperty comparetextproperty
 * \section Syntax
 *
 * comparetextproperty ('<window name\>', '<text object name\>', '<text property\>'[, <start position\>[, <end position\>]])
 *
 * \section Description
 *
 * Compares the text attribute properties
 *
 * Default value of start and end positions are 0 and length of the string.
 *
 * \retval 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page containstextproperty containstextproperty
 * \section Syntax
 *
 * containstextproperty ('<window name\>', '<text object name\>', '<text property\>'[, <start position\>[, <end position\>]])
 *
 * \section Description
 *
 * Checks for one or more text attribute properties
 *
 * Default value of start and end positions are 0 and length of the string.
 *
 * \retval 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/text.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page selectcalendardate selectcalendardate
 * \section Syntax
 *
 * selectcalendardate ('\<window name\>', '\<calendar object name\>', \<day\>, \<month\>, \<year\>)
 *
 * \section Description
 *
 * 
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/calendar.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page remap remap
 * \section Syntax
 *
 * remap ('\<window name\>'[, '\<component name\>'])
 * 
 * undoremap ('\<application-name\>', '\<dialog name\>') 
 *
 * \section Description
 *
 * We can handle dynamically created widgets (meaning widgets created at run time) using this remap function. Calling remap will generate appmap for the given dialog at run time and update the hash table. Then we can access the new widgets. But please make sure to call undoremap() once the required functions are performed so that the hash table will be reverted back to its original state. The reason for having undoremap() is that subsequent calls to remap() might corrupt the hash table containg the appmap entries.
 * 
 * Please not that the <application-name> should be same as the one given as the commmand-line argument for appmap generation. 
 *
 * \section ImplementationDetails
 *
 * It uses the same logic that appmap module uses to generate appmap. Please refer to the following link for the source code of the remap functionality
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/remap.c
 *
 * \section Example
 * 
 * remap ('dlggeditPreferences') # Remaps the complete gedit preferences dialog
 * 
 * remap ('dlggeditPreferences', 'ptabView') # Remaps all the controls under page tab with the name View of gedit Preferences dialog.
 * 
 * . .
 * 
 * undoremap ('evolution', 'dlgAppointment-Nosummary') 
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page getwindowlist getwindowlist
 * \section Syntax
 *
 * getwindowlist ()
 *
 * \section Description
 *
 * Gets all the window name, that are currently used. If none of the windows are accessed and if this function is the first call means, then LdtpExecutionError will be thrown.
 *
 * \retval list of window names will be returned on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 *
 * \section Example
 *
 * from ldtp import *
 *
 * guiexist ('*-gedit')
 *
 * click ('*-gedit', 'btnFind')
 *
 * guiexist ('dlgFind')
 *
 * getwindowlist () # Will return the gedit window, Find window, etc as list
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page getapplist getapplist
 * \section Syntax
 *
 * getapplist ()
 *
 * \section Description
 *
 * Will return all the accessibility application window title that are currently opened
 *
 * \retval list of window names will be returned on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 *
 * \section Example
 *
 * from ldtp import *
 *
 * getapplist () # Will return all the accessibility application window title that are currently opened
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page getchild getchild
 * \section Syntax
 *
 * getchild ('\<window name\>'[[, '\<component name\>'], [ '\<role\>']])
 *
 * \section Description
 *
 * Gets the list of object available in the window, which matches component name or role name or both.
 *
 * \retval List of objects on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 *
 * \section Example
 *
 * With respect to Find object of gedit application
 *
 * from ldtp import *
 *
 * getchild ('*-gedit', 'Find')
 *
 * getchild ('*-gedit', role = 'push button')
 *
 * getchild ('*-gedit', 'Find', role = 'push button')
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page getobjectlist getobjectlist
 * \section Syntax
 *
 * getobjectlist ('\<window name\>')
 *
 * \section Description
 *
 * Gets the list of object available in the window (if window exist, else exception will be thrown)
 *
 * \retval List of objects on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 *
 * \section Example
 *
 * With respect to Find dialog of gedit application
 *
 * from ldtp import *
 *
 * getobjectlist ('dlgFind')
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page getobjectinfo getobjectinfo
 * \section Syntax
 *
 * getobjectinfo ('\<window name\>', '\<object name\>')
 *
 * \section Description
 *
 * Gets the list of object information lik class, parent, label, label_by, child_index
 *
 * \retval list of object properies (example, class, parent, label, label_by, child_index) on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 *
 * \section Example
 *
 * With respect to gedit Find dialog
 *
 * from ldtp import *
 *
 * getobjectinfo ('dlgFind', 'btnFind')
 *
 * \author 
 */

/** \page getobjectproperty getobjectproperty
 * \section Syntax
 *
 * getobjectproperty ('<window name\>', '<object name\>', '\<object property\>')
 *
 * \section Description
 *
 * Get the object property if available, else exception will be thrown
 *
 * \retval object property string on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 *
 * \section Example
 *
 * With respect to find dialog of gedit application
 *
 * from ldtp import *
 *
 * getobjectproperty ('dlgFind', 'btnFind', 'label') # Returns '_Find' string in US.English locale
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page doubleclickrow doubleclickrow
 * \section Syntax
 *
 * doubleclickrow ('\<window name\>', '\<table name\>', '\<value of row in first column\>')
 *
 * \section Description
 *
 * Double clicks the row in table whose first column's (0th column) value is same as the contents of the third argument in the function call.
 *
 * \retval 1 on success, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c, http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page singleclickrow singleclickrow
 * \section Syntax
 *
 * singleclickrow ('\<window name\>', '\<table name\>', '\<value of row in first column\>')
 *
 * \section Description
 *
 * Single clicks the row in table whose first column's (0th column) value is same as the contents of the third argument in the function call.
 *
 * \retval 1 on success, else 0.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c, http://webcvs.freedesktop.org/ldtp/ldtp/src/table.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page doubleclick doubleclick
 * \section Syntax
 *
 * doubleclick ('\<window name\>', '\<component name\>')
 *
 * \section Description
 *
 * Double clicks the row in table whose first column's (0th column) value is same as the contents of the third argument in the function call.
 *
 * \retval 1 on success, else 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/tree-table.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 */

/** \page listsubmenus listsubmenus
 * \section Syntax
 *
 * listsubmenus ('window name\>', 'menu name\>')
 *
 * \section Description
 *
 * Get the list of sub menu item, in a menu in a ; seperated list
 *
 * \retval ';' seperated string on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/menu-item.c
 *
 * \section Example
 *
 * With respect to gedit application, File menu
 *
 * from ldtp import *
 *
 * listsubmenus ('*-gedit', 'mnuFile') # all the submenus of File menu in ';' seperated string
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page invokemenu invokemenu
 * \section Syntax
 *
 * invokemenu ('window name\>', 'object name\>')
 *
 * \section Description
 *
 * Invokes the menu in an embedded component (accessible) type
 *
 * \retval 1 on success, LdtpExecutionError exception on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/embedded-component.c
 *
 * \section Example
 *
 * With respect to gedit application, File menu
 *
 * from ldtp import *
 *
 * invokemenu ('frmBottomExpandedEdgePanel', 'Volume Control')
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page verifyscrollbar verifyscrollbar
 * \section Syntax
 *
 * verifyscrollbar ('<window name\>', '<scroll bar name\>')
 *
 * \section Description
 *
 * Checks whether the given object is scrollbar or not, also we can check whether scroll bar object is available or not
 *
 * \retval 1 on success, else 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/scroll-bar.c
 *
 * \section Example
 *
 * With respect to gedit application
 *
 * from ldtp import *
 *
 * verifyscrollbar ('*-gedit', 'scbr0') # assuming that the file currently opened content is more than one page, else the scrollbar object will not be created by accessibility interface
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page verifyscrollbarhorizontal verifyscrollbarhorizontal
 * \section Syntax
 *
 * verifyscrollbarhorizontal ('<window name\>', '<scroll bar name\>')
 *
 * \section Description
 *
 * Checks whether the given object is horizontal scrollbar or not
 *
 * \retval 1 on success, else 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/scroll-bar.c
 *
 * \section Example
 *
 * With respect to gedit application
 *
 * from ldtp import *

 * verifyscrollbarhorizontal ('*-gedit', 'scbr0') # assuming that you have more columns than the actual visible area, else the scrollbar object will not be created by accessibility interface
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page verifyscrollbarvertical verifyscrollbarvertical
 * \section Syntax
 *
 * verifyscrollbarvertical ('<window name\>', '<scroll bar name\>')
 *
 * \section Description
 *
 * Checks whether the given object is vertical scrollbar or not
 *
 * \retval 1 on success, else 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/scroll-bar.c
 *
 * \section Example
 *
 * With respect to gedit application
 *
 * from ldtp import *

 * verifyscrollbarhorizontal ('*-gedit', 'scbr0') # assuming that you have more columns than the actual visible area, else the scrollbar object will not be created by accessibility interface
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page verifyslider verifyslider
 * \section Syntax
 *
 * verifyslider ('<window name\>', '<slider name\>')
 *
 * \section Description
 *
 * 
 *
 * \retval 1 on success, else 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/slider.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page verifysliderhorizontal verifysliderhorizontal
 * \section Syntax
 *
 * verifysliderhorizontal ('<window name\>', '<slider name\>')
 *
 * \section Description
 *
 * 
 *
 * \retval 1 on success, else 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/slider.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page verifyslidervertical verifyslidervertical
 * \section Syntax
 *
 * verifyslidervertical ('<window name\>', '<slider name\>')
 *
 * \section Description
 *
 * 
 *
 * \retval 1 on success, else 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/slider.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page onwindowcreate onwindowcreate
 * \section Syntax
 *
 * onwindowcreate ('<window title\>', '<call back function\>')
 *
 * \section Description
 *
 * Watch, window create event, with the given title and call the respective callback function. Window title supports regular expression too.
 *
 * \retval 1 on success, else LdtpExecutionError exception
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c, http://webcvs.freedesktop.org/ldtp/ldtp/src/ldtp-gui.c
 *
 * \section Example
 *
 * With respect to gedit application, replace dialog
 *
 * <pre>
 *
 * from ldtp import *
 *
 * import threading
 *
 * 
 * callbackRunning = threading.Event ()
 *
 * callbackRunning.clear ()
 *
 * callbackState = threading.Event ()
 *
 * callbackState.clear ()
 *
 * 
 * def cb ():
 *
 *	callbackState.set ()
 *
 *	waittillguiexist ('dlgReplace')
 *
 *	click ('dlgReplace', 'btnClose')
 *
 *	callbackState.clear ()
 *
 *	callbackRunning.set ()
 *
 *	print 'callbackend'
 *
 * 
 * onwindowcreate ('Replace', cb)
 *
 * click ('*gedit', 'btnReplace')
 *
 * click ('*gedit', 'btnFind')
 *
 * waittillguiexist ('dlgFind')
 *
 * click ('dlgFind', 'btnClose')
 *
 * if callbackState.isSet ():
 *
 *	print 'Waiting for callback to complete'
 *
 *	callbackRunning.wait ()
 *
 *	print 'callbackset'
 *
 * print 'test end'
 *
 * </pre>
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page removecallback removecallback
 * \section Syntax
 *
 * removecallback ('<window title\>')
 *
 * \section Description
 *
 * Remove the callback function that was registered with onwindowcreate
 *
 * \retval 1 on success, else LdtpExecutionError exception
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c, http://webcvs.freedesktop.org/ldtp/ldtp/src/ldtp-gui.c
 *
 * \section Example
 *
 * With respect to gedit application, replace dialog
 *
 * <pre>
 *
 * from ldtp import *
 *
 * import threading
 *
 * 
 * callbackRunning = threading.Event ()
 *
 * callbackRunning.clear ()
 *
 * callbackState = threading.Event ()
 *
 * callbackState.clear ()
 *
 * 
 * def cb ():
 *
 *	callbackState.set ()
 *
 *	waittillguiexist ('dlgReplace')
 *
 *	click ('dlgReplace', 'btnClose')
 *
 *	callbackState.clear ()
 *
 *	callbackRunning.set ()
 *
 *	print 'callbackend'
 *
 * 
 * onwindowcreate ('Replace', cb)
 *
 * click ('*gedit', 'btnReplace')
 *
 * click ('*gedit', 'btnFind')
 *
 * waittillguiexist ('dlgFind')
 *
 * click ('dlgFind', 'btnClose')
 *
 * if callbackState.isSet ():
 *
 *	print 'Waiting for callback to complete'
 *
 *	callbackRunning.wait ()
 *
 *	print 'callbackset'
 *
 * print 'test end'
 *
 * removecallback ('Replace')
 *
 * </pre>
 *
 * \author Nagappan A <nagappan@gmail.com>
 */

/** \page doesmenuitemexist doesmenuitemexist
 * \section Syntax
 *
 * doesmenuitemexist ('\<window name\>', '\<menu hierarchy\>') 
 *
 * \section Description
 *
 * checks if the specified menuitem specified in the menu hierarchy is present or not
 *
 * \section ImplementationDetails
 *
 * \retval 1 if the menuitem is present, else 0
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/menu-item.c
 *
 * \section Example
 *
 * With respect to gedit menu structure
 * 
 * doesselectmenuitem ('gedit', 'mnuFile;mnuNew')
 * 
 * this function is required mainly to check those menuitems which will not be present always. An example of this kind of a menuitem is the close tab menu item under menu file in firefox web browser. 
 *
 * \author prem.jothimani@gmail.com
 */

/**
 * \page startlog startlog
 * \section Syntax
 * 
 * startlog ('\<log file name\>', [0 or 1])
 * 
 * second argument is optional and 1 is default value
 * 
 * 0 - Append log to an existing file
 * 
 * 1 - Write log to a new file. If file already exist, then erase existing file content and start log
 * 
 * \section Description
 * 
 * Start logging on the specified file. Default log level set is logging.WARNING. Though this can be changed with setloglevel LDTP API.
 * 
 * \section ImplementationDetails
 * Log file will be created if log file is not present in any case. If second argument is 1, then existing file content will be erased. If second argument is 0, then new logs will be append to existing log.
 * 
 * \retval 1 on Success and 0 on error
 * 
 * \section Example
 * 
 * If we want to overwrite existing log file or create new log file:
 * 
 * startlog ('evolution.xml', 1)
 * 
 * If we want to append existing log file or create new log file:
 * 
 * startlog ('evolution.xml', 0)
 * 
 * or 
 * 
 * startlog ('evolution.xml')
 * 
 * \author Nagappan <nagappan@gmail.com>
 */

/**
 * \page stoplog stoplog
 * \section Syntax
 * 
 * stoplog ()
 * 
 * \section Description
 * 
 * Stop logging
 * 
 * \section ImplementationDetails
 * If a log file has been previously opened for logging, that file pointer will be closed. So that the new logging will not be appened to the log file.
 * 
 * \section Example
 * 
 * stoplog ()
 * 
 * \author Nagappan <nagappan@gmail.com>
 */


/**
 * \page startldtplog startldtplog
 * \section Syntax
 * 
 * startldtplog ('\<log file name\>', [0 or 1])
 * 
 * second argument is optional and 1 is default value
 * 
 * 0 - Append ldtplog to an existing file
 * 
 * 1 - Write ldtp log to a new file. If file already exist, then erase existing file content and start ldtp log
 * 
 * \section Description
 * 
 * Start ldtp logging on the specified file
 * 
 * \section ImplementationDetails
 * Log file will be created if log file is not present in any case. If second argument is 1, then existing file content will be erased. If second argument is 0, then new logs will be append to existing log.
 * 
 * \retval 1 on Success and 0 on error
 * 
 * \section Example
 * 
 * If we want to overwrite existing log file or create new log file:
 * 
 * startldtplog ('evolution.xml', 1)
 * 
 * If we want to append existing log file or create new log file:
 * 
 * startldtplog ('evolution.xml', 0)
 * 
 * or 
 * 
 * startldtplog ('evolution.xml')
 * 
 * \author Nagappan <nagappan@gmail.com>
 */

/**
 * \page stopldtplog stopldtplog
 * \section Syntax
 * 
 * stopldtplog ()
 * 
 * \section Description
 * 
 * Stop ldtplogging
 * 
 * \section ImplementationDetails
 * If a log file has been previously opened for logging, that file pointer will be closed. So that the new logging will not be appened to the log file.
 * 
 * \section Example
 * 
 * stopldtplog ()
 * 
 * \author Nagappan <nagappan@gmail.com>
 */

/** \page imagecapture imagecapture
 * \section Syntax
 *
 * imagecapture ([\<window name\>, [\<output file\>, (opt)\<resolution-x\>, (opt)\<resolution-y\>, (opt)startx, (opt)starty]])
 *
 * \section Description
 *
 * Capture snap-shot of the window. Where startx & starty are offset. If window name is not provided, then the complete X screen is captured. If output file name is not provided, then a temporary file will be created and the file name will be returned. File has to be explicitly deleted by the user.
 *
 * \section ImplementationDetails
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * from ldtputils import *
 *
 * imagecapture ('Terminal', 'out.png') # out.jpg will be created in current directory. Give absolute path to save it in some other directory.
 *
 * imagecapture () # Captures the complete X screen and saves in a temp file and returns the file name.
 *
 * \note Window title name is case sensitive
 *
 * \section Dependency
 *
 * Digwin binary - http://sourceforge.net/projects/ltfx If a specific window has to be captured, then digwin is used to get the window id.
 *
 * Import utility of ImageMagick - http://www.imagemagick.org/script/import.php # Mandatory dependency, if you want to use this function.
 *
 * \author Nagashree <mnagashree@novell.com>
 */

/** \page imagecompare imagecompare
 * \section Syntax
 *
 * imagecompare (imgfile1, imgfile2)
 *
 * \section Description
 *
 * Compares two images and returns difference of them in percentage. If PIL package is not installed, LdtpExecutionError exception will be thrown.
 *
 * \retval difference in percentage on successful image comaprison, else LdtpExecutionError exception
 *
 * Note: Script designer can decide the pass / fail criteria based on the diff percentage.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * from ldtputils import *
 *
 * imagecompare ('in.jpg', 'out.jpg') # Assuming that in.jpg and out.jpg are in current directory. File path should be absolute path.
 *
 * \section Dependency
 *
 * Python Imaging Library - http://www.pythonware.com/products/pil/
 *
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 * \author Veerapuram Varadhan <v.varadhan@gmail.com>
 */

/** \page blackoutregion blackoutregion
 * \section Syntax
 *
 * blackoutregion (infile, outfile, topx, topy, botx, boty)
 *
 * \section Description
 *
 * Blacks out the region in the image given by
 * 
 * top-coords - topx,topy bottom-coords - botx,boty
 * 
 * of the region 
 *
 * \section ImplementationDetails
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * blackoutregion ('in.jpg','out.jpg',100,100,200,200)
 *
 * \section Dependency
 *
 * Python Imaging Library - http://www.pythonware.com/products/pil/
 *
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 */

/** \page Classpstats Class pstats
 * \section Syntax
 *
 * \<Object\> = pstats(\<application name\>, \<time interval\>)
 * 
 * \<Object\>.start()
 * 
 * \<Object\>.stop() 
 *
 * \section Description
 *
 * This process when run gathers the Memory usage and CPU utilization of all the processes of a particular application at specific time interval.
 *
 * \section ImplementationDetails
 *
 * When this functionality is to be used in a python test script you need to create a new object for pstats class.
 * 
 * The arguments passed while instantiating this class are Application name and Time interval.
 * 
 * As soon as the \<Object\>.start() method is called in the test script, memory usage and CPU utilization of the application start getting logged into the ldtp log file.
 * 
 * When \<Object\>.stop is called the thread gathering the information stops. 
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * If I want the resource usage of all processes related to evolution to be logged every 2 seconds, the following statements need to be incorporated in the test script
 * 
 * xstats = pstats ('evolution', 2)
 * 
 * xstats.start ()
 * 
 * \<Test Script\>
 * 
 * xstats.stop() 
 *
 * \section Dependency
 *
 * This functionality depends on the pystatgrab (http://www.i-scream.org/pystatgrab/) package. Make sure you have it installed before using this memory and CPU utilization gathering function in your ldtp test scripts.
 *
 * \author Subodh Soni <subodhsoni@gmail.com>
 */

/** \page closeappwindow closeappwindow
 * \section Syntax
 *
 * closeappwindow ('\<Window title name\>')
 *
 * \section Description
 *
 * Close application window based on Window title. Returns 1 if success and 0 if unable to close the specified application window.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * from ldtputils import * 
 *
 * closeappwindow ('Bug Buddy')
 * 
 * \note Window title name should be case sensitive 
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 *
 */

/** \page wait wait
 * \section Syntax
 *
 * wait ([\<number of seconds to suspend current execution\>])
 *
 * \section Description
 *
 * Suspend execution for the specified time period. Default wait time is 5 seconds.
 *
 * \note Time in seconds.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * To suspend the current sequence of execution for 5 seconds
 * 
 * from ldtputils import * 
 *
 * wait (5) 
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 *
 */

/** \page launchapp launchapp
 * \section Syntax
 *
 * launchapp ('\<application binary name\>', [use additional environment variables for accessibility])
 *
 * second argument is optional and its default argument is 0. If second argument is passed as 1, then GTK_MODULES and GNOME_ACCESSIBILITY will be added to the enivronment variable
 *
 * \section Description
 *
 * Application name specified as an argument will be launched.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * Launch file-roller application.
 *
 * from ldtputils import * 
 *
 * launchapp ('file-roller')
 *
 * launchapp ('gaim', 1) # Invoke the application after setting environment variables
 *
 * launchapp ('file-roller /home/ldtp/test.tar.gz', 0) # Invoke the application with optional command line argument
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 *
 */

/** \page getactivewin getactivewin
 * \section Syntax
 *
 * getactivewin ()
 *
 * \section Description
 *
 * 
 *
 * \retval The active window title string.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * title = getactivewin ()
 * 
 * print 'Current active window title - ' + title
 * 
 * Gets the current active window title (window that is currently in focus). 
 *
 * \section Dependency
 *
 * ltfx binary - http://sourceforge.net/projects/ltfx
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 *
 */

/** \page windowexists windowexists
 * \section Syntax
 *
 * windowexists ('\<window name\>')
 *
 * \section Description
 *
 * Check window name exists with the given name.
 *
 * \retval 1 if window exist and 0 otherwise.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * windowexists ('Mozilla Firefox')
 *
 * \section Dependency
 *
 * ltfx binary - http://sourceforge.net/projects/ltfx
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 *
 */

/** \page partialexists partialexists
 * \section Syntax
 *
 * partialexists ('\<window name\>')
 *
 * \section Description
 *
 * Check window name partially matches with the given name.
 *
 * \retval 1 if window exist and 0 otherwise.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * partialexists ('Firefox')
 *
 * \section Dependency
 *
 * ltfx binary - http://sourceforge.net/projects/ltfx
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 *
 */

/** \page activatewinpartialname activatewinpartialname
 * \section Syntax
 *
 * activatewinpartialname ('\<window name\>')
 *
 * \section Description
 *
 * Activate window based on the given name that matches partially.
 *
 * \retval 1 if window exist and 0 otherwise.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * activatewinpartialname ('Firefox')
 *
 * \section Dependency
 *
 * ltfx binary - http://sourceforge.net/projects/ltfx
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 *
 */

/** \page typekey typekey
 * \section Syntax
 *
 * typekey ('\<string to be typed\>')
 *
 * \section Description
 *
 * On the current focus area, the string given as argument will be typed.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section ImplementationDetails
 *
 * \retval 1 if window exist and 0 otherwise.
 * 
 * This function supports
 * 
 * \<alt\> - for alt key
 * 
 * \<ctrl\> - for control key
 * 
 * \<shift\> - for pressing shift key
 * 
 * \<enter\> - for pressing enter key
 * 
 * \<tab\> - for pressing tab key
 * 
 * \<del\> - for pressing del key
 * 
 * \<bksp\> - for pressing back space key
 * 
 * \<f1\> - for pressing F1 function key
 * 
 * ...
 * 
 * \<f12\> - for pressing F1 function key
 * 
 * \<up\> - for pressing up arrow key
 * 
 * \<down\> - for pressing down arrow key
 * 
 * \<right\> - for pressing right arrow key
 * 
 * \<left\> - for pressing left arrow key
 * 
 * \<esc\> - for pressing escape key
 * 
 * \<space\> - for pressing space bar
 * 
 * \<home\> - for pressing home key
 * 
 * \<end\> - for pressing end key
 * 
 * \<pageup\> - for pressing page up key
 * 
 * \<pagedown\> - for pressing page down key
 * 
 *
 * \section Example
 *
 * typekey ('\<tab\>testing LDTP using ltfx\<enter\>')
 * 
 * Intially a tab key will be pressed and then text will be typed and then enter key will be pressed 
 *
 * \section Dependency
 *
 * ltfx binary - http://sourceforge.net/projects/ltfx
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 *
 */

/** \page activatewin activatewin
 * \section Syntax
 *
 * activatewin ('\<window name\>')
 *
 * \section Description
 *
 * Activate window based on the given name.
 *
 * \retval 1 if window exist and 0 otherwise.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * activatewin ('Mozilla Firefox')
 *
 * \section Dependency
 *
 * ltfx binary - http://sourceforge.net/projects/ltfx
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 *
 */

/** \page waitwinname waitwinname
 * \section Syntax
 *
 * waitwinname ('\<window name\>')
 *
 * \section Description
 *
 * Wait for window with the given name to appear.
 *
 * \retval 1 if window exist and 0 otherwise.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * waitwinname ('Mozilla Firefox')
 *
 * \section Dependency
 *
 * ltfx binary - http://sourceforge.net/projects/ltfx
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 *
 */

/** \page waitwinpartialname waitwinpartialname
 * \section Syntax
 *
 * waitwinpartialname ('\<window name\>')
 *
 * \section Description
 *
 * Wait for window with the given name partially matches to appear.
 *
 * \retval 1 if window exist and 0 otherwise.
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtputils.py
 *
 * \section Example
 *
 * waitwinpartialname ('Firefox')
 *
 * \section Dependency
 *
 * ltfx binary - http://sourceforge.net/projects/ltfx
 *
 * \author Nagappan <nagappan@gmail.com>
 * \author Shankar Ganesh <shagan.glare@gmail.com>
 *
 */

/** \page getpanelchildcount getpanelchildcount
 * \section Syntax
 *
 * getpanelchildcount ('\<window name\>', '\<component name\>')
 *
 * \section Description
 *
 * Gets the number of childs available under the given panel
 *
 * \retval Returns the child count if present, else -1, if unable to find child count
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/panel.c
 *
 * \section Example
 *
 * With respect to gedit application
 *
 * from ldtp import *
 *
 * getpanelchildcount ('*-gedit', 'pnl0')
 *
 * \author Nagappan <nagappan@gmail.com>
 *
 */

/** \page bindtext bindtext
 * \section Syntax
 *
 * bindtext ('\<package name\>', '\<locale directory\>'[, '\<mode\>'])
 *
 * \section Description
 *
 * 
 *
 * \retval Returns 1 on success, LdtpExecutionError exception will be thrown on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c, http://webcvs.freedesktop.org/ldtp/ldtp/src/localization.c
 *
 * \section Example
 *
 * For mo file with name: "/opt/gnome/share/locale/ta/LC_MESSAGES/gedit.mo"
 *
 * bindtext ('gedit', '/opt/gnome/share/locale')
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 *
 */

/** \page setlocale setlocale
 * \section Syntax
 *
 * setlocale (['\<LANG\>'])
 *
 * \section Description
 *
 * 
 *
 * \retval Returns 1 on success, LdtpExecutionError exception will be thrown on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c, http://webcvs.freedesktop.org/ldtp/ldtp/src/localization.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Premkumar J <prem.jothimani@gmail.com>
 *
 */

/** \page setloglevel setloglevel
 * \section Syntax
 *
 * setloglevel (\<log level\>)
 *
 * \section Options
 *
 * List of log levels are available here - http://docs.python.org/lib/module-logging.html
 *
 * \section Description
 *
 * Set the log level, which will be used in client side logging. Default log level set is logging.WARNING
 *
 * \section ImplementationDetails
 *
 * Implemented based on python logging formats
 *
 * \retval Returns 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtp.py
 *
 * \section Example
 *
 * setloglevel (logging.WARNING)
 *
 * \author Nagappan A <nagappan@gmail.com>
 *
 */

/** \page addlogger addlogger
 * \section Syntax
 *
 * addlogger ('\<log configuration file\>')
 *
 * \section Description
 *
 * Add more python logging formats with a configuration file format based on python logging format
 *
 * \section ImplementationDetails
 *
 * Implemented based on python logging formats
 *
 * \retval Returns 1 on success
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtp.py
 *
 * \section Example
 *
 * addlogger ('/etc/ldtp.conf')
 *
 * \section Configration
 *
 * Refer: Python logging format configuration file
 *
 * \author Nagappan A <nagappan@gmail.com>
 *
 */

/** \page mouseleftclick mouseleftclick
 * \section Syntax
 *
 * mouseleftclick ('\<window name\>', '\<object name\>')
 *
 * \section Description
 *
 * 
 *
 * \retval Returns 1 on success, LdtpExecutionError exception will be thrown on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/device.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Prashanth Mohan <prashmohan@gmail.com>
 *
 */

/** \page mouserightclick mouserightclick
 * \section Syntax
 *
 * mouserightclick ('\<window name\>', '\<object name\>')
 *
 * \section Description
 *
 * 
 *
 * \retval Returns 1 on success, LdtpExecutionError exception will be thrown on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/device.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Prashanth Mohan <prashmohan@gmail.com>
 *
 */

/** \page mousemove mousemove
 * \section Syntax
 *
 * mousemove ('\<window name\>', '\<object name\>')
 *
 * \section Description
 *
 * 
 *
 * \retval Returns 1 on success, LdtpExecutionError exception will be thrown on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/device.c
 *
 * \section Example
 *
 * \todo
 *
 * \author Prashanth Mohan <prashmohan@gmail.com>
 *
 */

/** \page enterstring enterstring
 * \section Syntax
 *
 * enterstring ('\<window name\>', '\<object name\>', '\<data\>')
 *
 * \section Description
 *
 * Functionality of enterstring is similar to typekey of LTFX project. Main difference is this function works based on accessibility. So, we could specify the window name, object name and finally the data string.
 *
 * \retval Returns 1 on success, LdtpExecutionError exception will be thrown on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/device.c
 *
 * \section Example
 *
 * enterstring ('*-gedit', 'txt0', 'Testing LDTP\'s enterstring function')
 *
 * \author Prashanth Mohan <prashmohan@gmail.com>
 *
 */

/** \page generatekeyevent generatekeyevent
 * \section Syntax
 *
 * generatekeyevent ('\<data\>')
 *
 * \section Description
 *
 * Functionality of generatekeyevent is similar to typekey of LTFX project.
 *
 * \section ImplementationDetails
 *
 * Used SPI_generateKeyboardEvent to generate the keyboard events.
 *
 * \retval Returns 1 on success, LdtpExecutionError exception will be thrown on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/device.c
 *
 * \section Example
 *
 * generatekeyevent ('Testing LDTP\'s enterstring function')
 *
 * \author Prashanth Mohan <prashmohan@gmail.com>
 *
 */

/** \page generatemouseevent generatemouseevent
 * \section Syntax
 *
 * generatemouseevent (x, y [,'\<options\>'])
 *
 * \section Description
 *
 * Functionality of generatemouseevent, generates the default (left
 * click) or specified mouse event in the given X and Y
 * coordinates.
 *
 * \subsection Note
 *
 * This functionality depends on screen resolution / coordinates. Also
 * the event will be generated on the currently focused window.
 *
 * \subsection Options
 *
 * b1c - Left button click
 *
 * b2c - Middle button click
 *
 * b3c - Right button click
 *
 * b1d - Left button double click
 *
 * b2d - Middle button double click
 *
 * b3d - Right button double click
 *
 * abs - absolute motion
 *
 * rel - relative motion
 *
 * \section ImplementationDetails
 *
 * Used SPI_generateMouseEvent to generate the mouse events.
 *
 * \retval Returns 1 on success, LdtpExecutionError exception will be thrown on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 *
 * \section Example
 *
 * generatemouseevent (100, 200)
 *
 *
 * generatemouseevent (100, 200, "b1d") # Generate double click event
 *
 * \author Nagappan <nagappan@gmail.com>
 *
 */

/** \page stopscriptengine stopscriptengine
 * \section Syntax
 *
 * stopscriptengine ()
 *
 * \section Description
 *
 * Stops the LDTP engine, free all the resources. If we want to stop LDTP service, we can use this function to silently die.
 *
 * \retval None
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c
 *
 * \section Example
 *
 * from ldtp import *
 *
 * stopscriptengine ()
 *
 * \author Nagappan <nagappan@gmail.com>
 *
 */

/** \page hasstate hasstate
 * \section Syntax
 *
 * hasstate ('<window name\>', '<object name\>', <object SPI state-1>[, ..., <object SPI state-n>])
 *
 * \section Description
 *
 * Checks the SPI state of the given object.
 *
 * \retval 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/client-handler.c, http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtp.py
 *
 * \section Example
 *
 * With respect to gedit window, first tab
 *
 * from ldtp import *
 *
 * hasstate ('*-gedit', 'txt0', state.FOCUSABLE)
 *
 * hasstate ('*-gedit', 'txt0', state.FOCUSABLE + state.VISIBLE)
 *
 * \author Nagappan <nagappan@gmail.com>
 *
 */

/** \page press press
 * \section Syntax
 *
 * press ('<window name\>', '<object name\>')
 *
 * \section Description
 *
 * Toggle's the button state.
 *
 * \retval 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/src/toggle-button.c, http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtp.py
 *
 * \section Example
 *
 * \todo
 *
 * \author Rodney Dawes <dobey@novell.com>
 *
 */

/** \page objectexist objectexist
 * \section Syntax
 *
 * objectexist ('<window name\>', '<object name\>')
 *
 * \section Description
 *
 * To check whether a component exist in a given window
 *
 * \retval 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtp.py
 *
 * \section Example
 *
 * \todo
 *
 * \author Rodney Dawes <dobey@novell.com>
 *
 */

/** \page objtimeout objtimeout
 * \section Syntax
 *
 * objtimeout ([guiTimeOut])
 *
 * \section Description
 *
 * Instead of setting an environment variable you can change the object time out from default 5 seconds to what ever time period. guiTimeOut should be > 0.
 *
 * \retval 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtp.py
 *
 * \section Example
 *
 * objtimeout (10)
 *
 * \author Nagappan A <nagappan@gmail.com>
 *
 */

/** \page guitimeout guitimeout
 * \section Syntax
 *
 * guitimeout ([guiTimeOut])
 *
 * \section Description
 *
 * Instead of setting an environment variable you can change the object time out from default 30 seconds to what ever time period. guiTimeOut should be > 0.
 *
 * \retval 1 on success, 0 on failure
 *
 * Refer: http://webcvs.freedesktop.org/ldtp/ldtp/python/ldtp.py
 *
 * \section Example
 *
 * guitimeout (10)
 *
 * \author Nagappan A <nagappan@gmail.com>
 *
 */
