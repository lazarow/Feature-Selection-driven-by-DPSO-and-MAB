#!/bin/bash
python ../run-script.py ../datasets/soybean-large-preprocessed.csv --grid_search --print_header --no_fs >> ../results.csv
python ../run-script.py ../datasets/anneal-preprocessed.csv --grid_search --no_fs >> ../results.csv
python ../run-script.py ../datasets/arrhythmia-preprocessed.csv --grid_search --no_fs >> ../results.csv
python ../run-script.py ../datasets/ad-preprocessed.csv --grid_search --no_fs >> ../results.csv
