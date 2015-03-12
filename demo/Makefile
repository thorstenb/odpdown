
MARKDOWN=\
    demo-basics.md \
    demo-advanced.md \
    demo-full.md

.PHONY: default
default: $(patsubst %.md,%.pdf,$(MARKDOWN))

.PHONY: clean
clean:
	rm $(patsubst %.md,%.pdf,$(MARKDOWN)) $(patsubst %.md,%.odp,$(MARKDOWN))

%.odp : %.md discreet-dark.odp Makefile
	../odpdown -s emacs --break-master=Discreet_25_20Dark1 --content-master=Discreet_25_20Dark $< discreet-dark.odp $@

%.pdf : %.odp
	rm -f $@
	soffice --headless --convert-to pdf:impress_pdf_Export $<

