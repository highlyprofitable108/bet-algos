import openai
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from ortools.sat.python import cp_model

# Define constants
SALARY_CAP = 50000

# Set up OpenAI API credentials
openai.api_key = 'your_api_key_here'

def load_data():
    # Retrieve data from Baseball-Reference
    br_url = 'https://www.baseball-reference.com/leagues/MLB/2023-standard-batting.shtml'
    br_data = pd.read_html(br_url)[0]

    # Clean the data
    if 'Rk' in br_data.columns:
        br_data = br_data.drop(br_data.index[br_data['Rk'] == 'Rk'])
        br_data = br_data.rename(columns={'Name': 'name'})

    # Retrieve data from FanGraphs
    fg_url = 'https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season=2023&month=0&season1=2023&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=&enddate='
    fg_data = pd.read_html(fg_url)[11]

    # Clean the data
    if 'RK' in fg_data.columns:
        fg_data = fg_data.drop(fg_data.index[fg_data['RK'] == 'RK'])
        fg_data = fg_data.rename(columns={'Name': 'name', 'Team': 'team', 'G': 'games', 'PA': 'plate_appearances', 'HR': 'home_runs', 'R': 'runs', 'RBI': 'runs_batted_in', 'SB': 'stolen_bases', 'BB%': 'walk_percentage', 'K%': 'strikeout_percentage', 'ISO': 'isolated_power', 'BABIP': 'batting_average_on_balls_in_play', 'AVG': 'batting_average', 'OBP': 'on_base_percentage', 'SLG': 'slugging_percentage', 'wOBA': 'weighted_on_base_average', 'wRC+': 'weighted_runs_created_plus', 'FIP': 'fielding_independent_pitching'})

    return br_data, fg_data

def train_model(data):
    # Split data into features and target
    X = data.drop(['name', 'salary'], axis=1)
    y = data['salary']

    # Train a random forest regression model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    return model

def get_predictions(model, data):
    # Make predictions on the data
    X = data.drop(['name'], axis=1)
    predictions = model.predict(X)

    # Combine predictions with player names
    data = data[['name', 'salary']].copy()
    data['predicted_salary'] = predictions

    return data

def get_optimal_lineup(br_data, fg_data, num_simulations=100000):
    # Merge the data from Baseball-Reference and FanGraphs
    data = pd.merge(br_data, fg_data, on='name', how='inner')

   
