#!/bin/bash
python run-script.py datasets/soybean-large-preprocessed.csv --mab --print_header >> results.csv
python run-script.py datasets/anneal-preprocessed.csv --mab >> results.csv
python run-script.py datasets/arrhythmia-preprocessed.csv --mab >> results.csv
python run-script.py datasets/ad-preprocessed.csv --mab >> results.csv
