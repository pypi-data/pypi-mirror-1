.PHONY: all
all : $(wildcard locale/*/PyDumpFS.mo)
locale/pdumpfs.pot: pdumpfs.py
	pygettext.py -d pdumpfs -o $@ $<
%.po: locale/pdumpfs.pot
	msgmerge -U $@ $<
%.mo: %.po
	msgfmt -o $@ $<
