import ast
from getHouseholdData import get_current_producer_list, get_data_from_file, get_current_consumer_list


def delete_active_producers_as_possbile_consumers(household_data,tradingCostDict):
    """ This function removes all active producers as possible consumers from the
        tradingCost dictionary. This needs to be done as the tradingCost dictionary
        contains costs for every possible household pair. Thus it needs to be assured
        that prosumer households who currently supply electricity aren't wrongly
        interpreted as consumers"""

    keysToRemove = get_current_producer_list(household_data)
    cleanedDic = tradingCostDict.copy()
    #this meterId couldnt be connected with API_data so needs to be deleted
    keysToRemove.append('NO_METER_AVAILABLE')

    #removing entrys from dictionary
    for meterIds, tradingCost in tradingCostDict.items():
        for id in keysToRemove:
            if str(id) == str(meterIds[1]):
                del (cleanedDic[meterIds])

    return cleanedDic




def delete_inactive_producers(household_data, tradingCostDict):
    """ this function removes all inactive producer Ids from the tradingCost dictionary.
        This needs to be done as the tradingCost dictionary contains costs for every
        possible household pair. Thus it needs to be assured that prosumer households
        who currently demand electricity aren't wrongly interpreted as producers"""

    activeProducers = get_current_producer_list(household_data)
    activeCleanedDic = delete_active_producers_as_possbile_consumers(household_data,tradingCostDict).copy()

    for meterIds, tradingCost in delete_active_producers_as_possbile_consumers(household_data,tradingCostDict).items():
        if meterIds[0] not in activeProducers:
            del(activeCleanedDic[meterIds])

    return activeCleanedDic


