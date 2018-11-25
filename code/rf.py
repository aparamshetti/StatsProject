import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.metrics import confusion_matrix
from sklearn.metrics import confusion_matrix

#PCA dimension reduced files
X_train = pd.read_pickle("../X_train_pca.npk")
X_test = pd.read_pickle("../X_test_pca.npk")

#keeps the totalRansactionRevenue, class_pred = 0 if didnt buy anythin and 1 if did
y_test = pd.read_pickle("../y_test.pkl")
y_train = pd.read_pickle("../y_train.pkl")
import time
from sklearn.model_selection import GridSearchCV
# Create the parameter grid based on the results of random search 
param_grid = {
    'bootstrap': [True],
    # 'max_depth': [50,100],
#     'max_features': [2, 3],
    'min_samples_leaf': [.1, .05, .001],
#     'min_samples_split': [.05, .005],
    # 'n_estimators': [50, 100],
    'class_weight': ['balanced', 'balanced_subsample', None]
}
# Create a based model
rf = RandomForestClassifier(n_estimators = 100)
# Instantiate the grid search model
grid_search = GridSearchCV(estimator = rf, param_grid = param_grid, 
                          cv = 3, verbose = 2, n_jobs = -1, return_train_score=True)
print('created')
start  = time.time()
grid_search.fit(X_train, y_train['class_pred'])
print("done", time.time()-start)

print("params: ", grid_search.best_params_)
print("estimator: ", grid_search.best_estimator_)
print("CV_results: ", grid_search.cv_results_)
est = grid_search.best_estimator_

pred = est.predict(X_test)

print("Confusion matrix: ", confusion_matrix(y_test['class_pred'].values, pred))