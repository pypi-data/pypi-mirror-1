update:
	bin/buildout -q setup setup.py --long-description | rst2html.py > /dev/null
	bin/buildout setup setup.py register

release:
	bin/buildout setup setup.py register sdist bdist_egg upload --sign --show-response

test:
	bin/test
#	bin/buildout setup setup.py test
	bin/buildout -q setup setup.py --long-description | rst2html.py > /dev/null
