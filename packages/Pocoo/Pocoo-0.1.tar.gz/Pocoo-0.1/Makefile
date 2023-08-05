#
# Makefile for Pocoo
# ~~~~~~~~~~~~~~~~~~
#
# Combines scripts for common tasks.
#
# :copyright: 2006 by Georg Brandl.
# :license: GNU GPL, see LICENSE for more details.
#

export PYTHONPATH = $(shell python -c 'print ":".join(line.strip() for line in file("PYTHONPATH"))' 2>/dev/null)

.PHONY: apidocs check clean clean-pyc codetags devserver devshell epydoc \
	i18n pylint reindent test testdata

apidocs: epydoc

check:
	@scripts/check_sources.py -i apidocs -i pocoo/pkg/core/static/MochiKit \
		-i pocoo/pkg/core/static/AJS .

clean: clean-pyc
	rm -f codetags.html
	rm -rf apidocs

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

codetags:
	@scripts/find_codetags.py -i apidocs -i pocoo/pkg/core/static/AJS \
		-i scripts/pylintrc -i scripts/find_codetags.py -o codetags.html .

devserver:
	@(cd instance; python manage.py runserver)

devshell:
	@(cd instance; python manage.py shell)

epydoc:
	@rm -rf apidocs
	@python -Wi:default_transform `which epydoc` -o apidocs --css scripts/epydoc.css \
		--url http://trac.pocoo.org --no-frames --docformat restructuredtext -v pocoo
	@sed -i -e 's|^<br />||' \
			-e 's|\s\+$$||' \
			-e 's|^\s\+</pre>|</pre>|' \
			-e 's|\(<table class="[^"]*"\) border="1"|\1|' \
			-e 's|\(<table class="navbar" .*\) width="100%"|\1|' \
			-e 's|<td width="15%"|<td class="spacer"|' \
			apidocs/*.html
	@python scripts/fix_epydoc_markup.py apidocs

i18n:
	@scripts/build_gettext.py -c

pylint:
	@pylint --rcfile scripts/pylintrc pocoo

reindent:
	@scripts/reindent.py -r -B .

test:
	@python tests/run.py

testdata:
	@scripts/make_testdata.py 20

testdata-stress:
	@scripts/make_testdata.py 40
