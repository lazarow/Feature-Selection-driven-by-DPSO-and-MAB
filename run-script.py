#region Imports.
import argparse
import os
import sys
import pandas as pd
from sklearn import tree
import time
import numpy as np
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from multiprocessing import Pool, freeze_support, cpu_count
from pyswarms.backend.operators import compute_pbest
from pyswarms.backend.topology import Star
from pyswarms.backend.handlers import VelocityHandler
from pyswarms.base import DiscreteSwarmOptimizer
import random
import math
#endregion

#region Parsing the arguments and configuration.
parser = argparse.ArgumentParser()
parser.add_argument("dataset_filepath")
parser.add_argument("--debug", action="store_true")
parser.add_argument("--grid_search", action="store_true")
parser.add_argument("--mab", action="store_true")
parser.add_argument("--nof_mab_iterations", default=300)
parser.add_argument("--print_header", action="store_true")
parser.add_argument("--no_fs", action="store_true")
parser.add_argument("--seed", default=5471427)
args = parser.parse_args()
config = vars(args)
# For the fitness function:
config["k_for_cross_validation"] = 5
config["alpha"] = 0.88
# For PSO:
config["nof_pso_iterations"] = 100
config["w_min"] = 0.5
config["w_max"] = 0.995
# For MAB
config["epsilon"] = 0.25
config["nof_iterations_before_reward"] = 10
# For experiments:
config["nof_repetitions"] = 10
#endregion

#region Loading the dataset.
if os.path.isfile(config["dataset_filepath"]) == False:
    sys.exit("The dataset filepath must be set and need to be a valid file.")
dataset = pd.read_csv(config["dataset_filepath"])
X = dataset.iloc[: , 1:]
y = dataset.iloc[: , 0]
#endregion

#region Multi-processing support.
nof_processes = cpu_count()
pool = None
#endregion

#region Creating classifiers (multiple will be created if multi-processing is enabled).
classifiers = []
for i in range(nof_processes):
    classifiers.append(tree.DecisionTreeClassifier(
        criterion="gini",
        splitter="best",
        random_state=config["seed"] + i
    ))
#endregion

#region The accuracy function.
previous_accuracy_values = {}
def get_accuracy_for_selected_features(selected_features, process_index = 0):
    h = hash(str(selected_features))
    if h in previous_accuracy_values:
        return previous_accuracy_values[h]
    # k-fold Cross-Validation.
    kf = KFold(n_splits=config["k_for_cross_validation"], shuffle=True, random_state=config["seed"] + 200 + process_index)
    selected_features_list = [] # Slicing data based on the feature selection.
    for idx, x in np.ndenumerate(selected_features):
        if x == 1:
            selected_features_list.append(idx[0])
    X_subset = X.iloc[:,selected_features_list]
    acc_scores = []
    for train_index, test_index in kf.split(X_subset):
        # Splitting data into k-folds.
        X_train, X_test = X_subset.iloc[train_index,:], X_subset.iloc[test_index,:]
        y_train, y_test = y[train_index], y[test_index]
        classifiers[process_index].fit(X_train, y_train) # Learning the model.
        y_pred = classifiers[process_index].predict(X_test) # Validating the model.
        acc = accuracy_score(y_pred, y_test)
        acc_scores.append(acc)
    avg_acc_score = sum(acc_scores) / config["k_for_cross_validation"] # Average of accuracy.
    previous_accuracy_values[h] = avg_acc_score
    return avg_acc_score
#endregion

#region The fitness function.
total_nof_features = X.shape[1]
def fitness_function(selected_features, process_index):
    acc_score = get_accuracy_for_selected_features(selected_features, process_index)
    nof_selected_features = np.count_nonzero(selected_features == 1)
    return config["alpha"] * (1.0 - acc_score) + (1.0 - config["alpha"]) * (nof_selected_features / total_nof_features)
#endregion

#region The objective function for a set of particles.
def objective_function(particles):
    nof_particles = particles.shape[0]
    results = pool.starmap(fitness_function, [(particles[i], i % nof_processes) for i in range(nof_particles)])
    return np.array(results)
#endregion

#region the DPSO implementation.
class DPSO(DiscreteSwarmOptimizer):
    def __init__(self, options, n_particles=30, dimensions=total_nof_features):
        super(DPSO, self).__init__(
            n_particles=n_particles, dimensions=dimensions, binary=True, options=options,
            init_pos=None, velocity_clamp=None, ftol=-np.inf, ftol_iter=1,
        )
        self.reset()
        self.top = Star(static=False)
        self.vh = VelocityHandler(strategy="unmodified")
        self.vh.memory = self.swarm.position
        self.swarm.pbest_cost = np.full(self.swarm_size[0], np.inf)
        self.name = __name__
        self.time_step = 0
        self.total_time_steps = 0
    
    def optimize(self, iters):
        for i in range(iters):
            self.iterate()
            if config["debug"] and i % 20 == 0:
                print("DEBUG: Iteration: {} | Best: {:.4f}".format(i+1, self.swarm.best_cost))
        return self.get_best()

    def iterate(self):
        # Calculating the inertia weight:
        self.swarm.options["w"] = config["w_max"] - (config["w_max"] - config["w_min"]) * self.time_step / self.total_time_steps
        self.swarm.current_cost = objective_function(self.swarm.position)
        self.swarm.pbest_pos, self.swarm.pbest_cost = compute_pbest(self.swarm)
        self.swarm.best_pos, self.swarm.best_cost = self.top.compute_gbest(self.swarm)
        self.swarm.velocity = self.top.compute_velocity(self.swarm, self.velocity_clamp, self.vh)
        self.swarm.position = self._compute_position(self.swarm)
        self.time_step += 1

    def get_best(self):
        final_best_cost = self.swarm.best_cost
        final_best_pos = self.swarm.pbest_pos[
            self.swarm.pbest_cost.argmin()
        ].copy()
        return (final_best_cost, final_best_pos)

    def _compute_position(self, swarm):
        return (np.random.random_sample(size=swarm.dimensions) < self._sigmoid(swarm.velocity)) * 1

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def save_reward_point(self):
        self.reward_point = {
            "position": np.copy(self.swarm.position),
            "velocity": np.copy(self.swarm.velocity),
            "pbest_pos": np.copy(self.swarm.pbest_pos),
            "best_pos": np.copy(self.swarm.best_pos),
            "pbest_cost": np.copy(self.swarm.pbest_cost),
            "best_cost": np.copy(self.swarm.best_cost),
            "time_step": self.time_step
        }

    def restore_reward_point(self):
        self.swarm.position = np.copy(self.reward_point["position"])
        self.swarm.velocity = np.copy(self.reward_point["velocity"])
        self.swarm.pbest_pos = np.copy(self.reward_point["pbest_pos"])
        self.swarm.best_pos = np.copy(self.reward_point["best_pos"])
        self.swarm.pbest_cost = np.copy(self.reward_point["pbest_cost"])
        self.swarm.best_cost = np.copy(self.reward_point["best_cost"])
        self.time_step = self.reward_point["time_step"]

#endregion

if __name__ == '__main__':

    #region Multi-processing support.
    freeze_support()
    pool = Pool(processes=nof_processes)
    #endregion

    #region The output header.
    dataset = os.path.basename(config["dataset_filepath"]).split('.')[0]
    if config["print_header"]:
        print("Dataset","Name", "Test Index", "P.1", "P.2", "P.3", "Cost", "Accuracy", "Nof.Feature", "Time", "Feature.Selection", "MAB.rewards", "MAB.visits", sep=";")
        sys.stdout.flush()
    #endregion

    #region The baseline, i.e. all features are selected.
    if config["no_fs"]:
        start = time.time()
        selected_features = np.ones((X.shape[1],), dtype=int)
        acc_score = get_accuracy_for_selected_features(selected_features)
        end = time.time()
        print(dataset, "No feature selection", 1, "", "", "", (config["alpha"] * (1.0 - acc_score) + (1 - config["alpha"])), acc_score, len(selected_features), end-start, "", "", "", sep=";")
        sys.stdout.flush()
    #endregion

    #region Generating hyper-parameters space.
    hyper_parameters_space = []
    c_set = [0.5, 1.0, 1.5, 2, 2.5]
    for c1 in c_set: 
        for c2 in c_set:
            hyper_parameters_space.append({"c1": c1, "c2": c2})
    if config["debug"]:
        print("DEBUG:", len(hyper_parameters_space))
        print("DEBUG:", hyper_parameters_space)
    #endregion

    #region Grid-Search
    if config["grid_search"]:
        for hyper_parameters in hyper_parameters_space:
            for repetition in range(int(config["nof_repetitions"])):
                start = time.time()
                dpso = DPSO(options={"c1": hyper_parameters["c1"], "c2": hyper_parameters["c2"]})
                dpso.total_time_steps = config["nof_pso_iterations"]
                dpso.optimize(config["nof_pso_iterations"])
                cost, selected_features = dpso.get_best()
                acc_score = get_accuracy_for_selected_features(selected_features)
                end = time.time()
                print(dataset, "DPSO (Grid Search)", repetition + 1, hyper_parameters["c1"], hyper_parameters["c2"], "", cost, acc_score, np.count_nonzero(selected_features == 1), end-start, ','.join(map(str, selected_features)), "", "", sep=";")
                sys.stdout.flush()
    #endregion

    #region MAB.
    if config["mab"]:
        for repetition in range(int(config["nof_repetitions"])):
            start = time.time()
            dpso = DPSO(options={})
            dpso.save_reward_point()
            best_cost = np.inf
            best_selected_features = None
            real_total_time_steps = len(hyper_parameters_space) * config["nof_pso_iterations"]
            total_time_steps = real_total_time_steps
            dpso.total_time_steps = total_time_steps
            rewards = [0] * len(hyper_parameters_space)
            visits = [0] * len(hyper_parameters_space)
            time_step = 0
            while time_step < real_total_time_steps:
                if random.random() < config["epsilon"]:
                    choice = random.choice(range(len(hyper_parameters_space)))
                else:
                    choice = None
                    best_value = -np.inf
                    arms = [*range(len(hyper_parameters_space))]
                    random.shuffle(arms)
                    for i in arms:
                        if visits[i] == 0:
                            choice = i
                            break
                        value = 1.0 * rewards[i] / visits[i]
                        if value > best_value:
                            choice = i
                            best_value = value
                dpso.swarm.options["c1"] = hyper_parameters_space[choice]["c1"]
                dpso.swarm.options["c2"] = hyper_parameters_space[choice]["c2"]
                for j in range(config["nof_iterations_before_reward"]):
                    dpso.iterate()
                    time_step += 1
                cost, selected_features = dpso.get_best()
                reward = 0
                if cost < best_cost:
                    best_cost = cost
                    best_selected_features = selected_features
                    reward = 1
                    dpso.save_reward_point()
                else:
                    total_time_steps -= config["nof_iterations_before_reward"]
                    dpso.total_time_steps = total_time_steps
                    dpso.restore_reward_point()
                rewards[choice] += reward
                visits[choice] += 1
                if config["debug"]:
                    print("DEBUG: MAB iteration: {}".format(time_step), "Improvement" if reward == 1 else "Stagnation", rewards, visits, total_time_steps, sep=" | ")

                iter25 = round((real_total_time_steps * 0.25) / config["nof_iterations_before_reward"]) * config["nof_iterations_before_reward"]
                if time_step == iter25:
                    end = time.time()
                    acc_score = get_accuracy_for_selected_features(best_selected_features)
                    print(dataset, "DPSO (MAB)", repetition+1, time_step, "25%", "", best_cost, acc_score, np.count_nonzero(best_selected_features == 1), end-start, ','.join(map(str, best_selected_features)), ','.join(map(str, rewards)), ','.join(map(str, visits)), sep=";")  
                    sys.stdout.flush()
                iter50 = round((real_total_time_steps * 0.50) / config["nof_iterations_before_reward"]) * config["nof_iterations_before_reward"]
                if time_step == iter50:
                    end = time.time()
                    acc_score = get_accuracy_for_selected_features(best_selected_features)
                    print(dataset, "DPSO (MAB)", repetition+1, time_step, "50%", "", best_cost, acc_score, np.count_nonzero(best_selected_features == 1), end-start, ','.join(map(str, best_selected_features)), ','.join(map(str, rewards)), ','.join(map(str, visits)), sep=";")        
                    sys.stdout.flush()
                iter75 = round((real_total_time_steps * 0.75) / config["nof_iterations_before_reward"]) * config["nof_iterations_before_reward"]
                if time_step == iter75:
                    end = time.time()
                    acc_score = get_accuracy_for_selected_features(best_selected_features)
                    print(dataset, "DPSO (MAB)", repetition+1, time_step, "75%", "", best_cost, acc_score, np.count_nonzero(best_selected_features == 1), end-start, ','.join(map(str, best_selected_features)), ','.join(map(str, rewards)), ','.join(map(str, visits)), sep=";")        
                    sys.stdout.flush()

            acc_score = get_accuracy_for_selected_features(best_selected_features)
            end = time.time()
            print(dataset, "DPSO (MAB)", repetition+1, time_step, "100%", "", best_cost, acc_score, np.count_nonzero(best_selected_features == 1), end-start, ','.join(map(str, best_selected_features)), ','.join(map(str, rewards)), ','.join(map(str, visits)), sep=";")
            sys.stdout.flush()
    #endregion

    #region Multi-processing support.
    pool.close()
    pool.join()
    #endregion
