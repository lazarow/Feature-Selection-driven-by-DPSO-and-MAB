# MAB-optimized discrete PSO-based feature selection for enhanced classification performance

This repository contains the source code used in research on viewing the optimization of discrete PSO hyper-parameters 
as the adversarial multi-armed bandit problem. To verify the hypothesis, the possibility of using the solution in a 
practical feature selection problem for data classification was examined.

## Setup

The setup process based on Python's _virtual environments_. _Python 3.11.2_ was
used during the development.

Create [a virtual environment](https://virtualenv.pypa.io/en/latest/user_guide.html#introduction).
```
virtualenv .venv
```

[Activate the virtual environment](https://virtualenv.pypa.io/en/latest/user_guide.html#activators).
```
.\venv\Scripts\activate.bat
```

Install required libraries.
```
pip install -r requirements.txt
```

## Datasets

The experiments were conducted on 4 selected datasets from [the UCI repository](https://archive.ics.uci.edu/ml/index.php):
- [Soybean (Large) Data Set](https://archive.ics.uci.edu/ml/datasets/Soybean+(Large)),
- [Internet Advertisements Data Set](https://archive.ics.uci.edu/ml/datasets/internet+advertisements),
- [Arrhythmia Data Set](https://archive.ics.uci.edu/ml/datasets/arrhythmia),
- [Annealing Data Set](https://archive.ics.uci.edu/ml/datasets/Annealing).
