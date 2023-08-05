# Utility makefile to build html doc
# TODO: use setup.py extensions in order to do the same in a X-platform way

REST2HTML=rst2html --stylesheet=style/rest.css --link-stylesheet
PYTHON=python
PYFLAKES=pyflakes
TRACE2HTML=trace2html.py -v
FIREFOX=firefox
TESTRUNNER=runtests.py
#TESTRUNNER=setup.py test -q  # setuptools testrunner

all: web tags

html:
	$(REST2HTML) < README.txt > www/index.html
	$(REST2HTML) < src/evogrid/common/README.txt > www/components_overview.html
	$(REST2HTML) < src/evogrid/sharing/README.txt > www/sharing.html
	$(REST2HTML) < src/evogrid/mo/README.txt > www/multiobjective.html
	$(REST2HTML) < src/evogrid/numeric/README.txt > www/numeric.html
	$(REST2HTML) < src/evogrid/caching/README.txt > www/caching.html
	$(REST2HTML) < src/evogrid/common/tests/test_replicators.txt > www/replicators.html
	$(REST2HTML) < src/evogrid/common/tests/test_checkpointers.txt > www/checkpointers.html
	$(REST2HTML) < src/evogrid/common/tests/test_elite_archive.txt > www/archive.html
	$(REST2HTML) < src/evogrid/common/tests/test_evolvers.txt > www/evolvers.html

gatags:
	$(PYTHON) ga_tagger.py

test:
	$(PYTHON) $(TESTRUNNER) -vD # zope testrunner with post mortem debugging

coverage:
	$(TRACE2HTML) -w evogrid -o www/coverage -r $(TESTRUNNER)
	$(FIREFOX) www/coverage/index.html

web: html coverage gatags

quality: test
	$(PYFLAKES) src
	# $(TRACE2HTML) -w evogrid -o www/coverage --assert-increased --assert-min 80 -r runtest.py

clean:
	$(PYTHON) setup.py clean -a

install:
	$(PYTHON) setup.py install

tags:
	ctags -R .

