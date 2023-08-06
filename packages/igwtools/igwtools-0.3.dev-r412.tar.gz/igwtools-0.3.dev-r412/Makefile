bdist_egg:
	python setup.py bdist_egg

build:
	python setup.py build

install:
	python setup.py install
	$(MAKE) -C manpages install

develop:
	python setup.py develop --install-dir=~/local/lib/python2.5 --script-dir=~/local/bin

upload:
	python setup.py sdist bdist_egg register upload

test:
	python setup.py test
