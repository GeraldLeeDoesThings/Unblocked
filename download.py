import os
import json
from web3 import Web3, HTTPProvider


def make_serializable(val):
    val_type = type(val).__name__
    if val_type == "HexBytes":
        return val.hex()
    elif val_type == "list":
        return make_list_serializable(val)
    elif val_type == "dict":
        return make_dict_serializable(val)
    elif val_type == "AttributeDict":
        return make_serializable(val.__dict__)
    return val


def make_dict_serializable(data: dict):
    for key in data.keys():
        data[key] = make_serializable(data[key])
    return data


def make_list_serializable(data: list):
    return [make_serializable(val) for val in data]


# using web3py
url = "https://eth-mainnet.alchemyapi.io/v2/" + os.environ["ALCHEMY_KEY"]
web3 = Web3(HTTPProvider(url))

current_block = web3.eth.get_block('latest', True)
num_blocks = current_block['number']
current_block_num = num_blocks
aggregate = {}

num_transactions = 2  # change this to however many transactions you wish to save

while current_block_num > num_blocks - num_transactions:
    current_block = web3.eth.get_block(current_block_num, True)
    serialized_block = make_serializable(current_block)
    aggregate[current_block_num] = json.dumps(serialized_block)
    current_block_num = current_block_num - 1
    print(f"{num_blocks - current_block_num}/"f"{num_transactions}")

with open("data.json", "w") as file:
    json.dump(aggregate, file)
