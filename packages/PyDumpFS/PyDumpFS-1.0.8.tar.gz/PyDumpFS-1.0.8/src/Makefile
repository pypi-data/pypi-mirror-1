.PHONY: all
all : $(wildcard pydumpfs/locale/*/LC_MESSAGES/PyDumpFS.mo)
pydumpfs/locale/pdumpfs.pot: pydumpfs/__init__.py
	pygettext.py -d pdumpfs -o $@ $<
%.po: pydumpfs/locale/pdumpfs.pot
	msgmerge -U $@ $<
%.mo: %.po
	msgfmt -o $@ $<
