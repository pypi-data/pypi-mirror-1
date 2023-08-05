PACKAGE = pudge
PACKAGES = $(PACKAGE)
SITE = http://lesscode.org/projects/pudge
PYTHON = /opt/local/bin/python
PYDIST = /opt/py-dist
PYTEST_ARGS = -x -l
PYTHONPATH_PREFIX = $(CURDIR)/lib/python:/usr/local/lib/python$(PYTHON_VERSION)/site-packages/
PATH_PREFIX = /opt/local/bin

RM = /bin/rm -rf
FIND = /usr/bin/find

PY_MODULE = $(PACKAGE)
SVN_ROOT = svn://lesscode.org/$(PACKAGE)
DIST_DEST = lesscode.org:/var/projects/dist/$(PACKAGE)/
PYFILES := $(shell $(FIND) $(PACKAGE) -name '*.py')
PYCFILES := $(shell $(FIND) $(PACKAGE) -name '*.pyc')
CLEANFILES = MANIFEST build dist export daily release \
             $(PYCFILES)

VERSION = $(shell $(PYTHON) -c 'import $(PY_MODULE); print $(PY_MODULE).__version__')
DATE    = $(shell $(PYTHON) -c 'import $(PY_MODULE); print $(PY_MODULE).__date__[7:17]')
SVN_TAG = $(SVN_ROOT)/tags/release-$(VERSION)
SVN_BRANCH = $(shell svn info | grep '^URL:' | cut -f2 -d' ')

PYTHONPATH = $(PYTHONPATH_PREFIX):$(CURDIR):$(PYDIST):$(PYTHONPATH_SUFFIX)
PATH := $(PATH_PREFIX):$(PATH)

PYTHON22 := $(shell /usr/bin/which python2.2 2>/dev/null | egrep -v '^no ')
PYTHON23 := $(shell /usr/bin/which python2.3 2>/dev/null | egrep -v '^no ')
PYTHON24 := $(shell /usr/bin/which python2.4 2>/dev/null | egrep -v '^no ')
PYTHON_VERSION := $(shell $(PYTHON) -V 2>&1 | perl -p -e 's/^Python (\d\.\d).*/\1/')
TESTPYTHONS = $(PYTHON22) $(PYTHON23) $(PYTHON24)

PYTHON_PREP = PYTHONPATH=$(PYTHONPATH) $(PYTHON)
PYTEST =  $(PYTHON_PREP) $(PYDIST)/py/bin/py.test $(PYTEST_ARGS)

PUDGE = ./bin/pudge

OPEN = open

default:
	@echo TARGETS: dist release daily

tc: tc_help tc_bad_args

tc_help:
	-$(PUDGE) -h
	@echo

tc_bad_args:
	-$(PUDGE) -XX

testdoc: 
	$(PUDGE) --xhtml --dest=build/test/package pudge.test.package
	$(OPEN) build/test/package/index.html

doc: compile
	-mkdir -p build/doc
	$(PUDGE) --dest=build/doc \
					 --documents=doc/index.rst \
				   --license=gnu \
					 --modules=pudge \
					 --title='Pudge' \
					 --trac='http://lesscode.org/projects/pudge/'
	$(OPEN) build/doc/index.html

pudge: doc

compile:
	$(PYTHON) -c 'import compileall; compileall.compile_dir("$(PACKAGE)", force=0, quiet=1)'

todo:
	@find $(PACKAGE) -name '*.py' | \
  xargs egrep -n -e '# (TODO|XXX|HACK|FIXME)' | \
  perl -p -e 's/(.*):\s*#\s(TODO|XXX|HACK|FIXME):?(.*)/\1:\n\t\2:\3\n/'

check:
	@echo 'The following files have no __license__ attribute:'
	@find ./$(PACKAGE) -name '*.py' | \
		grep -v '\/test\/' | \
		xargs grep -L -e '__license__' | \
		perl -p -e 's/(.*)/\1:7:/' ;

etags:
	@echo "Generating TAGS file."
	find $(PACKAGE) -name '*.py' | xargs etags -l python

testprep:
	-mkdir -p build/test
	-mkdir -p build/test/colorizer
	-mkdir -p build/test/api

test: compile testprep
	$(PYTEST) $(PACKAGE)/test

$(PACKAGE)/test/%.py: compile testprep FORCE
	$(PYTEST) $(CURDIR)/$@

$(PACKAGE)/%.py: compile testprep FORCE
	$(PYTEST) $(CURDIR)/$(PACKAGE)/test/test_$*.py

dist:
	scp -p release/$(PACKAGE)-* $(DIST_DEST)

release: check
	$(RM) export
	mkdir export
	-mkdir release
	cd export; svn export $(SVN_TAG) $(PACKAGE)
	cd export/$(PACKAGE); $(MAKE) doc
	cd export/$(PACKAGE); \
		$(PYTHON) setup.py sdist --force-manifest ; \
		$(PYTHON) setup.py bdist_rpm ; \
		$(PYTHON) setup.py bdist_wininst
	mv export/$(PACKAGE)/dist/* release/

daily: doc
	$(RM) export
	mkdir export
	-mkdir release
	cd export; svn export $(SVN_BRANCH) $(PACKAGE)
	NOW_DATE=`date +'%Y\\/%m\\/%d'`; \
	NOW_VERSION=`date +'%Y%m%d'`; \
	echo $$NOW_DATE $$NOW_VERSION; \
	OLD=export/$(PACKAGE)/$(PY_MODULE)/__init__.py.old; \
	NEW=export/$(PACKAGE)/$(PY_MODULE)/__init__.py; \
	mv $$NEW $$OLD; \
	sed -e "s/__version__.*/__version__ = '$$NOW_VERSION'/" \
            -e "s/__date__.*/__date__ = '$$NOW_DATE'/" < $$OLD > $$NEW;
	cd export/$(PACKAGE); $(MAKE) doc
	cd export/$(PACKAGE); \
		$(PYTHON) setup.py sdist --force-manifest ; \
		$(PYTHON) setup.py bdist_rpm ; \
		$(PYTHON) setup.py bdist_wininst
	mv export/$(PACKAGE)/dist/* release/

clean:
	$(RM) $(CLEANFILES)

fullclean: FORCE clean
	$(RM) release

FORCE:
