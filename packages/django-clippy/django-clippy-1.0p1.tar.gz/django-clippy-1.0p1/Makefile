flash:
	swfmill simple library.xml library.swf && haxe compile.hxml

runserver:
	PYTHONPATH=. ./pythonenv/bin/python manage.py runserver

dependencies:
	virtualenv pythonenv
	pip -q install -E pythonenv -r requirements.txt

build:
	python setup.py sdist

upload:
	python setup.py sdist upload

clean:
	rm -Rf dist