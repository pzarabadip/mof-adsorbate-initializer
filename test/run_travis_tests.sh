#!/bin/sh

# run_travis_tests.sh: Run the tests for Travis CI
cd examples
python add_O.py &&
python add_O2.py &&
python add_CO.py &&
python add_N2O.py &&
python add_H2O.py &&
python add_all_H2O.py &&
python add_CH4_PEG.py &&
python add_O_auto.py &&
cd ../