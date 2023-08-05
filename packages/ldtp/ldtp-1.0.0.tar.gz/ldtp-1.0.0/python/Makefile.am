python_DATA =		\
	ldtp.py		\
	ldtputils.py	\
	ooldtp.py

pyc_DATA = $(python_DATA:.py=.pyc)
pycdir = $(pythondir)
gladedir=$(datadir)/ldtp/glade

%.pyc: %.py
	$(PYTHON_CMD) -c "import py_compile; py_compile.compile ('$<', '$@')"

bin_SCRIPTS =		\
	ldtp2		\
	ldtpcodegen	\
	ldtpeditor	\
	ldtprecord	\
	ldtprunner

glade_DATA = ldtpeditor.glade

SUBDIRS = ldtplib

DIST_SUBDIRS = ldtplib

EXTRA_DIST =		\
	$(bin_SCRIPTS)	\
	$(python_DATA)	\
	$(glade_DATA)

CLEANFILES =	\
	$(pyc_DATA)

MAINTAINERCLEANFILES =	\
	Makefile.in
