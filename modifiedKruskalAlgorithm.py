from ascendingOrderCostDict import order_costDict_in_ascending_order
import json
from getHouseholdData import get_data_from_file, get_current_producer_list, get_current_consumer_list, \
    get_current_producer_ids_to_supply_value, get_current_consumer_ids_to_demand_value
from balanceSupplyAndDemand import excess_demand, excess_supply
from activeCostDict import delete_inactive_producers
import json
import csv
import ast
import timeit
import os


def run_kruskal(consumerDemand, producerSupply, costDict):
    """ This Function runs the kruskal algorithm.
        It loops through the ascendingOrderCostDict and returns a list with
        all tradingCost and a dictionary which contains the meterIds of
        a trading pair matched to the traded amount"""

    # statistics
    tradingCosts = []
    tradedAmount = {}
    tradingCostsOfPairs = {}

    # modified Kruskal
    for matchedHouseholds, cost in costDict.items():

        # getting producer and consumer Id
        producerId = matchedHouseholds[0]
        consumerId = matchedHouseholds[1]

        # getting demand and supply value
        try:
            demandValue = consumerDemand[consumerId]
            supplyValue = producerSupply[producerId]

        except KeyError:
            # KeyError needs to be handled as number of households in the community isn't constant over time
            continue

        # find maximal possible trading amount for household pair
        tradedValue = min(demandValue, supplyValue)

        # update consumerDemand and producerSupply
        update_demandValue = demandValue - tradedValue
        update_supplyValue = supplyValue - tradedValue
        consumerDemand[consumerId] = update_demandValue
        producerSupply[producerId] = update_supplyValue

        # find tradingCosts
        tradeKosten = tradedValue * cost
        tradingCosts.append(tradeKosten)

        # for traceability add pair and traded amount to TradedAmount
        tradedAmount[(producerId, consumerId)] = tradedValue
        tradingCostsOfPairs[((producerId, consumerId))] = cost

    # find lowest trading price in community
    key_lowest = min(tradingCostsOfPairs, key=tradingCostsOfPairs.get)
    lowestPrice = tradingCostsOfPairs[key_lowest]
    key_highest = max(tradingCostsOfPairs, key=tradingCostsOfPairs.get)
    highestPrice = tradingCostsOfPairs[key_highest]

    return tradingCosts, tradedAmount, lowestPrice, highestPrice


def get_total_traded_amount(tradedAmount):
    """ this function returns the sum of all traded watt hours as totalAmount"""

    amounts = []
    for matchedHouseholds, amount in tradedAmount.items():
        amounts.append(amount)
    totalAmount = sum(amounts)

    return totalAmount


def get_total_tradingCosts(tradingCosts):
    """ this function returns the totaltradingCosts for the Kruskal algorithm"""

    totalTradingCost = sum(tradingCosts)

    return totalTradingCost


def main():

    #--------------load input data ---------------------------

    with open('pairsAndReductions.json', 'r') as file:
        pairs_and_reductions = json.load(file)

    with open('new_tradingCost_prosumers_to_all_households_tuples.json', 'r') as f:
        tempdata = json.load(f)
        tradingCostDict = ast.literal_eval(tempdata)


    data = '07_01_2020_13_00_00.json'

    #------------ algorithm ---------------------------------
    start_time_dataPrep = timeit.default_timer()
    household_data = get_data_from_file(data)
    activeCostDictionary = delete_inactive_producers(household_data, tradingCostDict)
    activeProducers = get_current_producer_list(household_data)
    activeConsumers = get_current_consumer_list(household_data)
    consumerDemand, totalCurrentDemand = get_current_consumer_ids_to_demand_value(household_data)
    producerSupply, totalCurrentSupply = get_current_producer_ids_to_supply_value(household_data)

    """check which case is the current one
    
        1. demand > supply
        2. demand = supply
        3. demand < supply """
    if len(activeProducers) > 0:
        # case 1
        if totalCurrentDemand > totalCurrentSupply:
            # print("------------------------------------------------------------------------------------")
            #   print("case 1: The total demand in the community is higher than total supply")

            # balancing the problem
            consumerDemand, proportionalEnercitySupply = excess_demand(totalCurrentDemand, totalCurrentSupply,
                                                                       consumerDemand, activeConsumers)

            # get time for data preparation
            end_time_dataPrep = timeit.default_timer()
            data_prep_time = end_time_dataPrep - start_time_dataPrep

            # run kruskal algorithm
            start_time_kruskal = timeit.default_timer()

            # order the current cost dictionary
            costDict = order_costDict_in_ascending_order(activeCostDictionary)

            tradingCosts, tradedAmount, lowestPrice, highestPrice = run_kruskal(consumerDemand, producerSupply,
                                                                                costDict)
            end_time_kruskal = timeit.default_timer()

            runtime_kruskal = end_time_kruskal - start_time_kruskal

            # print how much power had to be bought from outside the community
            externalTradeAmount = totalCurrentDemand - totalCurrentSupply
        # print("------------------------------------------------------------------------------------")
        #   print(str(externalTradeAmount) + "units of power have been bought from outside the community")

        # case 2
        # no further actions needed as the necessary requirement of the transportation problem is fulfilled
        if totalCurrentDemand == totalCurrentSupply:
            # get time for data preparation
            end_time_dataPrep = timeit.default_timer()
            data_prep_time = end_time_dataPrep - start_time_dataPrep

            # run kruskal algorithm
            start_time_kruskal = timeit.default_timer()

            # order the current cost dictionary
            costDict = order_costDict_in_ascending_order(activeCostDictionary)

            tradingCosts, tradedAmount, lowestPrice, highestPrice = run_kruskal(consumerDemand, producerSupply,
                                                                                costDict)
            end_time_kruskal = timeit.default_timer()

            runtime_kruskal = end_time_kruskal - start_time_kruskal

        # case 3
        if totalCurrentDemand < totalCurrentSupply:
            #    print("------------------------------------------------------------------------------------")
            #   print("case 3: total demand in the community is lower than total supply")

            # balancing the problem
            producerSupply, proportionalEnercityDemand = excess_supply(totalCurrentDemand, totalCurrentSupply,
                                                                       producerSupply, activeProducers)

            # get time for data preparation
            end_time_dataPrep = timeit.default_timer()
            data_prep_time = end_time_dataPrep - start_time_dataPrep

            # run kruskal algorithm
            start_time_kruskal = timeit.default_timer()

            # order the current cost dictionary
            costDict = order_costDict_in_ascending_order(activeCostDictionary)
            tradingCosts, tradedAmount, lowestPrice, highestPrice = run_kruskal(consumerDemand, producerSupply,
                                                                                costDict)

            end_time_kruskal = timeit.default_timer()

            runtime_kruskal = end_time_kruskal - start_time_kruskal

            externalTradeAmount = totalCurrentSupply - totalCurrentDemand

            # print how much power was sold to outside of the community
            externalTradeAmount = totalCurrentDemand - totalCurrentSupply
        #    print("------------------------------------------------------------------------------------")
        #     print(str(externalTradeAmount) + "units of power have been bought from outside the community")

        # print price per unit
        #   print("------------------------------------------------------------------------------------")
        #  print("reached price of power traded in the BloGPV-Community in this 15 minute period was ")
        #  print((get_total_tradingCosts(tradingCosts) / get_total_traded_amount(tradedAmount)))
        #  print("per unit")
        # print("------------------------------------------------------------------------------------")

        # ------------ check for used reductions -----------------------------------
        tradingPairs = list(tradedAmount.keys())

        """ suche die jeweiligen Hebel aus """
        used_reductions = {}
        konz_difference = []
        konz_differencePairs = []
        net_difference = []
        net_differencePairs = []
        localDistancePairs = []
        localDistance = []

        for matchedhouseholds in tradingPairs:
            producerId = matchedhouseholds[0]
            consumerId = matchedhouseholds[1]

            if pairs_and_reductions[producerId][consumerId]['lokalDistance'] == True:
                # this checks if this householdpair is already in the current statistic
                if matchedhouseholds not in localDistancePairs:
                    localDistancePairs.append(matchedhouseholds)
                    localDistance.append(1)

            if pairs_and_reductions[producerId][consumerId]['konzessionsDifference'] > 0:
                # this checks if this householdpair is already in the current statistic
                if matchedhouseholds not in konz_differencePairs:
                    konz_differencePairs.append(matchedhouseholds)
                    konz_difference.append(1)

            if pairs_and_reductions[producerId][consumerId]['netCostDifference'] > 0:
                # this checks if this householdpair is already in the current statistic
                if matchedhouseholds not in net_differencePairs:
                    net_differencePairs.append(matchedhouseholds)
                    net_difference.append(1)

        # used_reduction to track which price reduction have been used
        used_reductions['konzessionsDifference'] = sum(konz_difference)
        used_reductions['netCostDifference'] = sum(net_difference)
        used_reductions['lokalDistance'] = sum(localDistance)
        used_reductions['numberOfPairs'] = len(tradingPairs)


        # ------------------ data for analysis------------------------------------

        # save data from Kruskal to a dictionary
        results = {}
        results['totalCosts'] = get_total_tradingCosts(tradingCosts) / 1000
        results['totalTradedWatts'] = sum(tradedAmount.values()) / 1000
        results['averagePrice'] = (get_total_tradingCosts(tradingCosts) / get_total_traded_amount(tradedAmount))
        results['maximumPrice'] = highestPrice
        results['minimumPrice'] = lowestPrice
        results['runningTime'] = runtime_kruskal
        results['dataPrepTime'] = data_prep_time
        results['numberOfProducers'] = len(activeProducers)
        results['numberOfConsumers'] = len(activeConsumers)
        results['usedReductions'] = used_reductions
        results['timestamp'] = household_data['time']
        results['tradedAmounts'] = tradedAmount

        print(results)


    else:
        # time for data prep
        end_time_dataPrep = timeit.default_timer()
        data_prep_time = end_time_dataPrep - start_time_dataPrep
        results = {}
        results['totalCosts'] = 0
        results['totalTradedWatts'] = 0
        results['averagePrice'] = 30

        results['maximumPrice'] = 30
        results['minimumPrice'] = 30
        results['runningTime'] = 0
        results['dataPrepTime'] = data_prep_time
        results['numberOfProducers'] = len(activeProducers)
        results['numberOfConsumers'] = len(activeConsumers)
        results['usedReductions'] = 0
        results['timestamp'] = household_data['time']
        results['tradedAmounts'] = 0

        print(results)

if __name__ == '__main__':
    main()