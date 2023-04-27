from ortools.sat.python import cp_model
import pandas as pd

def generate_optimal_lineup(data, pricing_data, num_lineups=10):
    # Define constants
    position_names = ['C', '1B', '2B', '3B', 'SS', 'OF', 'OF', 'OF']
    salary_cap = 50000

    # Create model
    model = cp_model.CpModel()

    # Define decision variables
    lineup_vars = [model.NewIntVar(0, len(data)-1, f'player_{i}') for i in range(len(position_names))]

    # Define constraints
    model.Add(sum([data.loc[i, 'Salary'] * (lineup_vars.count(i) == 1) for i in range(len(data))]) <= salary_cap)
    for i, pos in enumerate(position_names):
        model.Add(lineup_vars.count(i) == 1)
        model.Add(data.loc[lineup_vars[i], 'Position'] == pos)

    # Define objective function
    model.Maximize(sum([data.loc[lineup_vars[i], 'Points'] for i in range(len(position_names))]))

    # Generate multiple lineups
    lineups = []
    for i in range(num_lineups):
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        players = data['Player'].tolist()
        lineup = pd.Series([players[x] for x in lineup_vars], index=position_names)
        lineups.append(lineup)
        # Add constraint to exclude previously found lineup
        excluded_vars = [model.NewBoolVar(f'excluded_{i}') for i in range(len(lineup_vars))]
        for j, player in enumerate(lineup_vars):
            model.AddBoolOr([excluded_vars[j], player != solver.Value(player)])
            model.AddBoolOr([excluded_vars[j], player == solver.Value(player)])
        model.Add(sum(excluded_vars) >= 1)

    return lineups
