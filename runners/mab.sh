#!/bin/bash
python ../run-script.py ../datasets/soybean-large-preprocessed.csv --mab --nof_mab_iterations 390 --print_header >> ../results.csv
python ../run-script.py ../datasets/soybean-large-preprocessed.csv --mab --nof_mab_iterations 780 >> ../results.csv
python ../run-script.py ../datasets/soybean-large-preprocessed.csv --mab --nof_mab_iterations 1170 >> ../results.csv
python ../run-script.py ../datasets/anneal-preprocessed.csv --mab --nof_mab_iterations 390 >> ../results.csv
python ../run-script.py ../datasets/anneal-preprocessed.csv --mab --nof_mab_iterations 780 >> ../results.csv
python ../run-script.py ../datasets/anneal-preprocessed.csv --mab --nof_mab_iterations 1170 >> ../results.csv
python ../run-script.py ../datasets/arrhythmia-preprocessed.csv --mab --nof_mab_iterations 390 >> ../results.csv
python ../run-script.py ../datasets/arrhythmia-preprocessed.csv --mab --nof_mab_iterations 780 >> ../results.csv
python ../run-script.py ../datasets/arrhythmia-preprocessed.csv --mab --nof_mab_iterations 1170 >> ../results.csv
python ../run-script.py ../datasets/ad-preprocessed.csv --mab --nof_mab_iterations 390 >> ../results.csv
python ../run-script.py ../datasets/ad-preprocessed.csv --mab --nof_mab_iterations 780 >> ../results.csv
python ../run-script.py ../datasets/ad-preprocessed.csv --mab --nof_mab_iterations 1170 >> ../results.csv
