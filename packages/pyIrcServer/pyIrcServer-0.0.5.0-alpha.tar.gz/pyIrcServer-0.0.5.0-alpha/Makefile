############################################################################
#    Copyright (C) 2004 by Lethalman                                       #
#    lethalman@fyrebird.net                                                #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

VERSION=0.0.5.0-alpha

all:

clean:
	rm -rf *.pyc */*.pyc *~ */*~ pyIrcServer-${VERSION}.tar.gz

dist: clean
	mkdir pyIrcServer-${VERSION}
	cp -rf *.py AUTHOR ChangeLog COPYING TODO README Makefile modules classes utils protocols config.xml pyIrcServer-${VERSION}
	tar -czf pyIrcServer-${VERSION}.tar.gz pyIrcServer-${VERSION}
	rm -rf pyIrcServer-${VERSION}

cvs: clean
	cp *py config.xml ChangeLog pyircserver
	cp classes/*py pyircserver/classes
	cp modules/*py pyircserver/modules
	cp utils/*py pyircserver/utils
	cp protocols/*py pyircserver/protocols

getcvs: clean
	cp pyircserver/*py pyircserver/ChangeLog .
	cp pyircserver/classes/*py classes
	cp pyircserver/modules/*py modules
	cp pyircserver/utils/*py utils
	
doc: clean
	if [ ! -d docs ]; then mkdir docs; fi
	@rm -rf docs/*
	@epydoc --css black --private-css black -n pyIrcServer -u http://pyircserver.iosn.it -o docs/pyIrcServer-CodeDocs_HTML __init__.py classes/*.py modules/*.py utils/*.py protocols/*.py
	@epydoc --css black --private-css black --latex --pdf -n pyIrcServer -u http://pyircserver.iosn.it -o docs/pyIrcServer-CodeDocs_LATEX __init__.py classes/*.py modules/*.py utils/*.py protocols/*.py
	@mv docs/pyIrcServer-CodeDocs_LATEX/api.pdf docs/pyIrcServer-CodeDocs_PDF.pdf
	@zip docs/pyIrcServer-CodeDocs_PDF.zip docs/pyIrcServer-CodeDocs_PDF.pdf
	@tar -czf docs/pyIrcServer-CodeDocs_LATEX.tar.gz docs/pyIrcServer-CodeDocs_LATEX
	@zip -r docs/pyIrcServer-CodeDocs_HTML.zip docs/pyIrcServer-CodeDocs_HTML
	@rm docs/pyIrcServer-CodeDocs_PDF.pdf
	@rm -rf docs/pyIrcServer-CodeDocs_LATEX
	@mv docs/pyIrcServer-CodeDocs_HTML docs/html
	@echo Documentation made successful!
