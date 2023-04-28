import os
import openai
import pandas as pd
import numpy as np
from ortools.sat.python import cp_model
from sklearn.model_selection import GridSearchCV
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestRegressor

# Define constants
SALARY_CAP = 50000

# Set up OpenAI API credentials
openai.api_key = os.environ['OPENAI_API_KEY']

def load_data():
    print("Loading data...")  # Added print statement
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

    print("Data loaded")  # Added print statement
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
    # Check for missing values and duplicates
    br_data.dropna(inplace=True)
    fg_data.dropna(inplace=True)
    br_data.drop_duplicates(inplace=True)
    fg_data.drop_duplicates(inplace=True)

    # Merge the data from Baseball-Reference and FanGraphs
    data = pd.merge(br_data, fg_data, on='name', how='inner')

    # Filter data for players with salary information
    data = data[data['salary'].notnull()]

    # Create new features based on existing ones
    data['OPS'] = data['OBP'] + data['SLG']
    data['K/BB'] = data['SO'] / data['BB']

    # Split data into features and target
    X = data.drop(['name', 'salary'], axis=1)
    y = data['salary']

    # Perform a grid search to find the best hyperparameters for the model
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [5, 10, 15],
        'min_samples_split': [2, 5, 10]
    }

    model = RandomForestRegressor(random_state=42)
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, n_jobs=-1)
    grid_search.fit(X_train, y_train)
    best_params = grid_search.best_params_
    model = RandomForestRegressor(n_estimators=best_params['n_estimators'],
                                   max_depth=best_params['max_depth'],
                                   min_samples_split=best_params['min_samples_split'],
                                   random_state=42)

    # Train a random forest regression model
    model.fit(X, y)

    # Make predictions on the data
    X_test = data.drop(['name', 'salary'], axis=1)
    y_pred = model.predict(X_test)
    data['predicted_salary'] = y_pred

    # Calculate projected points for each player
    data['projected_points'] = np.random.normal(data['points'].mean(), data['points'].std(), size=len(data))

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

    # Load the data from Baseball-Reference and FanGraphs
    br_data, fg_data = load_data()
    print("Data loaded")  # Added print statement

    # Train a random forest regression model on the data
    model = train_model(br_data)

    # Make salary predictions on the FanGraphs data
    fg_data_with_predictions = get_predictions(model, fg_data)

    # Generate the optimal lineup
    optimal_lineup = get_optimal_lineup(br_data, fg_data_with_predictions)

    # Print the optimal lineup
    print("Optimal Lineup:")
    for player in optimal_lineup:
        print(f"{player['position']}: {player['name']} (Salary: {player['salary']}, Expected Points: {player['expected_points']})")

if __name__ == "__main__":
    main()