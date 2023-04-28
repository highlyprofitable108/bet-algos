import os
import openai
import requests
import pandas as pd
import numpy as np
from ortools.sat.python import cp_model
from sklearn.model_selection import GridSearchCV
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


# Define constants
SALARY_CAP = 50000

# Set up OpenAI API credentials
openai.api_key = os.environ['OPENAI_API_KEY']

def load_data():
    print("Loading data...")

    # Retrieve data from Baseball-Reference
    br_url = 'https://www.baseball-reference.com/leagues/majors/2023-value-batting.shtml#players_value_batting'
    print("URL:", br_url)

    # read the HTML table into a pandas dataframe
    br_data = pd.read_html(br_url)[1]

    # filter the rows based on the first column
    filter_rows = br_data.iloc[:, 0].isin(['Rk', '1'])

    # get the index of the first row where the condition is true
    start_idx = filter_rows.idxmax()

    # slice the dataframe to get the desired table
    br_data = br_data.iloc[start_idx:, :]

    # reset the index
    br_data.reset_index(drop=True, inplace=True)

    print("Data loaded")
    print("br_data columns:", br_data.columns)
    return br_data

def train_model(data):
    # Split the data into input features (X) and output variable (y)
    X = data.drop(['Salary'], axis=1)
    y = data['Salary']

    # Check if there is enough data to split into training and testing sets
    if len(X) <= 1:
        raise ValueError('Not enough data to split into training and testing sets')

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Fit a linear regression model to the training data
    model = LinearRegression()
    model.fit(X_train, y_train)

    return model


def get_predictions(model, data):
    # Make predictions on the data
    X = data.drop(['name'], axis=1)
    predictions = model.predict(X)

    # Combine predictions with player names
    data = data[['name', 'Salary']].copy()
    data['predicted_salary'] = predictions

    return data

def get_optimal_lineup(br_data, num_simulations=100000):
    # Check for missing values and duplicates
    br_data.dropna(inplace=True)
    br_data.drop_duplicates(inplace=True)

    # Filter data for players with salary information
    data = br_data[br_data['Salary'].notnull()]
    
    # Train a random forest regression model
    model = train_model(data)

    # Make predictions on the data
    data_with_predictions = get_predictions(model, data)

    # Generate optimal lineup
    model = cp_model.CpModel()

    # Define decision variables
    players = data['name'].tolist()
    salaries = data['salary'].tolist()
    predicted_salaries = data['predicted_salary'].tolist()
    projected_points = data['projected_points'].tolist()

    player_vars = {}
    for i, player in enumerate(players):
        player_vars[i] = model.NewBoolVar(player)

    # Define constraints
    # Each lineup must have exactly one player at each position
    positions = ['C', '1B', '2B', '3B', 'SS', 'OF', 'OF', 'OF']
    for position in positions:
        model.Add(sum(player_vars[i] for i in range(len(players)) if position in player) == 1)

    # The total salary of the lineup must be less than or equal to the salary cap
    model.Add(sum(player_vars[i] * (salaries[i] + predicted_salaries[i]) for i in range(len(players))) <= SALARY_CAP)

        # Define objective function
    objective_coeffs = [(salaries[i] + predicted_salaries[i]) * projected_points[i] for i in range(len(players))]
    model.Maximize(sum(objective_coeffs[i] * player_vars[i] for i in range(len(players))))

    # Solve the model
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)

    # Extract the optimal lineup
    optimal_lineup = []
    for i in range(len(players)):
        if solver.Value(player_vars[i]) == 1:
            optimal_lineup.append({
                'name': players[i],
                'position': data.iloc[i]['position'],
                'salary': salaries[i],
                'projected_points': projected_points[i]
            })

    # Run simulations to estimate expected points for each lineup
    lineup_points = Parallel(n_jobs=-1)(delayed(simulate_lineup)(optimal_lineup) for i in range(num_simulations))
    expected_points = np.mean(lineup_points)

    # Add expected points to lineup information
    for player in optimal_lineup:
        player['expected_points'] = player['projected_points'] / expected_points * 100

    # Sort lineup by expected points
    optimal_lineup = sorted(optimal_lineup, key=lambda x: x['expected_points'], reverse=True)

    return optimal_lineup

def simulate_lineup(lineup):
    """Simulate a lineup and return the total points scored."""
    return sum(np.random.choice([player['projected_points'] for player in lineup], replace=False, size=9))

def main():
    # Start the script
    print("Script started")

    # Load the data from Baseball-Reference
    br_data = load_data()
    print("Data loaded")

    # Generate the optimal lineup
    optimal_lineup = get_optimal_lineup(br_data)

    # Print the optimal lineup
    print("Optimal Lineup:")
    for player in optimal_lineup:
        print(f"{player['position']}: {player['name']} (Salary: {player['salary']}, Expected Points: {player['expected_points']})")

if __name__ == "__main__":
    main()