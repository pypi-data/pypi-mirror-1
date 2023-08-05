export PYTHON=python2.4
export PROJECTNAME=chimera
export ZOPE_PRODUCTS=/home/bcsaller/zope/Products


CURRENT_VERSION=`shtool version -l python __version__.py`

all: test 
	@echo "make doc will produce documentation in the ./doc/ dir"

doc: 
	@${MAKE} -C docs all

test: build
	@${MAKE} -C tests test

clean: 
	@find . -name "*.pyc" -exec rm {} \;
	@find . -name "*~" -exec rm {} \;
	@find src -name "*.c" -exec rm {} \;
	@find src -name "callgrind.out.*" -exec rm {} \;	
	@find src -name "core" -type f -exec rm {} \;	
	@rm -rf build	
	@${MAKE} -C docs clean

tags:
	@ctags -e -R -o TAGS


version:
	@echo Incrementing version level for package
	@shtool version -l python -n ${PROJECTNAME} -d long -i l __version__.py

build: src/*.py src/*.pyx
	@${PYTHON} setup.py build

install: 
	@${PYTHON} setup.py install


install_zope: test Chimera/*.py 
	@rm -rf ${ZOPE_PRODUCTS}/Chimera
	@cp -r Chimera ${ZOPE_PRODUCTS}/Chimera
	@${PYTHON} ${ZOPE_PRODUCTS}/Chimera/tests/runalltests.py
	@echo If the tests pass Restart Zope to take advantage of these changes

release:
	@$(PYTHON) setup.py sdist
	@$(PYTHON) setup.py bdist_egg
	@tar czf dist/Chimera-$(CURRENT_VERSION).tar.gz Chimera
	@echo Release ready, check dist/

upload:
	@$(PYTHON) setup.py sdist upload
	@$(PYTHON) setup.py bdist_egg upload
