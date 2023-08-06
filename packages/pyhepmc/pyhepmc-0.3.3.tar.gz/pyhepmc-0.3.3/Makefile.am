ACLOCAL_AMFLAGS = -I m4

EXTRA_DIST = hepmc.i ez_setup.py

all-local: hepmc_wrap.cc
	$(PYTHON) setup.py build

install-exec-local:
	$(PYTHON) setup.py install --prefix=$(prefix)

uninstall-local:
	rm -rf $(libdir)/python*/site-packages/*hepmc*

clean-local:
	$(PYTHON) setup.py clean --all
	@rm -f $(top_builddir)/*.pyc

distclean-local:
	@rm -rf pyhepmc.egg-info
	@rm -rf dist
	@rm -rf hepmc.py
	@rm -rf hepmc_wrap.cc


## Bundling SWIG-built sources with the tarball for SL4 compat
EXTRA_DIST += hepmc_wrap.cc hepmc.py
hepmc_wrap.cc hepmc.py: hepmc.i
	swig -c++ -python -I$(HEPMCINCPATH) -o hepmc_wrap.cc $<



## Tests
EXTRA_DIST += test1.py
dist_noinst_DATA = LEP10.hepmc

installcheck-local:
	$(PYTHON) $(top_srcdir)/test1.py
