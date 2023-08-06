.EXPORT_ALL_VARIABLES:

CURDIR := $(shell pwd)

RST2HTML = rst2html

SOURCES := $(wildcard *.txt)
HTML_OBJS := $(patsubst %.txt,%.html,$(SOURCES))
ZIPBUNDLE := $(TOPDIR)/docs-upload.zip

%.html : %.txt
	$(RST2HTML) $< >$@

.PHONY: all
all: doc

.PHONY: doc docs
doc docs: html docbundle

.PHONY: html
html: $(HTML_OBJS)

.PHONY: docbundle
docbundle: $(ZIPBUNDLE)

$(ZIPBUNDLE): $(HTML_OBJS)
	$(MKDIR) upload
	$(CP) $(HTML_OBJS) upload/
	cd upload/ ; zip -9 -r $(ZIPBUNDLE) * ; cd ..
	$(RM) -rf upload

.PHONY: clean
clean:
	$(RM) $(HTML_OBJS)
	$(RM) $(ZIPBUNDLE)
