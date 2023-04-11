#!/bin/bash
python run-script.py datasets/soybean-large-preprocessed.csv --mab --nof_mab_iterations 300 >> results.csv
python run-script.py datasets/soybean-large-preprocessed.csv --mab --nof_mab_iterations 500 >> results.csv
python run-script.py datasets/soybean-large-preprocessed.csv --mab --nof_mab_iterations 1000 >> results.csv
python run-script.py datasets/anneal-preprocessed.csv --mab --nof_mab_iterations 300 >> results.csv
python run-script.py datasets/anneal-preprocessed.csv --mab --nof_mab_iterations 500 >> results.csv
python run-script.py datasets/anneal-preprocessed.csv --mab --nof_mab_iterations 1000 >> results.csv
python run-script.py datasets/arrhythmia-preprocessed.csv --mab --nof_mab_iterations 300 >> results.csv
python run-script.py datasets/arrhythmia-preprocessed.csv --mab --nof_mab_iterations 500 >> results.csv
python run-script.py datasets/arrhythmia-preprocessed.csv --mab --nof_mab_iterations 1000 >> results.csv
python run-script.py datasets/ad-preprocessed.csv --mab --nof_mab_iterations 300 >> results.csv
python run-script.py datasets/ad-preprocessed.csv --mab --nof_mab_iterations 500 >> results.csv
python run-script.py datasets/ad-preprocessed.csv --mab --nof_mab_iterations 1000 >> results.csv
