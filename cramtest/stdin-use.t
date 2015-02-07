  $ cat $TESTDIR/test.md | $TESTDIR/../odpdown - $TESTDIR/test.odp $CRAMTMP/out_slides.odp && test -n $CRAMTMP/out_slides.odp
