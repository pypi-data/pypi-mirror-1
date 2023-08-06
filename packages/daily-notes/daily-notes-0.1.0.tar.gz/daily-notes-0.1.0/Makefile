# Makefile - Makefile for daily-notes

PROGRAM_NAME = daily-notes
INSTALL = install
RM = rm -f
TARGET = $(PROGRAM_NAME).py
PREFIX = /usr
BIN_DIR = $(PREFIX)/bin
POFILE = *.po
MSGFMT = ./msgfmt.py
LOCALEDIR = /usr/share/locale

all: install

install:
	$(INSTALL) -m 755 src/$(TARGET) $(BIN_DIR)
	$(MSGFMT) po/*.po 
	$(shell for i in po/*.mo; do $(INSTALL) -m 644 $$i $(LOCALEDIR)/`echo $$i | /usr/bin/sed 's/.*\/\(.*\)\.mo$$/\1/'`/LC_MESSAGES/$(PROGRAM_NAME).mo; done;) 

clean:
	$(RM) po/*.mo

.PHONY: all install clean
