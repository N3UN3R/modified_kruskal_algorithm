from collections import OrderedDict
from activeCostDict import delete_inactive_producers
import timeit


def order_costDict_in_ascending_order(activeCostDictionary):
    """ this function gets the updated cost dictionary from activeCostDict.py
        and returns this cost dictionary in ascending order.
        As the cost dictionary could be interpreted as an adjacency list for
        the BloGPV-Community this step equals ordering the weighted edges in
        ascending order"""

    costDict_ordered = OrderedDict(sorted(activeCostDictionary.items(), key=lambda item: item[1]))

    return costDict_ordered






