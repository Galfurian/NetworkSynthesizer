#!/usr/bin/env bash
rm -f *.txt
rm -f *.log

echo "START" >> result.txt

python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 1
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 1
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 1
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 1
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 1

python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 2
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 2
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 2
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 2
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 2

python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 3
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 3
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 3
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 3
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 3

python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 4
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 4
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 4
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 4
python Synthesizer.py stress_test/stress_test_49/input.txt stress_test/nodes.txt stress_test/channels.txt 4

echo "DONE" >> result.txt
