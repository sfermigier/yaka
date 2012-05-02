PYTHON=python

test:
	$(PYTHON) -m nose.core tests

run: yaka_crm/yaka.db
	$(PYTHON) manage.py runserver

yaka_crm/yaka.db:
	$(PYTHON) manage.py initdb
	$(PYTHON) manage.py loaddata

full-test:
	tox -e py27

pep8:
	pep8 -r --ignore E111,E225,E501 *.py yaka tests

clean:
	find . -name "*.pyc" | xargs rm -f
	find . -name yaka.db | xargs rm -f
	rm -rf *.egg-info *.egg
	rm -rf whoosh whoosh_indexes tests/whoosh tests/whoosh_indexes
	rm -rf doc/_build

tidy: clean
	rm -rf .tox

