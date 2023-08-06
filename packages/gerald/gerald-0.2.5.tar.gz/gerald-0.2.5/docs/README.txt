File: README.txt
Author: Andrew J Todd esq
Date:   17th January, 2008

This folder contains the documentation for Gerald (http://halfcooked.com/code/gerald). The documentation is written in reStructuredText (http://docutils.sourceforge.net).

To convert one of the reST documents to the HTML format used on the project web site use a command like;

  $ rst2html.py --stylesheet-path=gerald.css \
                --embed-stylesheet \ 
                --initial-header-level=2 \
                <source file>.rst > <source file>.html

Or use ``genhtml.sh <source file>``
