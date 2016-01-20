
MARKDOWN=\
    demo-basics.md \
    demo-advanced.md \
    demo-full.md

ODPDOWN?=../odpdown

.PHONY: default
default: $(patsubst %.md,%.pdf,$(MARKDOWN))

.PHONY: clean
clean:
	rm $(patsubst %.md,%.pdf,$(MARKDOWN)) $(patsubst %.md,%.odp,$(MARKDOWN))

%.odp : %.md discreet-dark.odp Makefile
	$(ODPDOWN) -s emacs --break-master=Discreet_25_20Dark1 --content-master=Discreet_25_20Dark $< discreet-dark.odp $@

%.pdf : %.odp
	soffice --headless --convert-to pdf:impress_pdf_Export $<
