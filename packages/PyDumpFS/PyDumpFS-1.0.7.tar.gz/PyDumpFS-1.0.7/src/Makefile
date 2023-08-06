.PHONY: all
all : $(wildcard py_dumpfs/locale/*/LC_MESSAGES/PyDumpFS.mo)
py_dumpfs/locale/pdumpfs.pot: py_dumpfs/__init__.py
	pygettext.py -d pdumpfs -o $@ $<
%.po: py_dumpfs/locale/pdumpfs.pot
	msgmerge -U $@ $<
%.mo: %.po
	msgfmt -o $@ $<
