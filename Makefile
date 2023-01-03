SHELL := /bin/bash
.ONESHELL:

all:
	source ../envqecft/bin/activate
	python ./bookcreator.py
	css-html-js-minify build/static/css/ >/dev/null 2>&1
	sed -i '1s;^;/*BSD 3-Clause License*/\n;' build/static/css/screen.min.css

