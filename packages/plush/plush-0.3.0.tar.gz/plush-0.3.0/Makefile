# Plush Makefile
# $Id: Makefile 49828 2006-10-24 16:33:43Z bdelbosc $
#
.PHONY: build clean

TARGET := bertha:~/public_public_html/plush


build:
	python setup.py build

test:
	python setup.py test

pkg: sdist

sdist:
	python setup.py sdist

distrib:
	-scp dist/plush-*.tar.gz $(TARGET)/snapshots

cheesecake: sdist
	ls dist/plush*.tar.gz | xargs cheesecake_index -v --path

install:
	python setup.py install

register:
	-python2.4 setup.py register

uninstall:
	-rm -rf /usr/lib/python2.3/site-packages/plush*
	-rm -rf /usr/lib/python2.4/site-packages/plush*
	-rm -f /usr/local/bin/plush
	-rm -f /usr/bin/plush

clean:
	find . "(" -name "*~" -or  -name ".#*" -or  -name "#*#" -or -name "*.pyc" ")" -print0 | xargs -0 rm -f
	rm -rf ./build ./dist ./MANIFEST
