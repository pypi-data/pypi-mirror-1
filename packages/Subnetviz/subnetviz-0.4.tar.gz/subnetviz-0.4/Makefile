.PHONY: warn build prepare_release clean

warn:
	@echo "This Makefile isn't for end-user consumption.  Run setup.py."
	@exit 1

# Just for testing, to ensure no statically-detectable errors.  Actual
# users, run setup.py yourself.
build:
	$(MAKE) clean
	python setup.py build

prepare_release: build
	$(MAKE) clean

clean:
	rm -rf build
