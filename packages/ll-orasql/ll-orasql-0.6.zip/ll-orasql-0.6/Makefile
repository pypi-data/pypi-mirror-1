# $Header: /data/cvsroot/LivingLogic/Python/orasql/Makefile,v 1.3 2004/11/30 20:33:59 walter Exp $

# List of pseudo targets
.PHONY: all clean dist windist

# Output directory
OUTPUTDIR=$(HOME)/pythonroot

all:
	python$(PYVERSION) setup.py install --install-lib $(OUTPUTDIR)

clean:
	python$(PYVERSION) setup.py clean

install:
	python$(PYVERSION) setup.py install

dist:
	python$(PYVERSION) `which doc2txt.py` --title "History" NEWS.xml NEWS
	python$(PYVERSION) `which doc2txt.py` --title "Requirements and installation" INSTALL.xml INSTALL
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py bdist --formats=rpm
	rm NEWS INSTALL

windist:
	python$(PYVERSION) C:\\\\Programme\\\\Python24\\\\Scripts\\\\doc2txt.py --title "History" NEWS.xml NEWS
	python$(PYVERSION) C:\\\\Programme\\\\Python24\\\\Scripts\\doc2txt.py --title "Requirements and installation" INSTALL.xml INSTALL
	python$(PYVERSION) setup.py sdist --formats=zip
	python$(PYVERSION) setup.py bdist --formats=wininst
	rm NEWS INSTALL
