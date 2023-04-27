import pandas as pd
from models.data_integration import get_combined_data
from models.lineup_optimizer import generate_optimal_lineup

# Load pricing data
pricing_data = pd.read_csv('data/pricing.csv')

# Load data from multiple sources
data = get_combined_data()

# Generate optimal lineup
optimal_lineup = generate_optimal_lineup(data, pricing_data)

# Print the optimal lineup
print(optimal_lineup)
