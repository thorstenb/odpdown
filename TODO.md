# Things left to do

## Features

* add a metric ton of options for all the hard-coded decisions in the
  code (autofit, which styles, syntax highlight colours etc etc)
* before adding new styles, check for existing ones (adding multiple
  markdown snippets might have actually resulted our input odp file
  being an earlier md2odp output)
* add automatic title slide
  inspired by http://johnmacfarlane.net/pandoc/README.html#command-line-options
  and the pandoc_title_block extension
      % title
      % author(s) (separated by semicolons)
      % date
  also interesting for inspiration:
  http://kramdown.gettalong.org/syntax.html#non-content-elements
* fix open issues: https://github.com/thorstenb/odpgen/issues
* implement proper block quotes. see e.g.
  https://bitbucket.org/tutorials/markdowndemo/overview#markdown-header-paragraphs-and-blockquotes
  - our current implementation does not even handle nested quotes
  properly, let alone nested lists etc (odf cannot nest
  non-paragraph-content inside text:p, which the current
  implementation tries to do)

## Easy hacks

* grep for TODO comments in the code, kill them one by one
* conceptionally - rethink the use of relative font size
  increases. it's not really needed for code blocks, and for
  block quotes, why not use e.g. formatting ala dillinger.io
* integrate pep8 and pylint tests with nose:
  http://blog.jameskyle.org/2014/05/pep8-pylint-tests-with-nose-xunit/

## Misc

* work out and list known differences in markdown parser,
  e.g. relative to github or stackoverflow.
  related: http://blog.codinghorror.com/the-future-of-markdown/
