egg:
	python2.4 setup.py bdist_egg

dev-egg:
	rm -fr dist
	python2.4 setup.py egg_info -rbDEV bdist_egg
	cp dist/*egg /tmp

binary:
	python2.4 setup.py bdist

sdist:
	python2.4 setup.py sdist

clean:
	rm -fr dist build
	find . -name \*pyc -print |xargs rm
	find . -name \*pyo -print |xargs rm
