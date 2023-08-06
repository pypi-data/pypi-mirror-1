
tests:
	python test/test_pyprof2html.py

pypireg:
	python setup.py register
	python setup.py sdist bdist_egg upload

genhtml:
	python pyprof2html.py test/cprof.prof

clean:
	rm -rf *.pyc
	rm -rf pyprof2html/*.pyc
	rm -rf dist
	rm -rf pyprof2html.egg-info
	rm -rf pyprof2html/pyprof2html.egg-info
	rm -rf build
	rm -rf html

