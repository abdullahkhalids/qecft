all:
	. ../envqecft/bin/activate
	css-html-js-minify static/ >/dev/null 2>&1
	python ./bookcreator.py


