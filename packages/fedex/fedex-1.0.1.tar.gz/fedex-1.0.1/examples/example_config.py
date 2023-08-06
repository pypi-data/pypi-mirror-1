"""
This file holds various configuration options used for all of the examples.
"""
import os
import sys
# Use the fedex directory included in the downloaded package instead of
# any globally installed versions.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fedex.config import FedexConfig

CONFIG_OBJ = FedexConfig(key='txCf12dOfHg99RCt',
                         password='7A3Q73u6ygBlVKRUkyAEd9qL7',
                         account_number='248430818',
                         meter_number='101397836',
                         use_test_server=False)