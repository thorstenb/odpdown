#!/bin/sh
echo 'Running nosetests'
nosetests
echo
echo 'Running cramtests'
cram cramtest/*.t
