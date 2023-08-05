# $Header: /data/cvsroot/LivingLogic/Python/toxic/Makefile,v 1.4 2004/12/09 17:53:48 walter Exp $

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
	#python$(PYVERSION) `which doc2txt.py` --title "Migration and modernization guide" MIGRATION.xml MIGRATION
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py bdist --formats=rpm
	rm NEWS INSTALL

windist:
	python$(PYVERSION) C:\\\\Programme\\\\Python24\\\\Scripts\\\\doc2txt.py --title "History" NEWS.xml NEWS
	python$(PYVERSION) C:\\\\Programme\\\\Python24\\\\Scripts\\doc2txt.py --title "Requirements and installation" INSTALL.xml INSTALL
	#python$(PYVERSION) C:\\\\Programme\\\\Python24\\\\Scripts\\\\doc2txt.py --title "Migration and modernization guide" MIGRATION.xml MIGRATION
	python$(PYVERSION) setup.py sdist --formats=zip
	python$(PYVERSION) setup.py bdist --formats=wininst
	rm NEWS INSTALL
