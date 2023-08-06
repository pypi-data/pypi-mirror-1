sphinx-wxoptimize
Copyright (c) 2009 Rob McMullen (robm@users.sourceforge.net)


This is a post-processing tool for the sphinx document processing engine.  It
is designed to convert the HtmlHelp files into a format that are rendered
correctly using the wxWidgets wxHtmlHelpController.

See the usage for more information:

sphinx-wxoptimize --help


PREREQUISITES
=============

* Python: http://www.python.org

* sphinx: http://sphinx.pocoo.org

* BeautifulSoup: http://www.crummy.com/software/BeautifulSoup


INSTALL
=======

Installation is through the usual python packaging commands, either:

    python setup.py install

or using easy_install:

    easy_install sphinx-wxoptimize

Using easy_install will automatically install the prerequisite BeautifulSoup
library.
