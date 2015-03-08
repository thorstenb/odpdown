# Generate ODP files from markdown

[![PyPI version](https://badge.fury.io/py/odpdown.svg)](http://badge.fury.io/py/odpdown)
[![Build Status](https://travis-ci.org/thorstenb/odpdown.svg?branch=master)](https://travis-ci.org/thorstenb/odpdown)

## Attributions

Original Markdown Copyright (c) 2004-2005 John Gruber
http://daringfireball.net/projects/markdown/

Myself got kicked into action by seeing
https://github.com/puppetlabs/showoff and getting terribly envious by
realizing how much of a productivity gain that would be.

## Mission

Have a tool like pandoc, latex beamer etc, that you can write (or
auto-generate) input for within your favourite hacker's editor, and
generate nice-looking slides from. Using your corporation's mandatory,
CI-compliant and lovely-artsy Impress template. Including
syntax-highlighted code snippets of your latest hack, auto-fitted into
the slides.

## Installation

Getting ready should be a simple matter of running

    python setup.py install

from a terminal.

On Windows, run it via the command prompt (Start ‣ Accessories):

    setup.py install

Alternatively, running `odpdown` directly from the git checkout is
also possible, provided you've installed the prerequisites (most
significantly mistune, lpod, pygments and pillow) manually.

## Tests

Run `tox` to run the test suite.

## Usage

	usage: odpdown [-h] [-p PAGE] [-n] [-s HIGHLIGHT_STYLE]
	               [--break-master [BREAK_MASTER]]
	               [--content-master [CONTENT_MASTER]]
	               input_md template_odp output_odp

	Convert markdown text into OpenDocument presentations

	positional arguments:
	  input_md              Input markdown file
	  template_odp          Input ODP template file
	  output_odp            Output ODP file

	optional arguments:
	  -h, --help            show this help message and exit
	  -p PAGE, --page PAGE  Append markdown after given page. Negative numbers
	                        count from the end of the slide stack. [Defaults to
	                        -1]
	  -n, --no-autofit      Use to disable auto-shrinking font in text boxes, to
	                        fit available space.
	  -s HIGHLIGHT_STYLE, --highlight-style HIGHLIGHT_STYLE
	                        Set pygments color style for syntax-highlighting of
	                        code snippets. Available styles in stock pygments are:
	                        "default", "emacs", "friendly", and "colorful".
	                        [Defaults to colorful]
	  --break-master [BREAK_MASTER]
	                        Use this master page for the 1st level headlines. List
	                        available ones if called with empty or unknown name
	  --content-master [CONTENT_MASTER]
	                        Use this master page for the 2nd level headlines and
	                        content. List available ones if called with empty or
	                        unknown name

## Example

* Stick your markdown slides into template, use _break_slides_
  from the template's master pages for 1st level headings, and
  _content_slides_  as the master page for 2nd level headings and content:

      odpdown \
         --break-master=break_slides --content-master=content_slides \
         slides.md corp_template.odp out_slides.odp

* Stick a bunch of markdown chapters into template,
  after slide 1:

      cat intro.md deploy.md tuning.md | \
      odpdown -p 1 - corp_template.odp out_slides.odp

* Stick a bunch of of markdown chapters into existing preso, e.g. to
  keep a few hand-crafted slides inbetween:

      # intro comes after slide one
      odpdown -p 1 into.md hand_crafted.odp out_slides.odp

      # deploy comes after architecture slide, which is slide 2 in
      # hand_crafted.md and 2+10 after intro got added
      odpdown -p 12 deploy.md out_slides.odp out_slides2.odp

Have a lot of fun,

-- Thorsten
