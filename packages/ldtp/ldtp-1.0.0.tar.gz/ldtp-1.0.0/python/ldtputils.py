#############################################################################
#
#  Linux Desktop Testing Project http://ldtp.freedesktop.org
# 
#  Author:
#     M Nagashree <mnagashree@novell.com>
#     Veerapuram Varadhan <v.varadhan@gmail.com>
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

import sys, commands, os, string, ldtp, time, xml.dom.minidom
import threading, re, tempfile

statGrabMsg = None
try:
	import statgrab
except ImportError:
	statGrabMsg = 'pystatgrab package not installed'

def tuplelist2list (lst):
        d = []
        for x in range (1, len (lst) + 1):
                for y in range (1, len (lst[x-1]) + 1):
                        d.append (lst[x-1][y-1])
        return d

def getFullPath (path):
    if path[0] == "~":
        path = os.path.expanduser (path)
    elif path[0] == ".":
        path = os.path.abspath (path)

    return path

def imagecompare (imgfile1, imgfile2):
	try:
		import ImageChops, Image
	except ImportError:
		ldtp.log ('Python-Imaging package not installed', 'error')
		raise ldtp.LdtpExecutionError ('Python-Imaging package not installed')
	try:
		diffcount = 0.0
		im1 = Image.open (imgfile1)
		im2 = Image.open (imgfile2)

		imgcompdiff = ImageChops.difference (im1, im2)
		diffboundrect = imgcompdiff.getbbox ()
		imgdiffcrop = imgcompdiff.crop (diffboundrect)

		seq = list (imgdiffcrop.getdata ())
		seq = tuplelist2list (seq)
		#print seq
		for i in range (0, imgdiffcrop.size[0] * imgdiffcrop.size[1] * 3, 3):
			if seq[i] != 0 or seq[i+1] != 0 or seq[i+2] != 0:
				diffcount = diffcount + 1.0
		
		diffImgLen = imgcompdiff.size[0] * imgcompdiff.size[1] * 1.0
		diffpercent = (diffcount * 100) / diffImgLen
		ldtp.log ('length ' + str (diffImgLen))
		ldtp.log ('diffcount ' + str (diffcount))
		ldtp.log ('diff percent ' + str (diffpercent))
		return diffpercent
	except IOError:
		ldtp.log ('Input file does not exist', 'error')
		raise ldtp.LdtpExecutionError ('Input file does not exist')

def winname_to_winid (winname):
	fp = os.popen ('digwin -c')
	lines = fp.readlines ()
	fp.close ()
	winid = ''
	for i in lines:
		if string.find (string.upper (i), string.upper (winname)) != -1:
			winid = i
			break
       	if winid == '':
		ldtp.log (winname + ' - window doesnot exist', 'error')
		raise ldtp.error, winname + ' - window doesnot exist'
	winid = string.split (winid, ' ')[0]
	winid = string.split (winid, '(')[1]
	winid = string.split (winid, ')')[0]
	return winid

def imagecapture (winName = None, outFile = None, resolution1 = '1024', resolution2 = '768', x = '0', y = '0'):
	# winname == None, let us capture the entire screen
	# if output file name is not passed, then a random file name will be generated in
	# /tmp and it will be returned
	if winName == None:
		winid = 'root'
	else:
		status = commands.getstatusoutput ('which digwin')
		if status [0] != 0:
			raise ldtp.LdtpExecutionError ('To capture invidual window, you need to install digwin of LTFX')
		winid = winname_to_winid (winname)
		winid = '0x' + winid
	if outFile == None:
		file = tempfile.NamedTemporaryFile ()
		tmpFile = file.name + '.png'
		file.close ()
	else:
		tmpFile = outFile
	cmd = 'import -window ' + winid + ' -crop ' + resolution1 + 'x' + resolution2 + '+' + x + '+' + y  + ' ' + tmpFile
	status = commands.getstatusoutput (cmd)
	if status [0] != 0:
		ldtp.log ('Unable to capture', 'error')
		return None
	return tmpFile

def blackoutregion (infile, outfile, topx, topy, botx, boty):
	try:
		import ImageChops, Image
	except ImportError:
		ldtp.log ('Python-Imaging package not installed', 'error')
		raise ldtp.LdtpExecutionError ('Python-Imaging package not installed')
	im = Image.open (infile)
	box = (topx, topy, botx, boty)
	region = im.crop (box)
	region = region.point (lambda i: i * 0)
	im.paste (region, box)
	im.save (outfile)

# XML Data file parser
class LdtpDataFileParser:
	def __init__ (self, filename = None):
		self.ldtpdataxml = []
		if filename != None:
			ldtpDebug = os.getenv ('LDTP_DEBUG')
			try:
				dom = xml.dom.minidom.parse (filename)
				self.ldtpdataxml = dom.getElementsByTagName ("data")
				if self.ldtpdataxml == []:
					ldtp.log ('data xml tag not present')
					if ldtpDebug != None and ldtpDebug == '2':
						print 'data xml tag not present'
			except xml.parsers.expat.ExpatError, msg:
				ldtp.log ('XML Error: ' + str (msg), 'error')
			except IOError:
				ldtp.log ('XML \"' + filename + '\" file not found', 'error')
	def setfilename (self, filename):
		self.ldtpdataxml = []
		if filename != None:
			ldtpDebug = os.getenv ('LDTP_DEBUG')
			try:
				dom = xml.dom.minidom.parse (filename)
				self.ldtpdataxml = dom.getElementsByTagName ("data")
				if self.ldtpdataxml == []:
					ldtp.log ('data xml tag not present')
					if ldtpDebug != None and ldtpDebug == '2':
						print 'data xml tag not present'
			except xml.parsers.expat.ExpatError, msg:
				if ldtpDebug != None and ldtpDebug == '2':
					print 'XML Error: ' + str (msg)
				ldtp.log ('XML Error: ' + str (msg), 'error')
			except IOError:
				if ldtpDebug != None and ldtpDebug == '2':
					print 'XML \"' + filename + '\" file not found'
				ldtp.log ('XML \"' + filename + '\" file not found', 'error')
	def getText (self, nodelist):
		rc = ""
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				rc = rc + node.data
		return rc
	def gettagvalue (self, tagname):
		self.taglist = []
		if self.ldtpdataxml == []:
			return self.taglist
		for dataelements in self.ldtpdataxml:
			for data in dataelements.getElementsByTagName (tagname):
				self.taglist.append (self.getText (data.childNodes))
		return self.taglist

class pstats (threading.Thread):
	"""Capturing Memory and CPU Utilization statistics for an application and its related processes
	EXAMPLE USAGE:
		xstats = pstats('evolution', 2)
		# Start Logging by calling start
		xstats.start()
		# Stop the process statistics gathering thread by calling the stopstats method
		xstats.stop()"""

	def __init__ (self, appname, inter = 2):
		if statGrabMsg is not None:
			ldtp.log (statGrabMsg, 'error')
			raise ldtp.LdtpExecutionError (statGrabMsg)
		threading.Thread.__init__ (self)
		self.processname = appname
		self.interval = inter
		self.stop_flag = 0
	def run (self):
		while (self.stop_flag == 0):
			for i in statgrab.sg_get_process_stats ():
				if self.stop_flag == 1:
					break
				result = re.search (self.processname, str(i['process_name']))
				if (result):
					title = str (i['proctitle'])
					proctitle = re.split ("\s", title)
					procname = re.split ("\/", proctitle[0])
					# Put the stats into ldtp log file	
					ldtp.log (procname[-1] + ' - ' + str (i['proc_resident'] / (1024*1024)) + 'M',
						  'meminfo')
					ldtp.log (procname[-1] + ' - ' + str (round(i['cpu_percent'], 2)),
						  'cpuinfo')
			# Wait for interval seconds before gathering stats again
			time.sleep (self.interval)

	def stop (self):
		self.stop_flag = 1

############# Application Functions #################

def execute (cmd):
	status = commands.getstatusoutput (cmd)
        if status[0] != 0:
               	ldtp.log (status[1], 'error')
		raise ldtp.LdtpExecutionError (status[1])
	return 1
	
########### LTFX Functions ###############
def getactivewin ():
	#Get currently active window title name
	cmd = "ltfx -e 'get_active_win'"
	status = commands.getstatusoutput (cmd)
        if status[0] != 0:
               	ldtp.log (status[1], 'error')
		raise ldtp.LdtpExecutionError (status[1])
	return status[1]
	
def windowexists (window_name):
	#Check window name exists with the given name
	cmd = "ltfx -e \'win_exists \"" +  window_name + "\"\'"
	return execute (cmd)

def partialexists (window_name):
	#Check window name exists with the given partial name
	cmd = "ltfx -e \'win_exists_partial \"" +  window_name + "\"\'"
	return execute (cmd)

def activatewinpartialname (window_name):
	# Set active window based on the given partial name"
	cmd = "ltfx -e \'activate_win_partial \"" +  window_name + "\"\'"
	return execute (cmd)

def activatewin (window_name):
	#Set active window based on the given name
	cmd = "ltfx -e \'activate_win \"" +  window_name + "\"\'"	
	return execute (cmd)

def activatewinid (window_id):
	#Set active window based on the given window-id
	cmd = "ltfx -e \'activate_win_id \"" +  window_id + "\"\'"	
	return execute (cmd)

def closewindow  (window_name):
	#Close the window with the given title
	return 0

def waitwinname (window_name):
	#Wait for window with name to appear
	cmd = "ltfx -e 'wait_for_win \"" +  window_name + "\"\'"	
	return execute (cmd)

def waitwinpartialname (window_name):
	#Wait for window with partial name to appear
	cmd = "ltfx -e 'wait_for_win_partial \"" +  window_name + "\"\'"	
	return execute (cmd)

def waitwinclose (window_name):
	#Wait for window to close with the given name
	cmd = "ltfx -e 'wait_for_close \"" +  window_name + "\"\'"	
	return execute (cmd)

def waitwinpartialclose (window_name):
	#Wait for window to close with the given partial name
	cmd = "ltfx -e 'wait_for_close_partial \"" +  window_name + "\"\'"		
	return execute (cmd)

def typekey (window_name):
	#Type the given text in the focused window
	cmd = "ltfx -e 'type \"" +  window_name + "\"\'"	
	return execute (cmd)
