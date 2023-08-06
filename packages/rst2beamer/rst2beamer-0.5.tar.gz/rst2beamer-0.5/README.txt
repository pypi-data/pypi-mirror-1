Introduction
============

A docutils script converting restructured text into Beamer-flavoured LaTeX.

Beamer is a LaTeX document class for presentations. rst2beamer [#homepage]_
provides a Docutils [#docutils]_ writer that transforms restructured text
[#rst]_ into Beamer-flavoured LaTeX. and provides a commandline script for the
same. Via this script, ReST can therefore be used to prepare slides and
presentations.


Installation
============

rst2beamer can be installed in a number of ways.
setuptools [#setuptools]_ is preferred, but a manual installation will
suffice.

Via setuptools / easy_install
-----------------------------

From the commandline call::

	% easy_install rst2beamer

Superuser privileges may be required. 


Via setup.py
------------

Download a source tarball, unpack it and call setup.py to
install::

	% tar zxvf rst2beamer.tgz
	% cd rst2beamer
	% python setup.py install

Superuser privileges may be required. 


Manual
------

Download and unpack the tarball as above. Ensure Docutils is available. Copy
the script ``rst2beamer.py`` to a location it can be called from.


Usage
=====

*Depending on your platform, the scripts may be installed as ``.py`` scripts,
or some form of executable, or both.*

rst2beamer can be called::

        rst2beamer.py infile.txt > outfile.tex
        
where ``infile.txt`` contains the rst and ``outfile.tex`` contains the produced Beamer LaTeX.

Not all features of beamer have been implemented, just a (large) subset that
allows the quick production of good looking slides. Some examples can be found in the ``docs`` directory of the distribution. 



References
==========

.. [#homepage] rst2beamer homepages at `agapow.net <http://www.agapow/net/software/rst2beamer>`__ and `cs.siue.edu <http://home.cs.siue.edu/rkrauss/python_website/>`__

.. [#setuptools] `Installing setuptools <http://peak.telecommunity.com/DevCenter/setuptools#installing-setuptools>`__

.. [#docutils] `Docutils <http://docutils.sourceforge.net/>`__

.. [#rst] `Restructured text <http://docutils.sourceforge.net/rst.html>`__



