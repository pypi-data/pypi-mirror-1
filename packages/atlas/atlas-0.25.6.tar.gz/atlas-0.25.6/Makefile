

test:	unit_test system_test clean


system_test:
			make -C test test

unit_test:
			./util_test.py
			./filecache_test.py

clean:
			make -C test clean

upload:
			./setup.py sdist upload
#./setup.py sdist bdist_egg upload
