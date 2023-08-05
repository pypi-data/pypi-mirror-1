.PHONY: apidocs
apidocs:
	-mv apidocs apidocs_OLD
	epydoc -n "Anagrammer" --no-private --show-imports --no-frames src/anagrammer
	mv html apidocs
	rm -rf apidocs_OLD

.PHONY: test
test:
	( cd src && PYTHONPATH=.:$$PYTHONPATH python anagrammer/tests/__init__.py )

.PHONY: clean
clean:
	rm -rf build dist MANIFEST

.PHONY: package
package:
	rst2html README > README.html
	python setup.py bdist --format=rpm
	python setup.py bdist --format=zip
	python setup.py bdist --format=gztar
	python setup.py bdist --format=bztar
	python setup.py sdist --format=zip
	python setup.py sdist --format=gztar
	python setup.py sdist --format=bztar
	python setup.py bdist_dumb
