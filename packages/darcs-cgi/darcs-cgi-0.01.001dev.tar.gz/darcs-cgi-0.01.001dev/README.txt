This file is for you to describe the darcs-cgi application. Typically
you would include information such as the information below:

Dependencies
======================

PyMe is not included on PyPI, furthermore it is a distutils/swig project (as opposed to setuptools)

    . download and untar the source, last I checked was at http://pyme.sourceforge.net/
    . build the C/swig code via make
    . depending on your sh version, setup.py wont work. If so, change line 34
            << cmd = os.popen("sh gpgme-config --%s" % what, "r")
            >> cmd = os.popen("bash gpgme-config --%s" % what, "r")
    . easy_install ./ (thats the directory with setup.py)


Installation and Setup
======================

Install ``darcs-cgi`` using easy_install::

    easy_install darcs-cgi

Make a config file as follows::

    paster make-config darcs-cgi config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go.
