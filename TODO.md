# Things left to do

## Features

* auto-detect styles & master pages in input template, reuse or
  add custom ones in generator
* add a metric ton of options for all the hard-coded decisions in the
  code (autofit, which styles, syntax highlight colours etc etc)
* images:
  * keep aspect ratio
  * add caption bottom/right. e.g. via the following draw style for
    the image frame:
        <style:style style:name="bla" style:family="graphic" style:parent-style-name="whatevar">
         <style:graphic-properties draw:stroke="none" draw:fill="none" draw:textarea-horizontal-align="right" draw:textarea-vertical-align="bottom" style:mirror="none"/>
        </style:style>
* add automatic title slide
  inspired by http://johnmacfarlane.net/pandoc/README.html#command-line-options
  and the pandoc_title_block extension
      % title
      % author(s) (separated by semicolons)
      % date

## Easy hacks

* grep for TODO comments in the code, kill them one by one
* prefix generated styles with something unique (e.g. prog name)
* conceptionally - rethink the use of relative font size
  increases. it's not really needed for code blocks, and for
  block quotes, why not use e.g. formatting ala dillinger.io

## Misc

* work out and list known differences in markdown parser,
  e.g. relative to github or stackoverflow.
  related: http://blog.codinghorror.com/the-future-of-markdown/
