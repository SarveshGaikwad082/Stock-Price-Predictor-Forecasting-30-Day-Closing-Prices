# -*- coding: utf-8 -*-
"""Task.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JPAx7kURv5-oCOmXtI73D9M-mTRFcbrB

### Project Goal:

The primary goal of this project is to develop a predictive model that accurately forecasts stock closing prices for the next 30 days and identifies which stocks are expected to exceed their previous closing prices.
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# load the data
data = pd.read_csv(r"/content/drive/MyDrive/csv_files/task.csv")

data.head()

data.info()

data.describe()

data.isnull().sum()

"""There are columns that complete null lets delete"""

null_col = data.loc[:,data.isnull().sum()>5].columns
print(null_col)

data = data.drop(columns=null_col)

data = data.dropna()

# lets correct data type : Convert 'TradDt' and 'BizDt' to datetime format
data["TradDt"] = pd.to_datetime(data["TradDt"])
data["BizDt"]=pd.to_datetime(data["BizDt"])

# # Calculate the difference between 'BizDt' and the future date (30 days later)
future_date = data['BizDt'] + pd.to_timedelta(30, unit='D')
data['DaysToFuture'] = (future_date - data['BizDt']).dt.days

data.columns

data["Sgmt"].unique()

data["Src"].unique()

data["FinInstrmTp"].unique()

data["SctySrs"].unique()

data["SsnId"].unique()

data["NewBrdLotQty"].unique()

"""Above observation for further prediction there is irrevalant feature that remove.

"""

irrevalant_col = ["Sgmt","Src","FinInstrmTp","SctySrs","SsnId","NewBrdLotQty","FinInstrmId","ISIN","TckrSymb","FinInstrmNm"]
data = data.drop(columns=irrevalant_col)

data.info()

# Split data into X and y
X = data.drop(columns=["TradDt","BizDt","ClsPric"])
y=data["ClsPric"]

X

"""### Utilizing Correlation Analysis to Identify and Reduce Multicollinearity Issues"""

corr_x = X.corr()
corr_x

sns.heatmap(corr_x,annot=True)

threshold = 0.8
corr_matrix = X.corr()
high_corr_var = np.where(abs(corr_matrix) > threshold)
high_corr_var = [(corr_matrix.index[X], corr_matrix.columns[y])
                 for X, y in zip(*high_corr_var) if X != y and X < y]

high_corr_var

from statsmodels.stats.outliers_influence import variance_inflation_factor
vif = pd.DataFrame()
vif["Feature"] = X.columns
vif["VIF"] = [variance_inflation_factor(X.values,i) for i in range (X.shape[1])]
print(vif.sort_values(by="VIF",ascending=False))

max_vif = 10
remove_column = True

while remove_column:
    vif = pd.DataFrame()
    vif["Feature"] = X.columns
    vif["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]

    max_vif_feature = vif.loc[vif["VIF"].idxmax()]

    if max_vif_feature["VIF"] > max_vif:
        X = X.drop(max_vif_feature["Feature"],axis=1)
        print(f"Removed feature '{max_vif_feature['Feature']}' with VIF = {max_vif_feature['VIF']:.2f}")
    else:
        remove_column = False

"""### Updated Dataset: Removing Features with High Correlation"""

X.columns

X.head(5)

y.head(5)

from sklearn.model_selection import train_test_split,GridSearchCV
X_train,X_test,y_train,y_test  = train_test_split(X,y,test_size = 0.3,random_state = 42)

X_train.shape

y_train.shape

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score

models = {
    'Decision Tree': DecisionTreeRegressor(random_state=42),
    'Random Forest': RandomForestRegressor(random_state=42),
    'XGBoost': XGBRegressor(random_state=42)
}

for model_name, model in models.items():
    model.fit(X_train, y_train)
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    r2_train = r2_score(y_train, y_train_pred)
    r2_test = r2_score(y_test, y_test_pred)

    print(f"{model_name} - R-squared (Train): {r2_train:.4f}, R-squared (Test): {r2_test:.4f}")

"""#### Result : Based on the results provided, Random Forest seems to be the best choice. It has a high R-squared on both the training (0.9875) and test sets (0.9693), indicating good performance and generalization without overfitting, unlike the Decision Tree and XGBoost, which both show signs of potential overfitting (R-squared on Train = 1.0000)."""

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf = RandomForestRegressor(random_state=42)

grid_search = GridSearchCV(estimator=rf, param_grid=param_grid,
                           cv=5, n_jobs=-1, verbose=2, scoring='r2')

grid_search.fit(X_train, y_train)

print(f"Best Hyperparameters: {grid_search.best_params_}")
print(f"Best R-squared on Train set: {grid_search.best_score_:.4f}")

best_rf = grid_search.best_estimator_

y_test_pred = best_rf.predict(X_test)
r2_test = r2_score(y_test, y_test_pred)
print(f"R-squared (Test): {r2_test:.4f}")

from sklearn.model_selection import cross_val_score
cv_scores = cross_val_score(best_rf, X_train, y_train, cv=10, scoring='r2')
print(f"Cross-Validation R-squared Scores: {cv_scores}")
print(f"Mean CV R-squared: {cv_scores.mean():.4f}")

"""#### Observation: The model shows strong performance with R-squared scores close to 1 in most folds,indicating excellent fit. The mean R-squared of 0.9802 suggests consistent predictive capability across different subsets of the data."""

import joblib
joblib.dump(best_rf, 'random_forest_model.pkl')
loaded_model = joblib.load('random_forest_model.pkl')



loaded_model = joblib.load('random_forest_model.pkl')

test_data = {
    'PrvsClsgPric': [150.0],
    'TtlTradgVol': [3000],
    'TtlTrfVal': [450000.0],
    'TtlNbOfTxsExctd': [120],
    'DaysToFuture': [30]  # Updated to 30 days in the future
}

test_df = pd.DataFrame(test_data)

predictions = loaded_model.predict(test_df)

print(f"Previous Closing Price: {test_data['PrvsClsgPric'][0]}")
print(f"Predictions: {predictions}")

test_data = {
    'PrvsClsgPric': [175.5],
    'TtlTradgVol': [4200],
    'TtlTrfVal': [560000.0],
    'TtlNbOfTxsExctd': [150],
    'DaysToFuture': [30]
}
test_df = pd.DataFrame(test_data)
predictions = loaded_model.predict(test_df)
previous_price = test_data['PrvsClsgPric'][0]
predicted_price = predictions[0]

print(f"Previous Closing Price: {previous_price}")
print(f"Predicted Closing Price for the next 30 days: {predicted_price}")

if predicted_price > previous_price:
    print("The predicted price indicates an increase compared to the previous closing price.")
else:
    print("The predicted price indicates a decrease compared to the previous closing price.")

"""### Conclusion :
This project developed a Random Forest model to predict stock closing prices for the next 30 days and identify stocks likely to exceed their previous closing prices. After cross-validation, the model achieved an accuracy of 98.02%. These insights can help investors make better decisions and improve trading strategies. Future improvements could focus on refining the model and including additional data for enhanced predictions.
"""