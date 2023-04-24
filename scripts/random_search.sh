#!/bin/bash
python run-script.py datasets/soybean-large-preprocessed.csv --random_search --print_header >> results.csv
python run-script.py datasets/anneal-preprocessed.csv --random_search >> results.csv
python run-script.py datasets/arrhythmia-preprocessed.csv --random_search >> results.csv
python run-script.py datasets/ad-preprocessed.csv --random_search >> results.csv
