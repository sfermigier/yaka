PYTHON=python
TARGET=yaka@oss4cloud.org:yaka/production/

#
# testing
#
test:
	$(PYTHON) -m nose.core -v tests

unit:
	$(PYTHON) -m nose.core -v tests/unit

test-with-coverage:
	$(PYTHON) -m nose.core --with-coverage --cover-erase \
	   	--cover-package=yaka tests

test-with-profile:
	$(PYTHON) -m nose.core --with-profile tests

unit-with-coverage:
	$(PYTHON) -m nose.core --with-coverage --cover-erase \
	   	--cover-package=yaka tests/unit

unit-with-profile:
	$(PYTHON) -m nose.core --with-profile tests/unit

#
# Everything else
#
run: yaka/yaka.db
	$(PYTHON) manage.py runserver --host 0.0.0.0

yaka/yaka.db:
	$(PYTHON) manage.py initdb
	$(PYTHON) manage.py loaddata

full-test:
	tox -e py27

pep8:
	pep8 -r --ignore E111,E225,E501 *.py yaka tests

clean:
	find . -name "*.pyc" | xargs rm -f
	find . -name yaka.db | xargs rm -f
	rm -f maxid.data
	rm -rf data tests/data tests/integration/data
	rm -rf tmp tests/tmp tests/integration/tmp
	rm -rf cache tests/cache tests/integration/cache
	rm -rf *.egg-info *.egg .coverage
	rm -rf whoosh tests/whoosh tests/integration/whoosh
	rm -rf doc/_build
	rm -rf yaka/static/gen

tidy: clean
	rm -rf .tox

start-vagrant:
	vagrant up
	fab vagrant upgrade setup deploy

push:
	rsync -e ssh -avz ./ $(TARGET)

push-code:
	rsync -e ssh -avz ./yaka $(TARGET)/

update-pot:
	pybabel extract -F babel.cfg -o messages.pot .
	pybabel update -i messages.pot -d yaka/translations
	pybabel compile -d yaka/translations
