from getHouseholdData import get_current_consumer_list, get_current_producer_list, get_data_from_file, get_current_producer_ids_to_supply_value, get_current_consumer_ids_to_demand_value

""" this script balances supply and demand.
    For an interpretation as a transportation problem this assumption
    is necessary.
    It has been shown that the transportation problem fulfills all
    requirements made in the netting-paper.

    there's 3 possible cases for the demand - supply relation in the BloGPV-Community

    case 1: demand > supply
    case 2: demand = supply
    case 3: demand < supply """


def excess_demand(totalCurrentDemand, totalCurrentSupply, consumerDemand, activeConsumers):
    """case 1: demand > supply
    to fulfill the proportional fairness requirement every consumer household needs
    to be able to buy a share of the total power supply in the community.
    The proportional share is calculated from:
    proportionalDemand = householdsDemand / totalDemand
    In this case enercitySupply = demand - supply
    is the amount that will come from outside the community.
    By making sure every consumer household buys it's proportional share of enercitySupply
    its secured that demand = supply.
    Thus it fulfills the requirement of the transportation problem."""

    #dictionary for consumerIds and their demand from Enercity
    proportionalEnercitySupply = {}
    enercitySupply = totalCurrentDemand - totalCurrentSupply

    for consumerId in activeConsumers:
        for meterId, demandValue in consumerDemand.items():
            if consumerId == meterId:
                # calculating a households proportional share
                proportionalShare = demandValue / totalCurrentDemand

                # calculating a households trade volume with enercity
                proportionalEnercitySupply[consumerId] = proportionalShare * enercitySupply

                # updating demand dictionary
                consumerDemand[consumerId] -= proportionalShare * enercitySupply

    return consumerDemand, proportionalEnercitySupply


def excess_supply(totalCurrentDemand,totalCurrentSupply, producerSupply, activeProducers):
    """case 3: demand < supply
    to fulfill the proportional fairness requirement every producer household needs
    to be able to sell a share of the total power supply in the community.
    The proportional share is calculated from:
    proportionalSupply = householdsSupply / totalSupply
    In this case enercityDemand = supply - demand
    is the amount that will come from outside the community.
    By making sure every producer household sells it's proportional share of enercityDemand
    its secured that demand = supply.
    Thus it fulfills the requirement of the transportation problem."""

    # dictionary for supply sold to enercity
    proportionalEnercityDemand = {}
    # calculating excess supply
    enercityDemand = totalCurrentSupply - totalCurrentDemand

    for producerId in activeProducers:
        for meterId, supplyValue in producerSupply.items():
            if producerId == meterId:
                # calculating a households proportional share
                proportionalShare = supplyValue / totalCurrentSupply

                # calculating a households proportional selling to enercity
                proportionalEnercityDemand[producerId] = proportionalShare * enercityDemand

                # updating the supply dictionary
                producerSupply[producerId] -= proportionalShare * enercityDemand

    return producerSupply, proportionalEnercityDemand


