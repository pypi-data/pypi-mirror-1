# Development commands, not needed by non-sourceforge developers.

upload-web:
	./setup.py build_sphinx --source-dir doc/reference/source --build-dir doc/reference/build
	rm -rf /tmp/upload-web
	mkdir /tmp/upload-web
	cp -r doc/reference/build/html/* /tmp/upload-web
	cp web/favicon.ico /tmp/upload-web
	(A=`cat web/piwik.html` ; cd doc/reference/build/html ; for fname in `find -name '*.html'` ; do (cat $$fname | sed "s,</html>,," ; echo "$$A" ; echo '</html>') > /tmp/upload-web/$$fname ; done)
	rsync -aivP /tmp/upload-web/ $(USERNAME),curtain@web.sourceforge.net:htdocs/
