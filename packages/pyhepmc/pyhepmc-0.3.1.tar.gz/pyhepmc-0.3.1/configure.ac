dnl Process this file with autoconf to produce a configure script.
AC_INIT(hepmc-python, 0.3.1, andy@insectnation.org)
AC_CONFIG_HEADERS(Config.hh)
AC_CONFIG_SRCDIR(hepmc.i)

AM_INIT_AUTOMAKE

AC_DISABLE_STATIC
AC_PROG_LIBTOOL
AM_PATH_PYTHON(2.3)
AC_PROG_SWIG(1.3.21)
SWIG_ENABLE_CXX
SWIG_PYTHON

## Check for HepMC
AC_ARG_WITH([hepmc], 
  AC_HELP_STRING([--with-hepmc], [specify path to HepMC install prefix]), 
  [HEPMCPATH=${with_hepmc}], [HEPMCPATH=${prefix}])
AC_MSG_NOTICE([Looking for HepMC under $HEPMCPATH:])
HEPMCLIBPATH=$HEPMCPATH/lib
HEPMCINCPATH=$HEPMCPATH/include
AC_CHECK_FILE([$HEPMCPATH/include/HepMC/GenEvent.h], [], badhepmc=yes)
AC_CHECK_FILE([$HEPMCPATH/include/HepMC/GenVertex.h], [], badhepmc=yes)
AC_CHECK_FILE([$HEPMCPATH/include/HepMC/GenParticle.h], [], badhepmc=yes)
AC_CHECK_FILE([$HEPMCPATH/include/HepMC/IO_GenEvent.h], [], badhepmc=yes)
if test x${badhepmc} == "yes"; then
    AC_MSG_ERROR([Bad HepMC installation... try again.])
else
    AC_MSG_NOTICE([Using HepMC from $HEPMCPATH])
fi
AC_SUBST(HEPMCPATH)
AC_SUBST(HEPMCINCPATH)
AC_SUBST(HEPMCLIBPATH)

AC_OUTPUT(Makefile setup.py)
