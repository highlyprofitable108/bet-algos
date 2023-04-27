import datetime
import numpy
import pandas as pd

# Define constants
SALARY_CAP = 50000

def load_data():
    # Retrieve data from Baseball-Reference
    br_url = 'https://www.baseball-reference.com/leagues/MLB/2021-standard-batting.shtml'
    br_data = pd.read_html(br_url)[0]

    # Clean the data
    br_data = br_data.drop(br_data.index[br_data['Rk'] == 'Rk'])
    br_data = br_data.rename(columns={'Name': 'name'})

    return br_data

def train_model(data):
    # Split data into features and target
    X = data.drop(['name', 'salary'], axis=1)
    y = data['salary']

    # Train a linear regression model
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
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

def get_optimal_lineup(data, num_simulations=50000):
    # Filter data for players with salary information
    data = data[data['salary'].notnull()]

    # Split data into features and target
    X = data.drop(['name', 'salary'], axis=1)
    y = data['salary']

    # Train a linear regression model
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(X, y)

    # Make predictions on the data
    X_test = data.drop(['name', 'salary'], axis=1)
    y_pred = model.predict(X_test)
    data['predicted_salary'] = y_pred

    # Calculate projected points for each player
    data['projected_points'] = np.random.normal(data['points'].mean(), data['points'].std(), size=len(data))

    # Generate optimal lineup
    from ortools.sat.python import cp_model

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
    lineup_points = []
    for i in range(num_simulations):
        lineup_points.append(sum(np.random.choice([player['projected_points'] for player in optimal_lineup], replace=False, size=9)))

    expected_points = np.mean(lineup_points)

    # Add expected points to lineup information
    for player in optimal_lineup:
        player['expected_points'] = player['projected_points'] / expected_points * 100

    # Sort lineup by expected points
    optimal_lineup = sorted(optimal_lineup, key=lambda x: x['expected_points'], reverse=True)

    return optimal_lineup

def main():
    # Load data
    data = load_data()

    # Generate pricing data for today's date
    date = datetime.date.today().strftime('%Y-%m-%d')
    pricing_data = pd.DataFrame({'name': data['name'], 'position': data['position'], 'salary': data['salary']})

    # Train model and get predictions
    model = train_model(data)
    predictions = get_predictions(model, data)

    # Generate top 10 lineups for today's date
    top_lineups = []
    for i in range(10):
        # Get optimal lineup
        lineup = get_optimal_lineup(predictions)

        # Write lineup to file
        with open(f"output/lineup_{date}_{i+1}.txt", 'w') as f:
            f.write(f"Lineup {i+1}:\n")
            for player in lineup:
                f.write(f"{player['name']} ({player['position']}) - ${player['salary']} - {player['projected_points']:.2f} points - {player['expected_points']:.2f}% of expected points\n")
            f.write(f"Total salary: ${sum(player['salary'] for player in lineup)}\n")
            f.write(f"Expected points: {expected_points:.2f}\n")

        # Add lineup to list of top lineups
        top_lineups.append(lineup)

    # Print top 10 lineups
    print(f"Top 10 lineups for {date}:")
    for i, lineup in enumerate(top_lineups):
        print(f"Lineup {i+1}:")
        for player in lineup:
            print(f"{player['name']} - ${player['salary']}")
        print(f"Total salary: ${sum(player['salary'] for player in lineup)}")
        print()
