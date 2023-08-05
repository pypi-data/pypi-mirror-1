#############################################################################
#
#  Linux Desktop Testing Project http://ldtp.freedesktop.org
# 
#  Author:
#     Veerapuram Varadhan <v.varadhan@gmail.com>
#     Prashanth Mohan <prashmohan@gmail.com>
#     Venkateswaran S <wenkat.s@gmail.com>
#     Nagappan Alagappan <nagappan@gmail.com>
# 
#  Copyright 2004 - 2007 Novell, Inc.
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

__author__ = "Nagappan A <nagappan@gmail.com>, Veerapuram Varadhan <v.varadhan@gmail.com>, Prashanth Mohan <prashmohan@gmail.com>, Venkateswaran S <wenkat.s@gmail.com>"
__maintainer__ = "Nagappan A <nagappan@gmail.com>"
__version__ = "1.0.0"

import socket, os, types, sys, struct, traceback, time, commands
import threading, re, atexit, random, thread, select
from xml.parsers.expat import ExpatError
from xml.dom.minidom import parse, parseString
from xml.sax import saxutils
import ldtplib
from ldtplib.ldtplibutils import *

_ldtpDebug = os.getenv ('LDTP_DEBUG')

def generatexml (commandId, *args):
	"""This Function will parse some information into an LDTP packet
	INPUT: commandId --> command_id
	args --> [,window_name[,object_name[,args...]]]

	OUTPUT: returns a string in the LDTP packet (XML lib2) format"""
	# Argument length
	argsLen = len (args)
	
	_xml = '<?xml version=\"1.0\"?>' ## should this header be there in the packets?
	_xml += '<REQUEST>'
	# Fill action name
	_xml = _xml + '<ACTION>' + str (commandId) + '</ACTION>'
	if _ldtpDebug != None:
		print str (commandId) + ' (',
	if argsLen >= 1:
		_xml = _xml + '<ID>' + saxutils.escape (args [0]) + '</ID>'
	if commandId != command.INITAPPMAP and argsLen >= 2:
		_xml = _xml + '<CONTEXT>' + saxutils.escape (args [1]) + '</CONTEXT>'
		if _ldtpDebug != None:
			print args[1],
	if argsLen >= 3:
		_xml = _xml + '<COMPONENT>' + saxutils.escape (args [2]) + '</COMPONENT>'
		if _ldtpDebug != None:
			print ', ' + args[2],
	if argsLen >= 4:
		_xml = _xml + '<ARGUMENTS>'
		# Fixme: Dirty hack :( start
		if type (args[3]) == list:
			args = args[3]
			args.insert (0, '')
			args.insert (1, '')
			args.insert (2, '')
			argsLen = len (args)
		# Fixme: Dirty hack :( end
		for index in range (3, argsLen):
			if args[index] != None and args[index] != '':
				_xml = _xml + '<ARGUMENT><![CDATA[' + args[index] + ']]></ARGUMENT>'
				if _ldtpDebug != None:
					print ', ' + args[index],
		_xml = _xml + '</ARGUMENTS>'
	if commandId == command.INITAPPMAP:
		_xml = _xml + '<ARGUMENTS>'
		_xml = _xml + '<ARGUMENT><![CDATA[' + args[1] + ']]></ARGUMENT>'
		_xml = _xml + '</ARGUMENTS>'
		if _ldtpDebug != None:
			print '( ' + args[1],
	if _ldtpDebug != None:
		print ')'
	_xml += '</REQUEST>'
	return _xml

def parseobjectlist (xmldata):
	"""Returns the object list"""
	try:
		_objList = None
		dom = parseString (xmldata)
		try:
			_objList   = dom.getElementsByTagName ('OBJECTLIST')
		except IndexError:
			raise LdtpExecutionError ('Invalid Object List')
		if _objList == None:
			raise LdtpExecutionError ('Invalid Object List')
		taglist = []
		for dataelements in _objList:
			for data in dataelements.getElementsByTagName ('OBJECT'):
				taglist.append (getText (data.childNodes))
		return taglist
	except ExpatError, msg:
		raise LdtpExecutionError ('Parsing XML error: ' + str (msg))

def parsexml (xmlpacket):
	"""Returns the value obtained from the server's return LDTP packet"""

	_statusMsg      = None
	_statusCode     = None
	_serverResponse = None
	_responseType   = None
	_requestId      = None
	_serverResponse = None
	_responseObj    = None
	_serverResponseLen = 0

	try:
		dom = parseString (xmlpacket)
		try:
			_responseObj  = dom.getElementsByTagName ('RESPONSE')[0]
			_responseType = 'response'
		except IndexError:
			try:
				_responseObj   = dom.getElementsByTagName ('NOTIFICATION')[0]
				_responseType = 'notification'
			except IndexError, msg:
				raise LdtpExecutionError ('Invalid Response')
		try:
			_responseStatusObj = _responseObj.getElementsByTagName ('STATUS')[0]
			_statusCode = int (getText (_responseStatusObj.getElementsByTagName ('CODE')[0].childNodes))
			_statusMsg  = getText (_responseStatusObj.getElementsByTagName ('MESSAGE')[0].childNodes)
		except ValueError:
			raise LdtpExecutionError ('Invalid Status')
		except IndexError:
			raise LdtpExecutionError ('Invalid Status')
		try:
			data = _responseObj.getElementsByTagName ('DATA')[0]
			_serverResponse    = getCData (data.getElementsByTagName ('VALUE').item (0).childNodes).encode ('utf-8')
			_serverResponseLen = int (getText (data.getElementsByTagName ('LENGTH')[0].childNodes))
		except ValueError:
			raise LdtpExecutionError ('Invalid Data Length')
		except IndexError:
			# Data tag may not be present
			pass
		try:
			data = _responseObj.getElementsByTagName ('FILE')[0]
			fileName = getText (data.getElementsByTagName ('NAME').item (0).childNodes).encode ('utf-8')
			if os.path.exists (fileName) == False:
				raise LdtpExecutionError ('File %s does not exist' % fileName)
			fp = open (fileName)
			_serverResponse = ''
			for line in fp.readlines ():
				_serverResponse = _serverResponse + line
			_serverResponseLen = len (_serverResponse)
			#commands.getstatusoutput ('rm -f ' + fileName)
		except IndexError:
			# Data tag may not be present
			pass
		try:
			_requestId  = getText (_responseObj.getElementsByTagName ('ID')[0].childNodes)
		except IndexError:
			# On notification _requestId will be empty
			pass
	except ExpatError, msg:
		if msg.code == xml.parsers.expat.errors.XML_ERROR_NO_ELEMENTS:
			return None
		if xml.parsers.expat.ErrorString (msg.code) == xml.parsers.expat.errors.XML_ERROR_NO_ELEMENTS:
			return None
		raise LdtpExecutionError ('Parsing XML error: ' + str (msg))

	# Return all the respective values, let the calling function decide what to do with the values
	return _responseType, (_statusCode, _statusMsg, _requestId), (_serverResponseLen, _serverResponse)

def peekresponse ():
	return recvpacket (socket.MSG_PEEK)

def getresponse (packetId):
	while True:
		#print 'DEBUG', 'waiting for readflag', threading.currentThread ()
		_readFlag.wait ()
		#print 'DEBUG', 'readflag lock released'
		_readFlag.clear ()
		peekResponsePacket = peekresponse ()
		if peekResponsePacket == None:
			if _ldtpDebug != None and _ldtpDebug == '2':
				print 'Peekresponse None'
			raise LdtpExecutionError ('Server disconnected')
		if peekResponsePacket == '':
			if _ldtpDebug != None and _ldtpDebug == '2':
				print 'Peekresponse empty string'
			continue
		try:
			_responseType, _responseStatus, _responseData = parsexml (peekResponsePacket)
		except TypeError, msg:
			if _ldtpDebug != None and _ldtpDebug == '2':
				print 'TypeError', msg
			continue
		# For precautions, we are just checking, whether the packet is notification or not
		if _responseType == 'notification' or _responseType == None:
			continue
		if _responseStatus[2] == packetId:
			if _responseStatus [0] != 0 and _ldtpDebug != None:
				print '*** ' + _responseStatus [1]
			packet = recvpacket ()
			# As we have already parsed the packet,
			# we are just returning the parsed packet
			return _responseStatus, _responseData

def invokecallback (clientsocket, _responseType, _responseStatus, _responseData):
	packet = recvpacket (sockfd = clientsocket)
	# As we have already parsed the packet,
	# we are just going to invoke the callback function
	clientsock = None
	try:
		# Create a client socket
		clientsock = socket.socket (socket.AF_UNIX, socket.SOCK_STREAM)
	except socket.error,msg:
		raise LdtpExecutionError ('Error while creating UNIX socket  ' + str (msg))
	try:
		# Connect to server socket
		clientsock.connect (_socketPath)
	except TypeError:
		raise ConnectionLost ('Environment LDTP_AUTH_SOCK variable not set')

	global _serverPoll
	# Register newly created socket for polling
	_serverPoll.register (clientsock, select.POLLIN)

	# Add new client socket to socket fd pool
	_sockFdPool[threading.currentThread ()] = clientsock
	callback = _callbackFunctions.get (_responseData [1])
	_notificationFlag.set ()
	if (callable (callback)):
		callback ()
	# Unregister newly created socket from polling once its completed
	_serverPoll.unregister (clientsock)

def invokeltfxcallback (clientsocket, callback):
	clientsock = None
	try:
		# Create a client socket
		clientsock = socket.socket (socket.AF_UNIX, socket.SOCK_STREAM)
	except socket.error,msg:
		raise LdtpExecutionError ('Error while creating UNIX socket  ' + str (msg))
	try:
		# Connect to server socket
		clientsock.connect (_socketPath)
	except TypeError:
		raise ConnectionLost ('Environment LDTP_AUTH_SOCK variable not set')

	global _serverPoll
	# Register newly created socket for polling
	_serverPoll.register (clientsock, select.POLLIN)

	# Add new client socket to socket fd pool
	_sockFdPool[threading.currentThread ()] = clientsock
	_notificationFlag.set ()
	if (callable (callback)):
		callback ()
	# Unregister newly created socket from polling once its completed
	_serverPoll.unregister (clientsock)

class PollServer (threading.Thread):
	def __init__ (self):
		threading.Thread.__init__ (self)
		self._events = None
	def run (self):
		try:
			self.start_polling_server ()
		except:
			try:
				raise LdtpExecutionError (str (traceback.print_exc ()))
			except AttributeError:
				pass
			except:
				pass
	def start_polling_server (self):
		self._serverDisconnected = False
		global _serverPoll
		_serverPoll = select.poll ()
		_serverPoll.register (_mainSock, select.POLLIN)

		while True:
			try:
				#print 'DEBUG', 'entering poll'
				self._events = _serverPoll.poll ()
				#print 'DEBUG', 'poll break'
			except socket.error, msg:
				break
			except:
				_serverPoll.unregister (_mainSock)
				sys.exit ()
			try:
				if self._events == None:
					break
				for i in range (0, len (self._events)):
					#print 'DEBUG', i
					# if (self._events[i][1] & select.POLLERR or
					#     self._events[i][1] & select.POLLHUP or
					#     self._events[i][1] & select.POLLNVAL):
					# 	print 'DEBUG Disconnected', self._events[i][1]
					# 	print 'DEBUG', self._events[i][1] & select.POLLERR
					# 	print 'DEBUG', self._events[i][1] & select.POLLHUP
					# 	print 'DEBUG', self._events[i][1] & select.POLLNVAL
					# 	# If interrupted stop polling
					# 	self._serverDisconnected = True
					# 	break
					if (self._events[i][1] & select.POLLIN or self._events[i][1] & select.POLLPRI):
						_sockFdPool[threading.currentThread ()] = socket.fromfd (self._events[i][0],
													 socket.AF_UNIX,
													 socket.SOCK_STREAM)
						try:
							# print 'DEBUG', 'handle packet start', \
							# self._events[i][1] & select.POLLIN, \
							# self._events[i][1] & select.POLLPRI
							if self.handle_packet () == None:
								self._serverDisconnected = True
								# _readFlag.set ()
								break
						except LdtpExecutionError, msg:
							self._serverDisconnected = True
							# _readFlag.set ()
							break
					elif (self._events[i][1] & select.POLLNVAL):
						# Unregister newly created socket from polling once its completed
						_serverPoll.unregister (self._events[i][0])
					else:
						self._serverDisconnected = True
						break
				if self._serverDisconnected == True:
					break
			# Checking this exception due to bug # 333090 comment # 6
			except TypeError:
				_serverPoll.unregister (_mainSock)
				sys.exit ()
	def trace_window (self):
		global _ltfxCallbackFunctions
		try:
			if _notificationFlag.isSet () == True:
				# Let us allow only one callback function to execute at any point of time
				_notificationFlag.wait ()
				_notificationFlag.clear ()
				if _ltfxCallbackFunctions == {}:
					_notificationFlag.set ()
					return ''
				window_info = commands.getstatusoutput ('digwin -c')
				if window_info[0] != 0:
					_notificationFlag.set ()
					return ''
				callback = None
				regexp = re.compile ('\n+')
				window_list = regexp.split (window_info[1])
				for i in _ltfxCallbackFunctions:
					for j in window_list:
						try:
							regexp = re.compile (i)
							if z.search (j).group () != '':
								callback = _ltfxCallbackFunctions.get (i)
								thread.start_new_thread (invokeltfxcallback,
											 (_sockFdPool.get (threading.currentThread ()),
											  callback))
							else:
								_notificationFlag.set ()
								return ''
						except AttributeError:
							pass
				_notificationFlag.set ()
			else:
				# CPU goes high for some time, if this delay is not there
				# as the notification packet is still in the Queue, but the
				# new spanned thread takes some time to receive the notification packet
				# So this delay is required
				time.sleep (1)
			return ''
		except LdtpExecutionError:
			#_readFlag.set ()
			return ''
		except KeyboardInterrupt:
			return None
	def handle_packet (self):
		try:
			self._peekResponsePacket = peekresponse ()
		except KeyboardInterrupt:
			return None
		_responseType = None
		try:
			if self._peekResponsePacket == None:
				# When there is no data to read let us quit
				return None
			if self._peekResponsePacket != '':
				_responseType, _responseStatus, _responseData = parsexml (self._peekResponsePacket)
				if _responseType == None:
					return None
			else:
				_readFlag.set ()
		except TypeError:
			return ''
		except LdtpExecutionError:
			#_readFlag.set ()
			return ''
		except KeyboardInterrupt:
			return None
		try:
			if _responseType == 'notification':
				if _notificationFlag.isSet () == True:
					# Let us allow only one callback function to execute at any point of time
					_notificationFlag.wait ()
					_notificationFlag.clear ()
					thread.start_new_thread (invokecallback,
								 (_sockFdPool.get (threading.currentThread ()),
								  _responseType, _responseStatus, _responseData))
				else:
					# CPU goes high for some time, if this delay is not there
					# as the notification packet is still in the Queue, but the
					# new spanned thread takes some time to receive the notification packet
					# So this delay is required
					time.sleep (1)
			else:
				# print 'DEBUG readflag set 1'
				_readFlag.set ()
		except KeyboardInterrupt:
			return None
		return ''
	def shutdown (self):
		_readFlag.set ()

def shutdown ():
	if threading.activeCount () > 1:
		thread.exit ()
	stoplog ()
	sys.exit ()

commands.getstatusoutput ('rm -f /tmp/LDTP-XML-*')
_display = os.getenv ('DISPLAY')

if _display == None:
	raise LdtpExecutionError ('Missing DISPLAY environment variable. Running in text mode ?')	

_socketPath = '/tmp/ldtp-' + os.getenv ('USER') + '-' + _display

_ldtpUseTcp = False
_ldtpServerAddr = None
_ldtpServerPort = None
if os.environ.has_key("LDTP_SERVER_ADDR"):
	_ldtpServerAddr = os.environ["LDTP_SERVER_ADDR"]
	if os.environ.has_key("LDTP_SERVER_PORT"):
		_ldtpServerPort = int (os.environ["LDTP_SERVER_PORT"])
	else:
		_ldtpServerPort = 23456
	_ldtpUseTcp = True

# Init callback functions dictionary
_callbackFunctions = {}

# Init callback functions dictionary
_ltfxCallbackFunctions = {}

# Create read flag
_readFlag = threading.Event ()
# Clear the flag by default
_readFlag.clear ()

# Create notification flag
_notificationFlag = threading.Event ()
# Set the flag by default
_notificationFlag.set ()

# Contains poll fd's
_serverPoll = None

if _socketPath == '':
	raise ConnectionLost ('Server not running')
try:
	# Create a client socket
	_mainSock = None
	if _ldtpUseTcp:
		_mainSock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	else:
		_mainSock = socket.socket (socket.AF_UNIX, socket.SOCK_STREAM)
except socket.error,msg:
	if _ldtpUseTcp:
		raise LdtpExecutionError ('Error while creating socket  ' + str (msg))
	else:
		raise LdtpExecutionError ('Error while creating UNIX socket  ' + str (msg))	

# Let us retry connecting to the server for 3 times
_retryCount = 0

while True:
	try:
		try:
			# Connect to server socket
			if _ldtpUseTcp:
				_mainSock.connect((_ldtpServerAddr, _ldtpServerPort))
			else:
				_mainSock.connect (_socketPath)
			break
		except TypeError:
			raise ConnectionLost ('Environment LDTP_AUTH_SOCK variable not set')
	except socket.error, msg:
		if _retryCount == 3:
			raise ConnectionLost ('Could not establish connection ' + str (msg))
		_retryCount += 1
		#If we are not trying to connect to a remote server then we can attempt to
		#startup the ldtp server and then try to re-connect to it.
		if not _ldtpUseTcp:
			_pid = os.fork ()
			if _pid == 0:
				try:
                                    os.execvpe ('ldtp', [''], os.environ)
				except OSError:
					raise LdtpExecutionError ('ldtp executable not in PATH')
			else:
				# Let us wait for 1 second, let the server starts
				time.sleep (1)

_sockFdPool = ldtplib.ldtplibutils.sockFdPool
_sockFdPool [threading.currentThread ()] = _mainSock

# Start polling server
_pollThread = PollServer ()
_pollThread.setDaemon (True)
_pollThread.start ()
atexit.register (_pollThread.shutdown)
atexit.register (shutdown)

logger  = None
xmlhdlr = None

def selectevent (windowName, componentName, calendarEventName):
	"""Selects the row from the table of calendar events based on the calendar event name specified
	INPUT: selectevent ('<window name>', '<Calendar_view name>', '<calendar event name>')

	OUTPUT: Returns 1 on success and 0 on error."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTEVENT)
		_message = generatexml (command.SELECTEVENT, _requestId, windowName, componentName, calendarEventName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectevent failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))
			
def selecteventindex (windowName, componentName, eventNumber):
	"""Select an event from a calendar table using its index. Index for a calendar event starts from 1.
	INPUT: selecteventindex ('<window name>', '<component name>', <event number>)

	OUTPUT: Returns 1 on success and 0 on error."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTEVENTINDEX)
		_message = generatexml (command.SELECTEVENTINDEX, _requestId, windowName, componentName, str (eventNumber))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selecteventindex failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))
			
def verifyeventexist (windowName, componentName):
	"""verifies whether any events are present in a calendar table
	INPUT: verifyeventexist ('<window name>', '<component name>')

	OUTPUT: Returns 1 on success and 0 on no events."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYEVENTEXIST)
		_message = generatexml (command.VERIFYEVENTEXIST, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def check (windowName, componentName):
	"""Check (tick) the check box state. 
	INPUT: check ('<window name>', '<component name>') 

	OUTPUT: Returns 1 if state is checked, else 0."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.CHECK)
		_message = generatexml (command.CHECK, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('check failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))
			
def uncheck (windowName, componentName):
	"""Uncheck (un-tick) the check state.
	INPUT: uncheck ('<window name>', '<component name>')

	OUTPUT: Returns 1 if state is unchecked, else 0."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.UNCHECK)
		_message = generatexml (command.UNCHECK, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('uncheck failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def click (windowName, componentName):
	"""click on radio button / check box / push button/ combo box/ radio menu item/ toggle button/ radio button.
	INPUT: click ('<window name>', '<component name>')

	OUTPUT: Clicks the component_name."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.CLICK)
		_message = generatexml (command.CLICK, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('click failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def press (windowName, componentName):
	"""tell the button to press itself
	INPUT: press ('<window name>', '<component name>')

	OUTPUT: Presses the component_name."""
	try:
		_requestId = threading.currentThread ().getName () + str (command.PRESS)
		_message = generatexml (command.PRESS, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('press failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def menucheck (windowName, componentName):
	"""menucheck (tick) the menu item check state. 
	INPUT: menucheck ('<window name>', '<component name>') 

	OUTPUT: Returns 1 if state is checked, else 0."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.MENUCHECK)
		_message = generatexml (command.MENUCHECK, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('menucheck failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def menuuncheck (windowName, componentName):
	"""menuuncheck (un-tick) the check state.
	INPUT: menuuncheck ('<window name>', '<component name>')

	OUTPUT: Returns 1 if state is unchecked, else 0."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.MENUUNCHECK)
		_message = generatexml (command.MENUUNCHECK, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('menuuncheck failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def verifycheck (windowName, componentName):
	"""Checks the state of check box.
	INPUT: verifycheck ('<window name>', '<component name>')

	OUTPUT: If check box state is checked, then returns 1, else 0."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYCHECK)
		_message = generatexml (command.VERIFYCHECK, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifyuncheck (windowName, componentName):
	"""Checks the state of check box.
	INPUT: verifyuncheck ('<window name>', '<component name>')

	OUTPUT: If check box state is un-checked, then returns 1, else 0."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYUNCHECK)
		_message = generatexml (command.VERIFYUNCHECK, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifymenucheck (windowName, menuItem):
	"""
	INPUT: verifymenucheck ('<window name>', '<menu item>')

	OUTPUT: 1 on success, 0 on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYMENUCHECK)
		_message = generatexml (command.VERIFYMENUCHECK, _requestId, windowName, menuItem)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifymenuuncheck (windowName, menuItem):
	"""
	INPUT: verifymenuuncheck ('<window name>', '<menu item>')

	OUTPUT: 1 on success, 0 on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYMENUUNCHECK)
		_message = generatexml (command.VERIFYMENUUNCHECK, _requestId, windowName, menuItem)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifydropdown (windowName, componentName):
	"""
	INPUT: verifydropdown ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYDROPDOWN)
		_message = generatexml (command.VERIFYDROPDOWN, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

# CheckMenuItem Functions

def selectmenuitem (windowName, menuHierarchy):
	"""Selects the menu item specified.
	INPUT: selectmenuitem ('<window name>', '<menu hierarchy>')

	OUTPUT: 1 on success, LdtpExecutionError on failure."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTMENUITEM)
		_message = generatexml (command.SELECTMENUITEM, _requestId, windowName, menuHierarchy)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectmenuitem failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

#  Combobox Functions

def hidelist (windowName, componentName):
	""" Hides combo box drop down list in the current dialog. 
	Suppose in previous operation one testcase has clicked on combo box, 
	its drop down list will be displayed. If further no any operation has 
	been done on that combo box then to close that drop down list 'HideList' 
	action is required.
	INPUT: hidelist ('<window name>', '<component name>') 

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.HIDELIST)
		_message = generatexml (command.HIDELIST, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('hidelist failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def selectindex (windowName, componentName, index):
	""" SelectIndex action will select an item from combo box where value of index is pointing to its position in list/menu.
	INPUT: selectindex ('<window name>', '<component name>', <index>)

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTINDEX)
		_message = generatexml (command.SELECTINDEX, _requestId, windowName, componentName, str (index))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectindex failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def settextvalue (windowName, componentName, text):
	"""puts the text into the component given by the component name
	INPUT: settextvalue ('<window name>', '<component name>', '<text>')

	OUTPUT: returns 1 on success and 0 otherwise"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SETTEXTVALUE)
		_message = generatexml (command.SETTEXTVALUE, _requestId, windowName, componentName, text)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('settextvalue failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def gettextvalue (windowName, componentName, startPosition = None, endPosition = None):
	"""
	INPUT: gettextvalue ('<window name>', '<component name>', [start position], [end position])

	OUTPUT: returns 1 on success and 0 otherwise"""
	if startPosition != None:
		startPosition = str (startPosition)
	if endPosition != None:
		endPosition = str (endPosition)
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETTEXTVALUE)
		_message = generatexml (command.GETTEXTVALUE, _requestId, windowName, componentName, startPosition, endPosition)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('gettextvalue failed: ' + _responseStatus [1])
		return _responseData [1]
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def activatetext (windowName, componentName):
	"""
	INPUT: activatetext ('<window name>', '<component name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.ACTIVATETEXT)
		_message = generatexml (command.ACTIVATETEXT, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('activatetext failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def appendtext (windowName, componentName, text):
	"""
	INPUT: appendtext ('<window name>', '<component name'>)

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.APPENDTEXT)
		_message = generatexml (command.APPENDTEXT, _requestId, windowName, componentName, text)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('appendtext failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getcursorposition (windowName, componentName):
	"""
	INPUT: windowName --> Name in the title bar
	       componentName --> Name of the object (TextBox)

	OUTPUT: postion of the text cursor in the object (integer)"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETCURSORPOSITION)
		_message = generatexml (command.GETCURSOR, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getcursorposition failed: ' + _responseStatus [1])
		return long (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def setcursorposition (windowName, componentName, position):
	"""
	INPUT: windowName --> Name in the title bar
	       componentName --> Name of the object (TextBox)
	       position --> Position in the TextBox where cursor is to be moved to

	OUTPUT: None"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SETCURSORPOSITION)
		_message = generatexml (command.SETCURSORPOSITION, _requestId, windowName, componentName, str (position))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('setcursorposition failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))
	
def capturetofile (windowName, componentName, fileName = None):
	"""
	INPUT: capturetofile ('<window name>', '<component name>'[, '<file name>'])

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.CAPTURETOFILE)
		_message = generatexml (command.CAPTURETOFILE, _requestId, windowName, componentName, fileName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('capturetofile failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def showlist (windowName, componentName):
	""" Displays combo box drop down list in the current dialog.
	INPUT: showlist ('windowName', 'componentName')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SHOWLIST)
		_message = generatexml (command.SHOWLIST, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('showlist failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def verfyhidelist (windowName, componentName):
	""" Verifies if combo box drop down list in the current dialog is not visible.
	INPUT: verfyhidelist ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERFYHIDELIST)
		_message = generatexml (command.VERIFYHIDELIST, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifyselect (windowName, componentName, selectArgument):
	""" VerfySelect action will verify if combo box is set to value given in argument.
	INPUT: verifyselect ('<window name>', '<component name>', '<argument>')

	OUTPUT: VerifySelect function will try to find if text box associated with combo box
	is set to value specified in the argument."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSELECT)
		_message = generatexml (command.VERIFYSELECT, _requestId, windowName, componentName, selectArgument)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifysettext (windowName, componentName, text):
	""" checks if the text is inserted into the component given by the component name
	INPUT: verifysettext ('<window name>', '<component name>', '<text>')

	OUTPUT: returns 1 if the text is inserted into the specified component else returns 0 """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSETTEXT)
		_message = generatexml (command.VERIFYSETTEXT, _requestId, windowName, componentName, text)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifyshowlist (windowName, componentName):
	""" Verifies if combo box drop down list in the current dialog is visible.
	INPUT: verifyshowlist ('<window name>', '<component name>')

	OUTPUT: Combo box will generally have a list as its child or a menu as its child. 
	So this function gets object handle of list or menu object, checks if list or 
	menu items of combo box is visible, if yes then return zero else minus one."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSHOWLIST)
		_message = generatexml (command.VERIFYSHOWLIST, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def comboselect (windowName, componentName, menuItemName):
	"""Select a menu item or list item in a combo box
	INPUT: comboselect ('<window name>', '<component name>', '<menu item name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.COMBOSELECT)
		_message = generatexml (command.COMBOSELECT, _requestId, windowName, componentName, menuItemName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('comboselect failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def comboselectindex (windowName, componentName, index):
	"""
	INPUT: comboselectindex ('<window name>', '<component name>', <index>)

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.COMBOSELECTINDEX)
		_message = generatexml (command.COMBOSELECTINDEX, _requestId, windowName, componentName, str (index))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('comboselectindex failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def comparetextproperty (windowName, componentName, textProperty, startPosition = None, endPosition = None):
	"""
	INPUT: comparetextproperty ('<window name>', '<component name>', <text property>[, <start position>[, <end position>]])

	OUTPUT: 1 on success, 0 on failure"""
	if startPosition != None:
		startPosition = str (startPosition)
	if endPosition != None:
		endPosition = str (endPosition)
	try:
		_requestId  = threading.currentThread ().getName () + str (command.COMPARETEXTPROPERTY)
		_message = generatexml (command.COMPARETEXTPROPERTY, _requestId, windowName, componentName, textProperty, startPosition, endPosition)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def containstextproperty (windowName, componentName, textProperty, startPosition = None, endPosition = None):
	"""
	INPUT: containstextproperty ('<window name>', '<component name>', <text property>[, <start position>[, <end position>]])

	OUTPUT: 1 on success, 0 on failure"""
	if startPosition != None:
		startPosition = str (startPosition)
	if endPosition != None:
		endPosition = str (endPosition)
	try:
		_requestId  = threading.currentThread ().getName () + str (command.CONTAINSTEXTPROPERTY)
		_message = generatexml (command.CONTAINSTEXTPROPERTY, _requestId, windowName, componentName, textProperty, startPosition, endPosition)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def gettextproperty (windowName, componentName, startPosition = None, endPosition = None):
	"""
	INPUT: gettextproperty ('<window name>', '<component name>'[, <start position>[, <end position>]])

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	if startPosition != None:
		startPosition = str (startPosition)
	if endPosition != None:
		endPosition = str (endPosition)
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETTEXTPROPERTY)
		_message = generatexml (command.GETTEXTPROPERTY, _requestId, windowName, componentName, startPosition, endPosition)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('gettextproperty failed: ' + _responseStatus [1])
		return _responseData [1]
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def copytext (windowName, componentName, startPosition = None, endPosition = None):
	"""
	INPUT: copytext ('<window name>', '<component name>'[, <start position>[, <end position>]])

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	if startPosition != None:
		startPosition = str (startPosition)
	if endPosition != None:
		endPosition = str (endPosition)
	try:
		_requestId  = threading.currentThread ().getName () + str (command.COPYTEXT)
		_message = generatexml (command.COPYTEXT, _requestId, windowName, componentName, startPosition, endPosition)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('copytext failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def cuttext (windowName, componentName, startPosition = None, endPosition = None):
	"""
	INPUT: cuttext ('<window name>', '<component name>'[, <start position>[, <end position>]])

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	if startPosition != None:
		startPosition = str (startPosition)
	if endPosition != None:
		endPosition = str (endPosition)
	try:
		_requestId  = threading.currentThread ().getName () + str (command.CUTTEXT)
		_message = generatexml (command.CUTTEXT, _requestId, windowName, componentName, startPosition, endPosition)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('cuttext failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def inserttext (windowName, componentName, position, text):
	"""
	INPUT: inserttext ('<window name>', '<component name>', <position>, '<text to be inserted>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.INSERTTEXT)
		_message = generatexml (command.INSERTTEXT, _requestId, windowName, componentName, str (position), text)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('inserttext failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def deletetext (windowName, componentName, startPosition = None, endPosition = None):
	"""
	INPUT: deletetext ('<window name>', '<component name>'[, <start position>[, <end position>]])

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	if startPosition != None:
		startPosition = str (startPosition)
	if endPosition != None:
		endPosition = str (endPosition)
	try:
		_requestId  = threading.currentThread ().getName () + str (command.DELETETEXT)
		_message = generatexml (command.DELETETEXT, _requestId, windowName, componentName, startPosition, endPosition)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('deletetext failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def selecttextbyindexandregion (windowName, componentName,
				startPosition = None, endPosition = None, selectionNum = None):
	"""
	INPUT: selecttextbyindexandregion ('<window name>', '<component name>'[, <start position>[, <end position>[, <selection number>]]])

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	if startPosition != None:
		startPosition = str (startPosition)
	if endPosition != None:
		endPosition = str (endPosition)
	if selectionNum != None:
		selectionNum = str (selectionNum)
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTTEXTBYINDEXANDREGION)
		_message = generatexml (command.SELECTTEXTBYINDEXANDREGION, _requestId, windowName, \
						componentName, startPosition, endPosition, selectionNum)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selecttextbyindexandregion failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def selecttextbyname (windowName, componentName):
	"""
	INPUT: selecttextbyname ('<window name>', '<component name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTTEXTBYNAME)
		_message = generatexml (command.SELECTTEXTBYNAME, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selecttextbyname failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def pastetext (windowName, componentName, position = None):
	"""
	INPUT: pastetext ('<window name>', '<component name>'[, <position>])

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	if position != None:
		position = str (position)
	try:
		_requestId  = threading.currentThread ().getName () + str (command.PASTETEXT)
		_message = generatexml (command.PASTETEXT, _requestId, windowName, componentName, position)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('pastetext failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def expandtablecell (windowName, componentName, position):
	"""
	INPUT: expandtablecell ('<window name>', '<component name>', <position>)

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.EXPANDTABLECELL)
		_message = generatexml (command.EXPANDTABLECELL, _requestId, windowName, componentName, str (position))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('expandtablecell failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getcharcount (windowName, componentName):
	"""
	INPUT: getcharcount ('<window name>', '<component name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETCHARCOUNT)
		_message = generatexml (command.GETCHARCOUNT, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getcharcount failed: ' + _responseStatus [1])
		return int (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def geteventcount (windowName, componentName):
	"""
	INPUT: geteventcount ('<window name>', '<component name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETEVENTCOUNT)
		_message = generatexml (command.GETEVENTCOUNT, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('geteventcount failed: ' + _responseStatus [1])
		return int (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getlabel (windowName, componentName):
	"""
	INPUT: getlabel ('<window name>', '<component name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETLABEL)
		_message = generatexml (command.GETLABEL, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getlabel failed: ' + _responseStatus [1])
		return _responseData [1]
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getlabelatindex (windowName, componentName, index):
	"""
	INPUT: getlabelatindex ('<window name>', '<component name>', <index>)

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETLABELATINDEX)
		_message = generatexml (command.GETLABELATINDEX, _requestId, windowName, componentName, index)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getlabelatindex failed: ' + _responseStatus [1])
		return _responseData [1]
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def selectlabelspanelbyname (windowName, labelName):
	"""
	INPUT: selectlabelspanelbyname ('<window name>', '<label name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTLABELSPANELBYNAME)
		_message = generatexml (command.SELECTLABELSPANELBYNAME, _requestId, windowName, labelName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectlabelspanelbyname failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getpanelchildcount (windowName, componentName):
	"""
	INPUT: getpanelchildcount ('<window name>', '<component name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETPANELCHILDCOUNT)
		_message = generatexml (command.GETPANELCHILDCOUNT, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getpanelchildcount failed: ' + _responseStatus [1])
		return int (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getslidervalue (windowName, componentName):
	"""
	INPUT: getslidervalue ('<window name>', '<component name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETSLIDERVALUE)
		_message = generatexml (command.GETSLIDERVALUE, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getslidervalue failed: ' + _responseStatus [1])
		return float (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getstatusbartext (windowName, componentName):
	"""
	INPUT: getstatusbartext ('<window name>', '<component name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETSTATUSBARTEXT)
		_message = generatexml (command.GETSTATUSBARTEXT, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getstatusbartext failed: ' + _responseStatus [1])
		return _responseData [1]
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def gettreetablerowindex (windowName, componentName, rowText):
	"""
	INPUT: gettreetablerowindex ('<window name>', '<component name>', '<row text>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETTREETABLEROWINDEX)
		_message = generatexml (command.GETTREETABLEROWINDEX, _requestId, windowName, componentName, rowText)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('gettreetablerowindex failed: ' + _responseStatus [1])
		return int (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def grabfocus (windowName, componentName = None):
	"""
	INPUT: grabfocus ('<window name>'[, '<component name>'])

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GRABFOCUS)
		if (componentName != None):
			_message = generatexml (command.GRABFOCUS, _requestId, windowName, componentName)
		else:
			_message = generatexml (command.GRABFOCUS, _requestId, windowName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('grabfocus failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def istextstateenabled (windowName, componentName):
	"""
	INPUT: istextstateenabled ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.ISTEXTSTATEENABLED)
		_message = generatexml (command.ISTEXTSTATEENABLED, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def listsubmenus (windowName, componentName):
	"""
	INPUT: listsubmenus ('<window name>', '<component name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.LISTSUBMENUS)
		_message = generatexml (command.LISTSUBMENUS, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('listsubmenus failed: ' + _responseStatus [1])
		return _responseData [1]
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def invokemenu (windowName, componentName):
	"""
	INPUT: invokemenu ('<window name>', '<component name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.INVOKEMENU)
		_message = generatexml (command.INVOKEMENU, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('invokemenu failed: ' + _responseStatus [1])
		return _responseData [1]
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def rightclick (windowName, componentName, menuItem, data = None):
	"""
	INPUT: rightclick ('<window name>', '<component name>', '<menu item to be selected after right clic>'[, '<data>'])

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.RIGHTCLICK)
		_message = generatexml (command.RIGHTCLICK, _requestId, windowName, componentName, menuItem, data)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('rightclick failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def selectcalendardate (windowName, componentName, day, month, year):
	"""
	INPUT: selectcalendardate ('<window name>', '<component name>', <day>, <month>, <year>)

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTCALENDARDATE)
		_message = generatexml (command.SELECTCALENDARDATE, _requestId, windowName, componentName, str (day), str (month), str (year))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectcalendardate failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def selectitem (windowName, componentName, item):
	"""
	INPUT: selectitem ('<window name>', '<component name>', '<list item to be selected in combo box>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTITEM)
		_message = generatexml (command.SELECTITEM, _requestId, windowName, componentName, item)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectitem failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def selecttextitem (windowName, componentName, item):
	"""
	INPUT: selecttextitem ('<window name>', '<component name>', '<text item to be selected in combo box>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTTEXTITEM)
		_message = generatexml (command.SELECTEXTITEM, _requestId, windowName, componentName, item)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selecttextitem failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def setcellvalue (windowName, componentName, row, column, item):
	"""
	INPUT: setcellvalue ('<window name>', '<component name>', <row number>, <column number>, '<text to set>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SETCELLVALUE)
		_message = generatexml (command.SETCELLVALUE, _requestId, windowName,
					componentName, str (row), str (column), item)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('setcellvalue failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def sortcolumn (windowName, componentName, item):
	"""
	INPUT: sortcolumn ('<window name>', '<component name>', '<sort based on column name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SORTCOLUMN)
		_message = generatexml (command.SORTCOLUMN, _requestId, windowName, componentName, item)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('sortcolumn failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def sortcolumnindex (windowName, componentName, index):
	"""
	INPUT: sortcolumnindex ('<window name>', '<component name>', <sort based on column index>)

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SORTCOLUMNINDEX)
		_message = generatexml (command.SORTCOLUMNINDEX, _requestId, windowName, componentName, str (index))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('sortcolumnindex failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def verifybuttoncount (windowName, componentName, count):
	"""
	INPUT: verifybuttoncount ('<window name>', '<component name>', <button count>)

	OUTPUT: 1 on success, 0 on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYBUTTONCOUNT)
		_message = generatexml (command.VERIFYBUTTONCOUNT, _requestId, windowName, componentName, str (count))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

#  General Functions

def waittillguiexist (windowName, componentName = '', guiTimeOut = None):
	""" If the given window name exist, this function returns 1. If window doesnot exist, 
	then this function returns 0. Difference between guiexist and waitguiexist is, 
	waitguiexist waits for maximum 30 seconds. Still the window doesn't appear, 
	then 0 is returned. We can set the environment variable 'GUI_TIMEOUT' to change 
	the default waiting time.
	INPUT: waittillguiexist ('<window name>')

	OUTPUT: returns 1 on success and 0 on no existing window """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.WAITTILLGUIEXIST)
		if guiTimeOut and type (guiTimeOut) == int:
			guiTimeOut = str (guiTimeOut)
		else:
			guiTimeOut = os.getenv ('GUI_TIMEOUT')
			if guiTimeOut is None:
				guiTimeOut = str (30)
		_message = generatexml (command.WAITTILLGUIEXIST, _requestId, windowName, componentName, guiTimeOut)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def waittillguinotexist (windowName, componentName = '', guiTimeOut = None):
	""" If the given window name does not exist, this function returns 1. If window exist, 
	then this function returns 0. Difference between guiexist and waitguinotexist is, 
	waitguinotexist waits for maximum 30 seconds. Still the window does not disappear, 
	then 0 is returned. We can set the environment variable 'GUI_TIMEOUT' to change the 
	default waiting time.
	INPUT: waittillguinotexist ('<window name>')

	OUTPUT: returns 1 on success and 0 on no existing window """
	try:
		if guiTimeOut and type (guiTimeOut) == int:
			guiTimeOut = str (guiTimeOut)
		else:
			guiTimeOut = os.getenv ('GUI_TIMEOUT')
			if guiTimeOut is None:
				guiTimeOut = str (30)
		_requestId  = threading.currentThread ().getName () + str (command.WAITTILLGUINOTEXIST)
		_message = generatexml (command.WAITTILLGUINOTEXIST, _requestId, windowName, componentName, guiTimeOut)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def guiexist (windowName, componentName = ''):
	""" If the given window name exist, this function returns 1. If window doesnot exist, 
	then this function returns 0.
	INPUT: guiexist ('<window name>') 

	OUTPUT: returns 1 on success and 0 on no existing window """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GUIEXIST)
		_message = generatexml (command.GUIEXIST, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def guitimeout (guiTimeOut = 30):
	""" Set gui time out period, If this function called with out arguments, then the default timeout is 30 seconds
	INPUT: guitimeout (30) 

	OUTPUT: returns 1 on success and 0 on failure"""
	try:
		if type (guiTimeOut) == int:
			guiTimeOut = str (guiTimeOut)
		else:
			guiTimeOut = os.getenv ('GUI_TIMEOUT')
			if guiTimeOut is None:
				guiTimeOut = str (30)
		_requestId  = threading.currentThread ().getName () + str (command.GUITIMEOUT)
		_message = generatexml (command.GUITIMEOUT, _requestId, guiTimeOut)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def objtimeout (objTimeOut = 5):
	""" Set obj time out period, If this function called with out arguments, then the default timeout is 5 seconds
	INPUT: objtimeout (5) 

	OUTPUT: returns 1 on success and 0 on failure"""
	try:
		if type (objTimeOut) == int:
			objTimeOut = str (objTimeOut)
		else:
			objTimeOut = os.getenv ('OBJ_TIMEOUT')
			if objTimeOut is None:
				objTimeOut = str (5)
		_requestId  = threading.currentThread ().getName () + str (command.OBJTIMEOUT)
		_message = generatexml (command.OBJTIMEOUT, _requestId, objTimeOut)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def objectexist (windowName, componentName):
	""" Check that the given componentName exists in the hierarchy under
	windowName. Returns 1 if componentName exists, 0 otherwise
	INPUT: objectexist ('<window name>', '<component name>')

	OUTPUT: returns 1 if component exists, 0 otherwise """
	try:
		objinfo = getobjectinfo (windowName, componentName)
		if (objinfo):
			return 1
	except LdtpExecutionError:
		return 0

def initappmap (appmapFileName):
	""" Application map will be loaded
	INPUT: initappmap ('<application map name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.INITAPPMAP)
		_message = generatexml (command.INITAPPMAP, _requestId, appmapFileName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('initappmap failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def setappmap (appmapFileName):
	""" A new application map will be loaded. Existing appmap will be unloaded.
	INPUT: setappmap ('<new application map name>')

	OUTPUT: 1 on success, LdtpExecutionError on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SETAPPMAP)
		_message = generatexml (command.SETAPPMAP, _requestId, appmapFileName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('setappmap failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def setcontext (oldContext, newContext):
	""" Set context of window
	INPUT: setcontext ('<old window title>', '<new window title>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""

	try:
		_requestId  = threading.currentThread ().getName () + str (command.SETCONTEXT)
		_message = generatexml (command.SETCONTEXT, _requestId, oldContext, newContext)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('setcontext failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def releasecontext (oldContext = "", newContext = ""):
	""" Release context of window
	INPUT: releasecontext (oldContext, newContext)

	OUTPUT: 1 on success, LdtpExecutionError on failure"""

	try:
		_requestId  = threading.currentThread ().getName () + str (command.RELEASECONTEXT)
		_message = generatexml (command.RELEASECONTEXT, _requestId, oldContext, newContext)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('releasecontext failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def onwindowcreate (windowTitle, callbackFuncName):
	""" On new window creation event, notify
	INPUT: onwindowcreate ('<window title to watch>', <callback function to be called on window create event>)

	OUTPUT: 1 on success, LdtpExecutionError on failure"""

	try:
		_requestId  = threading.currentThread ().getName () + str (command.ONWINDOWCREATE)
		_message = generatexml (command.ONWINDOWCREATE, _requestId, windowTitle)
		_callbackFunctions [windowTitle] = callbackFuncName
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('onwindowcreate failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def removecallback (windowTitle):
	""" remove reigstered callback
	INPUT: removecallback ('<window title to watch>')

	OUTPUT: 1 on success, LdtpExecutionError on failure"""

	try:
		if _callbackFunctions.has_key (windowTitle):
			del _callbackFunctions [windowTitle]
			_requestId  = threading.currentThread ().getName () + str (command.REMOVECALLBACK)
			_message = generatexml (command.REMOVECALLBACK, _requestId, windowTitle)
			sendpacket (_message)
			_responseStatus, _responseData = getresponse (_requestId)
			if _responseStatus [0] != 0:
				raise LdtpExecutionError ('removecallback failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def reinitldtp ():
	""" Reinitialize LDTP, which will close existing at-spi connection
	and reestablish it.
	INPUT: reinitldtp ()

	OUTPUT: 1 on success, LdtpExecutionError on failure"""

	try:
		_requestId  = threading.currentThread ().getName () + str (command.REINITLDTP)
		_message = generatexml (command.REINITLDTP, _requestId)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('reinitldtp failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def remap (windowName, componentName = ''):
	""" We can handle dynamically created widgets (meaning widgets created at run time) using 
	this remap function. Calling remap will generate appmap for the given dialog at run 
	time and update the hash table. Then we can access the new widgets.

	Please note that the <application-name> should be same as the one given as the commmand-line 
	argument for appmap generation. 
	INPUT: remap ('<application-name>', '<window name>')

	OUTPUT: It uses the same logic that appmap module uses to generate appmap."""

	try:
		_requestId  = threading.currentThread ().getName () + str (command.REMAP)
		_message = generatexml (command.REMAP, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('remap failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

# Deprecated undoremap function as it is no longer needed

def undoremap (applicationName, windowName):
	""" This function is deprecated and no longer needs to be called.
	This function is a no-op and immediately returns, but exists to
	maintain compatibility with scripts which call it.

	INPUT: undoremap ('<application-name>', 'window name>')
	"""
	return 1

#  Log Function

def startldtplog (logFileName, fileOverWrite = 1):
	""" Start logging on the specified file. second arugment is optional and 1 is default value
	0 - Append log to an existing file
	1 - Write log to a new file. If file already exist, 
	then erase existing file content and start log

	INPUT: startldtplog ('<log file name>', [0 or 1])

	OUTPUT: Log file will be created if log file is not present in any case. If second argument is 1, 
	then existing file content will be erased. If second argument is 0, then new logs will be 
	append to existing log.

	It returns 1 on Success and 0 on error  """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.STARTLOG)
		_message = generatexml (command.STARTLOG, _requestId, logFileName, str (fileOverWrite))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			pass
		return 1
	except LdtpExecutionError:
		pass

def ldtplog (message, priority = ''):
	""" Logs the message in the log.xml with the tag which can be viewed after the execution of scripts
	INPUT: ldtplog('<Message to be logged>','<tag>')

	OUTPUT: The required message will be logged into the log.xml on execution of scripts
	It returns 1 on Success and 0 on error  """

	try:
		_requestId  = threading.currentThread ().getName () + str (command.LOG)
		_message = generatexml (command.LOG, _requestId, message, priority)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			pass
		return 1
	except ConnectionLost:
		pass
	except LdtpExecutionError:
		pass

def stopldtplog ():
	""" Stop logging.
	INPUT: stopldtplog()

	OUTPUT: If a log file has been previously opened for logging, that file pointer will be closed. 
	So that the new logging will not be appened to the log file. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.STOPLOG)
		_message = generatexml (command.STOPLOG, _requestId)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			pass
		return 1
	except ConnectionLost:
		pass
	except LdtpExecutionError:
		pass

def setloglevel (level):
	return setInternalLogLevel (level, logger)

def startlog (logFileName, fileOverWrite = 1):
	""" Start logging on the specified file. second arugment is optional and 1 is default value
	0 - Append log to an existing file
	1 - Write log to a new file. If file already exist, 
	then erase existing file content and start log

	INPUT: startlog ('<log file name>', [0 or 1])

	OUTPUT: Log file will be created if log file is not present in any case. If second argument is 1, 
	then existing file content will be erased. If second argument is 0, then new logs will be 
	append to existing log.

	It returns 1 on Success and 0 on error  """
	global logger, xmlhdlr
	logger, xmlhdlr = startInternalLog (logFileName, fileOverWrite, 'XML')
	if logger is not None:
		return 1
	else:
		return 0

def log (message, priority = None):
	""" Logs the message in the log.xml with the tag which can be viewed after the execution of scripts
	INPUT: log('<Message to be logged>','<tag>')

	OUTPUT: The required message will be logged into the log.xml on execution of scripts
	It returns 1 on Success and 0 on error  """
	return internalLog (message, priority, logger)

def addlogger (confFileName):
	addInternalLogger (confFileName)
	return 1

def stoplog (handler = None):
	""" Stop logging.
	INPUT: stoplog()

	OUTPUT: If a log file has been previously opened for logging, that file pointer will be closed. 
	So that the new logging will not be appened to the log file. """
	return internalStopLog (handler, xmlhdlr, logger)

def selectrow (windowName, tableName, rowText, nthMatch = 0):
	"""Selects the row with the text in the table
	INPUT: selectrow ('<window name>', '<table name>', '<row text to be selected>')

	OUTPUT: Returns 1 on success and 0 on error."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTROW)
		_message = generatexml (command.SELECTROW, _requestId, windowName, tableName, rowText, str (nthMatch))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectrow failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))
	
def selectrowindex (windowName, tableName, rowIndex):
	"""Selects the row with the index in the table
	INPUT: selectrowindex ('<window name>', '<table name>', <row index>)

	OUTPUT: Returns 1 on success and 0 on error."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTROWINDEX)
		_message = generatexml (command.SELECTROWINDEX, _requestId, windowName, tableName, str (rowIndex))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectrowindex failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

#  MenuItem Functions

def doesmenuitemexist (windowName, menuHierarchy):
	""" checks if the specified menuitem specified in the menu hierarchy is present or not
	INPUT: doesmenuitemexist ('<window name>', '<menu hierarchy>')

	OUTPUT: Returns 1 if the menuitem is present and 0 otherwise """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.DOESMENUITEMEXIST)
		_message = generatexml (command.DOESMENUITEMEXIST, _requestId, windowName, menuHierarchy)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

#  Panel Functions

def selectpanel (windowName, componentName, panelNumber):
	""" Select a panel using the panel number in a list of panels
	INPUT: selectpanel ('<window name>', '<component name>', <panel number>)

	OUTPUT: Returns 1 on success and 0 on error """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTPANEL)
		_message = generatexml (command.SELECTPANEL, _requestId, windowName, componentName, str (panelNumber))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectpanel failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def selectpanelname (windowName, componentName, panelName):
	""" Select a panel using the panel name in a list of panels
	INPUT: selectpanelname ('<window name>', '<component name>', <panel name>)

	OUTPUT: Returns 1 on success and 0 on error """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTPANELNAME)
		_message = generatexml (command.SELECTPANELNAME, _requestId, windowName, componentName, panelName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectpanelname failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

#  PushButton Functions

def verifypushbutton (windowName, componentName):
	""" Verify whether the given object is push button or not.
	INPUT: verifypushbutton ('<window name>', '<component name>')

	OUTPUT: Returns 1 if object is push button, else 0. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYPUSHBUTTON)
		_message = generatexml (command.VERIFYPUSHBUTTON, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def stateenabled (windowName, componentName):
	""" Checks the radio button object state enabled or not
	INPUT: stateenabled ('<window name>', '<component name>')

	OUTPUT: Returns 1 if state is enabled, else 0."""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.STATEENABLED)
		_message = generatexml (command.STATEENABLED, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

#  ScrollBar Functions

def onedown (windowName, componentName, iterations):
	""" Move the scroll bar down 'n' times, where 'n' is the number of iterations 
	specified in  the argument field.
	INPUT: onedown ('<window name>', '<scroll component name>', '<number of iterations>')

	OUTPUT: Scrolls down if value does not exceed the maximum limit, else fails. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.ONEDOWN)
		_message = generatexml (command.ONEDOWN, _requestId, windowName, componentName, str (iterations))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('onedown failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def oneleft (windowName, componentName, iterations):
	""" Move the (horizontal) scroll bar left 'n' times,
	where 'n' is the number of iterations specified in the argument field.
	INPUT: oneleft ('<window name>', '<scroll component name>', '<number of iterations>')

	OUTPUT: Scrolls left if value does not exceed the maximum limit, else fails. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.ONELEFT)
		_message = generatexml (command.ONELEFT, _requestId, windowName, componentName, str (iterations))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('oneleft failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def oneright (windowName, componentName, iterations):
	""" Move the (horizontal) scroll bar right 'n' times,
	where 'n' is the number of iterations specified in the argument field.
	INPUT: oneright ('<window name>', '<scroll component name>', '<number of iterations>')

	OUTPUT: Scrolls right if value does not exceed the maximum limit, else fails. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.ONERIGHT)
		_message = generatexml (command.ONERIGHT, _requestId, windowName, componentName, str (iterations))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('oneright failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def oneup (windowName, componentName, iterations):
	""" Move the scroll bar up 'n' times, where 'n' is the number of iterations 
	specified in  the argument field.
	INPUT: oneup ('<window name>', '<scroll component name>', '<number of iterations>')

	OUTPUT: Scrolls up if value does not exceed the maximum limit, else fails. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.ONEUP)
		_message = generatexml (command.ONEUP, _requestId, windowName, componentName, str (iterations))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('oneup failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))
    
def scrolldown (windowName, componentName):
	""" Move the (vertical) scroll bar to the bottom.
	INPUT: scrolldown ('<window name>', '<scroll component name>')

	OUTPUT: Returns 1 if action is performed, else 0. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SCROLLDOWN)
		_message = generatexml (command.SCROLLDOWN, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('scrolldown failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def scrollleft (windowName, componentName):
	""" Move the (horizontal) scroll bar to the left.
	INPUT: scrollleft ('<window name>', '<scroll component name>')

	OUTPUT: Returns 1 if action is performed, else 0. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SCROLLLEFT)
		_message = generatexml (command.SCROLLLEFT, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('scrollleft failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def scrollright (windowName, componentName):
	""" Move the (horizontal) scroll bar to the right.
	INPUT: scrollright ('<window name>', '<scroll component name>')

	OUTPUT: Returns 1 if action is performed, else 0. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SCROLLRIGHT)
		_message = generatexml (command.SCROLLRIGHT, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('scrollright failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))
	
def scrollup (windowName, componentName):
	""" Move the (vertical) scroll bar to the top.
	INPUT: scrollup ('<window name>', '<scroll component name>')

	OUTPUT: Returns 1 if action is performed, else 0. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SCROLLUP)
		_message = generatexml (command.SCROLLUP, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('scrollup failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def verifyscrollbar (windowName, componentName):
	"""
	INPUT: verifyscrollbar ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSCROLLBAR)
		_message = generatexml (command.VERIFYSCROLLBAR, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifyscrollbarvertical (windowName, componentName):
	"""
	INPUT: verifyscrollbarvertical ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSCROLLBARVERTICAL)
		_message = generatexml (command.VERIFYSCROLLBARVERTICAL, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifyscrollbarhorizontal (windowName, componentName):
	"""
	INPUT: verifyscrollbarhorizontal ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSCROLLBARHORIZONTAL)
		_message = generatexml (command.VERIFYSCROLLBARHORIZONTAL, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifyslider (windowName, componentName):
	"""
	INPUT: verifyslider ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSLIDER)
		_message = generatexml (command.VERIFYSLIDER, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifyslidervertical (windowName, componentName):
	"""
	INPUT: verifyslidervertical ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSLIDERVERTICAL)
		_message = generatexml (command.VERIFYSLIDERVERTICAL, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifysliderhorizontal (windowName, componentName):
	"""
	INPUT: verifysliderhorizontal ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSLIDERHORIZONTAL)
		_message = generatexml (command.VERIFYSLIDERHORIZONTAL, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifystatusbar (windowName, componentName):
	"""
	INPUT: verifystatusbar ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSTATUSBAR)
		_message = generatexml (command.VERIFYSTATUSBAR, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifystatusbarvisible (windowName, componentName):
	"""
	INPUT: verifystatusbarvisible ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSTATUSBARVISIBLE)
		_message = generatexml (command.VERIFYSTATUSBARVISIBLE, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifytoggled (windowName, componentName):
	"""
	INPUT: verifytoggled ('<window name>', '<component name>')

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYTOGGLED)
		_message = generatexml (command.VERIFYTOGGLED, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifyvisiblebuttoncount (windowName, componentName, count):
	"""
	INPUT: verifyvisiblebuttoncount ('<window name>', '<component name>', <button count>)

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYVISIBLEBUTTONCOUNT)
		_message = generatexml (command.VERIFYVISIBLEBUTTONCOUNT, _requestId, windowName, componentName, str (count))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

#  Slider Functions

def decrease (windowName, componentName, iterations):
	""" Decrease the value of the slider 'n' times, where 'n' is the number of 
    	iterations specified in the argument field.
	INPUT: decrease ('<window name>', '<slider name>', '<number of iterations>')

	OUTPUT: Decreases the value if it does not fall below the minimum limit, else fails. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.DECREASE)
		_message = generatexml (command.DECREASE, _requestId, windowName, componentName, str (iterations))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('decrease failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def increase (windowName, componentName, iterations):
	""" Increase the value of the slider 'n' times, where 'n' is the number of 
    	iterations specified in the argument field.
	INPUT: increase ('<window name>', '<slider name>', '<number of iterations>')

	OUTPUT: Increases the value if it does not fall below the minimum limit, else fails. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.INCREASE)
		_message = generatexml (command.INCREASE, _requestId, windowName, componentName, str (iterations))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('increase failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def setmax (windowName, componentName):
	""" Set the slider to the maximum value.
	INPUT: setmax ('<window name>', '<slider name>')

	OUTPUT: Returns 1 if action is performed, else 0. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SETMAX)
		_message = generatexml (command.SETMAX, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('setmax failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def setmin (windowName, componentName):
	""" Set the slider to the minimum value.
	INPUT: setmin ('<window name>', '<slider name>')

	OUTPUT: Returns 1 if action is performed, else 0. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SETMIN)
		_message = generatexml (command.SETMIN, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('setmin failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

#  SpinButton Functions

def setvalue (windowName, componentName, value):
	""" Sets the value of the spin button.
	INPUT: setvalue ('<window name>', '<spinbutton name>', '<value>')

	OUTPUT: Returns 1 on success and 0 on error. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SETVALUE)
		_message = generatexml (command.SETVALUE, _requestId, windowName, componentName, str (value))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('setvalue failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getvalue (windowName, componentName):
	""" Gets the value in the spin button.
	INPUT: getvalue ('<window name>', '<spinbutton name>')

	OUTPUT: Returns 1 on success and 0 on error. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETVALUE)
		_message = generatexml (command.GETVALUE, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getvalue failed: ' + _responseStatus [1])
		return float (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def verifysetvalue (windowName, componentName, value) :
	""" Verifies the value set in spin button.
	INPUT: verifysetvalue ('<window name>', '<spinbutton name>', '<value>')

	OUTPUT: Returns 1 on success and 0 on error. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYSETVALUE)
		_message = generatexml (command.VERIFYSETVALUE, _requestId, windowName, componentName, str (value))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

#  TabControl Functions

def selecttab (windowName, componentName, tabName):
	""" Select the given tab name in the tab list
	INPUT: selecttab ('<window name>', '<tab list name>', '<tab name>')

	OUTPUT: Returns 1 if the tab is selected, otherwise exception will be thrown """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTTAB)
		_message = generatexml (command.SELECTTAB, _requestId, windowName, componentName, tabName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selecttab failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def selecttabindex (windowName, componentName, tabIndex):
	""" Select a particular tab in the list of tabs
	INPUT: selecttabindex ('<windwo name>', '<tab list name>', <index of the tab>)

	OUTPUT: Returns 1 if the tab is selected, otherwise exception will be thrown """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTTABINDEX)
		_message = generatexml (command.SELECTTABINDEX, _requestId, windowName, componentName, str (tabIndex))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selecttabindex failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def gettabcount (windowName, componentName):
	""" Gets the number of tabs in an object
	INPUT: gettabcount ('<window name>', '<object name>')
	       e.g. getttabcount ('terminal','ptl0')

	OUTPUT: Returns the number of tabs in the object """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETTTABCOUNT)
		_message = generatexml (command.GETTABCOUNT, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('gettabcount failed: ' + _responseStatus [1])
		return long(_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def checkrow (windowName, componentName, rowIndex, columnIndex = 0):
	""" checks the row with the given index value in table. This can take an 
	optional column index and perform the action on that particular column. 
	If the column index is not given, 0 is taken as the default value.
	Index value starts from 0.
	INPUT: checkrow ('<window name>', '<table name>', <row index>, <col index>)

	OUTPUT: Returns 1 on success and 0 on error. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.CHECKROW)
		_message = generatexml (command.CHECKROW, _requestId, windowName, componentName, str (rowIndex), str (columnIndex))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('checkrow failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def verifycheckrow (windowName, componentName, rowIndex, columnIndex = 0):
	"""
	INPUT: verifycheckrow ('<window name>', '<component name>', <row index>[, <column index>])

	OUTPUT: 1 on success, 0 on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYCHECKROW)
		_message = generatexml (command.VERIFYCHECKROW, _requestId, windowName, componentName, str (rowIndex), str (columnIndex))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def doesrowexist (windowName, componentName, rowText):
	""" Checks whether the table contains any row with any of its cell containing 
	the given string as its value.Please note that it checks for an exact match.
	INPUT: doesrowexist ('<window name>', '<table name>', '<string to be matched>')

	OUTPUT: Returns 1 if there are rows with the given string in any of its cell else 0. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.DOESROWEXIST)
		_message = generatexml (command.DOESROWEXIST, _requestId, windowName, componentName, rowText)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0
    
def doubleclick (windowName, componentName):
	"""
	INPUT: doubleclick ('<window name>', '<table name>')

	OUTPUT: Returns 1 on success and exception on error"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.DOUBLECLICK)
		_message = generatexml (command.DOUBLECLICK, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('doubleclick failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def doubleclickrow (windowName, componentName, rowText):
	""" Double clicks the row in table whose first column's (0th column) value 
	is same as the contents of the third argument in the function call.
	INPUT: doubleclickrow ('<window name>', '<table name>', '<value of row in first column>')

	OUTPUT: Returns 1 on success and 0 on error. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.DOUBLECLICKROW)
		_message = generatexml (command.DOUBLECLICKROW, _requestId, windowName, componentName, rowText)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('doubleclickrow failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def singleclickrow (windowName, componentName, rowText):
	""" Single clicks the row in the table whose first column's (0th column) value is the
	the same as the contents of the 'rowText' or third arguement in the function call.
	INPUT: singleclickrow ('<window name>', '<table name>', '<value of the header/top column>')
	
	OUTPUT: Returns 1 on success and 0 on error."""
	try:
		_requestId = threading.currentThread ().getName () + str (command.SINGLECLICKROW)
		_message = generatexml (command.SINGLECLICKROW, _requestId, windowName, componentName, rowText)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError('singleclickrow failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getcellvalue (windowName, componentName, row, column = 0):
	""" returns the text in a cell at given row and column of a tree table
	INPUT: getcellvalue ('<window name>', '<component name>', '<row>', '<column>')

	OUTPUT: returns the string """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETCELLVALUE)
		_message = generatexml (command.GETCELLVALUE, _requestId, windowName, componentName, str (row), str (column))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getcellvalue failed: ' + _responseStatus [1])
		return _responseData [1]
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getrowcount (windowName, componentName):
	""" returns the number of rows in the table
	INPUT: getrowcount ('<window name>', '<table name>' )

	OUTPUT: Returns the number of rows present in the table mentioned """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETROWCOUNT)
		_message = generatexml (command.GETROWCOUNT, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getrowcount failed: ' + _responseStatus [1])
		return int (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))
    
def gettablerowindex (windowName, componentName, rowText):
	""" Returns the id of the row containing the given <cellvalue>
	INPUT: gettablerowindex ('<window name>','<tablename>','<cellvalue>')

	OUTPUT: Return id of the row containing the given cell value, if it is found else return -1 """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETTABLEROWINDEX)
		_message = generatexml (command.GETTABLEROWINDEX, _requestId, windowName, componentName, rowText)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return -1L
		return int (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def selectlastrow (windowName, componentName):
	""" Selects the last row of a table.
	INPUT: selectlastrow ('<window name>', '<table name>')

	OUTPUT: Returns 1 on success and 0 on error. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTLASTROW)
		_message = generatexml (command.SELECTLASTROW, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectlastrow failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def selectrowpartialmatch (windowName, componentName, rowPartialText):
	""" selects the row having cell that contains the given text.
	INPUT: selectrowpartialmatch ('<window name>', '<tree table name>', '<texttobesearchedfor>')

	OUTPUT: returns 1 on success and throws an exception on error """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SELECTROWPARTIALMATCH)
		_message = generatexml (command.SELECTROWPARTIALMATCH, _requestId, windowName, componentName, rowPartialText)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('selectrowpartialmatch failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def verifypartialmatch (windowName, componentName, rowPartialText):
	""" 
	INPUT: verifypartialmatch ('<window name>', '<component name>', '<partial text to match>')

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYPARTIALMATCH)
		_message = generatexml (command.VERIFYPARTIALMATCH, _requestId, windowName, componentName, rowPartialText)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifypartialtablecell (windowName, componentName, rowIndex, columnIndex, rowPartialText):
	""" 
	INPUT: verifypartialtablecell ('<window name>', '<component name>', <row index>, <column index>, '<partial text>')

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYPARTIALTABLECELL)
		_message = generatexml (command.VERIFYPARTIALTABLECELL, _requestId, windowName, componentName,
					str (rowIndex), str (columnIndex), rowPartialText)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def uncheckrow (windowName, componentName, rowIndex, columnIndex = 0):
	""" Unchecks the row with the given index value in table. This can take an 
	optional column index and perform the action on that particular column. 
	If the column index is not given, 0 is taken as the default value. Index 
	value starts from 0.
	INPUT: uncheckrow ('<window name>', '<table name>', <row index>, [<col index>])

	OUTPUT: Returns 1 on success and 0 on error. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.UNCHECKROW)
		_message = generatexml (command.UNCHECKROW, _requestId, windowName, componentName, str (rowIndex), str (columnIndex))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('uncheckrow failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def verifyuncheckrow (windowName, componentName, rowIndex, columnIndex = 0):
	""" 
	INPUT: verifyuncheckrow ('<window name>', '<component name>', <row index>[, <column index>])

	OUTPUT: 1 on success, 0 on failure """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYUNCHECKROW)
		_message = generatexml (command.VERIFYUNCHECKROW, _requestId, windowName, componentName, str (rowIndex), str (columnIndex))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifytablecell (windowName, componentName, rowIndex, columnIndex, textToCompare):
	""" Verifies the tablecell value with the String Passed ie., fifth argument
	INPUT: verifytablecell ('<window name>', '<table name>', '<row no>','<column no>','<string to be compared>')

	OUTPUT: Returns 1 on success and 0 on error. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYTABLECELL)
		_message = generatexml (command.VERIFYTABLECELL, _requestId, windowName, componentName,
					str (rowIndex), str (columnIndex), textToCompare)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0

def verifypartialcellvalue (windowName, componentName, rowIndex, columnIndex, partialTextToCompare):
	""" Verifies the tablecell value with the sub String Passed ie., fifth argument
	INPUT: verifypartialtablecell ('<window name>', '<table name>', '<row no>','<column no>','< sub string to be compared>')

	OUTPUT: Returns 1 on success and 0 on error. """
	try:
		_requestId  = threading.currentThread ().getName () + str (command.VERIFYPARTIALTABLECELL)
		_message = generatexml (command.VERIFYPARTIALCELLVALUE, _requestId, windowName, componentName,
					str (rowIndex), str (columnIndex), partialTextToCompare)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError, msg:
		return 0
    
def getwindowlist ():
	"""
	INPUT: getwindowlist ()

	OUTPUT: list of windows on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETWINDOWLIST)
		_message = generatexml (command.GETWINDOWLIST, _requestId)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getwindowlist failed: ' + _responseStatus [1])
		return parseobjectlist (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getapplist ():
	"""
	INPUT: getapplist ()

	OUTPUT: list of applications on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETAPPLIST)
		_message = generatexml (command.GETAPPLIST, _requestId)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getapplist failed: ' + _responseStatus [1])
		return parseobjectlist (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getobjectlist (windowName):
	"""
	INPUT: getobjectlist ('<window name>')

	OUTPUT: List of objects of the window on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETOBJECTLIST)
		_message = generatexml (command.GETOBJECTLIST, _requestId, windowName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getobjectlist failed: ' + _responseStatus [1])
		return parseobjectlist (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getchild (windowName, componentName = '', role = ''):
	"""
	INPUT: getchild ('<window name>'[, '<component name>'[, '<role type>']])

	OUTPUT: List of childrens on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETCHILD)
		_message = ''
		if role != None and role != '':
			role = re.sub (' ', '_', role)
			_message = generatexml (command.GETCHILD, _requestId, windowName, componentName, role)
		else:
			_message = generatexml (command.GETOBJECTINFO, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getchild failed: ' + _responseStatus [1])
		return parseobjectlist (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getobjectinfo (windowName, componentName):
	"""
	INPUT: getobjectinfo ('<window name>', '<component name>')

	OUTPUT: List of object informations on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETOBJECTINFO)
		_message = generatexml (command.GETOBJECTINFO, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getobjectinfo failed: ' + _responseStatus [1])
		return parseobjectlist (_responseData [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def getobjectproperty (windowName, componentName, propertyName):
	"""
	INPUT: getobjectproperty ('<window name>', '<component name>', '<property name>')

	OUTPUT: property value on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GETOBJECTPROPERTY)
		_message = generatexml (command.GETOBJECTPROPERTY, _requestId, windowName, componentName, propertyName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('getobjectproperty failed: ' + _responseStatus [1])
		return _responseData [1]
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def setlocale (locale = None):
	try:
		_requestId  = threading.currentThread ().getName () + str (command.SETLOCALE)
		_message = None
		if locale == None:
			_message = generatexml (command.SETLOCALE, _requestId, os.getenv ('LANG'))
		else:
			os.environ ['LANG'] = locale
			_message = generatexml (command.SETLOCALE, _requestId, locale)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('setlocale failed: ' + _responseStatus [1])
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))	

def bindtext (packageName, localeDir, mode = 'mo'):
	"""
	INPUT: TODO

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		setlocale
		_requestId  = threading.currentThread ().getName () + str (command.BINDTEXT)
		_message = generatexml (command.BINDTEXT, _requestId, packageName, localeDir, mode)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('bindtext failed: ' + _responseStatus [1])
		return _responseData [1]
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def generatemouseevent (x, y, eventType = 'b1c'):
	"""
	INPUT:
	X - Coordinate
	Y - Coordinate
	eventType

	OUTPUT: None"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GENERATEMOUSEEVENT)
		_message = generatexml (command.GENERATEMOUSEEVENT, _requestId, str (x), str (y), eventType)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('generatemouseevent failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def mouseleftclick (windowName, componentName):
	"""
	INPUT: windowName --> Window containing object
               componentName --> object's name

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.MOUSELEFTCLICK)
		_message = generatexml (command.MOUSELEFTCLICK, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('mouseleftclick failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def mouserightclick (windowName, componentName):
	"""
	INPUT: windowName --> Window containing object
               componentName --> object's name

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.MOUSERIGHTCLICK)
		_message = generatexml (command.MOUSERIGHTCLICK, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('mouserightclick failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def mousemove (windowName, componentName):
	"""
	INPUT: windowName --> Window containing object
               componentName --> object's name

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.MOUSEMOVE)
		_message = generatexml (command.MOUSEMOVE, _requestId, windowName, componentName)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('mousemove failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def enterstring (windowName, componentName = None, data = None):
	"""
	INPUT: windowName --> Window containing object
               componentName --> object's name
	       data --> string to be simulated as entered from keyboard
	       Special non printing characters are enter within '<' and '>'
	       e.g. <capslock>,<ctrl>, etc while other characters are entered
	       in a straight forward fashion. e.g. '<ctrl>Nwww.google.com'
	       If only first argument is passed then it will be considered as 'data' argument

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.KBDENTER)
		_message = ''
		if componentName is not None and data is not None:
			_message = generatexml (command.KBDENTER, _requestId, windowName, componentName, data)
		elif componentName is None and data is None:
			_message = generatexml (command.GENERATEKEYEVENT, _requestId, windowName)
		else:
			raise LdtpExecutionError ('Invalid syntax')
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('enterstring failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def generatekeyevent (data):
	"""
	INPUT: data --> string to be simulated as entered from keyboard
	Special non printing characters are enter within '<' and '>'
	e.g. <capslock>,<ctrl>, etc while other characters are entered
	in a straight forward fashion. e.g. '<ctrl>Nwww.google.com'    

	OUTPUT: 1 on success, LdtpExecutionError on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.GENERATEKEYEVENT)
		_message = generatexml (command.GENERATEKEYEVENT, _requestId, data)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			raise LdtpExecutionError ('generatekeyevent failed: ' + _responseStatus [1])
		return 1
	except LdtpExecutionError, msg:
		raise LdtpExecutionError (str (msg))

def stopscriptengine ():
	"""
	INPUT: stopscriptengine ()

	OUTPUT: None"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.STOPSCRIPTENGINE)
		_message = generatexml (command.STOPSCRIPTENGINE, _requestId)
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
	except LdtpExecutionError:
		pass

def hasstate (windowName, componentName, state):
	"""
	INPUT: hasstate ('<window name>', '<component name>', <verify the object has this state>)

	OUTPUT: 1 on success, 0 on failure"""
	try:
		_requestId  = threading.currentThread ().getName () + str (command.HASSTATE)
		_message = generatexml (command.HASSTATE, _requestId, windowName, componentName, str (state))
		sendpacket (_message)
		_responseStatus, _responseData = getresponse (_requestId)
		if _responseStatus [0] != 0:
			return 0
		return 1
	except LdtpExecutionError:
		return 0

def launchapp (appName, env = 1):
	"""
	INPUT: launchapp ('<application name>'[, 1 or 0])
	If 1, then set GTK_MODULES and GNOME_ACCESSIBILITY environment variables
	If 0, don't set the environment variables

	OUTPUT: LdtpExecutionError on failure"""
        if _ldtpUseTcp == True:
            _requestId  = threading.currentThread ().getName () + str (command.LAUNCHAPP)
            _message = generatexml (command.LAUNCHAPP, _requestId, appName, str (env))
            sendpacket (_message)
            _responseStatus, _responseData = getresponse (_requestId)
	    if _responseStatus [0] != 0:
		    raise LdtpExecutionError ('File ' + str (appName) + ' does not exist in the PATH.')
        else:
            if env == 1:
                os.putenv ('GTK_MODULES', 'gail:atkbridge');
                os.putenv ('GNOME_ACCESSIBILITY', '1');
            _status = commands.getstatusoutput ('which ' + str (appName))
            if _status [0] != 0:
                raise LdtpExecutionError ('File ' + str (appName) + ' does not exist in the PATH.')
            pid = os.fork ()
            if pid == 0:
                _status = commands.getstatusoutput (str (appName))
                os._exit (os.EX_OK)
            # Let us wait so that the application launches
	    time.sleep (5)
