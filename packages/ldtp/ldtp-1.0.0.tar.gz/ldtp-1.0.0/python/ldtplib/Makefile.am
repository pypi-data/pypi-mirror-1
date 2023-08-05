ldtp_DATA =		\
	acss.py		\
	ldtprecorder.py	\
	ldtpcommon.py	\
	libldtpcodegen.py	\
	ldtplibutils.py	\
	atspi.py	\
	debug.py	\
	__init__.py	\
	rolenames.py	\
	settings.py	\
	orca_i18n.py

pyc_DATA = $(ldtp_DATA:.py=.pyc)
pycdir = $(ldtpdir)

%.pyc: %.py
	$(PYTHON_CMD) -c "import py_compile; py_compile.compile ('$<', '$@')"

SUBDIRS = 

DIST_SUBDIRS = 

EXTRA_DIST =		\
	$(ldtp_DATA)

CLEANFILES =	\
	$(pyc_DATA)

MAINTAINERCLEANFILES =	\
	Makefile.in
