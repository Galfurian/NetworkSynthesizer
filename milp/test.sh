#!/usr/bin/env bash
rm -f *.txt
rm -f *.log
python Synthesizer.py examples/TestCase1/input.txt examples/nodes.txt examples/channels.txt 1
python Synthesizer.py examples/TestCase1/input.txt examples/nodes.txt examples/channels.txt 2
python Synthesizer.py examples/TestCase1/input.txt examples/nodes.txt examples/channels.txt 3
python Synthesizer.py examples/TestCase1/input.txt examples/nodes.txt examples/channels.txt 4

python Synthesizer.py examples/TestCase2/input.txt examples/nodes.txt examples/channels.txt 1
python Synthesizer.py examples/TestCase2/input.txt examples/nodes.txt examples/channels.txt 2
python Synthesizer.py examples/TestCase2/input.txt examples/nodes.txt examples/channels.txt 3
python Synthesizer.py examples/TestCase2/input.txt examples/nodes.txt examples/channels.txt 4

python Synthesizer.py examples/TestCase3/input.txt examples/nodes.txt examples/channels.txt 1
python Synthesizer.py examples/TestCase3/input.txt examples/nodes.txt examples/channels.txt 2
python Synthesizer.py examples/TestCase3/input.txt examples/nodes.txt examples/channels.txt 3
python Synthesizer.py examples/TestCase3/input.txt examples/nodes.txt examples/channels.txt 4

python Synthesizer.py examples/TestCase4/input.txt examples/nodes.txt examples/channels.txt 1
python Synthesizer.py examples/TestCase4/input.txt examples/nodes.txt examples/channels.txt 2
python Synthesizer.py examples/TestCase4/input.txt examples/nodes.txt examples/channels.txt 3
python Synthesizer.py examples/TestCase4/input.txt examples/nodes.txt examples/channels.txt 4

python Synthesizer.py examples/Office/input.txt examples/nodes.txt examples/channels.txt 1
python Synthesizer.py examples/Office/input.txt examples/nodes.txt examples/channels.txt 2
python Synthesizer.py examples/Office/input.txt examples/nodes.txt examples/channels.txt 3
python Synthesizer.py examples/Office/input.txt examples/nodes.txt examples/channels.txt 4

python Synthesizer.py examples/Office10/input.txt examples/nodes.txt examples/channels.txt 1
python Synthesizer.py examples/Office10/input.txt examples/nodes.txt examples/channels.txt 2
python Synthesizer.py examples/Office10/input.txt examples/nodes.txt examples/channels.txt 3
python Synthesizer.py examples/Office10/input.txt examples/nodes.txt examples/channels.txt 4