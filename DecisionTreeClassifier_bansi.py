# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_9kdxUDaEyfxWroqqMR9NzOT50KHOzL2
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder

product1 = '/content/Products_Information.csv'

#update date column to datetime and set it as index

# Read the CSV file with date parsing
product = pd.read_csv(product1, parse_dates=['date'])

# Convert the 'date_column' to datetime if it's not already

product['date'] = pd.to_datetime(product['date'])
product.set_index('date', inplace=True)

#Ensure 'product_type' is of categorical data type
product['product_type']=product['product_type'].astype('category')

#Build dictionary for store product grouping


# Separate the data from the answer
start_date = '2013-01-01'
end_date = '2017-07-30'
filtered = product[(product.index >= start_date) & (product.index <= end_date)]

segmented_data = {}
# Grouping the data by store and product, and storing each group in the dictionary
for (store, product_type), group in filtered.groupby(['store_nbr', 'product_type'], observed=True):
    segmented_data[(store, product_type)] = group[['sales', 'special_offer', 'id']]


store1beauty = segmented_data[(1, 'BEAUTY')]

# Assuming X_train, y_train, X_test, y_test are prepared datasets
#train dataset= 60%
train_size = int(len(store1beauty) * 0.6)
val_size = len(store1beauty) - train_size

X = store1beauty.drop(columns=['sales'])
y = store1beauty['sales']

X_train, X_val = X.iloc[:train_size], X.iloc[val_size:]
y_train, y_val = y.iloc[:train_size], y.iloc[val_size:]

# Initialize the label encoder
lencoder = LabelEncoder()

# Fit and transform the target variable in the combined data (training + validation)
y_combined = pd.concat([y_train, y_val], axis=0)
y_combined_encoded = lencoder.fit_transform(y_combined)

# Use the fitted label encoder to transform the target variable in the training and validation data
y_train_encoded = y_combined_encoded[:len(y_train)]
y_val_encoded = y_combined_encoded[len(y_train):]

# Choose a DT model
dtree3 = DecisionTreeClassifier(criterion="entropy", max_depth=3)
dtree1 = DecisionTreeClassifier(criterion="entropy", max_depth=1)

# Cross-validation scores for max_depth=3
scores_dtree3 = cross_val_score(dtree3, X_train, y_train_encoded, cv=5, scoring='accuracy')
print("Cross-validation scores for Decision Tree (max_depth=3):")
print(scores_dtree3)

# Cross-validation scores for max_depth=1
scores_dtree1 = cross_val_score(dtree1, X_train, y_train_encoded, cv=5, scoring='accuracy')
print("Cross-validation scores for Decision Tree (max_depth=1):")
print(scores_dtree1)

# Fit chosen model on the whole training data
dtree1.fit(X_train, y_train_encoded)
score = dtree1.score(X_val, y_val_encoded)
print(f"Score on validation set: {score:.2f}")

# Predictions
predictions = dtree1.predict(X_val)
print("Predicted: ", lencoder.inverse_transform(predictions))
print("   Actual: ", lencoder.inverse_transform(y_val_encoded))


print(f"Score on test set: {score:.2f}")

plot_tree(dtree1, filled=True, rounded=True)

# Defining forecasting date
future_dates = pd.date_range(start='2017-07-31', end='2017-08-15', freq='D')  # Define future dates

# Create feature data for these future dates (similar to X_train)
# This could involve extracting or generating features for these dates
# Example: Create a DataFrame with columns similar to X_train for the future dates

# Concatenate future dates and feature data into X_future DataFrame
start_date1 = '2017-07-31'
end_date1 = '2017-08-15'
ans = product[(product.index >= start_date1) & (product.index <= end_date1)]
segmented_data_ans = {}
# Grouping the data by store and product, and storing each group in the dictionary
for (store, product_type), group in ans.groupby(['store_nbr', 'product_type'], observed=True):
    segmented_data_ans[(store, product_type)] = group[['sales', 'special_offer', 'id']]

store1beauty_ans = segmented_data_ans[(1, 'BEAUTY')]

X_future = store1beauty_ans.drop(columns=['sales'])
X_future.index = future_dates

# Use the trained model to predict sales for future dates
future_predictions_encoded = dtree1.predict(X_future)

# Inverse transform the encoded predictions to get the actual sales values
future_predictions = lencoder.inverse_transform(future_predictions_encoded)

# Create a DataFrame with the forecasted sales and corresponding dates
forecast_df = pd.DataFrame({'date': future_dates, 'Sales Forecast': future_predictions})
forecast_df.set_index('date', inplace=True)

# Print or use the forecasted sales
print(forecast_df)