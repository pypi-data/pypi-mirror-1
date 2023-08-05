if GCC_CMD
	AM_CFLAGS = -Wall -Wunused -Wmissing-prototypes -Wmissing-declarations
endif

INCLUDES = \
	$(LIBXML2_CFLAGS)	\
	$(GLIB2_CFLAGS)		\
	$(CSPI_1_0_CFLAGS)

bin_PROGRAMS = ldtp

ldtp_SOURCES = \
	ldtp.c				\
	ldtp.h				\
	ldtp-command.h			\
	ldtp-server.c			\
	ldtp-server.h			\
	ldtp-logger.c			\
	ldtp-logger.h			\
	client-handler.c		\
	client-handler.h		\
	ldtp-request.h			\
	ldtp-request.c			\
	ldtp-response.h			\
	ldtp-utils.c			\
	ldtp-utils.h			\
	ldtp-gui.c			\
	ldtp-gui.h			\
	ldtp-gui-comp.h			\
	ldtp-error.c			\
	ldtp-error.h			\
	localization.c			\
	localization.h			\
	calendar.c			\
	calendar-view.c			\
	check-box.c			\
	check-menu-item.c		\
	combo-box.c			\
	icon.c				\
	label.c				\
	layered-pane.c			\
	ldtp-appmap.c			\
	ldtp-appmap.h			\
	list.c				\
	menu.c				\
	menu-item.c			\
	page-tab-list.c			\
	panel.c				\
	push-button.c			\
	radio-button.c			\
	radio-menu-item.c		\
	remap.c				\
	remap.h				\
	scroll-bar.c			\
	scroll-pane.c			\
	slider.c			\
	spin-button.c			\
	status-bar.c			\
	table.c				\
	text.c				\
	toggle-button.c			\
	tool-bar.c			\
	tree-table.c			\
	device.c			\
	device.h			\
	embedded-component.c

ldtp_LDADD = \
	$(LIBXML2_LIBS)		\
	$(GLIB2_LIBS)		\
	$(PTHREAD_LIB)		\
	$(CSPI_1_0_LIBS)	\
	$(LOCALIZATION_LIB)
