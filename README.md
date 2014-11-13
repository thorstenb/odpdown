# Generate ODP files from markdown

## Mission

Have a tool like pandoc, latex beamer etc, that you can write (or
auto-generate) input for within your favourite hacker's editor, and
generate nice-looking slides from. Using your corporation's mandatory,
CI-compliant and lovely-artsy Impress template.

## Usage

    usage: odpgenerator.py [-h] [-p PAGE] input_md template_odp output_odp
    
    Convert markdown text into OpenDocument presentations
    
    positional arguments:
      input.md              Input markdown file
      template.odp          Input ODP template file
      output.odp            Output ODP file
    
    optional arguments:
      -h, --help            show this help message and exit
      -p PAGE, --page PAGE  Append markdown after given page. Negative numbers
                            count from the end of the slide stack

## Example

* Stick a bunch of markdown chapters into template, after slide 1:

      cat intro.md deploy.md tuning.md | ./odpgenerator.py -p 1 - corp_template.odp out_slides.odp

* Stick a bunch of of markdown chapters into existing preso, e.g. to
  keep a few hand-crafted slides inbetween:

      # intro comes after slide one
      odpgenerator.py -p 1 into.md hand_crafted.odp out_slides.odp
      
      # deploy comes after architecture slide, which is slide 2 in
      # hand_crafted.md and 2+10 after intro got added
      ./odpgenerator.py -p 12 deploy.md out_slides.odp out_slides.odp
