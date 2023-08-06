# $Header$


.PHONY: develop install dist livinglogic register upload windist winupload winlivinglogic


install:
	python$(PYVERSION) setup.py install


develop:
	python$(PYVERSION) setup.py develop


dist:
	rm -rf dist/*
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	python$(PYVERSION) setup.py bdist --formats=egg
	python$(PYVERSION) -mll.scripts.ucp -v -uftp -gftp dist/*.tar.gz dist/*.tar.bz2 dist/*.zip dist/*.egg ssh://root@isar.livinglogic.de/~ftp/pub/livinglogic/nightshade/


register:
	python$(PYVERSION) setup.py register


livinglogic:
	rm -rf dist/*
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	python$(PYVERSION) setup.py bdist --formats=egg
	python$(PYVERSION) -mll.scripts.ucp -v dist/*.tar.gz dist/*.tar.bz2 dist/*.zip dist/*.egg ssh://intranet@intranet.livinglogic.de/~/documentroot/intranet.livinglogic.de/python-downloads/


upload:
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar upload
	python$(PYVERSION) setup.py sdist --formats=zip upload
	python$(PYVERSION) setup.py bdist --formats=egg upload


windist:
	rm -rf dist/*
	python$(PYVERSION) setup.py bdist --formats=wininst
	python$(PYVERSION) -mll.scripts.ucp -v -uftp -gftp dist/*.exe ssh://root@isar.livinglogic.de/~ftp/pub/livinglogic/orasql/


winupload:
	python$(PYVERSION) setup.py bdist --formats=wininst upload


winlivinglogic:
	python$(PYVERSION) setup.py bdist --formats=wininst
	python$(PYVERSION) -mll.scripts.ucp -v -uintranet -gintranet dist/*.exe ssh://intranet@intranet.livinglogic.de/~/documentroot/intranet.livinglogic.de/python-downloads/
