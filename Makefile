TOX=tox

.PHONY: lint
lint:
	$(TOX) -c tox.ini -e lint

.PHONY: test
test:
	$(TOX) -c tox.ini -e test

.PHONY: upload-release
upload-release:
	python setup.py register sdist upload

PYREVERSE_OPTS = --output=pdf
.PHONY: view
view:
	-rm -Rf _pyreverse
	mkdir _pyreverse
	PYTHONPATH=src pyreverse ${PYREVERSE_OPTS} --project="hypotheses-udev" src/hypotheses-udev
	mv classes_hypotheses-udev.pdf _pyreverse
	mv packages_hypotheses-udev.pdf _pyreverse

.PHONY: archive
archive:
	git archive --output=./hypotheses-udev.tar.gz HEAD

.PHONY: docs
docs:
	cd doc/_build/html; zip -r ../../../docs *
