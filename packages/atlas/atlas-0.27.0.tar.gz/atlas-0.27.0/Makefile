

test:	unit_test system_test clean


system_test:
			make -C test test

unit_test:
			make -C src test

clean:
			make -C test clean
			sudo rm -rf build dist temp atlas.egg-info
			rm -f src/*.pyc
			rm -f src/mod/*.pyc
			rm -f test/*.pyc

upload: 
			./setup.py sdist upload
