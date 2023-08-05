TESTRUNNER = "tests/run_tests.py"

build: tests
	python setup.py build

install:
	python setup.py install


.PHONY: tests clean
tests:
	python $(TESTRUNNER)

clean:
	find . -name \*.pyc -exec rm -rf {} +
	rm -rf build
