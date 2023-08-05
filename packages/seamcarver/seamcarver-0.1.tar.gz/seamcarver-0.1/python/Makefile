# Makefile
# for generating ctypes bindings automatically

SHELL=/bin/bash
H2XML=h2xml.py
XML2PY=xml2py.py

HEADER=$(PWD)/../lib/seamcarver.h

export PATH:=/home/nilton/tmp/gccxml/bin:$(PATH)

all: _seamcarver.py

_seamcarver.xml: $(HEADER)
	$(H2XML) $< -o $@ -c

_seamcarver.py: _seamcarver.xml
	LD_LIBRARY_PATH=../lib $(XML2PY) $< -k defst -v -r 'seamcarver_.*' -r 'SEAMCARVER_.*' -l libseamcarver.so -o $@

clean:
	-rm -f _seamcarver.xml _seamcarver.py
