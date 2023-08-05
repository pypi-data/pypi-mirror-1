export PYTHON=python2.4

PYTHONPATH+=${CURDIR}/..
export PYTHONPATH

PROJECTNAME=ots

all:
	@${PYTHON} setup.py build

install: 
	@${PYTHON} setup.py install

dist:
	@${PYTHON} setup.py bdist

clean: 
	@find . -name "*.pyc" -exec rm {} \;
	@find . -name "*~" -exec rm {} \;
	@rm -rf build
	@rm -rf dist

tags:
	@ctags -e -R -o TAGS

