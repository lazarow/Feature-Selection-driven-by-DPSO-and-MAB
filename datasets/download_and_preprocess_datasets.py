import os
import sys
import urllib.request
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.impute import SimpleImputer

dir_path = os.path.dirname(os.path.realpath(__file__))

#region Downloading the datasets.
print("Downloading the datasets ", end="")
sys.stdout.flush()
datasets = [
    {"url": "https://archive.ics.uci.edu/ml/machine-learning-databases/soybean/soybean-large.data", "save_path": dir_path + "/soybean-large.csv"},
    {"url": "https://archive.ics.uci.edu/ml/machine-learning-databases/internet_ads/ad.data", "save_path": dir_path + "/ad.csv"},
    {"url": "https://archive.ics.uci.edu/ml/machine-learning-databases/arrhythmia/arrhythmia.data", "save_path": dir_path + "/arrhythmia.csv"},
    {"url": "https://archive.ics.uci.edu/ml/machine-learning-databases/annealing/anneal.data", "save_path": dir_path + "/anneal.csv"},
]
for dataset in datasets:
    if os.path.exists(dataset["save_path"]) == False:
        urllib.request.urlretrieve(dataset["url"], dataset["save_path"])
    print(".", end="")
    sys.stdout.flush()
print(" has been completed.")
#endregion

#region the Soybean (Large) Data Set dataset.
print("The Soybean (Large) Data Set " , end="")
sys.stdout.flush()

target = "disease"

features = [
    "date", "plant-stand", "precip", "temp", "hail", "crop-hist", "area-damaged", "severity", "seed-tmt", "germination", "plant-growth",
    "leaves", "leafspots-halo", "leafspots-marg", "leafspot-size", "leaf-shread", "leaf-malf", "leaf-mild", "stem", "lodging", "stem-cankers",
    "canker-lesion", "fruiting-bodies", "external decay", "mycelium", "int-discolor", "sclerotia", "fruit-pods", "fruit spots", "seed",
    "mold-growth", "seed-discolor", "seed-size", "shriveling", "roots"
]

dataset = pd.read_csv(dir_path + "/soybean-large.csv", header=None, names=[target] + features)

# Handling missing values with the most frequent value strategy.
imputer = SimpleImputer(missing_values="?", strategy='most_frequent') 
for feature in features:
    dataset[feature] = dataset[feature].astype(str)
    dataset[feature] = imputer.fit_transform(dataset[feature].values.reshape(-1,1))[:,0]
    dataset[feature] = dataset[feature].apply(pd.to_numeric)
print(".", end="")
sys.stdout.flush()

# Encoding the classes (the target feature).
label_encoder = preprocessing.LabelEncoder()
dataset[target]= label_encoder.fit_transform(dataset[target])
print(".", end="")
sys.stdout.flush()

# One-hot encoding if needed.
ordinal_features = ["date", "plant-stand", "precip", "temp", "germination"]
nominal_features = []
for feature in features:
    if feature not in ordinal_features:
        nominal_features.append(feature)
for feature in nominal_features:
    if len(dataset[feature].unique()) < 3:
        continue
    dataset = pd.concat([dataset, pd.get_dummies(dataset[feature], prefix=feature)], axis=1)

"""
ordinal_features = []
nominal_features = []


label_encoder = preprocessing.LabelEncoder()
dataset[target] = label_encoder.fit_transform(dataset[target])
for index, feature in enumerate(features):
    dataset[feature] = label_encoder.fit_transform(dataset[feature])
"""

dataset.to_csv(dir_path + "/soybean-large-preprocessed.csv", index=False)
print(" has been preprocessed and saved.")
#endregion
