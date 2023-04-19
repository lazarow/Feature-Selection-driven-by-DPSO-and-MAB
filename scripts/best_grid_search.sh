#!/bin/bash
python run-script.py datasets/soybean-large-preprocessed.csv --best_grid_search --print_header >> results.csv
python run-script.py datasets/anneal-preprocessed.csv --best_grid_search >> results.csv
python run-script.py datasets/arrhythmia-preprocessed.csv --best_grid_search >> results.csv
python run-script.py datasets/ad-preprocessed.csv --best_grid_search >> results.csv
