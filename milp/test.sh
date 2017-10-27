#!/usr/bin/env bash
rm -f *.txt
rm -f *.log

for directory in $(find examples -maxdepth 1 -mindepth 1 -type d | sort -V);
do
	python Synthesizer.py $directory/input.txt examples/nodes.txt examples/channels.txt 1
	python Synthesizer.py $directory/input.txt examples/nodes.txt examples/channels.txt 2
	python Synthesizer.py $directory/input.txt examples/nodes.txt examples/channels.txt 3
	python Synthesizer.py $directory/input.txt examples/nodes.txt examples/channels.txt 4
done
