export PYTHON=python

PYTHONPATH+=${CURDIR}/..
export PYTHONPATH


all: clean build test

build:
	@pyflakes *.py

ez_inst:
	@make clean
	@make egg
	@easy_install ./dist/memojito*egg

test:	
	@${PYTHON} src/memojito.py

devtest:
	@make dev	
	@make test
	@make undev

install: 
	@${PYTHON} setup.py install

dist:
	@${PYTHON} setup.py bdist
egg:
	@${PYTHON} setup.py bdist_egg

tryme:  
	@make dev

untryme: 

	@make undev

dev:
	@${PYTHON} setup.py develop

undev: 
	@make clean
	@${PYTHON} setup.py un

clean: 
	@find . -name "*.pyc" -exec rm {} \;
	@find . -name "*~" -exec rm {} \;
	@rm -rf build
	@rm -rf dist
	@rm -rf callgrind.*
	@rm -rf *.svg *.dot
	@rm -rf fuse.c

tags:
	@ctags -e -R -o TAGS

debug:
	gdb --command=.gdbdebug python

