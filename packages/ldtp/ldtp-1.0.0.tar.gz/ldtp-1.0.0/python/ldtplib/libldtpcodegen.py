#!/usr/bin/env python 
#############################################################################
#
#  Linux Desktop Testing Project http://ldtp.freedesktop.org
# 
#  Author:
#      Nagappan A (nagappan@gmail.com)   
# 
#  Copyright 2004 - 2007 Novell, Inc.
# 
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2 of the License, or (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
# 
#  You should have received a copy of the GNU Lesser General Public
#  License along with this program; if not, write to the
#  Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#  Boston, MA 02110, USA.
#
#############################################################################

from xml.dom.minidom import *
from xml.parsers.expat import ExpatError
from xml.sax import saxutils
import socket, os, sys, struct, time, threading, re, random, thread, traceback
import types, atexit, select, signal

from ldtplib.ldtplibutils import *

_ldtpDebug = os.getenv ('LDTP_DEBUG')

class command:
	INVALID       = 0
	STOP          = 1
	WINDOWEXIST   = 2
	GETWINDOWNAME = 3
	GETOBJECTNAME = 4

class ConnectionLost (Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr (self.value)

# generate XML content
def generatexml (commandId, _requestId, name = None, application = None, argument = None):
	_xml = '<?xml version=\"1.0\"?>'
	_xml += '<REQUEST>'
	# Fill action name
	_xml = _xml + '<ID>' + _requestId + '</ID>'
	_xml = _xml + '<COMMAND>' + str (commandId) + '</COMMAND>'
	if application != None:
		_xml = _xml + '<APPLICATION>' + saxutils.escape (application) + '</APPLICATION>'
	if name is not None:
		_xml = _xml + '<NAME>' + saxutils.escape (name) + '</NAME>'
	_xml = _xml + '<ARGUMENTS>'
	_xml = _xml + '<ARGUMENT>ALL</ARGUMENT>'
	_xml = _xml + '</ARGUMENTS>'
	_xml += '</REQUEST>'
	return _xml

# Send given packet to server
def sendpacket (msg):
	global _mainSock
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
		
		# Encode the message in UTF-8 so we don't break on extended
		# characters in the application GUIs
		buf = msg.encode ('utf-8')

		if _mainSock == None:
			_sendLck.release ()
			return
		# Pack length (integer value) in network byte order
		msglen = struct.pack ('!i', len (buf))
		# Send message length
		_mainSock.send (msglen)

		# Send message
		_mainSock.send (buf)
		if _ldtpDebug != None and _ldtpDebug == '2':
			print 'Send packet', buf
		#_sendLck.release ()
	except socket.error, msg:
		raise LdtpExecutionError ('Server aborted')
	except:
		if _ldtpDebug:
			print traceback.print_exc ()
		raise LdtpExecutionError (traceback.print_exc ())
	finally:
		if flag:
			# Reason for using the flag:
			# 'Do not call this method when the lock is unlocked.'
			_sendLck.release ()
			flag = False

def recvpacket (peek_flag = 0):
	global _mainSock
	flag = False
	try:
		_recvLck.acquire ()
		flag = True
		_responsePacket = None
		_mainSock.settimeout (5.0)
		# Hardcoded 4 bytes, as the server sends 4 bytes as packet length
		data = _mainSock.recv (4, peek_flag)
		if data == '' or data == None:
			if flag == True:
				# Reason for using the flag:
				# 'Do not call this method when the lock is unlocked.'
				_recvLck.release ()
			flag = False
			return None
		_packetSize, = struct.unpack ('!i', data)
		if peek_flag == 0 and _ldtpDebug != None and _ldtpDebug == '2':
			print 'Received packet size', _packetSize
		# MSG_PEEK
		# This flag causes the receive operation to return data from the beginning
		# of the receive queue without removing that data from  the  queue.
		# Thus, a subsequent receive call will return the same data.

		if peek_flag != 0:
			# MSG_PEEK
			_responsePacket = _mainSock.recv (4 + _packetSize, peek_flag)
		else:
			_responsePacket = _mainSock.recv (_packetSize, peek_flag)
		if peek_flag != 0:
			_pattern = re.compile ('\<\?xml')
			_searchObj = re.search (_pattern, _responsePacket)
			_finalPacket = _responsePacket[_searchObj.start () :]
			_responsePacket = _finalPacket
		#_recvLck.release ()
		if peek_flag == 0 and _ldtpDebug != None and _ldtpDebug == '2':
			print 'Received response Packet', _responsePacket
		return _responsePacket
	except struct.error, msg:
		raise LdtpExecutionError ('Invalid packet length ' + str (msg))
	except socket.timeout:
		if _ldtpDebug != None and _ldtpDebug == '2':
			print 'Timeout'
		return ''
	except:
		raise LdtpExecutionError ('Error while receiving packet ' + str (traceback.print_exc ()))
	finally:
		if flag:
			# Reason for using the flag:
			# 'Do not call this method when the lock is unlocked.'
			_recvLck.release ()
			flag = False

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

def parsexml (xmldata):
	"""Returns the value obtained from the server's return LDTP packet"""
	_statusMsg      = None
	_statusCode     = None
	_responseType   = None
	_requestId      = None
	_responseObj    = None
	_data           = None

	try:
		dom = parseString (xmldata)
		try:
			_responseObj   = dom.getElementsByTagName ('RESPONSE')[0]
			_responseType = 'response'
		except IndexError:
			try:
				_responseObj   = dom.getElementsByTagName ('NOTIFICATION')[0]
				#_responseType = 'notification'
				return 'notification', None, None
			except IndexError:
				try:
					_responseObj   = dom.getElementsByTagName ('KEYBOARD')[0]
					#_responseType = 'keyboard'
					return 'keyboard', None, None
				except IndexError:
					return None
		try:
			_responseStatusObj = _responseObj.getElementsByTagName ('STATUS')[0]
			_statusCode = int (getText (_responseStatusObj.getElementsByTagName ('CODE')[0].childNodes))
		except ValueError:
			return None
		except IndexError:
			return None
		try:
			_statusMsg  = getText (_responseStatusObj.getElementsByTagName ('MESSAGE')[0].childNodes)
		except ValueError:
			pass
		except IndexError:
			pass
		try:
			_requestId  = getText (_responseObj.getElementsByTagName ('ID')[0].childNodes)
		except IndexError:
			# On notification _requestId will be empty
			pass
		try:
			_data = getText (_responseObj.getElementsByTagName ('DATA')[0].childNodes).encode ('utf-8')
		except ValueError:
			pass
		except IndexError:
			# Data tag may not be present
			pass
	except ExpatError, msg:
		if xml.parsers.expat.ErrorString (msg.code) == xml.parsers.expat.errors.XML_ERROR_NO_ELEMENTS:
			return None
		raise LdtpExecutionError ('Parsing XML error: ' + str (msg))
	return _responseType, (_statusCode, _statusMsg, _requestId), _data

def parsenotificationxml (xmldata):
	"""Returns the value obtained from the server's return LDTP packet"""
	_windowName = None
	_objectName = None
	_objectType = None
	_eventType  = None
	_key        = None
	_data       = None
	_detail1    = None
	_detail2    = None
	_timeElapsed     = None
	_notificationObj = None

	try:
		dom = parseString (xmldata)
		try:
			_notificationObj   = dom.getElementsByTagName ('NOTIFICATION')[0]
		except IndexError:
			return None
		try:
			_windowName = getText (_notificationObj.getElementsByTagName ('WINDOWNAME')[0].childNodes)
			_objectName = getText (_notificationObj.getElementsByTagName ('OBJECTNAME')[0].childNodes)
			_objectType = getText (_notificationObj.getElementsByTagName ('OBJECTTYPE')[0].childNodes)
			_eventType  = getText (_notificationObj.getElementsByTagName ('EVENTTYPE')[0].childNodes)
			_timeElapsed  = getText (_notificationObj.getElementsByTagName ('TIMEELAPSED')[0].childNodes)
		except ValueError:
			return None
		except IndexError:
			return None
		try:
			_key  = getText (_notificationObj.getElementsByTagName ('KEY')[0].childNodes)
		except ValueError:
			pass
		except IndexError:
			pass
		try:
			_data  = getText (_notificationObj.getElementsByTagName ('DATA')[0].childNodes)
		except ValueError:
			pass
		except IndexError:
			pass
		try:
			_detail1  = getText (_notificationObj.getElementsByTagName ('DETAIL1')[0].childNodes)
		except ValueError:
			pass
		except IndexError:
			pass
		try:
			_detail2  = getText (_notificationObj.getElementsByTagName ('DETAIL2')[0].childNodes)
		except ValueError:
			pass
		except IndexError:
			pass
	except ExpatError, msg:
		if xml.parsers.expat.ErrorString (msg.code) == xml.parsers.expat.errors.XML_ERROR_NO_ELEMENTS:
			return None
		raise LdtpExecutionError ('Parsing XML error: ' + str (msg))
	return _windowName, _objectName, _objectType, _eventType, _timeElapsed, _key, _data, _detail1, _detail2

def parsekeyboardxml (xmldata):
	"""Returns the value obtained from the server's return LDTP packet"""
	_keyboardData = None
	_timeElapsed  = None
	_keyboardObj  = None

	try:
		dom = parseString (xmldata)
		try:
			_keyboardObj   = dom.getElementsByTagName ('KEYBOARD')[0]
		except IndexError:
			return None
		try:
			_keyboardData = getText (_keyboardObj.getElementsByTagName ('DATA')[0].childNodes)
		except ValueError:
			return None
		except IndexError:
			return None
	except ExpatError, msg:
		if xml.parsers.expat.ErrorString (msg.code) == xml.parsers.expat.errors.XML_ERROR_NO_ELEMENTS:
			return None
		raise LdtpExecutionError ('Parsing XML error: ' + str (msg))
	return _keyboardData

#def getresponse (packetId):
#	while True:
#		_readFlag.wait ()
#		_readFlag.clear ()
#		_ldtpDebug = os.getenv ('LDTP_DEBUG')
#		peekResponsePacket = peekresponse ()
#		if peekResponsePacket == None or peekResponsePacket == '':
#			if _ldtpDebug != None and _ldtpDebug == '2':
#				print 'Peekresponse None'
#			continue
#		try:
#			_responseType, _responseStatus, _responseData = parsexml (peekResponsePacket)
#		except TypeError, msg:
#			if _ldtpDebug != None and _ldtpDebug == '2':
#				print 'TypeError', msg
#			continue
#		# For precautions, we are just checking, whether the packet is notification or not
#		if _responseType == 'notification' or _responseType == 'keyboard' or _responseType == None:
#			continue
#		if _responseStatus [2] == packetId:
#			if _responseStatus [0] != 0 and _ldtpDebug != None:
#				print '*** ' + _responseStatus [1]
#			packet = recvpacket ()
#			# As we have already parsed the packet,
#			# we are just returning the parsed packet
#			return _responseStatus, _responseData

class PollServer (threading.Thread):
	def __init__ (self,  pckt):
		self.pckt = pckt
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
				self._events = _serverPoll.poll ()
			except socket.error, msg:
				break
			except:
				_serverPoll.unregister (_mainSock)
				sys.exit ()
			try:
				if self._events == None:
					break
				for i in range (0, len (self._events)):
					if (self._events [i][1] & select.POLLIN or self._events [i][1] & select.POLLPRI):
						try:
							if self.handlePacket () == None:
								self._serverDisconnected = True
								break
						except LdtpExecutionError, msg:
							self._serverDisconnected = True
							# _readFlag.set ()
							break
						except:
							print traceback.print_exc ()
					elif (self._events [i][1] & select.POLLNVAL):
						# Unregister newly created socket from polling once its completed
						_serverPoll.unregister (self._events [i][0])
					else:
						self._serverDisconnected = True
						break
				if self._serverDisconnected == True:
					break
			# Checking this exception due to bug # 333090 comment # 6
			except TypeError:
				_serverPoll.unregister (_mainSock)
				sys.exit ()
	def handlePacket (self):
		self._responsePacket = None
		try:
			self._responsePacket = recvpacket ()
		except KeyboardInterrupt:
			return None
		self._responseType = None
		self._responseStatus = None
		self._responseData = None
		try:
			if self._responsePacket == None:
				# When there is no data to read let us quit
				return None
			if self._responsePacket != '':
				self._responseType, self._responseStatus, self._responseData = parsexml (self._responsePacket)
				if self._responseType == None:
					return None
			else:
				_readFlag.set ()
		except TypeError:
			if _ldtpDebug:
				print traceback.print_exc ()
			return ''
		except LdtpExecutionError, msg:
			if _ldtpDebug:
				print traceback.print_exc ()
			#_readFlag.set ()
			return ''
		except KeyboardInterrupt:
			return None
		try:
			if self._responseType == 'notification':
				if _notificationFlag.isSet ():
					# Let us allow only one callback function to execute at any point of time
					_notificationFlag.wait ()
					_notificationFlag.clear ()
					_windowName, _objectName, _objectType, _eventType, \
						     _timeElapsed, _key, _data, _detail1, \
						     _detail2 = parsenotificationxml (self._responsePacket)
					#packet = recvpacket ()
					# As we have already parsed the packet,
					# we are just returning the parsed packet
					self.pckt.pushPacket (self._responseType, _windowName, _objectName, _objectType, _eventType, \
							 _timeElapsed, _key, _data, _detail1, _detail2)
					_notificationFlag.set ()
				else:
					# CPU goes high for some time, if this delay is not there
					# as the notification packet is still in the Queue, but the
					# new spanned thread takes some time to receive the notification packet
					# So this delay is required
					time.sleep (1)
			elif self._responseType == 'keyboard':
				if _keyboardFlag.isSet ():
					# Let us allow only one callback function to execute at any point of time
					_keyboardFlag.wait ()
					_keyboardFlag.clear ()
					_keyboardData = parsekeyboardxml (self._responsePacket)
					# As we have already parsed the packet,
					# we are just returning the parsed packet
					#packet = recvpacket ()
					self.pckt.pushPacket (self._responseType, data = _keyboardData)
					_keyboardFlag.set ()
				else:
					# CPU goes high for some time, if this delay is not there
					# as the keyboard packet is still in the Queue, but the
					# new spanned thread takes some time to receive the keyboard packet
					# So this delay is required
					time.sleep (1)
			else:
				_readFlag.set ()
		except KeyboardInterrupt:
			return None
		return ''
	def getresponse (self, packetId):
		while True:
			_readFlag.wait ()
			_readFlag.clear ()
			if self._responseType != 'response':
				continue
			if self._responseStatus [2] == packetId:
				if _ldtpDebug and self._responseStatus [0] != 0:
					print '*** ' + self._responseStatus [1]
				#packet = recvpacket ()
				# As we have already parsed the packet,
				# we are just returning the parsed packet
			return self._responseStatus, self._responseData

	def shutdown (self):
		_readFlag.set ()

class packetInfo:
	def __init__ (self, packetType, windowName, objectName, objectType, eventType,
		      timeElapsed, key = None, data = None, detail1 = None,
		      detail2 = None):
		self.packetType = packetType
		self.windowName = windowName
		self.objectName = objectName
		self.objectType = objectType
		self.eventType = eventType
		self.timeElapsed = timeElapsed
		self.key = key
		self.data = data
		self.detail1 = detail1
		self.detail2 = detail2

class packet:
	def __init__ (self):
		self._packet = {}
		self._endPacketId = 0
		self._startPacketId = 0
		self._pushPacketEvent = threading.Event ()
		self._popPacketEvent = threading.Event ()
		self._pushPacketEvent.set ()
		self._popPacketEvent.set ()
	def pushPacket (self, packetType, windowName = None, objectName = None, objectType = None,
			eventType = None, timeElapsed = None, key = None, data = None,
			detail1 = None, detail2 = None):
		if self._pushPacketEvent.isSet ():
			self._pushPacketEvent.wait ()
			self._pushPacketEvent.clear ()
			_pcktInfo = packetInfo (packetType, windowName, objectName, objectType, eventType,
						timeElapsed, key, data, detail1, detail2)
			self._packet [self._endPacketId] = _pcktInfo
			self._endPacketId += 1
			self._pushPacketEvent.set ()
	def fetchPacket (self):
		if self._popPacketEvent.isSet ():
			self._popPacketEvent.wait ()
			self._popPacketEvent.clear ()
			_pcktInfo = None
			if self._startPacketId in self._packet:
				_pcktInfo = self._packet.pop (self._startPacketId)
			else:
				self._popPacketEvent.set ()
				return None
			self._startPacketId += 1
			self._popPacketEvent.set ()
			return _pcktInfo
	def peekPacket (self, pcktId = None):
		_pcktInfo = None
		if pcktId is not None:
			if pcktId in self._packet:
				_pcktInfo = self._packet [pcktId]
		else:
			if self._startPacketId in self._packet:
				_pcktInfo = self._packet [self._startPacketId]
		return _pcktInfo

def doesWindowExist (windowName):
	try:
		global _pollThread
		_requestId  = str (random.randint (0, sys.maxint))
		_message = generatexml (command.WINDOWEXIST, _requestId, windowName)
		sendpacket (_message)
		_responseStatus, _responseData = _pollThread.getresponse (_requestId)
		if _responseStatus [0] == 0:
			return True
		else:
			return False
	except:
		return False

def getObjectName (objName):
	try:
		global _pollThread
		_requestId  = str (random.randint (0, sys.maxint))
		_message = generatexml (command.GETOBJECTNAME, _requestId, objName)
		sendpacket (_message)
		_responseStatus, _responseData = _pollThread.getresponse (_requestId)
		if _responseStatus [0] == 0:
			return _responseData
		else:
			return None
	except:
		print traceback.print_exc ()
		return None

def addWait (callbackFunc, timeElapsed):
	global generatedCode
	if _ldtpDebug:
		print 'Time elapsed',  int (timeElapsed)
	try:
		if int (timeElapsed) > 0:
			codeToBeAdded = 'wait (' + timeElapsed + ')\n'
			generatedCode += codeToBeAdded
			callbackFunc (codeToBeAdded)
	except ValueError:
		pass

def callback (guiCallbackFunc, data, timeElapsed = None):
	global generatedCode
	if timeElapsed is not None:
		addWait (guiCallbackFunc, timeElapsed)
	generatedCode += data
	guiCallbackFunc (data)

def processData (pckt, callbackFunc):
	try:
		processDataDebug (pckt, callbackFunc)
	except:
		print traceback.print_exc ()

def processDataDebug (pckt, callbackFunc):
	global generatedCode
	# Its a hack, please remove it, once debugging is done
	while True:
		try:
			_pcktInfo = pckt.peekPacket ()
			if _pcktInfo:
				if pckt._startPacketId == pckt._endPacketId:
					# If both are same, let us wait till we receive the next packet
					pckt._pushPacketEvent.wait ()
				if _ldtpDebug and _ldtpDebug == '2':
					print 'libldtpcodegen', _pcktInfo.windowName, _pcktInfo.objectName,
					print _pcktInfo.objectType, _pcktInfo.eventType,
					print _pcktInfo.key, _pcktInfo.data
				if _pcktInfo.packetType == 'keyboard':
					# FIXME: Manipulate the keyboard strings with the text box
					_data = re.sub ("\"", "\\\"", _pcktInfo.data)
					callback (callbackFunc, 'enterstring (\"'+ _data + '\")\n', None)
					_pcktInfo = pckt.fetchPacket ()
					continue
				if _pcktInfo.objectType == 'push button':
					if _ldtpDebug:
						print pckt._startPacketId, pckt._endPacketId
					if _pcktInfo.eventType.startswith ('object:state-changed:armed') and \
					       pckt._startPacketId != pckt._endPacketId:
						_tmpPckt = pckt.peekPacket (pckt._startPacketId + 1)
						if _ldtpDebug and _ldtpDebug == 2 and _tmpPckt != None:
							print '*** tmpPckt', _tmpPckt
						if _tmpPckt == None or (_tmpPckt.objectType == _pcktInfo.objectType and \
										_tmpPckt.windowName == _pcktInfo.windowName and \
										_tmpPckt.objectName == _pcktInfo.objectName and \
										_tmpPckt.eventType.startswith ('focus:')):
							_data = re.sub ("\"", "\\\"", _pcktInfo.objectName)
							callback (callbackFunc, 'click (\"'+ _pcktInfo.windowName + \
									  '\", \"' + _data + '\")\n', _pcktInfo.timeElapsed)
							_pcktInfo = pckt.fetchPacket ()
							_pcktInfo = pckt.fetchPacket () # Note we are fetching two times
							continue
					elif _pcktInfo.eventType.startswith ('focus:') and doesWindowExist (_pcktInfo.windowName):
						if _ldtpDebug:
							print '*** Window exist'
						_pcktInfo = pckt.fetchPacket ()
						continue
					elif _pcktInfo.eventType.startswith ('focus:') and \
					       pckt._startPacketId != pckt._endPacketId:
						_tmpPckt = pckt.peekPacket (pckt._startPacketId + 1)
						if _ldtpDebug and _ldtpDebug == 2:
							print '*** tmpPckt', _tmpPckt
						if _tmpPckt == None or (_tmpPckt.objectType == _pcktInfo.objectType and \
									_tmpPckt.windowName == _pcktInfo.windowName and \
									_tmpPckt.objectName == _pcktInfo.objectName and \
									_tmpPckt.eventType.startswith ('object:state-changed:armed')):
							_data = re.sub ("\"", "\\\"", _pcktInfo.objectName)
							callback (callbackFunc, 'click (\"'+ _pcktInfo.windowName + \
									  '\", \"' + _data + '\")\n',
								  _pcktInfo.timeElapsed)
							_pcktInfo = pckt.fetchPacket ()
							_pcktInfo = pckt.fetchPacket () # Note we are fetching two times
							continue
					_data = re.sub ("\"", "\\\"", _pcktInfo.objectName)
					callback (callbackFunc, 'click (\"'+ _pcktInfo.windowName + \
							  '\", \"' + _data + '\")\n', _pcktInfo.timeElapsed)
					_pcktInfo = pckt.fetchPacket ()
					continue
				elif _pcktInfo.eventType.startswith ('object:state-changed:checked'):
					if _pcktInfo.objectType == 'check box':
						_data = re.sub ("\"", "\\\"", _pcktInfo.objectName)
						if _pcktInfo.detail1 == '1':
							callback (callbackFunc, 'check (\"'+ _pcktInfo.windowName + \
									  '\", \"' + _data + '\")\n',
								  _pcktInfo.timeElapsed)
						else:
							callback (callbackFunc, 'uncheck (\"'+ _pcktInfo.windowName + \
									  '\", \"' + _data + '\")\n',
								  _pcktInfo.timeElapsed)
						_pcktInfo = pckt.fetchPacket ()
						continue
					elif _pcktInfo.objectType == 'radio button' or \
						 _pcktInfo.objectType == 'toggle button':
						_data = re.sub ("\"", "\\\"", _pcktInfo.objectName)
						callback (callbackFunc, 'click (\"'+ _pcktInfo.windowName + \
								  '\", \"' + _data + '\")\n',
							  _pcktInfo.timeElapsed)
						_pcktInfo = pckt.fetchPacket ()
						continue
					else:
						_pcktInfo = pckt.fetchPacket ()
						if _ldtpDebug:
							print 'Invalid packet with object:state-changed:checked event type ??'
						continue
				elif _pcktInfo.eventType.startswith ('object:state-changed:selected'):
					if _pcktInfo.objectType == 'page tab':
						_responseData = getObjectName (_pcktInfo.objectName)
						if _responseData is not None:
							_data = re.sub ("\"", "\\\"", _pcktInfo.data)
							callback (callbackFunc, 'selecttab (\"'+ _pcktInfo.windowName + \
									  '\", \"' + _responseData + '\", \"' + \
									  _data + '\")\n',
								  _pcktInfo.timeElapsed)
						_pcktInfo = pckt.fetchPacket ()
						continue
					elif _pcktInfo.objectType == 'table cell':
						_responseData = getObjectName (_pcktInfo.objectName)
						if _responseData is not None:
							# Escape " as \" in data argument
							_data = re.sub ("\"", "\\\"", _pcktInfo.data)
							callback (callbackFunc, 'selectrow (\"'+ _pcktInfo.windowName + \
									  '\", \"' + _responseData + '\", \"' + \
									  _data + '\")\n',
								  _pcktInfo.timeElapsed)
						_pcktInfo = pckt.fetchPacket ()
						continue
					else:
						_pcktInfo = pckt.fetchPacket ()
						if _ldtpDebug:
							print 'Invalid packet with object:state-changed:selected event type ??'
						continue
				elif _pcktInfo.eventType.startswith ('focus:') and \
					 _pcktInfo.objectType == 'table cell':
					_tmpPckt = None
					if pckt._startPacketId != pckt._endPacketId:
						_tmpPckt = pckt.peekPacket (pckt._startPacketId + 1)
						if _tmpPckt is not None and str (_tmpPckt.eventType).startswith ('focus:') == False and \
						       _tmpPckt.objectType != _pcktInfo.objectType:
							_tmpPckt = None
					if _tmpPckt == None or (_tmpPckt.objectType == _pcktInfo.objectType and \
								_tmpPckt.windowName == _pcktInfo.windowName and \
								_tmpPckt.objectName == _pcktInfo.objectName and \
								_tmpPckt.eventType.startswith ('focus:')):
						_responseData = getObjectName (_pcktInfo.objectName)
						if _responseData is not None:
							_data = re.sub ("\"", "\\\"", _pcktInfo.data)
							callback (callbackFunc, 'selectrow (\"'+ _pcktInfo.windowName + \
									  '\", \"' + _responseData + '\", \"' + \
									  _data + '\")\n', _pcktInfo.timeElapsed)
						_pcktInfo = pckt.fetchPacket ()
						if _tmpPckt is not None:
							_pcktInfo = pckt.fetchPacket ()
					continue
				elif _pcktInfo.eventType.startswith ('window:create'):
					callback (callbackFunc, 'waittillguiexist (\"' + _pcktInfo.windowName + '\")\n')
					_pcktInfo = pckt.fetchPacket ()
					continue
				elif _pcktInfo.eventType.startswith ('window:destroy'):
					callback (callbackFunc, 'waittillguinotexist (\"' + _pcktInfo.windowName + '\")\n')
					_pcktInfo = pckt.fetchPacket ()
					continue
				elif _pcktInfo.objectType == 'spin button':
					_data = re.sub ("\"", "\\\"", _pcktInfo.data)
					callback (callbackFunc, 'setvalue (\"'+ _pcktInfo.windowName + \
							  '\", \"' + _pcktInfo.objectName + '\", \"' + \
							  _data + '\")\n',
						  _pcktInfo.timeElapsed)
					_pcktInfo = pckt.fetchPacket ()
#					if pckt._startPacketId != pckt._endPacketId:
#						_tmpPckt = pckt.peekPacket (pckt._startPacketId + 1)
#						if _ldtpDebug and _ldtpDebug == 2:
#							print '*** tmpPckt', _tmpPckt
#						if _tmpPckt == None or (_tmpPckt.objectType == _pcktInfo.objectType and \
#									_tmpPckt.windowName == _pcktInfo.windowName and \
#									_tmpPckt.objectName == _pcktInfo.objectName):
#							addWait (generatedCode, callbackFunc, _pcktInfo.timeElapsed)
#							generatedCode += 'setvalue (\"'+ _pcktInfo.windowName + \
#									 '\", \"' + _pcktInfo.objectName + '\", \"' + \
#									 _pcktInfo.data + '\")\n'
#							callbackFunc ('setvalue (\"'+ _pcktInfo.windowName + \
#									 '\", \"' + _pcktInfo.objectName + '\", \"' + \
#									 _pcktInfo.data + '\")\n')
#							if _tmpPckt is not None:
#								_pcktInfo = pckt.fetchPacket ()
#							_pcktInfo = pckt.fetchPacket ()
#					else:
#						addWait (generatedCode, callbackFunc, _pcktInfo.timeElapsed)
#						generatedCode += 'setvalue (\"'+ _pcktInfo.windowName + \
#								 '\", \"' + _pcktInfo.objectName + '\", \"' + \
#								 _pcktInfo.data + '\")\n'
#						callbackFunc ('setvalue (\"'+ _pcktInfo.windowName + \
#								 '\", \"' + _pcktInfo.objectName + '\", \"' + \
#								 _pcktInfo.data + '\")\n')
#						_pcktInfo = pckt.fetchPacket ()
					continue
				elif _pcktInfo.objectType == 'text':
					_objName = _pcktInfo.objectName
					if re.search ('#', _objName) is not None:
						_responseData = getObjectName (_pcktInfo.objectName)
						if _responseData is not None:
							_objName = _responseData
					_data = re.sub ("\"", "\\\"", _pcktInfo.data)
					callback (callbackFunc, 'settextvalue (\"'+ _pcktInfo.windowName + \
							  '\", \"' + _objName + '\", \"' + \
							  _data + '\")\n',
						  _pcktInfo.timeElapsed)
					_pcktInfo = pckt.fetchPacket ()
					continue
				elif _pcktInfo.objectType == 'combo box':
					_data = re.sub ("\"", "\\\"", _pcktInfo.data)
					callback (callbackFunc, 'comboselect (\"'+ _pcktInfo.windowName + \
							  '\", \"' + _pcktInfo.objectName + '\", \"' + \
							  _data + '\")\n',
						  _pcktInfo.timeElapsed)
					_pcktInfo = pckt.fetchPacket ()
					continue
				elif _pcktInfo.objectType == 'menu item':
					_data = re.sub ("\"", "\\\"", _pcktInfo.objectName)
					callback (callbackFunc, 'selectmenuitem (\"'+ _pcktInfo.windowName + \
							  '\", \"' + _data + '\")\n',
						  _pcktInfo.timeElapsed)
					_pcktInfo = pckt.fetchPacket ()
					continue
				elif _pcktInfo.objectType == 'right click':
					_objName = _pcktInfo.objectName
					if re.search ('#', _objName) is not None:
						_responseData = getObjectName (_pcktInfo.objectName)
						if _responseData is not None:
							_objName = _responseData
					_data = re.sub ("\"", "\\\"", _pcktInfo.data)
					callback (callbackFunc, 'rightclick (\"'+ _pcktInfo.windowName + \
							  '\", \"' + _objName + '\", \"' + \
							  _data + '\")\n',
						  _pcktInfo.timeElapsed)
					_pcktInfo = pckt.fetchPacket ()
					continue
				elif _pcktInfo.objectType == 'panel' and \
					 _pcktInfo.eventType.startswith ('object:state-changed:focused'):
					_objName = _pcktInfo.objectName
					if re.search ('#', _objName) is not None:
						_responseData = getObjectName (_pcktInfo.objectName)
						if _responseData is not None:
							_objName = _responseData
					_data = re.sub ("\"", "\\\"", _pcktInfo.data)
					callback (callbackFunc, 'selectpanelname (\"'+ _pcktInfo.windowName + \
							  '\", \"' + _objName + '\", \"' + \
							  _data + '\")\n',
						  _pcktInfo.timeElapsed)
					_pcktInfo = pckt.fetchPacket ()
					continue
				else:
					if _ldtpDebug:
						print 'Unknown object type', _pcktInfo.objectType
					_pcktInfo = pckt.fetchPacket ()
					continue
			else:
				time.sleep (1)
		except KeyboardInterrupt:
			break
		except:
			print traceback.print_exc ()
			pckt.fetchPacket ()
			raise

def stoprecord (filename = None):
	try:
		global _pollThread
		_requestId  = str (random.randint (0, sys.maxint))
		_message = generatexml (command.STOP, _requestId)
		sendpacket (_message)
		_responseStatus, _responseData = _pollThread.getresponse (_requestId)
	except:
		pass

def shutdown ():
	if calledFromGui == True:
		return
	if threading.activeCount () > 1:
		thread.exit ()
	sys.exit ()

def __shutdownAndExit (signum, frame):
    global generatedCode,  _mainSock
    stoprecord ()
    if _mainSock is not None:
        _mainSock.close ()
    shutdown ()
    if _ldtpDebug:
        print ''
        print ''
        print ''
        print generatedCode.encode ('utf8')
        print ''
        print ''
        print ''

def stop ():
	__shutdownAndExit (0, 0)

_socketPath = '/tmp/ldtp-record-' + os.getenv ('USER') + '-' + os.getenv ('DISPLAY')

# Create read flag
_readFlag = threading.Event ()
# Clear the flag by default
_readFlag.clear ()

# Create notification flag
_notificationFlag = threading.Event ()
# Set the flag by default
_notificationFlag.set ()

# Create keyboard flag
_keyboardFlag = threading.Event ()
# Set the flag by default
_keyboardFlag.set ()

# Contains poll fd's
_serverPoll = None

# Send lock
_sendLck = threading.Lock ()
# Recieve lock
_recvLck = threading.Lock ()

_mainSock = None
_pollThread = None
calledFromGui = False
generatedCode = ''

#All default parameters, and checking whether action is stoprecord, are to be removed
def start (callbackFunc, appName = 'ALL', args = None):
	if callbackFunc == None or callable (callbackFunc) == False:
		raise LdtpExecutionError ('Callback function is not callable')
	global _mainSock, _pollThread,  generatedCode
	try:
		# Create a client socket
		_mainSock = socket.socket (socket.AF_UNIX, socket.SOCK_STREAM)
	except socket.error,msg:
		raise LdtpExecutionError ('Error while creating UNIX socket  ' + str (msg))

	# Let us retry connecting to the server for 3 times
	retryCount = 0

	while True:
		try:
			try:
				# Connect to server socket
				_mainSock.connect (_socketPath)
				break
			except TypeError:
				raise ConnectionLost ('Unable to establish connection with ldtp code generator')
		except socket.error, msg:
			if retryCount == 3:
				raise ConnectionLost ('Could not establish connection ' + str (msg))
			retryCount += 1
			_pid = os.fork ()
			if _pid == 0:
				try:
					os.execvpe ('ldtpcodegen', [''], os.environ)
					os._exit (os.EX_OK)
				except OSError:
					raise LdtpExecutionError ('ldtp executable not in PATH')
			else:
				# Let us wait for 1 second, let the server starts
				time.sleep (1)

	pckt = packet ()
	generatedCode = 'from ldtp import *\n\n'

	# Start polling server
	_pollThread = PollServer (pckt)
	_pollThread.setDaemon (True)
	_pollThread.start ()
	atexit.register (_pollThread.shutdown)
	#atexit.register (shutdown)

	thread.start_new_thread (processData, (pckt, callbackFunc))
