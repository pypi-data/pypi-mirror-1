ACLOCAL_AMFLAGS = -I m4

BUILT_SOURCES = hepmc_wrap.cc hepmc.py
CLEANFILES = $(BUILT_SOURCES)
SWIG_SOURCE = hepmc.i
EXTRA_DIST = $(SWIG_SOURCE)

all-local:	$(BUILT_SOURCES)
	$(PYTHON) setup.py build

install-exec-local:
	$(PYTHON) setup.py install --prefix=$(prefix)
#$(DESTDIR)

uninstall-local:
	rm -rf $(DESTDIR)$(libdir)/python*/site-packages/*hepmc*

clean-local:
	@rm -f *.pyc 
	$(PYTHON) setup.py clean --all

distclean-local:
	@rm -rf pyhepmc.egg-info
	@rm -rf dist

hepmc_wrap.cc hepmc.py: $(SWIG_SOURCE)
	$(SWIG) $(SWIG_PYTHON_OPT) -I$(HEPMCPATH)/include -o hepmc_wrap.cc $<



## Tests
EXTRA_DIST += test1.py
dist_noinst_DATA = LEP10.hepmc

installcheck-local:
	$(PYTHON) $(top_srcdir)/test1.py
