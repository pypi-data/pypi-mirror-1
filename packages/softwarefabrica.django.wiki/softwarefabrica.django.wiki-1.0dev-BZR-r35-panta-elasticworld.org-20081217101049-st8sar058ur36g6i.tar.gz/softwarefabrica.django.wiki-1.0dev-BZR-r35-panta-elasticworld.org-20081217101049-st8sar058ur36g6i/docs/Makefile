.EXPORT_ALL_VARIABLES:

RST2HTML = rst2html

SOURCES := $(wildcard *.txt)
HTML_OBJS := $(patsubst %.txt,%.html,$(SOURCES))

%.html : %.txt
	$(RST2HTML) $< >$@

.PHONY: all
all: doc

.PHONY: doc docs
doc docs: html

.PHONY: html
html: $(HTML_OBJS)

.PHONY: clean
clean:
	$(RM) $(HTML_OBJS)
