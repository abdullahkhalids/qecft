SHELL := /bin/bash
.ONESHELL:
.SILENT:

all:
	source envqecft/bin/activate
	python ./bookcreator.py
	echo "Minifying css files in build/static/css/"
	css-html-js-minify build/static/css/ >/dev/null 2>&1
	echo "Add license information to one css file."
	sed -i '1s;^;/*BSD 3-Clause License*/\n;' build/static/css/screen.min.css
	python ./htmltopdf.py

