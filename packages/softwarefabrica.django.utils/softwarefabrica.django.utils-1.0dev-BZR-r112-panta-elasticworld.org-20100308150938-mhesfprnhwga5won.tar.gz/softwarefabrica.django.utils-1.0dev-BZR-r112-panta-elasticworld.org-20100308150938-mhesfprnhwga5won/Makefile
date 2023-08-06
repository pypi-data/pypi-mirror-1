.EXPORT_ALL_VARIABLES:

SHELL = /bin/bash
MAKE  = make
MKDIR = /bin/mkdir
CP    = /bin/cp
RM    = /bin/rm -f
MV    = /bin/mv
CAT   = /bin/cat
FIND  = /usr/bin/find
XARGS = /usr/bin/xargs
PYTHON = python
BZR   = bzr

PYTHON24 = python2.4
PYTHON25 = python2.5
PYTHON26 = python2.6

SUBDIRS = docs

LP_NAME = sf-django-utils

# ------------------------------------------------------------------------
# E N V I R O N M E N T
# ------------------------------------------------------------------------

ifeq (0,${MAKELEVEL})
TOPDIR    := $(shell pwd)
whoami    := $(shell whoami)
MAKE      := ${MAKE} whoami=${whoami}
endif

BUILDDIR := $(TOPDIR)/build

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

# the package *MUST* be built before at least once with the default Python
# (the one that has bzrlib), to generate a proper up-to-date bzrcachedrev.py
# so we add a dependency to 'package' to every version specific packageXX

.PHONY: prebuild
prebuild:
	-$(RM) -rf $(BUILDDIR)
	-$(FIND) $(TOPDIR) -name '*.pyc' | $(XARGS) $(RM)
	-$(RM) -rf *.egg-info

.PHONY: package
package: doc
	-$(RM) -rf $(BUILDDIR)
	-$(FIND) $(TOPDIR) -name '*.pyc' | $(XARGS) $(RM)
	-$(RM) -rf *.egg-info
	$(PYTHON) setup.py bdist_egg
	@echo "Default Python package build complete."

.PHONY: package24
package24: doc package
	-$(RM) -rf $(BUILDDIR)
	-$(FIND) $(TOPDIR) -name '*.pyc' | $(XARGS) $(RM)
	-$(RM) -rf *.egg-info
	$(PYTHON24) setup.py bdist_egg
	@echo "Python 2.4 package build complete."

.PHONY: package25
package25: doc package
	-$(RM) -rf $(BUILDDIR)
	-$(FIND) $(TOPDIR) -name '*.pyc' | $(XARGS) $(RM)
	-$(RM) -rf *.egg-info
	$(PYTHON25) setup.py bdist_egg
	@echo "Python 2.5 package build complete."

.PHONY: package26
package26: doc package
	-$(RM) -rf $(BUILDDIR)
	-$(FIND) $(TOPDIR) -name '*.pyc' | $(XARGS) $(RM)
	-$(RM) -rf *.egg-info
	$(PYTHON26) setup.py bdist_egg
	@echo "Python 2.6 package build complete."

.PHONY: spackage srcpackage
spackage srcpackage: doc
	-$(RM) -rf $(BUILDDIR)
	-$(FIND) $(TOPDIR) -name '*.pyc' | $(XARGS) $(RM)
	-$(RM) -rf *.egg-info
	$(PYTHON) setup.py sdist
	@echo "Source package build complete."

.PHONY: upload-official
upload-official: spackage package
	-$(RM) -rf $(BUILDDIR)
	-$(FIND) $(TOPDIR) -name '*.pyc' | $(XARGS) $(RM)
	-$(RM) -rf *.egg-info
	$(PYTHON) setup.py sdist bdist_egg upload

.PHONY: upload
upload: upload-official upload24 upload25 upload26
	-$(RM) -rf $(BUILDDIR)
	-$(FIND) $(TOPDIR) -name '*.pyc' | $(XARGS) $(RM)
	-$(RM) -rf *.egg-info

.PHONY: upload24
upload24: spackage package24
	-$(RM) -rf $(BUILDDIR)
	-$(FIND) $(TOPDIR) -name '*.pyc' | $(XARGS) $(RM)
	-$(RM) -rf *.egg-info
	$(PYTHON24) setup.py bdist_egg upload

.PHONY: upload25
upload25: spackage package25
	-$(RM) -rf $(BUILDDIR)
	-$(FIND) $(TOPDIR) -name '*.pyc' | $(XARGS) $(RM)
	-$(RM) -rf *.egg-info
	$(PYTHON25) setup.py bdist_egg upload

.PHONY: upload26
upload26: spackage package26
	-$(RM) -rf $(BUILDDIR)
	-$(FIND) $(TOPDIR) -name '*.pyc' | $(XARGS) $(RM)
	-$(RM) -rf *.egg-info
	$(PYTHON26) setup.py bdist_egg upload

.PHONY: dev develop
dev develop:
	$(PYTHON) setup.py develop

.PHONY: commit
commit:
	$(BZR) push lp:$(LP_NAME)
