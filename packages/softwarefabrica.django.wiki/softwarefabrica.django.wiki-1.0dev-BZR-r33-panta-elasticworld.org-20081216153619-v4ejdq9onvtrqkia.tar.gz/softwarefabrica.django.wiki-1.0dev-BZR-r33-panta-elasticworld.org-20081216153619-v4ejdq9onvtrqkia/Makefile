.EXPORT_ALL_VARIABLES:

SHELL = /bin/bash
MAKE  = make
MKDIR = /bin/mkdir
CP    = /bin/cp
RM    = /bin/rm -f
MV    = /bin/mv
CAT   = /bin/cat
PYTHON = python

SUBDIRS = docs

# ------------------------------------------------------------------------
# E N V I R O N M E N T
# ------------------------------------------------------------------------

ifeq (0,${MAKELEVEL})
TOPDIR    := $(shell pwd)
whoami    := $(shell whoami)
MAKE      := ${MAKE} whoami=${whoami}
endif

.PHONY: all
all: doc package spackage upload
ifdef SUBDIRS
	for i in $(SUBDIRS); do $(MAKE) TOPDIR=${TOPDIR} -C $$i; done
endif
	@echo "Build complete."

.PHONY: doc docs
doc docs:
ifdef SUBDIRS
	for i in $(SUBDIRS); do $(MAKE) TOPDIR=${TOPDIR} -C $$i doc; done
endif
	@echo "Documentation build complete."

.PHONY: clean
clean:
ifdef SUBDIRS
	for i in $(SUBDIRS); do $(MAKE) TOPDIR=${TOPDIR} -C $$i clean; done
endif

.PHONY: package
package: doc
	$(PYTHON) setup.py bdist_egg
	@echo "Package build complete."

.PHONY: spackage srcpackage
spackage srcpackage: doc
	$(PYTHON) setup.py sdist
	@echo "Source package build complete."

.PHONY: upload
upload: spackage package
	$(PYTHON) setup.py bdist_egg sdist upload

.PHONY: dev develop
dev develop:
	$(PYTHON) setup.py develop
