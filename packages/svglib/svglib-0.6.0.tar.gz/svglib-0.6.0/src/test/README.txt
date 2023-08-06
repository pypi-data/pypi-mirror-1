.. -*- mode: rst -*-

This folder contains the testsuite for `svglib`. In order to run it 
open a terminal, change into this folder and execute the following 
command::
 
  $ python test_svglib.py

This will run the entire testsuite and produce result files in PDF
format in the subdirectories samples, W3C_SVG_12_TinyTestSuite/svg
and wikipedia, the last two of which only, when the corresponding
SVG input files could be downloaded from the internet at the start
of the test or if they are still available locally.

As an experimental feature some of the tests try using a vector conversion tool named `UniConvertor <http://sourceforge.net/projects/uniconvertor>`_ 
(if available) for producing PDFs for comparison with `svglib`.

