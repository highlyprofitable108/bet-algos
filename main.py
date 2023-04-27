import openai
import datetime
import pandas as pd
import numpy as np
import lxml

# Define constants
SALARY_CAP = 50000

# Set up OpenAI API credentials
openai.api_key = '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'

def load_data():
    # Retrieve data from Baseball-Reference
    br_url = 'https://www.baseball-reference.com/leagues/MLB/2021-standard-batting.shtml'
    br_data = pd.read_html(br_url)[0]

    # Clean the data
    if 'Rk' in br_data.columns:
        br_data = br_data.drop(br_data.index[br_data['Rk'] == 'Rk'])
        br_data = br_data.rename(columns={'Name': 'name'})

    # Retrieve data from FanGraphs
    fg_url = 'https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season=2021&month=0&season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=&enddate='
    fg_data = pd.read_html(fg_url)[10]

    # Clean the data
    if 'RK' in fg_data.columns:
        fg_data = fg_data.drop(fg_data.index[fg_data['RK'] == 'RK'])
    fg_data = fg_data.rename(columns={'Name': 'name', 'Team': 'team', 'G': 'games', 'PA': 'plate_appearances', 'HR': 'home_runs', 'R': 'runs', 'RBI': 'runs_batted_in', 'SB': 'stolen_bases', 'BB%': 'walk_percentage', 'K%': 'strikeout_percentage', 'ISO': 'isolated_power', 'BABIP': 'batting_average_on_balls_in_play', 'AVG': 'batting_average', 'OBP': 'on_base_percentage', 'SLG': 'slugging_percentage', 'wOBA': 'weighted_on_base_average', 'wRC+': 'weighted_runs_created_plus'})


    # Match Baseball-Reference player names to FanGraphs player names
    br_data['name'] = br_data['name'].str.replace('[^\w\s]','').str.lower()
    fg_data['name'] = fg_data['Name'].str.replace('[^\w\s]','').str.lower()

	# Merge the data
    data = pd.merge(br_data, fg_data, on='name')

    
    return data

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

def get_lineup_explanations(lineups):
    # Generate explanations for each lineup
    explanations = []
    for lineup in lineups:
        # Generate text prompt for OpenAI API
        prompt = f"Explain the reasoning behind the optimal baseball lineup for today's games: {', '.join([player['name'] for player in lineup])}"

        # Call OpenAI API to generate explanation
        response = openai.Completion.create(
            engine='text-davinci-002',
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )

        # Extract explanation from API response
        explanation = response.choices[0].text.strip()
        explanations.append(explanation)

    return explanations

if __name__ == '__main__':
    # Load data
    data = load_data()

    # Train model and make predictions
    model = train_model(data)
    data = get_predictions(model, data)

    # Generate optimal lineup
    lineups = [get_optimal_lineup(data) for _ in range(10)]

    # Generate explanations for each lineup
    explanations = get_lineup_explanations(lineups)

    # Print the lineup and explanation for each simulation
    for i, lineup in enumerate(lineups):
        print(f"Simulation {i+1}:")
        for player in lineup:
            print(f"{player['name']} ({player['position']}): ${player['salary']}, {player['projected_points']:.2f} projected points, {player['expected_points']:.2f}% of total points")
        print(f"Explanation: {explanations[i]}")
        print()
