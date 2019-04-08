package-name="ion"
version = `cat ./VERSION`

test:
	echo "no tests"

upload: test vpatch
	devpi upload

install-locally:
	pip install -U .

publish:
	devpi push "$(package-name)-$(version)" "ai-unit/prod"

vpatch:
	bumpversion patch

vminor:
	bumpversion minor

vmajor:
	bumpversion major
