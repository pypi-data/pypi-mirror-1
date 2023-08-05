# $Header: /data/cvsroot/LivingLogic/Python/core/Makefile,v 1.5 2006/06/28 16:17:56 walter Exp $

# List of pseudo targets
.PHONY: all clean dist windist

# Output directory
OUTPUTDIR=$(HOME)/pythonroot

all:
	python$(PYVERSION) setup.py install

clean:
	python$(PYVERSION) setup.py clean

dist:
	python$(PYVERSION) `which doc2txt.py` --title "History" NEWS.xml NEWS
	python$(PYVERSION) `which doc2txt.py` --title "Old history" OLDNEWS.xml OLDNEWS
	python$(PYVERSION) `which doc2txt.py` --title "Requirements and installation" INSTALL.xml INSTALL
	python$(PYVERSION) `which doc2txt.py` --title "Old migration and modernization guide" OLDMIGRATION.xml OLDMIGRATION
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py bdist --formats=rpm
	python$(PYVERSION) setup.py bdist --formats=egg
	rm NEWS OLDNEWS INSTALL OLDMIGRATION

windist:
	python$(PYVERSION) C:\\\\Programme\\\\Python24\\\\Scripts\\\\doc2txt.py --title "History" NEWS.xml NEWS
	python$(PYVERSION) C:\\\\Programme\\\\Python24\\\\Scripts\\\\doc2txt.py OLDNEWS.xml OLDNEWS
	python$(PYVERSION) C:\\\\Programme\\\\Python24\\\\Scripts\\\\doc2txt.py --title "Requirements and installation" INSTALL.xml INSTALL
	python$(PYVERSION) C:\\\\Programme\\\\Python24\\\\Scripts\\\\doc2txt.py OLDMIGRATION.xml OLDMIGRATION
	python$(PYVERSION) setup.py sdist --formats=zip
	python$(PYVERSION) setup.py bdist --formats=wininst
	python$(PYVERSION) setup.py bdist --formats=egg
	rm NEWS OLDNEWS INSTALL OLDMIGRATION
