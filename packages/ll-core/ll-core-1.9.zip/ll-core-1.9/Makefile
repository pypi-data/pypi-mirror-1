# $Header: /data/cvsroot/LivingLogic/Python/core/Makefile,v 1.14.2.5 2007/03/30 13:46:59 walter Exp $


.PHONY: develop install text dist register upload wintext windist livinglogic


develop: text
	python$(PYVERSION) setup.py develop


install: text
	python$(PYVERSION) setup.py install


text:
	python$(PYVERSION) -mll.xist.scripts.doc2txt --title "History" NEWS.xml NEWS
	python$(PYVERSION) -mll.xist.scripts.doc2txt --title "Old history" OLDNEWS.xml OLDNEWS
	python$(PYVERSION) -mll.xist.scripts.doc2txt --title "Requirements and installation" INSTALL.xml INSTALL
	python$(PYVERSION) -mll.xist.scripts.doc2txt --title "Old migration and modernization guide" OLDMIGRATION.xml OLDMIGRATION


dist: text
	rm -rf dist/*
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	python$(PYVERSION) setup.py bdist --formats=rpm
	python$(PYVERSION) -mll.scripts.ucp -v -uftp -gftp dist/*.tar.gz dist/*.tar.bz2 dist/*.zip ssh://root@isar.livinglogic.de/~ftp/pub/livinglogic/core/


register:
	python$(PYVERSION) setup.py register


upload: text
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar upload
	python$(PYVERSION) setup.py sdist --formats=zip upload
	python$(PYVERSION) setup.py bdist --formats=rpm upload


livinglogic: text
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	python$(PYVERSION) -mll.scripts.ucp -v dist/*.tar.gz dist/*.tar.bz2 dist/*.zip ssh://intranet@intranet.livinglogic.de/~/documentroot/intranet.livinglogic.de/python-downloads/


wintext:
	#python$(PYVERSION) -mll.xist.scripts.doc2txt --title "History" NEWS.xml NEWS
	#python$(PYVERSION) -mll.xist.scripts.doc2txt OLDNEWS.xml OLDNEWS
	#python$(PYVERSION) -mll.xist.scripts.doc2txt --title "Requirements and installation" INSTALL.xml INSTALL
	#python$(PYVERSION) -mll.xist.scripts.doc2txt OLDMIGRATION.xml OLDMIGRATION


windist: wintext
	rm -rf dist/*
	python$(PYVERSION) setup.py bdist --formats=wininst
	python -mll.scripts.ucp -v -cno -uftp -gftp dist/*.exe ssh://root@isar.livinglogic.de/~ftp/pub/livinglogic/core/


winupload: wintext
	python$(PYVERSION) setup.py bdist --formats=wininst upload
	python$(PYVERSION) setup.py bdist --formats=egg upload


winlivinglogic: wintext
	rm -rf dist/*
	python$(PYVERSION) setup.py bdist --formats=wininst
	python$(PYVERSION) -mll.scripts.ucp -v -cno -uintranet -gintranet dist/*.exe ssh://intranet@intranet.livinglogic.de/~/documentroot/intranet.livinglogic.de/python-downloads/
