import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

# Load the data
pitcher_data = pd.read_csv('pitcher_data.csv')
hitter_data = pd.read_csv('hitter_data.csv')

# Define the target variable and features for pitchers
pitcher_target = 'proj_DK_pts_per_inn'
pitcher_features = ['ERA', 'WHIP', 'K/9', 'BB/9', 'HR/9', 'FIP', 'xFIP', 'SwStr%', 'LOB%']

# Prepare the data for training for pitchers
X_pitcher = pitcher_data[pitcher_features]
y_pitcher = pitcher_data[pitcher_target]
scaler_pitcher = StandardScaler()
X_pitcher_scaled = scaler_pitcher.fit_transform(X_pitcher)
X_pitcher_train, X_pitcher_test, y_pitcher_train, y_pitcher_test = train_test_split(X_pitcher_scaled, y_pitcher, test_size=0.2, random_state=42)

# Train a linear regression model for pitchers
pitcher_model = LinearRegression()
pitcher_model.fit(X_pitcher_train, y_pitcher_train)

# Make predictions on the test data for pitchers
y_pitcher_pred = pitcher_model.predict(X_pitcher_test)

# Evaluate the performance of the pitcher model
pitcher_RMSE = mean_squared_error(y_pitcher_test, y_pitcher_pred, squared=False)
print('Pitcher Root Mean Squared Error:', pitcher_RMSE)

# Define the target variable and features for hitters
hitter_target = 'proj_DK_pts_per_PA'
hitter_features = ['AVG', 'OBP', 'SLG', 'OPS', 'wOBA', 'wRC+', 'WAR', 'ISO', 'BB%', 'K%']

# Prepare the data for training for hitters
X_hitter = hitter_data[hitter_features]
y_hitter = hitter_data[hitter_target]
scaler_hitter = StandardScaler()
X_hitter_scaled = scaler_hitter.fit_transform(X_hitter)
X_hitter_train, X_hitter_test, y_hitter_train, y_hitter_test = train_test_split(X_hitter_scaled, y_hitter, test_size=0.2, random_state=42)

# Train a linear regression model for hitters
hitter_model = LinearRegression()
hitter_model.fit(X_hitter_train, y_hitter_train)

# Make predictions on the test data for hitters
y_hitter_pred = hitter_model.predict(X_hitter_test)

# Evaluate the performance of the hitter model
hitter_RMSE = mean_squared_error(y_hitter_test, y_hitter_pred, squared=False)
print('Hitter Root Mean Squared Error:', hitter_RMSE)
