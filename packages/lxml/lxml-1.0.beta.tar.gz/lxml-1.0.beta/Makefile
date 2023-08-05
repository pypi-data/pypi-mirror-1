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

bench_inplace: inplace
	$(PYTHON) bench.py -i

ftest_build: build
	$(PYTHON) test.py -f $(TESTFLAGS) $(TESTOPTS)

ftest_inplace: inplace
	$(PYTHON) test.py -f $(TESTFLAGS) $(TESTOPTS)

# XXX What should the default be?
test: test_inplace

bench: bench_inplace

ftest: ftest_inplace

clean:
	find . \( -name '*.o' -o -name '*.c' -o -name '*.so' -o -name '*.py[co]' -o -name '*.dll' \) -exec rm -f {} \;
	rm -rf build

realclean: clean
	rm -f TAGS
	$(PYTHON) setup.py clean -a
