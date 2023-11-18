#%%#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score, mean_squared_error, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay


class ZeroSalesForecaster:
    def predict(self, periods):
        return np.zeros(periods)


class StationarySalesForecaster:
    # Loading the data form the file
    product = pd.read_csv("/Users/ttonny0326/BA_ORRA/Python_Programming/Products_Information.csv")
    # Convert the 'date' column to datetime format and set it as the index
    product['date'] = pd.to_datetime(product['date'])
    product.set_index('date', inplace=True)
    # Ensure 'product_type' is of categorical data type
    product['product_type'] = product['product_type'].astype('category')
    # Build a dictionary for the store-product grouping 
    segmented_data = {}
    # Grouping the data by store and product, and storing each group in the dictionary
    for (store, product_type), group in product.groupby(['store_nbr', 'product_type'], observed=True):
            segmented_data[(store, product_type)] = group[['sales', 'special_offer', 'id']]

    # Initial the self values in the StationarySalesForecaster class
    def __init__(self, store_number, product_type, order=(8, 2, 6), train_end_date='2016-12-31', validation_end_date='2017-07-31'):
        # self.segmented_data = segmented_data
        self.store_number = store_number
        self.product_type = product_type
        self.order = order
        self.train_end_date = train_end_date
        self.validation_end_date = validation_end_date
        self.model = None

    def arima_fit(self):
        # Retrieve the specific segment of the data
        specific_segment = self.segmented_data[(self.store_number, self.product_type)]

        # Ensuring the date index is in datetime format
        specific_segment.index = pd.to_datetime(specific_segment.index)
        # Splitting the data for training
        train_data = specific_segment[:self.train_end_date]['sales']
        validation_data = specific_segment[self.train_end_date:self.validation_end_date]['sales']
        # Splitting the data for testing 
        test_data = specific_segment[self.validation_end_date:]['sales']

        # Fit the ARIMA model
        self.model = ARIMA(train_data, order=self.order)
        self.model = self.model.fit()

    def arima_predict(self):
        # Retrieve the specific segment of the data
        specific_segment = self.segmented_data[(self.store_number, self.product_type)]
        
        # Setting up for the testing data
        test_data = specific_segment[self.validation_end_date:]['sales']
        
        # Forecasting sales for the specified number of steps
        forecast = self.model.forecast(steps=len(test_data))

        # Plot the forecast alongside the actual test data
        plt.figure(figsize=(12,6))
        plt.plot(test_data.index, forecast, color='blue', label='Predicted Sales')
        plt.plot(test_data.index, test_data, color='red', label='Actual Sales')
        plt.title('Sales Forecast vs Actuals')
        plt.xlabel('Date')
        plt.ylabel('Sales')
        plt.legend()
        plt.show()

        # Evaluate the model's performance
        mse = mean_squared_error(test_data, forecast)
        print("Mean Squared Error:", mse)

    



class NonStationarySalesForecaster:
    # Loading the data form the file
    product = pd.read_csv("/Users/ttonny0326/BA_ORRA/Python_Programming/Products_Information.csv")
    # Convert the 'date' column to datetime format and set it as the index
    product['date'] = pd.to_datetime(product['date'])
    product.set_index('date', inplace=True)
    # Ensure 'product_type' is of categorical data type
    product['product_type'] = product['product_type'].astype('category')
    # Build a dictionary for the store-product grouping 
    segmented_data = {}
    # Grouping the data by store and product, and storing each group in the dictionary
    for (store, product_type), group in product.groupby(['store_nbr', 'product_type'], observed=True):
            segmented_data[(store, product_type)] = group[['sales', 'special_offer', 'id', 'store_nbr']]

    def __init__(self, store_number, product_type, train_end_date='2016-12-31', validation_end_date='2017-07-31', n_estimators=250, max_depth=15, random_state=42, max_features= 'sqrt', min_samples_leaf=2, min_samples_split=5):
        self.store_number = store_number
        self.product_type = product_type
        self.train_end_date = train_end_date
        self.validation_end_date = validation_end_date
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.max_features = max_features
        self.model = None

    def randomforest_fit(self):
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split, cross_val_score
        specific_segment = self.segmented_data[(self.store_number, self.product_type)]

        # Prepare the features and target variable
        X_train = specific_segment[:self.validation_end_date][['special_offer', 'id', 'store_nbr']].values
        Y_train = specific_segment[:self.validation_end_date]['sales']

        # Initialize the RandomForestRegressor with specified parameters
        self.model = RandomForestRegressor(n_estimators = self.n_estimators, 
                                           max_depth = self.max_depth, 
                                           random_state = self.random_state,
                                           max_features = self.max_features
                                           )
        # Perform cross-validation
        # cv_scores = cross_val_score(self.model, X_train, Y_train, cv=10)  # cv=5 for 5-folds cross-validation

        # Train the model on the entire training data
        self.model.fit(X_train, Y_train)

        # Print the mean cross-validation score
        # print("Average Cross-Validation Score:", np.mean(cv_scores))

    def randomforest_predict(self):
        specific_segment = self.segmented_data[(self.store_number, self.product_type)]

        X_test = specific_segment[self.validation_end_date:][['special_offer', 'id', 'store_nbr']].values

        Y_test = specific_segment[self.validation_end_date:]['sales']

        y_predict = self.model.predict(X_test)

        mse = mean_squared_error(Y_test, y_predict)

        # Plot the forecast alongside the actual test data
        plt.figure(figsize=(12,6))
        plt.plot(Y_test.index, y_predict, color='blue', label='Predicted Sales')
        plt.plot(Y_test.index, Y_test, color='red', label='Actual Sales')
        plt.title('Sales Forecast vs Actuals')
        plt.xlabel('Date')
        plt.ylabel('Sales')
        plt.legend()
        plt.show()

        # Print the MSE
        print("Mean Squared Error:", mse)

    def randomforest_fine_tune(self):
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import GridSearchCV
        specific_segment = self.segmented_data[(self.store_number, self.product_type)]

        # Prepare the features and target variable
        X_train = specific_segment[:self.train_end_date][['special_offer', 'id', 'store_nbr']].values
        Y_train = specific_segment[:self.train_end_date]['sales']

        # Define the parameter grid to search
        param_grid = {
            'n_estimators': [20, 50, 100, 150, 200, 250, 300, 350, 400, 500],
            'max_depth': [10, 12, 15, 20, 25, 30, 35, 40, 45, 50],
            'min_samples_split': [2, 5, 10, 15],
            'min_samples_leaf': [1, 2, 4, 6, 10],
            'max_features': ['auto', 'sqrt']
        }

        # Initialize the RandomForestRegressor
        rf = RandomForestRegressor(random_state=self.random_state)

        # Perform grid search with cross-validation
        grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2, scoring='neg_mean_squared_error')
        grid_search.fit(X_train, Y_train)

        # Update the model with the best parameters
        self.model = grid_search.best_estimator_

        # Print the best parameters
        print("Best Parameters:", grid_search.best_params_)
    



    def prepare_data(self, data):
        # Implement your feature engineering here
        pass

    def prepare_prediction_data(self, start_date, end_date):
        # Prepare the data for prediction for the given date range
        pass





# class Machine_Learning:
#     def __init__(self, ):


# StationarySalesForecaster(ARIMA, store1, BEAUTY, 5)

# days = 0


# for i in non_stationary_result['Store-Product']:
#     nonStationarySalesForecaster(ARIMA, i, days)

# %%