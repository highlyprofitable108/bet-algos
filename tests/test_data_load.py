import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle

def load_data(batting_filepath, pitching_filepath):
    """Load test data from csv files."""

    batting_data = pd.read_csv(batting_filepath)
    pitching_data = pd.read_csv(pitching_filepath)

    # Combine data and add player positions
    batting_data['position'] = 'B'
    pitching_data['position'] = 'P'
    test_data = pd.concat([batting_data, pitching_data])

    return test_data

def preprocess_data(test_data):
    """Preprocess test data to be compatible with the model."""

    # Remove unnecessary columns and fill NaN values
    test_data = test_data.drop(columns=['playerID', 'yearID'])
    test_data = test_data.fillna(value=0)

    # Standardize numerical features
    numerical_features = ['G', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'SB', 'CS', 'BB', 'SO', 'IBB', 'HBP', 'SH', 'SF', 'GIDP']
    scaler = StandardScaler()
    test_data[numerical_features] = scaler.fit_transform(test_data[numerical_features])

    return test_data

def main():
    # Set filepaths for test data csv files
    batting_filepath = 'test_batting_data.csv'
    pitching_filepath = 'test_pitching_data.csv'

    # Load test data
    test_data = load_data(batting_filepath, pitching_filepath)

    # Preprocess test data
    preprocessed_data = preprocess_data(test_data)

    # Save preprocessed data as .pkl file
    with open('test_preprocessed_data.pkl', 'wb') as f:
        pickle.dump(preprocessed_data, f)

    # Print out information about the preprocessed data
    n_samples = len(preprocessed_data)
    positions = preprocessed_data['position'].unique()
    n_batters = len(preprocessed_data[preprocessed_data['position'] == 'B'])
    n_pitchers = len(preprocessed_data[preprocessed_data['position'] == 'P'])
    print(f'Test data preprocessed. {n_samples} preprocessed samples found, including {n_batters} batters and {n_pitchers} pitchers.')
    print(f'Positions found: {positions}')

if __name__ == '__main__':
    main()
