import pytest
import pandas as pd
from data.dk import get_dk_pricing

def test_dk_pricing():
    # Load Lahman data
    lahman_data = pd.read_csv('data/lahman.csv')

    # Get DraftKings pricing data
    dk_pricing = get_dk_pricing()

    # Compare pricing data to Lahman data
    for name, price in dk_pricing.items():
        player = lahman_data.loc[lahman_data['name'] == name]
        assert not player.empty
        assert player.iloc[0]['salary'] == price
