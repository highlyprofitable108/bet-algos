import requests

def get_dk_pricing():
    # Make API request to DraftKings to get pricing data
    response = requests.get('https://api.draftkings.com/lineups/v1/featured?format=json')
    data = response.json()

    # Extract pricing data from response
    players = data['draftables']
    pricing_data = {}
    for player in players:
        name = player['displayName']
        price = player['salary']
        pricing_data[name] = price

    return pricing_data
