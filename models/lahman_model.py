```python
import pandas as pd

# Define constants
SALARY_CAP = 50000

def load_data():
    # Load Lahman data
    lahman_data = pd.read_csv('data/lahman.csv')

    # Convert salary data to integers
    lahman_data['salary'] = lahman_data['salary'].astype(int)

    return lahman_data

def train_model(data):
    # Split data into features and target
    X = data.drop(['name', 'salary', 'position', 'team'], axis=1)
    y = data['salary']

    # Train a linear regression model
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(X, y)

    return model

def get_predictions(model, data):
    # Make predictions on the data
    X = data.drop(['name', 'salary', 'position', 'team'], axis=1)
    predictions = model.predict(X)

    # Combine predictions with player names and positions
    data = data[['name', 'position', 'salary']].copy()
    data['predicted_score'] = predictions

    return data

def get_optimal_lineup(predictions, pricing):
    # Combine predictions and pricing data
    data = pd.concat([predictions, pricing], axis=1)

    # Sort by predicted score in descending order
    data = data.sort_values(by='predicted_score', ascending=False)

    # Select the top 9 players by predicted score
    top_players = data.head(9)

    # Calculate the total cost of the top players
    total_cost = top_players['salary'].sum()

    # Check if total cost is within the salary cap
    if total_cost > SALARY_CAP:
        # If total cost is over the salary cap, select the top 9 players within the salary cap
        top_players = data[data['salary'] <= SALARY_CAP].head(9)

    # Sort by position and then by predicted score in descending order
    top_players = top_players.sort_values(by=['position', 'predicted_score'], ascending=[True, False])

    # Create the lineup as a list of dictionaries
    lineup = []
    for _, row in top_players.iterrows():
        player = {'name': row['name'], 'position': row['position'], 'price': row['salary']}
        lineup.append(player)

    return lineup

def main():
    # Load data
    data = load_data()

    # Train model
    model = train_model(data)

    # Loop through dates and generate top 10 lineups for each day
    for date in pd.date_range(start='2022-01-01', end='2022-01-10'):
        # Filter data for current date
        date_data = data[data['date'] == date]

        # Get predictions for current date
        predictions = get_predictions(model, date_data)

        # Load pricing data for current date
        pricing_file = f"data/pricing_{date.strftime('%Y-%m-%d')}.csv"
        pricing = pd.read_csv(pricing_file)

        # Generate top 10 lineups for current date
        for i in range(10):
            # Get optimal lineup
            lineup = get_optimal_lineup(predictions, pricing)

            # Write lineup to file
            with open(f"output/lineup_{date.strftime('%Y-%m-%d')}_{i+1}.txt", 'w') as f:
                for player in lineup:
                    f.write(f"{player['name']} ({player['position']}) - ${player['salary']}\n")

            # Remove players from pricing data
            for player in lineup:
                pricing = pricing[pricing['name'] != player['name']]

if __name__ == '__main__':
    main()
