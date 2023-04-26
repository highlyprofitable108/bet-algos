import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from lahman_model import pitcher_model, hitter_model

# Load the test data
pitcher_test_data = pd.read_csv('pitcher_test_data.csv')
hitter_test_data = pd.read_csv('hitter_test_data.csv')

# Define the target variable and features for pitchers
pitcher_target = 'proj_DK_pts_per_inn'
pitcher_features = ['ERA', 'WHIP', 'K/9', 'BB/9', 'HR/9', 'FIP', 'xFIP', 'SwStr%', 'LOB%']

# Prepare the test data for pitchers
X_pitcher_test = pitcher_test_data[pitcher_features]
y_pitcher_test = pitcher_test_data[pitcher_target]
scaler_pitcher = StandardScaler()
X_pitcher_test_scaled = scaler_pitcher.transform(X_pitcher_test)

# Make predictions on the test data for pitchers
y_pitcher_pred = pitcher_model.predict(X_pitcher_test_scaled)

# Evaluate the performance of the pitcher model on the test data
pitcher_RMSE = mean_squared_error(y_pitcher_test, y_pitcher_pred, squared=False)
print('Pitcher Root Mean Squared Error:', pitcher_RMSE)

# Define the target variable and features for hitters
hitter_target = 'proj_DK_pts_per_PA'
hitter_features = ['AVG', 'OBP', 'SLG', 'OPS', 'wOBA', 'wRC+', 'WAR', 'ISO', 'BB%', 'K%']

# Prepare the test data for hitters
X_hitter_test = hitter_test_data[hitter_features]
y_hitter_test = hitter_test_data[hitter_target]
scaler_hitter = StandardScaler()
X_hitter_test_scaled = scaler_hitter.transform(X_hitter_test)

# Make predictions on the test data for hitters
y_hitter_pred = hitter_model.predict(X_hitter_test_scaled)

# Evaluate the performance of the hitter model on the test data
hitter_RMSE = mean_squared_error(y_hitter_test, y_hitter_pred, squared=False)
print('Hitter Root Mean Squared Error:', hitter_RMSE)
