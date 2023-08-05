PYTHON=python
LOCALES_BASE=`pwd`/src/zcontact/locales/

all: inplace

# Build in-place
inplace:
	$(PYTHON) bootstrap.py
	./bin/buildout -Nv

install:
	./bin/paster make-config zcontact .

run:
	./bin/paster serve deploy.ini

clean:
	find . \( -name '*.o' -o -name '*.so' -o -name '*.py[co]' -o -name '*.dll' \) -exec rm -f {} \;

test:
	./bin/test -ufm zcontact

release:
	$(PYTHON) setup.py sdist register upload

coverage:
	./bin/test -um zcontact --coverage=coverage
	./bin/coverage parts/test/coverage reports
