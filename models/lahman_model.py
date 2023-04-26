import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

# Load the data
pitcher_data = pd.read_csv('pitcher_data.csv')
hitter_data = pd.read_csv('hitter_data.csv')

# Data exploration and visualization for pitchers
pitcher_target = 'proj_DK_pts_per_inn'
pitcher_features = ['ERA', 'WHIP', 'K/9', 'BB/9', 'HR/9', 'FIP', 'xFIP', 'SwStr%', 'LOB%']
pitcher_df = pitcher_data[pitcher_features + [pitcher_target]]
sns.pairplot(pitcher_df)
plt.show()
corr = pitcher_df.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.show()

# Data exploration and visualization for hitters
hitter_target = 'proj_DK_pts_per_PA'
hitter_features = ['AVG', 'OBP', 'SLG', 'OPS', 'wOBA', 'wRC+', 'WAR', 'ISO', 'BB%', 'K%']
hitter_df = hitter_data[hitter_features + [hitter_target]]
sns.pairplot(hitter_df)
plt.show()
corr = hitter_df.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.show()

# Prepare the data for training for pitchers
X_pitcher = pitcher_data[pitcher_features]
y_pitcher = pitcher_data[pitcher_target]
scaler_pitcher = StandardScaler()
X_pitcher_scaled = scaler_pitcher.fit_transform(X_pitcher)

# Cross-validation for pitchers
pitcher_models = [LinearRegression(), Lasso(), Ridge()]
for model in pitcher_models:
    scores = cross_val_score(model, X_pitcher_scaled, y_pitcher, cv=5, scoring='neg_root_mean_squared_error')
    print(f"{model.__class__.__name__} RMSE: {-scores.mean():.2f} +/- {scores.std():.2f}")

# Hyperparameter tuning for pitchers
param_grid = {'alpha': np.logspace(-3, 3, 7)}
pitcher_lasso = Lasso()
pitcher_ridge = Ridge()
pitcher_lasso_cv = GridSearchCV(pitcher_lasso, param_grid, cv=5, scoring='neg_root_mean_squared_error')
pitcher_ridge_cv = GridSearchCV(pitcher_ridge, param_grid, cv=5, scoring='neg_root_mean_squared_error')
pitcher_lasso_cv.fit(X_pitcher_scaled, y_pitcher)
pitcher_ridge_cv.fit(X_pitcher_scaled, y_pitcher)
print(f"Lasso RMSE: {-pitcher_lasso_cv.best_score_:.2f} (alpha={pitcher_lasso_cv.best_params_['alpha']})")
print(f"Ridge RMSE: {-pitcher_ridge_cv.best_score_:.2f} (alpha={pitcher_ridge_cv.best_params_['alpha']})")

# Train a linear regression model for pitchers with the best hyperparameters
pitcher_model = Ridge(alpha=pitcher_ridge_cv.best_params_['alpha'])
X_pitcher_train, X_pitcher_test, y_pitcher_train, y_pitcher_test = train_test_split(X_pitcher_scaled, y_pitcher, test_size=0.2, random_state=42)
pitcher_model.fit(X_pitcher_train, y_pitcher_train)

# Make predictions on the test data for pitchers
y_pitcher_pred = pitcher_model.predict(X_pitcher_test)

# Evaluate the performance of the pitcher model
pitcher_RMSE = mean_squared_error(y_pitcher_test, y_pitcher_pred, squared=False)
print('Pitcher Root Mean Squared Error:', pitcher_RMSE)

# Prepare the data for training for hitters
X_hitter = hitter_data[hitter_features]
y_hitter = hitter_data[hitter_target]
scaler_hitter = StandardScaler()
X_hitter_scaled = scaler_hitter.fit_transform(X_hitter)

# Cross-validation for hitters
hitter_models = [LinearRegression(), Lasso(), Ridge()]
for model in hitter_models:
    scores = cross_val_score(model, X_hitter_scaled, y_hitter, cv=5, scoring='neg_root_mean_squared_error')
    print(f"{model.__class__.__name__} RMSE: {-scores.mean():.2f} +/- {scores.std():.2f}")

# Hyperparameter tuning for hitters
param_grid = {'alpha': np.logspace(-3, 3, 7)}
hitter_lasso = Lasso()
hitter_ridge = Ridge()
hitter_lasso_cv = GridSearchCV(hitter_lasso, param_grid, cv=5, scoring='neg_root_mean_squared_error')
hitter_ridge_cv = GridSearchCV(hitter_ridge, param_grid, cv=5, scoring='neg_root_mean_squared_error')
hitter_lasso_cv.fit(X_hitter_scaled, y_hitter)
hitter_ridge_cv.fit(X_hitter_scaled, y_hitter)
print(f"Lasso RMSE: {-hitter_lasso_cv.best_score_:.2f} (alpha={hitter_lasso_cv.best_params_['alpha']})")
print(f"Ridge RMSE: {-hitter_ridge_cv.best_score_:.2f} (alpha={hitter_ridge_cv.best_params_['alpha']})")

# Train a linear regression model for hitters with the best hyperparameters
hitter_model = Ridge(alpha=hitter_ridge_cv.best_params_['alpha'])
X_hitter_train, X_hitter_test, y_hitter_train, y_hitter_test = train_test_split(X_hitter_scaled, y_hitter, test_size=0.2, random_state=42)
hitter_model.fit(X_hitter_train, y_hitter_train)

# Make predictions on the test data for hitters
y_hitter_pred = hitter_model.predict(X_hitter_test)

# Evaluate the performance of the hitter model
hitter_RMSE = mean_squared_error(y_hitter_test, y_hitter_pred, squared=False)
print('Hitter Root Mean Squared Error:', hitter_RMSE)
