import argparse
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

def load_data(filepath):
    """Load test data."""
    return pd.read_csv(filepath)

def load_model(filepath):
    """Load trained model."""
    return joblib.load(filepath)

def evaluate_performance(model, X_test, y_test):
    """Evaluate model performance."""
    y_pred = model.predict(X_test)
    mse = np.mean((y_test - y_pred)**2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(y_test - y_pred))
    r2 = model.score(X_test, y_test)
    explained_var = 1 - (np.var(y_test - y_pred) / np.var(y_test))
    print('Model Performance:')
    print(f'- RMSE: {rmse:.2f}')
    print(f'- MAE: {mae:.2f}')
    print(f'- R^2: {r2:.2f}')
    print(f'- Explained Variance: {explained_var:.2f}')
    return y_pred

def visualize_performance(y_test, y_pred):
    """Visualize model performance."""
    plt.scatter(y_test, y_pred)
    plt.title('Model Performance')
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    plt.show()

def save_predictions(y_test, y_pred, filepath):
    """Save predicted values to csv."""
    pred_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
    pred_df.to_csv(filepath, index=False)

def main():
    parser = argparse.ArgumentParser(description='Test trained pitcher performance prediction model.')
    parser.add_argument('test_data_file', type=str, help='filepath of test data csv')
    parser.add_argument('model_file', type=str, help='filepath of trained model')
    parser.add_argument('predictions_file', type=str, help='filepath to save predicted values csv')
    args = parser.parse_args()

    # Load data and model
    test_data = load_data(args.test_data_file)
    model = load_model(args.model_file)

    # Define target and features
    pitcher_target = 'proj_DK_pts_per_inn'
    pitcher_features = ['ERA', 'WHIP', 'K/9', 'BB/9', 'HR/9', 'FIP', 'xFIP', 'SwStr%', 'LOB%']

    # Prepare test data
    X_test = test_data[pitcher_features].values
    y_test = test_data[pitcher_target].values

    # Evaluate model performance
    y_pred = evaluate_performance(model, X_test, y_test)

    # Visualize model performance
    visualize_performance(y_test, y_pred)

    # Save predicted values to csv
    save_predictions(y_test, y_pred, args.predictions_file)

if __name__ == '__main__':
    main()
