#!/usr/bin/env bash
#rm -f *.txt
#rm -f *.log

echo "START" >> result.txt

for directory in $(find stress_test -maxdepth 1 -mindepth 1 -type d | sort -V);
do
	python Synthesizer.py $directory/input.txt stress_test/nodes.txt stress_test/channels.txt 1
done

echo "DONE" >> result.txt
