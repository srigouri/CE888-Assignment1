# -*- coding: utf-8 -*-
"""IHDP_Causal.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/srigouri/CE888-Causal/blob/main/IHDP_Causal.ipynb

# Causal Inference on IHDP Dataset:

---
Description:

Using Random Forest Regression,Random forest with Inverse Propensity Weighting (IPW), CATE estimator X-Learner with RandomForest as base learner to estimate causal effects in IHDP data.

-(Reference: CE888 Lab4 Task)

-Evaluation metrics are called from causalfuncs.py (Reference: https://github.com/dmachlanski/CE888_2022/blob/main/project/metrics.py)

-Data source: https://github.com/dmachlanski/CE888_2022/tree/main/project/data

#### Packages

Loading required packages:
"""

!pip install econml

"""Importing Libraries:




"""

from econml.metalearners import XLearner
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import scipy.stats as st
import matplotlib.pyplot as plt
import seaborn as sns
from causalfuncs import *
from sklearn.model_selection import GridSearchCV

"""#### Data

Loading IHDP Data from https://raw.githubusercontent.com/dmachlanski/CE888_2022/main/project/data/ihdp.csv:
"""

ihdp_data=pd.read_csv('https://raw.githubusercontent.com/dmachlanski/CE888_2022/main/project/data/ihdp.csv')

"""Exploring the IHDP Data:"""

ihdp_data.head()

"""To check number of rows and columns in IHDP dataset:

"""

ihdp_data.shape

"""
IHDP data has got 29 columns in which columns with names x1 to x25 are input features,t denotes for treatment,yf is the factual outcome,ycf is the counterfactual outcome and ite is the Individual Treatment Effect.The values for particular columns are extracted using integer-location based indexing and
assigning these values to the variables X,T,Yf,Ycf and ite respectively.

"""

X=ihdp_data[['x1','x2','x3','x4','x5','x6','x7','x8','x9','x10','x11','x12','x13','x14','x15','x16','x17','x18','x19','x20','x21','x22','x23','x24','x25']]
T=ihdp_data.iloc[:,25:26].values
Yf=ihdp_data.iloc[:,26:27].values
Ycf=ihdp_data.iloc[:,27:28].values
ite=ihdp_data.iloc[:,28:29].values

"""####Data Pre-processing:

Splitting the data to Training, validation and testing data.First splitting complete dataset to Training and Testing data in 80/20 ratio.Then again splitting training data to Training and Validation data in 80/20 ratio.
"""

X_train, X_test, T_train, T_test, Yf_train, Yf_test,Ycf_train,Ycf_test,ite_train, ite_test = train_test_split(X, T, Yf,Ycf, ite, test_size=0.2)
X_train, X_val,T_train,T_val,Yf_train,Yf_val,Ycf_train,Ycf_val,ite_train,ite_val = train_test_split(X_train,T_train,Yf_train,Ycf_train,ite_train,test_size=0.20)

"""Checking the shapes of training,Validation,Testing Data

"""

print("X_train shape: {}".format(X_train.shape))
print("X_val shape: {}".format(X_val.shape))
print("X_test shape: {}".format(X_test.shape))
print("T_train shape: {}".format(T_train.shape))
print("T_val shape: {}".format(T_val.shape))
print("T_test shape: {}".format(T_test.shape))
print("Yf_train shape: {}".format(Yf_train.shape))
print("Yf_val shape: {}".format(Yf_val.shape))
print("Yf_test shape: {}".format(Yf_test.shape))
print("Ycf_train shape: {}".format(Ycf_train.shape))
print("Ycf_val shape: {}".format(Ycf_val.shape))
print("Ycf_test shape: {}".format(Ycf_test.shape))
print("ite_train shape: {}".format(ite_train.shape))
print("ite_val shape: {}".format(ite_val.shape))
print("ite_test shape: {}".format(ite_test.shape))

"""Standardizing the input training data X.No standardization required for treatment variable T as the data is binary."""

scaler_x = StandardScaler()
X_train = scaler_x.fit_transform(X_train)
X_val = scaler_x.transform(X_val)
X_test = scaler_x.transform(X_test)

plt.hist(ite)

"""Checking the means of Individual treatment effects after splitting the data:"""

np.mean(ite_train),np.mean(ite_val),np.mean(ite_test)

"""#### 3.Random Forest Regression:

Training The Model:
Using three estimators for training the model:

Random forest regressor,
Random forest with Inverse Propensity Weighting (IPW),
X-learner with RF as base learners.

Concatenating X variable with 25 input features and T i.e treatment 
variable to train the model along with treatment.
"""

XT_train = np.concatenate((X_train,T_train),axis=1)

#Fitting Random Forest Regressor on training data:

rf = RandomForestRegressor()
rf.fit(XT_train, Yf_train.flatten())

#For validation of model, y1_val and y0_val are predicted by setting treatment to 1 and 0 respectively.
#Treatment variable (T=0,T=1) is again merged accordingly with X data.
#Predicted outcomes for both treated and controlled for each individuals as y1_val,y0_val and obtained treatement effect using ite=y1-y0.

xt0_val = np.concatenate([X_val, np.zeros_like(T_val)], axis=1)
rf_y0_val = rf.predict(xt0_val)

xt1_val = np.concatenate([X_val, np.ones_like(T_val)], axis=1)
rf_y1_val = rf.predict(xt1_val)

rf_te_val = rf_y1_val - rf_y0_val
np.mean(rf_te_val)

"""Predictions using Test data:

y1_test and y0_test are predicted by setting treatment to 1 and 0 respectively.
Setting T to a 1 and 0 for all individuals using zeros_like and one_like and merge with X_test to obtain treatment effect estimates
Outcomes for both treated and controlled for each individuals as y1_test,y0_test and obtained treatement effect using ite=y1-y0
"""

xt0_test = np.concatenate([X_test, np.zeros_like(T_test)], axis=1)
rf_y0_test = rf.predict(xt0_test)

xt1_test = np.concatenate([X_test, np.ones_like(T_test)], axis=1)
rf_y1_test = rf.predict(xt1_test)

rf_te_test = rf_y1_test - rf_y0_test
np.mean(rf_te_test)

"""#### 4.RandomForestClassifier with Inverse Propensity Score(IPSW):

Training using RandomForestClassifier extending with with the Inverse Propensity Weighting (IPW),to model unit's probability of receiving the treatment, P(ti|xi). This is a classic binary classification problem using input X,treatment T. P(ti|xi)  is called a propensity score.

To get the sample weights, get_ps_weights function is called from causalfuncs.py which is available at https://github.com/srigouri/CE888-Causal/blob/main/causalfuncs.py
"""

from causalfuncs import get_ps_weights
prop_clf = RandomForestClassifier()
weights = get_ps_weights(prop_clf, X_train, T_train)

rf_ipsw = RandomForestRegressor()
rf_ipsw.fit(XT_train, Yf_train.flatten(), sample_weight=weights)

#Making Predictions using Classifier with Inverse Propensity Scores (IPSW) and computing ITE's.
#Mean of ITEs is calculated.

rf_ipsw_y0_test =rf_ipsw.predict(xt0_test) 
rf_ipsw_y1_test =rf_ipsw.predict(xt1_test) 

rf_ipsw_te_test = rf_ipsw_y1_test - rf_ipsw_y0_test 
np.mean(rf_ipsw_te_test)

"""#### 5.X-Learner:
  CATE estimator X-learner is a meta-learner implemented via EconML. Uses provided regressors and classifiers to model and predict effect. We need not merge inputs and treatment to train the model. 
"""

xl = XLearner(models=RandomForestRegressor(), propensity_model=RandomForestClassifier())
xl.fit(Yf_train, T_train.flatten(), X=X_train)

xl_te_test = xl.effect(X_test)

"""#### Evaluation

Metrics Chosen: ϵATE  and  ϵPEHE
"""

# Using 'abs_ate' function from causalfuncs.py, true ITEs and predicted ITEs to get the measurements.
rf_ate_test = abs_ate(ite_test,rf_te_test)
rf_ipsw_ate_test = abs_ate(ite_test,rf_ipsw_te_test)
xl_ate_test = abs_ate(ite_test,xl_te_test) 

# Using 'pehe' function from causalfuncs.py, true ITEs and predicted ITEs to get the measurements.
rf_pehe_test =pehe(ite_test,rf_te_test) 
rf_ipsw_pehe_test = pehe(ite_test,rf_ipsw_te_test) 
xl_pehe_test = pehe(ite_test,xl_te_test)

results = []
results.append(['RF', rf_ate_test, rf_pehe_test])
results.append(['RF (IPW)', rf_ipsw_ate_test, rf_ipsw_pehe_test])
results.append(['XL', xl_ate_test, xl_pehe_test])

cols = ['Method', 'ATE test', 'PEHE test']

df = pd.DataFrame(results, columns=cols)
df

"""#### Confidence Intervals

Confidence intervals of predicted ATEs
"""

rf_ate_bounds = mean_ci(rf_te_test)
rf_ipsw_ate_bounds = mean_ci(rf_ipsw_te_test)
xl_ate_bounds = mean_ci(xl_te_test)


results = []
results.append(['RF', rf_ate_bounds[0], rf_ate_bounds[1], rf_ate_bounds[2]])
results.append(['RF (IPSW)', rf_ipsw_ate_bounds[0], rf_ipsw_ate_bounds[1], rf_ipsw_ate_bounds[2]])
results.append(['XL', xl_ate_bounds[0], xl_ate_bounds[1], xl_ate_bounds[2]])

cols = ['Method', 'ATE mean', 'CI lower', 'CI upper']

df2 = pd.DataFrame(results, columns=cols)
df2

"""#### Visualizations

Box plot showing treatment effect with different models:
"""

plt.figure()
plt.boxplot([rf_te_test, rf_ipsw_te_test, xl_te_test.flatten()], labels=['RF', 'RF (IPSW)', 'X-learner'])
plt.ylabel('Treatment Effect')

plt.show()

"""Scatter plot showing treatment effect with different models:

"""

plt.figure(figsize=(12, 10))
m_size = 10
plt.scatter(Yf_test,rf_te_test, label="RF", s=m_size)
plt.scatter(Yf_test,rf_ipsw_te_test, label="RF (IPW)", s=m_size)
plt.scatter(Yf_test,xl_te_test, label="X-learner", s=m_size)
plt.xlabel('X')
plt.ylabel('Treatment Effect')
plt.legend()
plt.show()