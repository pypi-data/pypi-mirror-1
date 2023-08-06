
all: tests

install:
	cp -p pyrg.py /usr/local/bin/pyrg && chmod 755 /usr/local/bin/pyrg

tests:
	python test/testall.py

pypireg:
	python setup.py register
	python setup.py sdist bdist_egg upload

clean:
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf pyrg/*.egg-info
	rm pyrg/*.pyc
