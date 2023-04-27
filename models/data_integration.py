import pandas as pd

def get_combined_data():
    # Retrieve data from Baseball-Reference
    br_url = 'https://www.baseball-reference.com/leagues/MLB/2021-standard-batting.shtml'
    br_data = pd.read_html(br_url)[0]

    # Retrieve data from FanGraphs
    fg_url = 'https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season=2021&month=0&season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=&enddate='
    fg_data = pd.read_html(fg_url)[10]

    # Clean and merge the data
    br_data = br_data.drop(br_data.index[br_data['Rk'] == 'Rk'])
    br_data = br_data.rename(columns={'Name': 'Player'})
    fg_data = fg_data.rename(columns={'Name': 'Player'})
    combined_data = pd.merge(br_data, fg_data, on='Player', how='outer')

    return combined_data
