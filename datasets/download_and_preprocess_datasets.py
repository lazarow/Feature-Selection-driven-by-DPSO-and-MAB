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
ordinal_features = ["date", "temp"]
nominal_features = []
for feature in features:
    if feature not in ordinal_features:
        nominal_features.append(feature)
dataset = pd.read_csv(dir_path + "/soybean-large.csv", header=None, names=[target] + features)
number_of_features_before = len(dataset.columns) - 1
print(".", end="")
sys.stdout.flush()

# Handling missing values with the most frequent value strategy.
imputer = SimpleImputer(missing_values="?", strategy='most_frequent') 
for feature in features:
    if dataset[feature].eq("?").any():
        dataset[feature] = dataset[feature].astype(str)
        dataset[feature] = imputer.fit_transform(dataset[feature].values.reshape(-1,1))[:,0]
print(".", end="")
sys.stdout.flush()

# Encoding the classes (the target feature).
label_encoder = preprocessing.LabelEncoder()
dataset[target]= label_encoder.fit_transform(dataset[target])
print(".", end="")
sys.stdout.flush()

# One-hot encoding if needed.
for feature in nominal_features:
    if len(dataset[feature].unique()) < 3:
        continue
    dataset = pd.concat([dataset, pd.get_dummies(dataset[feature], prefix=feature)], axis=1)
    dataset = dataset.drop(columns=[feature])
print(".", end="")
sys.stdout.flush()

dataset = dataset.apply(pd.to_numeric)
print(".", end="")
sys.stdout.flush()

dataset.to_csv(dir_path + "/soybean-large-preprocessed.csv", index=False)
number_of_features_after = len(dataset.columns) - 1
number_of_classes = len(dataset[target].unique())
number_of_instances = dataset.shape[0]
print(" has been preprocessed and saved.")
print("Number of features (before preprocessing):", number_of_features_before)
print("Number of features (after preprocessing):", number_of_features_after)
print("Number of classes:", number_of_classes)
print("Number of instances:", number_of_instances)
#endregion


#region the Arrhythmia Data Set dataset.
print("Arrhythmia Data Set " , end="")
sys.stdout.flush()

target = "arrhythmia"
features = []
for i in range(279):
    feature = "feature" + str(i + 1)
    features.append(feature)
dataset = pd.read_csv(dir_path + "/arrhythmia.csv", header=None, names=features + [target])
number_of_features_before = len(dataset.columns) - 1
print(".", end="")
sys.stdout.flush()

nominal_features = ["feature2"]
for i in [16, 28, 40, 52, 64, 76, 88, 100, 112, 124, 136, 148]:
    for j in range(6):
        nominal_features.append("feature" + str(i + 6 + j))
linear_features = []
for feature in features:
    if feature not in nominal_features:
        linear_features.append(feature)

# Handling missing values with the most frequent value strategy.
imputer = SimpleImputer(missing_values="?", strategy='most_frequent') 
for feature in nominal_features:
    if dataset[feature].eq("?").any():
        dataset[feature] = imputer.fit_transform(dataset[feature].values.reshape(-1,1))[:,0]
# Handling missing values with the mean strategy.
imputer = SimpleImputer(missing_values=np.NaN, strategy='mean') 
for feature in linear_features:
    dataset[feature] = dataset[feature].replace("?", np.NaN)
    if dataset[feature].eq(np.NaN).any():
        dataset[feature] = imputer.fit_transform(dataset[feature].values.reshape(-1,1))[:,0]
print(".", end="")
sys.stdout.flush()

# One-hot encoding if needed.
for feature in nominal_features:
    if len(dataset[feature].unique()) < 3:
        continue
    dataset = pd.concat([dataset, pd.get_dummies(dataset[feature], prefix=feature)], axis=1)
    dataset = dataset.drop(columns=[feature])
dataset = dataset.copy()
print(".", end="")
sys.stdout.flush()

# Moving the target column to the beginning of the table.
column_to_move = dataset.pop(target)
dataset.insert(0, target, column_to_move)
print(".", end="")
sys.stdout.flush()

dataset = dataset.apply(pd.to_numeric)
print(".", end="")
sys.stdout.flush()

dataset.to_csv(dir_path + "/arrhythmia-preprocessed.csv", index=False)
print(" has been preprocessed and saved.")
number_of_features_after = len(dataset.columns) - 1
number_of_classes = len(dataset[target].unique())
number_of_instances = dataset.shape[0]
print(" has been preprocessed and saved.")
print("Number of features (before preprocessing):", number_of_features_before)
print("Number of features (after preprocessing):", number_of_features_after)
print("Number of classes:", number_of_classes)
print("Number of instances:", number_of_instances)
#endregion


#region the Annealing Data Set dataset.
print("Annealing Data Set " , end="")
sys.stdout.flush()

target = "classes"
features = [
    "family", "product-type", "steel", "carbon", "hardness", "temper_rolling", "condition", "formability", "strength",
    "non-ageing", "surface-finish", "surface-quality", "enamelability", "bc", "bf", "bt", "bw/me", "bl", "m",
    "chrom", "phos", "cbond", "marvi", "exptl", "ferro", "corr", "blue/bright/varn/clean", "lustre",
    "jurofm", "s", "p", "shape", "thick", "width", "len", "oil", "bore", "packing"
]
continuous_features = ["carbon", "hardness", "strength", "thick", "width", "len"]
ordinal_features = ["formability", "enamelability", "packing"]
nominal_features = []
for feature in features:
    if feature not in continuous_features:
        if feature not in ordinal_features:
            nominal_features.append(feature)
dataset = pd.read_csv(dir_path + "/anneal.csv", header=None, names=features + [target])
number_of_features_before = len(dataset.columns) - 1
print(".", end="")
sys.stdout.flush()

# Handling missing values with the most frequent value strategy.
imputer = SimpleImputer(missing_values="?", strategy='most_frequent') 
for feature in (nominal_features + ordinal_features):
    if dataset[feature].eq("?").any():
        if dataset[feature].eq("?").all() == False:
            dataset[feature] = imputer.fit_transform(dataset[feature].values.reshape(-1,1))[:,0]
# Handling missing values with the mean strategy.
imputer = SimpleImputer(missing_values=np.NaN, strategy='mean') 
for feature in continuous_features:
    dataset[feature] = dataset[feature].replace("?", np.NaN)
    if dataset[feature].eq(np.NaN).any():
        dataset[feature] = imputer.fit_transform(dataset[feature].values.reshape(-1,1))[:,0]
print(".", end="")
sys.stdout.flush()

# Encoding the classes (the target feature).
label_encoder = preprocessing.LabelEncoder()
dataset[target]= label_encoder.fit_transform(dataset[target])
# Encoding the nominal features.
for feature in nominal_features:
    dataset[feature]= label_encoder.fit_transform(dataset[feature])
print(".", end="")
sys.stdout.flush()

# One-hot encoding if needed.
for feature in nominal_features:
    if len(dataset[feature].unique()) < 3:
        continue
    dataset = pd.concat([dataset, pd.get_dummies(dataset[feature], prefix=feature)], axis=1)
    dataset = dataset.drop(columns=[feature])
dataset = dataset.copy()
print(".", end="")
sys.stdout.flush()

# Moving the target column to the beginning of the table.
column_to_move = dataset.pop(target)
dataset.insert(0, target, column_to_move)
print(".", end="")
sys.stdout.flush()

dataset = dataset.apply(pd.to_numeric)
print(".", end="")
sys.stdout.flush()

dataset.to_csv(dir_path + "/anneal-preprocessed.csv", index=False)
print(" has been preprocessed and saved.")
number_of_features_after = len(dataset.columns) - 1
number_of_classes = len(dataset[target].unique())
number_of_instances = dataset.shape[0]
print(" has been preprocessed and saved.")
print("Number of features (before preprocessing):", number_of_features_before)
print("Number of features (after preprocessing):", number_of_features_after)
print("Number of classes:", number_of_classes)
print("Number of instances:", number_of_instances)
#endregion


#region the Internet Advertisements Data Set dataset.
print("Internet Advertisements Data Set " , end="")
sys.stdout.flush()

target = "is-ad"
features = ["height", "width", "aratio"]
types = {"height": str, "width": str, "aratio": str}
for i in range(1555):
    feature = "feature" + str(i + 1)
    features.append(feature)
    types[feature] = str;
dataset = pd.read_csv(dir_path + "/ad.csv", header=None, names=features + [target], dtype=types)
number_of_features_before = len(dataset.columns) - 1
print(".", end="")
sys.stdout.flush()

# Handling missing data for continuous categories.
for feature in ["height", "width", "aratio"]:
    dataset[feature] = dataset[feature].str.strip()
    dataset[feature] = dataset[feature].replace("?", -1)
# Handling missing data for binary categories.
imputer = SimpleImputer(missing_values="?", strategy='most_frequent') 
for i in range(1555):
    feature = "feature" + str(i + 1)
    if dataset[feature].eq("?").any():
        dataset[feature] = imputer.fit_transform(dataset[feature].values.reshape(-1,1))[:,0]
dataset[target]= dataset[target].map({'ad.': 1, 'nonad.': 0})
print(".", end="")
sys.stdout.flush()

# Adding a new column for indication unknown data for continuous categories.
has_unknown_data = []
for index, row in dataset.iterrows():
    if row["width"] == -1 or row["height"] == -1 or row["aratio"].strip() == -1:
        has_unknown_data.append(1)
    else:
        has_unknown_data.append(0)
dataset.insert(0, "has-unknown-data", has_unknown_data)
print(".", end="")
sys.stdout.flush()

# Moving the target column to the beginning of the table.
column_to_move = dataset.pop(target)
dataset.insert(0, target, column_to_move)
print(".", end="")
sys.stdout.flush()

dataset = dataset.apply(pd.to_numeric)
print(".", end="")
sys.stdout.flush()

dataset.to_csv(dir_path + "/ad-preprocessed.csv", index=False)
print(" has been preprocessed and saved.")
number_of_features_after = len(dataset.columns) - 1
number_of_classes = len(dataset[target].unique())
number_of_instances = dataset.shape[0]
print(" has been preprocessed and saved.")
print("Number of features (before preprocessing):", number_of_features_before)
print("Number of features (after preprocessing):", number_of_features_after)
print("Number of classes:", number_of_classes)
print("Number of instances:", number_of_instances)
#endregion
