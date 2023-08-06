_cnodes.c:_cnodes.pyx
	pyrexc _cnodes.pyx
test:
	python -m cnodes
clean:
	rm -f cnodes.c cnodes.so
help:
	echo "Simply type make"
install: _cnodes.c
	python setup.py install
build: _cnodes.c
	python setup.py build
sdist: _cnodes.c
	python setup.py sdist
