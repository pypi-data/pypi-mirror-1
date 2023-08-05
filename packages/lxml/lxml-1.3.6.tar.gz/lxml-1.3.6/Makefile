PYTHON?=python
TESTFLAGS=-p -v
TESTOPTS=
SETUPFLAGS=

all: inplace

# Build in-place
inplace:
	$(PYTHON) setup.py $(SETUPFLAGS) build_ext -i

build:
	$(PYTHON) setup.py $(SETUPFLAGS) build

test_build: build
	$(PYTHON) test.py $(TESTFLAGS) $(TESTOPTS)

test_inplace: inplace
	$(PYTHON) test.py $(TESTFLAGS) $(TESTOPTS)
	PYTHONPATH=src $(PYTHON) selftest.py
	PYTHONPATH=src $(PYTHON) selftest2.py

valgrind_test_inplace: inplace
	valgrind --tool=memcheck --leak-check=full --num-callers=30 --suppressions=valgrind-python.supp \
		$(PYTHON) test.py

bench_inplace: inplace
	$(PYTHON) bench.py -i

ftest_build: build
	$(PYTHON) test.py -f $(TESTFLAGS) $(TESTOPTS)

ftest_inplace: inplace
	$(PYTHON) test.py -f $(TESTFLAGS) $(TESTOPTS)

html: inplace
	mkdir -p doc/html
	PYTHONPATH=src $(PYTHON) doc/mkhtml.py doc/html . `cat version.txt`
	rm -fr doc/html/api
	[ -x "`which epydoc`" ] \
		&& (cd src && PYTHONPATH=. epydoc -o ../doc/html/api --name lxml --url http://codespeak.net/lxml/ lxml/) \
		|| (echo "not generating epydoc API documentation")

# XXX What should the default be?
test: test_inplace

valtest: valgrind_test_inplace

bench: bench_inplace

ftest: ftest_inplace

clean:
	find . \( -name '*.o' -o -name '*.c' -o -name '*.so' -o -name '*.py[cod]' -o -name '*.dll' \) -exec rm -f {} \;
	rm -rf build

realclean: clean
	rm -f TAGS
	$(PYTHON) setup.py clean -a
