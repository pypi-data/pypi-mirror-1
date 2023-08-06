ACLOCAL_AMFLAGS = -I m4

BUILT_SOURCES = hepmc_wrap.cc
SWIG_SOURCES  = hepmc.i
dist_bin_SCRIPTS = mcview
python_PYTHON = hepmc.py
pyexec_LTLIBRARIES = _hepmc.la
_hepmc_la_SOURCES = hepmc_wrap.cc $(SWIG_SOURCES)
_hepmc_la_CPPFLAGS = $(SWIG_PYTHON_CPPFLAGS) -I$(HEPMCPATH)/include
_hepmc_la_LDFLAGS = -module -L$(HEPMCPATH)/lib
_hepmc_la_LIBADD = -lHepMC

hepmc_wrap.cc hepmc.py : $(SWIG_SOURCES)
	$(SWIG) $(SWIG_PYTHON_OPT) -I$(HEPMCPATH)/include -o hepmc_wrap.cc $<

TESTS = test1.py

clean-local:
	@rm -f *.pyc 