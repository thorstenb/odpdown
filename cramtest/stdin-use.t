  $ cat $TESTDIR/test.md | $TESTDIR/../odpgenerator.py - $TESTDIR/test.odp $CRAMTMP/out_slides.odp && test -n $CRAMTMP/out_slides.odp
