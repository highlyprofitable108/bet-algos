mport pandas as pd
from models.data_integration import get_combined_data
from models.lineup_optimizer import generate_optimal_lineup

# Load pricing data
pricing_data = pd.read_csv('data/pricing.csv')

# Load data from multiple sources
data = get_combined_data()

# Generate optimal lineups
optimal_lineups = generate_optimal_lineup(data, pricing_data, num_lineups=10)

# Print the top 10 lineups
for i, lineup_data in enumerate(optimal_lineups):
    print(f"Lineup {i+1}:")
    print(lineup_data['lineup'])
    print(f"Projected points: {lineup_data['lineup_points']:.2f}")
    print("Player projected points:")
    for j, player_points in enumerate(lineup_data['player_points']):
        print(f"{lineup_data['lineup'][j]}: {player_points:.2f}")
    print()
