#!/bin/bash
python run-script.py datasets/soybean-large-preprocessed.csv --mab --print_header >> mab_results.csv
python run-script.py datasets/anneal-preprocessed.csv --mab >> mab_results.csv
python run-script.py datasets/arrhythmia-preprocessed.csv --mab >> mab_results.csv
python run-script.py datasets/ad-preprocessed.csv --mab >> mab_results.csv
