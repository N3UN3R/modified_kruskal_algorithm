import json

def create_tuple_costDict():
    """ function that reads in a nested dictionary with all possible costs
        and returns a dictionary with matched households and the specific costs of
        each pair
        the returned dictionary is saved to a json file called
        'trading_costs_tuples"""

    with open('500750consumer500_producer750_costs.json','r') as data:
        costs = json.load(data)

    tuple_dict = {}

    for prosumerId, matchedHouseholds in costs.items():
        for householdId, cost in matchedHouseholds.items():
            tuple_dict[(prosumerId,householdId)] = round(cost,5)*10**5

    with open(('consumer500_producer750_tupleCosts.json'),'w') as file:
        json.dump(str(tuple_dict),file)

    return tuple_dict


print(create_tuple_costDict())