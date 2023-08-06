ACLOCAL_AMFLAGS = -I m4

EXTRA_DIST = hepmc.i ez_setup.py

all-local: hepmc.i
#	install -m 644 $(top_srcdir)/hepmc.i $(top_builddir)
#	install -m 644 $(top_srcdir)/ez_setup.py $(top_builddir)
	$(PYTHON) setup.py build

install-exec-local:
	$(PYTHON) setup.py install --prefix=$(prefix)

uninstall-local:
	rm -rf $(libdir)/python*/site-packages/*hepmc*

clean-local:
	$(PYTHON) setup.py clean --all
	@rm -f $(top_builddir)/*.pyc
#	@rm -f $(top_builddir)/hepmc.i
#	@rm -f $(top_builddir)/ez_setup.py

distclean-local:
	@rm -rf pyhepmc.egg-info
	@rm -rf dist
	@rm -rf hepmc.py
	@rm -rf hepmc_wrap.cpp

#hepmc_wrap.cc hepmc.py: hepmc.i
#	$(SWIG) $(SWIG_PYTHON_OPT) -I$(HEPMCINCPATH) -o hepmc_wrap.cc $<



## Tests
EXTRA_DIST += test1.py
dist_noinst_DATA = LEP10.hepmc

installcheck-local:
	$(PYTHON) $(top_srcdir)/test1.py
