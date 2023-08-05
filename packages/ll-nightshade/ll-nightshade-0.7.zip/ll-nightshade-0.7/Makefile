# $Header: /data/cvsroot/LivingLogic/Python/nightshade/Makefile,v 1.3 2007/03/12 17:57:31 walter Exp $


.PHONY: develop install livinglogic winlivinglogic


install:
	python$(PYVERSION) setup.py install


develop:
	python$(PYVERSION) setup.py develop


text:
	python$(PYVERSION) `which doc2txt.py` --title "History" NEWS.xml NEWS
	python$(PYVERSION) `which doc2txt.py` --title "Requirements and installation" INSTALL.xml INSTALL


dist: text
	rm -rf dist/*
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	python$(PYVERSION) setup.py bdist --formats=egg
	cd dist && scp.py -v -uftp -gftp *.tar.gz *.tar.bz2 *.zip *.egg root@isar.livinglogic.de:~ftp/pub/livinglogic/nightshade/


register:
	python$(PYVERSION) setup.py register


livinglogic: text
	rm -rf dist/*
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	python$(PYVERSION) setup.py bdist --formats=egg
	scp dist/*.tar.gz dist/*.tar.bz2 dist/*.zip dist/*.egg intranet@intranet.livinglogic.de:~/documentroot/intranet.livinglogic.de/python-downloads/


upload: text
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar upload
	python$(PYVERSION) setup.py sdist --formats=zip upload
	python$(PYVERSION) setup.py bdist --formats=egg upload


windist: wintext
	rm -rf dist/*
	python$(PYVERSION) setup.py bdist --formats=wininst
	cd dist && python$(PYVERSION) -mscp -v -uftp -gftp *.exe root@isar.livinglogic.de:~ftp/pub/livinglogic/orasql/


winupload: wintext
	python$(PYVERSION) setup.py bdist --formats=wininst upload


winlivinglogic: wintext
	python$(PYVERSION) setup.py bdist --formats=wininst
	cd dist && python$(PYVERSION) -mscp -v -uintranet -gintranet *.exe intranet@intranet.livinglogic.de:~/documentroot/intranet.livinglogic.de/python-downloads/
