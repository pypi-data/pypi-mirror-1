# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXBUILD= sphinx-build
FORMAT=html
BUILDDIR=/home/sasha/nodes-ai/doc/_build/$(FORMAT)
SRCDIR=/home/sasha/nodes-ai/doc
SPHINXOPTS=
EXPSITE=/home/sasha/nodes-site-nonsvn


.PHONY: build clean fix linkcheck forzip prepare

build:
	$(SPHINXBUILD) -b $(FORMAT) $(SPHINXOPTS) $(SRCDIR) $(BUILDDIR)

clean:
	svn revert $(BUILDDIR)

fix: build
	svn add $(BUILDDIR)/*.html 2>/dev/null
	svn commit $(BUILDDIR) -m "Automatic update"

forzip: build
	rm -rf $(EXPSITE)
	svn export $(BUILDDIR) $(EXPSITE)
	chmod +r -R $(EXPSITE)

prepare: fix zipit
	@echo "OK doc prepared"

linkcheck:
	mkdir -p $(BUILDDIR)/linkcheck
	$(SPHINXBUILD) -b linkcheck $(SPHINXOPTS) $(SRCDIR) $(BUILDDIR)/linkcheck

