DESTDIR = /usr/local

lxml:
	@rm -rf lxml
	@tar xzf dependencies/lxml-1.3.6.tgz
	(cd lxml-1.3.6; python setup.py build; mv build/lib.*/lxml ..)
	@rm -rf lxml-1.3.6

install: lxml
	mkdir -p "$(DESTDIR)/share/pygolem"
	cp -r lxml simplejson golem dictionaries "$(DESTDIR)/share/pygolem"
	for i in bin/*; do sed -e 's"#INSTALLDIR"sys.path.insert(0, \"$(DESTDIR)/share/pygolem\")"' $$i > "$(DESTDIR)/$$i"; chmod +x "$(DESTDIR)/$$i"; done
